#!/bin/bash

# Database backup verification script
# This script verifies that the database backup can be restored

# Configuration
BACKUP_DIR="/backups"
TEST_DB_NAME="anwalts_test_restore"
LOG_FILE="/var/log/database-verify.log"

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

log "Starting backup verification"

# Find the latest backup
LATEST_BACKUP=$(ls -t ${BACKUP_DIR}/anwalts_*.sql.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    log "ERROR: No backup files found in ${BACKUP_DIR}"
    exit 1
fi

log "Latest backup file: $LATEST_BACKUP"

# Create test database
if docker exec anwalts_postgres psql -U anwalts_user -c "CREATE DATABASE ${TEST_DB_NAME}"; then
    log "Test database created successfully"
else
    log "ERROR: Failed to create test database"
    exit 1
fi

# Restore backup to test database
if zcat ${LATEST_BACKUP} | docker exec -i anwalts_postgres psql -U anwalts_user -d ${TEST_DB_NAME}; then
    log "Backup restored successfully to test database"
else
    log "ERROR: Failed to restore backup to test database"
    docker exec anwalts_postgres psql -U anwalts_user -c "DROP DATABASE ${TEST_DB_NAME}"
    exit 1
fi

# Verify data integrity (basic check)
if docker exec anwalts_postgres psql -U anwalts_user -d ${TEST_DB_NAME} -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1; then
    log "Data integrity check passed"
else
    log "ERROR: Data integrity check failed"
fi

# Clean up test database
if docker exec anwalts_postgres psql -U anwalts_user -c "DROP DATABASE ${TEST_DB_NAME}"; then
    log "Test database dropped successfully"
else
    log "WARNING: Failed to drop test database"
fi

log "Backup verification completed"