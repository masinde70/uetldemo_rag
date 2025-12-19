"""
Seed Database with Demo Data for SISUiQ.

This module seeds PostgreSQL with demo data for development/testing.
Run directly: python -m backend.seed
Or via Docker Compose: docker compose exec backend python -m backend.seed

Features:
- Idempotent: uses get_or_create to prevent duplicates
- Async-compatible with project's SQLAlchemy setup
- Prints summary of created vs existing records
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import async_session_maker, engine
from backend.models import (
    AnalyticsSnapshot,
    Base,
    ChatMessage,
    ChatMode,
    ChatSession,
    Document,
    DocumentSource,
    DocumentType,
    MessageRole,
    User,
    UserRole,
)
from backend.services.auth import hash_password

T = TypeVar("T", bound=Base)


# --- Statistics tracking ---
class SeedStats:
    """Track seed operation statistics."""

    def __init__(self):
        self.created: dict[str, int] = {}
        self.existed: dict[str, int] = {}

    def record_created(self, entity: str):
        self.created[entity] = self.created.get(entity, 0) + 1

    def record_existed(self, entity: str):
        self.existed[entity] = self.existed.get(entity, 0) + 1

    def print_summary(self):
        print("\n" + "=" * 50)
        print("🌱 SEED SUMMARY")
        print("=" * 50)

        all_entities = set(self.created.keys()) | set(self.existed.keys())
        for entity in sorted(all_entities):
            created = self.created.get(entity, 0)
            existed = self.existed.get(entity, 0)
            print(f"  {entity}:")
            print(f"    ✅ Created: {created}")
            print(f"    ℹ️  Already existed: {existed}")

        total_created = sum(self.created.values())
        total_existed = sum(self.existed.values())
        print("-" * 50)
        print(f"  TOTAL: {total_created} created, {total_existed} already existed")
        print("=" * 50 + "\n")


stats = SeedStats()


# --- Helper functions ---


async def get_or_create(
    db: AsyncSession,
    model: type[T],
    lookup_field: str,
    lookup_value,
    defaults: dict | None = None,
) -> tuple[T, bool]:
    """
    Get an existing record or create a new one.

    Args:
        db: Database session
        model: SQLAlchemy model class
        lookup_field: Field name to search by
        lookup_value: Value to search for
        defaults: Default values for creating new record

    Returns:
        Tuple of (instance, created) where created is True if new record was made
    """
    stmt = select(model).where(getattr(model, lookup_field) == lookup_value)
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance:
        return instance, False

    # Create new instance
    data = {lookup_field: lookup_value, **(defaults or {})}
    instance = model(**data)
    db.add(instance)
    await db.flush()  # Get ID without committing
    return instance, True


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def past_time(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """Get a time in the past."""
    return utc_now() - timedelta(days=days, hours=hours, minutes=minutes)


# --- Seed functions ---


async def seed_demo_user(db: AsyncSession) -> User:
    """Seed demo admin user with password."""
    user, created = await get_or_create(
        db,
        User,
        lookup_field="email",
        lookup_value="admin@sisuiq.local",
        defaults={
            "name": "Admin User",
            "role": UserRole.ADMIN,
            "password_hash": hash_password("admin123"),
            "is_active": True,
        },
    )

    if created:
        stats.record_created("User")
        print(f"✅ Created admin user: {user.email}")
    else:
        stats.record_existed("User")
        print(f"ℹ️  Admin user already exists: {user.email}")

    # Also create a regular demo user
    demo_user, demo_created = await get_or_create(
        db,
        User,
        lookup_field="email",
        lookup_value="demo@sisuiq.local",
        defaults={
            "name": "Demo User",
            "role": UserRole.USER,
            "password_hash": hash_password("demo123"),
            "is_active": True,
        },
    )

    if demo_created:
        stats.record_created("User")
        print(f"✅ Created demo user: {demo_user.email}")
    else:
        stats.record_existed("User")
        print(f"ℹ️  Demo user already exists: {demo_user.email}")

    return user


async def seed_chat_sessions(db: AsyncSession, user: User):
    """Seed three chat sessions with messages."""

    sessions_data = [
        {
            "mode": ChatMode.STRATEGY_QA,
            "title": "Strategic Plan Questions",
            "created_at": past_time(days=2, hours=3),
            "messages": [
                {
                    "role": MessageRole.USER,
                    "content": "What are the main strategic pillars in UETCL's 2024-2029 plan?",
                    "offset_minutes": 0,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "UETCL's 2024-2029 Strategic Plan is built around five key pillars:\n\n1. **Grid Expansion & Modernization** - Expanding transmission capacity to meet growing demand\n2. **System Reliability** - Improving SAIFI and SAIDI performance indicators\n3. **Financial Sustainability** - Optimizing revenue collection and reducing losses\n4. **Stakeholder Engagement** - Strengthening relationships with ERA and distribution companies\n5. **Talent Development** - Building technical and leadership capabilities\n\nEach pillar has specific KPIs and initiatives defined for the planning period.",
                    "offset_minutes": 1,
                },
                {
                    "role": MessageRole.USER,
                    "content": "What are the target KPIs for system reliability?",
                    "offset_minutes": 5,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "The system reliability KPI targets for 2024-2029 include:\n\n- **SAIFI Target**: Reduce to below 4.0 interruptions per customer per year by 2029\n- **SAIDI Target**: Reduce average outage duration to under 8 hours per customer per year\n- **System Availability**: Maintain grid availability above 99.2%\n- **Fault Response Time**: Reduce average response time to under 2 hours\n\nThese targets are aligned with ERA's performance standards and will be monitored quarterly.",
                    "offset_minutes": 6,
                },
            ],
        },
        {
            "mode": ChatMode.REGULATORY,
            "title": "ERA Compliance Review",
            "created_at": past_time(days=1, hours=5),
            "messages": [
                {
                    "role": MessageRole.USER,
                    "content": "What are ERA's key performance indicators for transmission licensees?",
                    "offset_minutes": 0,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "ERA monitors transmission licensees against several key performance indicators:\n\n**Technical Indicators:**\n- System Average Interruption Frequency Index (SAIFI)\n- System Average Interruption Duration Index (SAIDI)\n- Transmission losses (% of energy injected)\n- System availability factor\n\n**Commercial Indicators:**\n- Billing accuracy\n- Revenue collection rate\n- Customer complaint resolution time\n\n**Safety & Environmental:**\n- Accident frequency rate\n- Environmental compliance score\n\nThese are reported quarterly to ERA as part of license compliance requirements.",
                    "offset_minutes": 2,
                },
                {
                    "role": MessageRole.USER,
                    "content": "How often must UETCL submit performance reports to ERA?",
                    "offset_minutes": 8,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "UETCL must submit the following reports to ERA:\n\n**Quarterly:**\n- Performance indicators report (SAIFI, SAIDI, losses)\n- Financial performance summary\n- Major incident reports\n\n**Annually:**\n- Comprehensive performance review\n- Audited financial statements\n- Investment and expansion updates\n- Tariff review submissions\n\n**Ad-hoc:**\n- Major outage notifications (within 24 hours)\n- Grid expansion proposals\n- License amendment requests\n\nAll submissions must follow ERA's prescribed formats and deadlines.",
                    "offset_minutes": 10,
                },
            ],
        },
        {
            "mode": ChatMode.ANALYTICS,
            "title": "Outage Analysis Q4 2024",
            "created_at": past_time(hours=12),
            "messages": [
                {
                    "role": MessageRole.USER,
                    "content": "Analyze the outage patterns from the uploaded data. What are the main causes?",
                    "offset_minutes": 0,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "Based on the analysis of the outage data, here are the key findings:\n\n**Top 5 Outage Causes:**\n1. **Equipment Failure** - 34% of incidents (mainly transformer faults)\n2. **Weather Events** - 28% (lightning strikes, storms)\n3. **Vegetation** - 18% (tree contact with lines)\n4. **Third-Party Damage** - 12% (construction activities)\n5. **Scheduled Maintenance** - 8%\n\n**Regional Distribution:**\n- Central Region: 42% of outages\n- Eastern Region: 31%\n- Western Region: 27%\n\n**Recommendations:**\n- Prioritize vegetation management in high-incident corridors\n- Accelerate transformer replacement program\n- Install lightning arresters on vulnerable lines",
                    "offset_minutes": 3,
                },
                {
                    "role": MessageRole.USER,
                    "content": "How does this compare to ERA's targets?",
                    "offset_minutes": 10,
                },
                {
                    "role": MessageRole.ASSISTANT,
                    "content": "Comparing current performance against ERA targets:\n\n| Metric | Current | ERA Target | Status |\n|--------|---------|------------|--------|\n| SAIFI | 5.2 | <4.5 | ⚠️ Above target |\n| SAIDI | 10.3 hrs | <9.0 hrs | ⚠️ Above target |\n| Losses | 3.8% | <3.5% | ⚠️ Slightly above |\n\n**Gap Analysis:**\n- SAIFI gap: 0.7 interruptions (need 13% improvement)\n- SAIDI gap: 1.3 hours (need 14% improvement)\n\n**Strategic Alignment:**\nThe Strategic Plan's reliability pillar initiatives should close these gaps by 2027 if implemented on schedule. Priority should be given to the transformer replacement and vegetation management programs.",
                    "offset_minutes": 12,
                },
            ],
        },
    ]

    for session_data in sessions_data:
        # Check if session with this title exists for user
        stmt = select(ChatSession).where(
            ChatSession.user_id == user.id,
            ChatSession.title == session_data["title"],
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            stats.record_existed("ChatSession")
            stats.record_existed("ChatMessage")  # Assume messages exist too
            print(f"ℹ️  Session already exists: {session_data['title']}")
            continue

        # Create session
        session = ChatSession(
            user_id=user.id,
            mode=session_data["mode"],
            title=session_data["title"],
            created_at=session_data["created_at"],
        )
        db.add(session)
        await db.flush()
        stats.record_created("ChatSession")
        print(f"✅ Created session: {session_data['title']}")

        # Create messages
        for msg_data in session_data["messages"]:
            message = ChatMessage(
                session_id=session.id,
                role=msg_data["role"],
                content=msg_data["content"],
                created_at=session_data["created_at"]
                + timedelta(minutes=msg_data["offset_minutes"]),
            )
            db.add(message)
            stats.record_created("ChatMessage")

        print(f"  ✅ Created {len(session_data['messages'])} messages")


async def seed_analytics_snapshot(db: AsyncSession):
    """Seed demo analytics snapshot."""
    snapshot, created = await get_or_create(
        db,
        AnalyticsSnapshot,
        lookup_field="dataset_name",
        lookup_value="demo_outages",
        defaults={
            "payload": {
                "total_events": 1247,
                "total_customers_affected": 89432,
                "saifi": 5.2,
                "saidi": 10.3,
                "top_regions": [
                    {"region": "Central", "events": 524, "percentage": 42.0},
                    {"region": "Eastern", "events": 386, "percentage": 31.0},
                    {"region": "Western", "events": 337, "percentage": 27.0},
                ],
                "outage_causes": {
                    "equipment_failure": 34,
                    "weather": 28,
                    "vegetation": 18,
                    "third_party": 12,
                    "maintenance": 8,
                },
                "monthly_trend": [
                    {"month": "Oct 2024", "events": 98},
                    {"month": "Nov 2024", "events": 112},
                    {"month": "Dec 2024", "events": 87},
                ],
                "note": "Demo dataset for Q4 2024 outage analysis. Data is synthetic for demonstration purposes.",
            },
            "file_path": "data/analytics/demo_outages.csv",
            "created_at": past_time(days=1),
        },
    )

    if created:
        stats.record_created("AnalyticsSnapshot")
        print(f"✅ Created analytics snapshot: {snapshot.dataset_name}")
    else:
        stats.record_existed("AnalyticsSnapshot")
        print(f"ℹ️  Analytics snapshot already exists: {snapshot.dataset_name}")


async def seed_documents(db: AsyncSession):
    """Seed document metadata (no chunks/embeddings)."""
    documents_data = [
        {
            "name": "strategic_plan.pdf",
            "type": DocumentType.STRATEGY,
            "source": DocumentSource.UETCL,
            "file_path": "backend/storage/docs/strategic_plan.pdf",
        },
        {
            "name": "grid_development_plan.pdf",
            "type": DocumentType.STRATEGY,
            "source": DocumentSource.UETCL,
            "file_path": "backend/storage/docs/grid_development_plan.pdf",
        },
    ]

    for doc_data in documents_data:
        doc, created = await get_or_create(
            db,
            Document,
            lookup_field="name",
            lookup_value=doc_data["name"],
            defaults={
                "type": doc_data["type"],
                "source": doc_data["source"],
                "file_path": doc_data["file_path"],
                "created_at": past_time(days=7),
            },
        )

        if created:
            stats.record_created("Document")
            print(f"✅ Created document: {doc.name}")
        else:
            stats.record_existed("Document")
            print(f"ℹ️  Document already exists: {doc.name}")


async def ensure_tables():
    """Ensure database tables exist using Alembic if configured, else create_all."""
    import subprocess
    import os

    # Check if Alembic is configured
    alembic_ini = os.path.join(os.path.dirname(__file__), "alembic.ini")

    if os.path.exists(alembic_ini):
        print("📦 Running Alembic migrations...")
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ Alembic migrations complete")
                return
            else:
                print(f"⚠️  Alembic failed: {result.stderr}")
                print("   Falling back to create_all...")
        except FileNotFoundError:
            print("⚠️  Alembic not found, using create_all...")
    else:
        print("ℹ️  No alembic.ini found, using create_all...")

    # Fallback to create_all
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created via create_all")


async def run_seed():
    """Main seed function."""
    print("\n" + "=" * 50)
    print("🌱 SISUiQ Database Seeder")
    print("=" * 50 + "\n")

    # Ensure tables exist
    await ensure_tables()

    print("\n📝 Seeding demo data...\n")

    async with async_session_maker() as db:
        try:
            # Seed in order of dependencies
            user = await seed_demo_user(db)
            await seed_chat_sessions(db, user)
            await seed_analytics_snapshot(db)
            await seed_documents(db)

            # Commit all changes
            await db.commit()
            print("\n✅ All changes committed successfully")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise

    # Print summary
    stats.print_summary()


def main():
    """Entry point for running seed script."""
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
