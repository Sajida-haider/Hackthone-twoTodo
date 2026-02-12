# Log Retention Policy Documentation

## Overview

This document defines the retention policy for agent decision logs, including retention periods, archival procedures, and deletion policies.

**Key Principle**: Retain logs long enough for compliance and analysis, but not indefinitely to manage storage costs.

## Retention Periods

### By Log Type

| Log Type | Retention Period | Archive After | Rationale |
|----------|-----------------|---------------|-----------|
| Decision Logs | 90 days | 30 days | Compliance and decision analysis |
| Operation Logs | 90 days | 30 days | Audit trail for operations |
| Governance Logs | 90 days | 30 days | Security and compliance |
| Verification Logs | 30 days | 7 days | Operational analysis only |
| Approval Logs | 365 days | 90 days | Long-term audit and compliance |
| Rollback Logs | 90 days | 30 days | Incident analysis |
| Circuit Breaker Logs | 180 days | 60 days | Safety mechanism analysis |

### Retention Configuration

```yaml
governance:
  audit:
    retention_period: 90d          # Default retention
    archive_after: 30d             # Move to archive after 30 days
    compress_archives: true        # Compress archived logs
    delete_after_retention: true   # Delete after retention period

    # Per-log-type overrides
    retention_overrides:
      approval_logs: 365d
      verification_logs: 30d
      circuit_breaker_logs: 180d
```

## Log Lifecycle

### Stage 1: Active Logs (0-30 days)

**Location**: `logs/agent-decisions/YYYY-MM-DD/`

**Characteristics**:
- Uncompressed for fast access
- Indexed for quick searching
- Frequently accessed for monitoring
- Real-time analysis

**Storage**: High-performance SSD

**Access**: Immediate, no latency

### Stage 2: Archived Logs (30-90 days)

**Location**: `logs/archive/YYYY-MM/`

**Characteristics**:
- Compressed (gzip) to save space
- Less frequently accessed
- Available for historical analysis
- Compliance retention

**Storage**: Standard storage (HDD or S3 Standard)

**Access**: Slightly slower, requires decompression

### Stage 3: Deleted (After 90 days)

**Action**: Permanently deleted

**Exception**: Approval logs retained for 365 days

**Compliance**: Meets standard retention requirements

## Archival Process

### Automatic Archival

Logs are automatically archived after 30 days:

```bash
#!/bin/bash
# archive-logs.sh - Run daily via cron

ACTIVE_DIR="logs/agent-decisions"
ARCHIVE_DIR="logs/archive"
ARCHIVE_AGE=30  # days

# Find logs older than 30 days
find $ACTIVE_DIR -type f -name "*.log" -mtime +$ARCHIVE_AGE | while read log; do
  # Extract date from path
  DATE=$(echo $log | grep -oP '\d{4}-\d{2}-\d{2}')
  MONTH=$(echo $DATE | cut -d'-' -f1,2)

  # Create archive directory
  mkdir -p $ARCHIVE_DIR/$MONTH

  # Compress and move to archive
  gzip -c $log > $ARCHIVE_DIR/$MONTH/$(basename $log).gz

  # Verify archive created successfully
  if [ -f $ARCHIVE_DIR/$MONTH/$(basename $log).gz ]; then
    rm $log
    echo "Archived: $log"
  else
    echo "ERROR: Failed to archive $log"
  fi
done
```

### Manual Archival

For immediate archival:

```bash
# Archive specific date
./scripts/archive-logs.sh --date 2026-01-15

# Archive date range
./scripts/archive-logs.sh --from 2026-01-01 --to 2026-01-31

# Archive all logs older than 30 days
./scripts/archive-logs.sh --older-than 30
```

## Deletion Process

### Automatic Deletion

Logs are automatically deleted after retention period:

```bash
#!/bin/bash
# delete-old-logs.sh - Run daily via cron

ARCHIVE_DIR="logs/archive"
RETENTION_DAYS=90

# Delete archived logs older than retention period
find $ARCHIVE_DIR -type f -name "*.log.gz" -mtime +$RETENTION_DAYS | while read log; do
  # Check if approval log (365 day retention)
  if echo $log | grep -q "approval"; then
    # Check if older than 365 days
    if [ $(find $log -mtime +365 | wc -l) -gt 0 ]; then
      rm $log
      echo "Deleted approval log: $log"
    fi
  else
    # Standard 90 day retention
    rm $log
    echo "Deleted: $log"
  fi
done
```

### Manual Deletion

For compliance or legal hold, prevent automatic deletion:

```bash
# Mark logs for legal hold (prevent deletion)
touch logs/archive/2026-01/.legal-hold

# Remove legal hold
rm logs/archive/2026-01/.legal-hold
```

## Storage Management

### Storage Estimates

**Uncompressed Logs**:
- Decision logs: ~1 KB per decision
- Operation logs: ~2 KB per operation
- Governance logs: ~1 KB per check
- Daily volume: ~10-50 MB (depending on activity)
- Monthly volume: ~300-1500 MB

**Compressed Logs** (gzip):
- Compression ratio: ~10:1
- Monthly archive: ~30-150 MB
- Annual storage: ~360-1800 MB

### Storage Tiers

