#!/bin/bash

# ZgrWise Database Restore Script
# This script restores the PostgreSQL database from a backup

set -e

# Configuration
BACKUP_DIR="/backups"
DB_NAME="zgrwise"
DB_USER="zgr"
DB_HOST="db"
DB_PORT="5432"

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/zgrwise_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file '$BACKUP_FILE' not found"
    exit 1
fi

echo "Starting database restore at $(date)"
echo "Restoring from: $BACKUP_FILE"

# Confirm restore operation
read -p "Are you sure you want to restore the database? This will overwrite existing data. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Create a temporary database for testing
TEMP_DB="zgrwise_restore_test_$$"
echo "Creating temporary database: $TEMP_DB"

# Restore to temporary database first
pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
    --verbose \
    --no-password \
    --create \
    --dbname="$TEMP_DB" \
    "$BACKUP_FILE"

echo "Restore to temporary database completed"

# Test the restored database
echo "Testing restored database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Ask for final confirmation
read -p "Database restore test successful. Proceed with production restore? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning up temporary database..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $TEMP_DB;"
    echo "Restore cancelled"
    exit 1
fi

# Drop and recreate the main database
echo "Dropping existing database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"

# Restore to main database
echo "Restoring to main database..."
pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --no-password \
    "$BACKUP_FILE"

# Clean up temporary database
echo "Cleaning up temporary database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $TEMP_DB;"

echo "Database restore completed successfully at $(date)"
