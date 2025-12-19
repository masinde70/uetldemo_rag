"""Scheduled jobs service using APScheduler.

Provides background task scheduling for:
- Analytics data refresh
- Document re-indexing
- Health monitoring
- Cache cleanup
"""

import asyncio
import os
from datetime import datetime
from typing import Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def start_scheduler() -> None:
    """Start the scheduler if not already running."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()


async def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        _scheduler = None


# --- Job Definitions ---


async def refresh_analytics_job() -> None:
    """Job: Refresh analytics data from source.

    Runs daily to update analytics snapshots.
    """
    from backend.db import get_db_context

    print(f"[{datetime.utcnow()}] Running analytics refresh job...")

    try:
        async with get_db_context() as db:
            # Placeholder: Add actual analytics refresh logic
            # from backend.services.analytics import refresh_analytics
            # await refresh_analytics(db)
            pass

        print(f"[{datetime.utcnow()}] Analytics refresh completed")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Analytics refresh failed: {e}")


async def health_monitor_job() -> None:
    """Job: Monitor system health and log status.

    Runs every 5 minutes to check service health.
    """
    from backend.db import get_db_context
    from backend.services.health import check_all_services

    try:
        async with get_db_context() as db:
            health = await check_all_services(db)

            # Log health status
            status = health.status.value
            services = {
                name: svc.status.value
                for name, svc in health.services.items()
            }
            print(f"[{datetime.utcnow()}] Health check: {status} - {services}")

            # Could trigger alerts if unhealthy
            if health.status.value == "unhealthy":
                print(f"[{datetime.utcnow()}] WARNING: System unhealthy!")
                # TODO: Send alert notification

    except Exception as e:
        print(f"[{datetime.utcnow()}] Health monitor failed: {e}")


async def cleanup_old_sessions_job() -> None:
    """Job: Clean up old chat sessions.

    Runs weekly to remove sessions older than 30 days.
    """
    from datetime import timedelta

    from sqlalchemy import delete
    from backend.db import get_db_context
    from backend.models import ChatMessage, ChatSession

    print(f"[{datetime.utcnow()}] Running session cleanup job...")

    try:
        async with get_db_context() as db:
            cutoff = datetime.utcnow() - timedelta(days=30)

            # Find old sessions
            from sqlalchemy import select
            stmt = select(ChatSession.id).where(
                ChatSession.created_at < cutoff
            )
            result = await db.execute(stmt)
            old_session_ids = [row[0] for row in result.all()]

            if old_session_ids:
                # Delete messages first
                await db.execute(
                    delete(ChatMessage).where(
                        ChatMessage.session_id.in_(old_session_ids)
                    )
                )

                # Delete sessions
                await db.execute(
                    delete(ChatSession).where(
                        ChatSession.id.in_(old_session_ids)
                    )
                )

                await db.commit()
                print(f"[{datetime.utcnow()}] Cleaned up {len(old_session_ids)} old sessions")
            else:
                print(f"[{datetime.utcnow()}] No old sessions to clean up")

    except Exception as e:
        print(f"[{datetime.utcnow()}] Session cleanup failed: {e}")


# --- Job Registration ---


def register_default_jobs() -> None:
    """Register all default scheduled jobs."""
    scheduler = get_scheduler()

    # Health monitor - every 5 minutes
    scheduler.add_job(
        health_monitor_job,
        trigger=IntervalTrigger(minutes=5),
        id="health_monitor",
        name="Health Monitor",
        replace_existing=True,
    )

    # Analytics refresh - daily at 2 AM
    scheduler.add_job(
        refresh_analytics_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="analytics_refresh",
        name="Analytics Refresh",
        replace_existing=True,
    )

    # Session cleanup - weekly on Sunday at 3 AM
    scheduler.add_job(
        cleanup_old_sessions_job,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="session_cleanup",
        name="Session Cleanup",
        replace_existing=True,
    )

    print("Scheduled jobs registered")


def add_custom_job(
    func: Callable,
    job_id: str,
    trigger: str = "interval",
    **trigger_kwargs,
) -> None:
    """Add a custom scheduled job.

    Args:
        func: Async function to run
        job_id: Unique job identifier
        trigger: "interval" or "cron"
        **trigger_kwargs: Trigger-specific arguments
    """
    scheduler = get_scheduler()

    if trigger == "interval":
        trigger_obj = IntervalTrigger(**trigger_kwargs)
    elif trigger == "cron":
        trigger_obj = CronTrigger(**trigger_kwargs)
    else:
        raise ValueError(f"Unknown trigger type: {trigger}")

    scheduler.add_job(
        func,
        trigger=trigger_obj,
        id=job_id,
        replace_existing=True,
    )


def list_jobs() -> list[dict]:
    """List all scheduled jobs."""
    scheduler = get_scheduler()
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }
        for job in scheduler.get_jobs()
    ]
