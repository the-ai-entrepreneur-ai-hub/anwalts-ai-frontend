#!/bin/bash
# AnwaltsAI Database Backup Script
# Automated daily backup with 30-day retention

set -e

# Configuration
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="anwalts_ai_${DATE}.sql.gz"
LOG_FILE="/var/log/anwalts-backup.log"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Log start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting database backup..." | tee -a "$LOG_FILE"

# Perform backup
if docker exec anwalts_postgres pg_dump -U anwalts_user anwalts_ai | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ? Backup successful: $BACKUP_FILE" | tee -a "$LOG_FILE"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup size: $BACKUP_SIZE" | tee -a "$LOG_FILE"
    
    # Cleanup old backups (retain last 30 days)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning up backups older than 30 days..." | tee -a "$LOG_FILE"
    find "$BACKUP_DIR" -name "anwalts_ai_*.sql.gz" -mtime +30 -delete
    
    # Count remaining backups
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "anwalts_ai_*.sql.gz" | wc -l)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Total backups retained: $BACKUP_COUNT" | tee -a "$LOG_FILE"
    
    # Verify backup integrity (check if file is valid gzip)
    if gzip -t "$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ? Backup integrity verified" | tee -a "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ?? WARNING: Backup integrity check failed!" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ? ERROR: Backup failed!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup complete!" | tee -a "$LOG_FILE"
