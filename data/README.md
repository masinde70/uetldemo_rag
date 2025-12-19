# Data Directory

This directory contains the data sources for the SISUiQ demo.

## Directory Structure

```
data/
├── strategy/      # UETCL Strategic Plan documents (PDFs)
├── era/          # ERA regulatory documents and web content
└── analytics/    # Outage data and operational analytics (CSV)
```

## Data Sources

### Strategy Documents (`strategy/`)
Place UETCL's 2024-2029 Strategic Plan PDFs here:
- Strategic plan main document
- Annexes and supporting documents
- KPI frameworks
- Implementation roadmaps

**Expected format**: PDF

### ERA Regulatory Documents (`era/`)
Place ERA (Electricity Regulatory Authority) documents here:
- Regulatory guidelines
- Compliance frameworks
- Performance indicators
- License requirements
- Policy documents

**Sources**:
- ERA website content
- Regulatory publications
- Technical standards

**Expected formats**: PDF, HTML (converted), markdown

### Analytics Data (`analytics/`)
Place operational data files here:
- Outage records (CSV)
- Performance metrics
- Historical data
- KPI measurements

**Expected format**: CSV with headers

#### Example Outage CSV Format:
```csv
date,region,cause,duration_hours,affected_customers
2024-01-15,Central,Equipment Failure,2.5,1500
2024-01-20,Northern,Weather,4.0,3200
```

## Data Ingestion

### Strategy Documents
```bash
# Using ingestion script
python scripts/ingest/ingest_strategy.py --input data/strategy/

# Via API
curl -X POST http://localhost:8000/api/ingest/docs \
  -F "file=@data/strategy/strategic_plan.pdf" \
  -F "doc_type=strategy"
```

### ERA Documents
```bash
# Using ingestion script
python scripts/ingest/ingest_era.py --input data/era/

# Via API
curl -X POST http://localhost:8000/api/ingest/docs \
  -F "file=@data/era/regulatory_guidelines.pdf" \
  -F "doc_type=regulatory"
```

### Analytics Data
```bash
# Using ingestion script
python scripts/ingest/ingest_analytics.py --input data/analytics/outages.csv

# Via API
curl -X POST http://localhost:8000/api/ingest/data \
  -F "file=@data/analytics/outages.csv" \
  -F "data_type=outages"
```

## Data Privacy & Security

⚠️ **Important Notes**:
- This directory is excluded from git (see `.gitignore`)
- Do not commit sensitive or proprietary documents
- Use sample/anonymized data for public demos
- Ensure compliance with data protection regulations

## Sample Data

For testing purposes, you can use the sample data generation scripts:

```bash
python scripts/generate_sample_data.py
```

This will create:
- Sample strategy document excerpts
- Mock ERA regulatory content
- Synthetic outage data

## Data Quality Guidelines

### Strategy Documents
- ✅ Clear document structure
- ✅ Well-defined sections and headers
- ✅ Consistent formatting
- ✅ Readable text (not scanned images)

### ERA Documents
- ✅ Official sources
- ✅ Current/up-to-date content
- ✅ Complete documents (not excerpts)
- ✅ Properly formatted

### Analytics CSV
- ✅ UTF-8 encoding
- ✅ Consistent date format (YYYY-MM-DD)
- ✅ No missing required fields
- ✅ Valid numeric values
- ✅ Consistent categorical values

## Updating Data

When adding new data:

1. Place files in appropriate directory
2. Run ingestion script or API endpoint
3. Verify ingestion in admin dashboard
4. Test retrieval with sample queries

## Data Maintenance

- Regular updates: Quarterly or as needed
- Archive old data: Keep historical records
- Validate quality: Check for errors or inconsistencies
- Document changes: Keep changelog of major updates