| Tier | Age | Storage Type | Cost | Access Time |
|------|-----|--------------|------|-------------|
| Hot | 0-7 days | SSD | High | Immediate |
| Warm | 7-30 days | SSD | High | Immediate |
| Cool | 30-90 days | HDD/S3 Standard | Medium | Seconds |
| Cold | 90-365 days | S3 Glacier | Low | Minutes-Hours |

### Storage Optimization

```yaml
storage:
  hot_tier:
    age: 0-7d
    storage: local_ssd
    replication: 3x

  warm_tier:
    age: 7-30d
    storage: local_ssd
    replication: 2x

  cool_tier:
    age: 30-90d
    storage: s3_standard
    compression: gzip
    replication: s3_default

  cold_tier:
    age: 90-365d
    storage: s3_glacier
    compression: gzip
    retrieval_time: 3-5h
```

## Compliance Requirements

### Regulatory Compliance

**SOC 2**:
- Retain security logs for 90 days minimum
- Audit trail for all changes
- Immutable log storage

**GDPR**:
- Retain personal data processing logs
- Support data deletion requests
- Document retention rationale

**HIPAA**:
- Retain access logs for 6 years
- Audit trail for PHI access
- Secure log storage

**PCI DSS**:
- Retain audit logs for 1 year minimum
- Immediate access for 3 months
- Archived access for remaining period

### Compliance Configuration

```yaml
compliance:
  soc2:
    enabled: true
    minimum_retention: 90d
    immutable_logs: true

  gdpr:
    enabled: true
    support_deletion_requests: true
    document_retention: true

  hipaa:
    enabled: false
    retention_period: 6y

  pci_dss:
    enabled: false
    retention_period: 1y
    immediate_access_period: 3m
```

## Access Control

### Access Levels

**Read Access**:
- DevOps team: All logs
- Security team: Governance and approval logs
- Auditors: All logs (read-only)
- Developers: Decision and operation logs (own services)

**Write Access**:
- Agent processes: Append-only
- No human write access

**Delete Access**:
- Automated retention process only
- Manual deletion requires approval

### Access Logging

All log access is logged:

```json
{
  "timestamp": "2026-02-10T18:00:00Z",
  "event_type": "log_accessed",
  "user": "john.doe@example.com",
  "log_file": "logs/agent-decisions/2026-02-10/decisions.log",
  "access_type": "read",
  "access_method": "web_ui",
  "ip_address": "10.0.1.50"
}
```

## Backup and Recovery

### Backup Strategy

**Daily Backups**:
- All active logs (0-30 days)
- Incremental backups
- Retention: 7 days

**Weekly Backups**:
- All archived logs (30-90 days)
- Full backups
- Retention: 4 weeks

**Monthly Backups**:
- All logs
- Full backups
- Retention: 12 months

### Backup Configuration

```yaml
backup:
  daily:
    enabled: true
    schedule: "0 2 * * *"  # 2 AM daily
    type: incremental
    retention: 7d
    destination: s3://backups/daily/

  weekly:
    enabled: true
    schedule: "0 3 * * 0"  # 3 AM Sunday
    type: full
    retention: 4w
    destination: s3://backups/weekly/

  monthly:
    enabled: true
    schedule: "0 4 1 * *"  # 4 AM 1st of month
    type: full
    retention: 12m
    destination: s3://backups/monthly/
```

### Recovery Procedures

**Restore from Backup**:
```bash
# Restore specific date
./scripts/restore-logs.sh --date 2026-02-10

# Restore date range
./scripts/restore-logs.sh --from 2026-02-01 --to 2026-02-10

# Restore all logs
./scripts/restore-logs.sh --all
```

## Monitoring and Alerts

### Storage Monitoring

```yaml
alerts:
  - name: Log Storage High
    condition: storage_usage > 80%
    severity: warning
    action: Review retention policy

  - name: Archive Failure
    condition: archive_job_failed
    severity: critical
    action: Investigate and retry

  - name: Deletion Failure
    condition: deletion_job_failed
    severity: warning
    action: Manual cleanup required
```

### Retention Metrics

- **Active Log Size**: Current size of active logs
- **Archive Size**: Current size of archived logs
- **Deletion Rate**: Logs deleted per day
- **Archive Rate**: Logs archived per day
- **Storage Growth**: Rate of storage increase

## Best Practices

1. **Regular Review**: Review retention policy quarterly
2. **Compliance First**: Ensure retention meets compliance requirements
3. **Storage Optimization**: Compress and tier logs appropriately
4. **Access Control**: Restrict log access to authorized personnel
5. **Backup Regularly**: Maintain backups for disaster recovery
6. **Monitor Storage**: Alert on storage issues before they become critical
7. **Document Changes**: Log all retention policy changes

## Troubleshooting

### Problem: Storage filling up

**Solutions**:
- Verify archival process running
- Check compression enabled
- Review retention periods
- Delete old archives if compliant

### Problem: Cannot find old logs

**Solutions**:
- Check archive directory
- Verify logs not deleted prematurely
- Restore from backup if needed
- Review retention configuration

### Problem: Compliance violation

**Solutions**:
- Extend retention period
- Restore deleted logs from backup
- Document incident
- Update retention policy

## See Also

- [Audit Logging Documentation](./AUDIT_LOGGING.md) - Log format and structure
- [Compliance Guide](./COMPLIANCE.md) - Regulatory requirements
- [Backup Procedures](./BACKUP.md) - Backup and recovery
