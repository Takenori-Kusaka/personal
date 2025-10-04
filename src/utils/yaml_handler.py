"""
YAML handling utilities for resume management system.
Handles YAML file operations, validation, and data structure management.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class YAMLHandler:
    """Handle YAML file operations for resume data."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize YAML handler.

        Args:
            schema_path: Path to schema definition file
        """
        self.schema_path = schema_path
        self.schema = self._load_schema() if schema_path else None

    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """
        Load YAML file with error handling.

        Args:
            file_path: Path to YAML file

        Returns:
            Dictionary containing YAML data

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                logger.info(f"Successfully loaded YAML from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"YAML file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            raise

    def save_yaml(self, data: Dict[str, Any], file_path: Path) -> None:
        """
        Save data to YAML file.

        Args:
            data: Dictionary to save
            file_path: Output file path
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(
                    data,
                    file,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2
                )
                logger.info(f"Successfully saved YAML to {file_path}")
        except Exception as e:
            logger.error(f"Error saving YAML to {file_path}: {e}")
            raise

    def _load_schema(self) -> Dict[str, Any]:
        """Load schema definition."""
        if not self.schema_path or not self.schema_path.exists():
            logger.warning("Schema file not found")
            return {}

        return self.load_yaml(self.schema_path)

    def migrate_legacy_data(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate legacy profile.yml data to new structure.

        Args:
            legacy_data: Old format data

        Returns:
            Migrated data in new format
        """
        migrated = {
            "profile": {
                "meta": {
                    "version": "2.0",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "generated_by": "resume-system-v2"
                }
            }
        }

        # Migrate personal information
        if "名前" in legacy_data:
            migrated["profile"]["personal"] = {
                "name": legacy_data.get("名前"),
                "gender": legacy_data.get("性別"),
                "birth_date": legacy_data.get("生年月日"),
                "age": legacy_data.get("年齢"),
                "location": legacy_data.get("出身地"),
                "hobbies": legacy_data.get("趣味", [])
            }

        # Migrate education
        if "経歴" in legacy_data and "学歴" in legacy_data["経歴"]:
            education = []
            for key, edu_data in legacy_data["経歴"]["学歴"].items():
                education.append({
                    "level": key,
                    "school_name": edu_data.get("学校名"),
                    "department": edu_data.get("学科"),
                    "graduation_date": edu_data.get("卒業年月"),
                    "notes": edu_data.get("備考")
                })
            migrated["profile"]["education"] = education

        # Migrate career
        if "経歴" in legacy_data and "職歴" in legacy_data["経歴"]:
            companies = []

            for company_data in legacy_data["経歴"]["職歴"]:
                company = {
                    "company_id": self._generate_company_id(company_data.get("会社名")),
                    "name": company_data.get("会社名"),
                    "period": {
                        "start_date": company_data.get("期間", {}).get("入社年月"),
                        "end_date": company_data.get("期間", {}).get("退社年月")
                    },
                    "position": company_data.get("職種"),
                    "business_content": company_data.get("業務内容"),
                    "reason_for_leaving": company_data.get("退社理由"),
                    "skills": company_data.get("スキル", {})
                }

                # Migrate projects
                projects = []
                if "職務" in company_data:
                    for i, project_data in enumerate(company_data["職務"]):
                        project = {
                            "project_id": f"{company['company_id']}_project_{i+1:03d}",
                            "title": project_data.get("プロジェクト概要"),
                            "period": {
                                "start_date": project_data.get("期間", {}).get("開始年月"),
                                "end_date": project_data.get("期間", {}).get("終了年月")
                            },
                            "role": project_data.get("役割"),
                            "responsibilities": project_data.get("主な担当業務", []),
                            "team_size": project_data.get("プロジェクトメンバー数"),
                            "achievements": project_data.get("成果", [])
                        }
                        projects.append(project)

                company["projects"] = projects
                companies.append(company)

            migrated["profile"]["career"] = {"companies": companies}

        logger.info("Successfully migrated legacy data to new format")
        return migrated

    def _generate_company_id(self, company_name: str) -> str:
        """Generate company ID from company name."""
        if not company_name:
            return "unknown"

        # Simple ID generation - replace spaces and special characters
        company_id = company_name.replace("株式会社", "").replace("有限会社", "")
        company_id = company_id.replace(" ", "_").replace("　", "_")

        # Map known companies to specific IDs
        id_mapping = {
            "太陽精機": "taiyo_seiki",
            "メイテック": "meitec",
            "オムロンソフトウェア": "omron_software"
        }

        for key, mapped_id in id_mapping.items():
            if key in company_name:
                return mapped_id

        return company_id.lower()

    def validate_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate data structure against schema.

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        if not self.schema:
            logger.warning("No schema available for validation")
            return True

        # Basic validation - check required sections
        profile = data.get("profile", {})

        required_sections = ["personal", "education", "career"]
        for section in required_sections:
            if section not in profile:
                logger.error(f"Missing required section: {section}")
                return False

        logger.info("Data structure validation passed")
        return True