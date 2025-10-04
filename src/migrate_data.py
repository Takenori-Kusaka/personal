#!/usr/bin/env python3
"""
Data migration script for resume management system.
Migrates legacy profile.yml to new v2.0 format.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.yaml_handler import YAMLHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main migration function."""
    # Define paths
    project_root = Path(__file__).parent.parent
    legacy_file = project_root / "profile.yml"
    new_file = project_root / "data" / "profile.yml"
    schema_file = project_root / "data" / "schema.yml"
    backup_file = project_root / "profile_legacy_backup.yml"

    logger.info("Starting data migration process...")

    # Initialize YAML handler
    yaml_handler = YAMLHandler(schema_path=schema_file)

    try:
        # Load legacy data
        if not legacy_file.exists():
            logger.error(f"Legacy file not found: {legacy_file}")
            return False

        legacy_data = yaml_handler.load_yaml(legacy_file)
        logger.info(f"Loaded legacy data with {len(legacy_data)} top-level keys")

        # Create backup
        yaml_handler.save_yaml(legacy_data, backup_file)
        logger.info(f"Created backup at {backup_file}")

        # Migrate to new format
        migrated_data = yaml_handler.migrate_legacy_data(legacy_data)

        # Validate migrated data
        if not yaml_handler.validate_structure(migrated_data):
            logger.error("Migrated data failed validation")
            return False

        # Save migrated data
        new_file.parent.mkdir(parents=True, exist_ok=True)
        yaml_handler.save_yaml(migrated_data, new_file)

        logger.info(f"Successfully migrated data to {new_file}")
        logger.info("Migration completed successfully!")

        # Print summary
        print_migration_summary(legacy_data, migrated_data)

        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def print_migration_summary(legacy_data, migrated_data):
    """Print migration summary."""
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)

    profile = migrated_data.get("profile", {})

    # Personal info
    personal = profile.get("personal", {})
    print(f"Name: {personal.get('name')}")
    print(f"Age: {personal.get('age')}")

    # Education
    education = profile.get("education", [])
    print(f"Education entries: {len(education)}")

    # Career
    career = profile.get("career", {})
    companies = career.get("companies", [])
    print(f"Companies: {len(companies)}")

    total_projects = sum(len(company.get("projects", [])) for company in companies)
    print(f"Total projects: {total_projects}")

    print("\nCompany details:")
    for company in companies:
        projects_count = len(company.get("projects", []))
        print(f"  - {company.get('name')}: {projects_count} projects")

    print("\n" + "="*60)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)