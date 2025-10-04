"""
Git Automation and Deployment System
Intelligent Git operations and GitHub Pages deployment automation

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import asyncio
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from automation.config.settings import GitConfig
from automation.utils.logging_setup import StructuredLogger, PerformanceTracker
from automation.utils.file_handler import FileHandler

@dataclass
class GitCommitInfo:
    """Git commit information"""
    hash: str
    message: str
    files_changed: List[str]
    timestamp: datetime
    branch: str

@dataclass
class DeploymentResult:
    """Deployment operation result"""
    success: bool
    commits_created: int = 0
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    deployment_url: Optional[str] = None
    files_deployed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class GitAutomation:
    """
    Intelligent Git operations for automated content deployment
    Handles branching, commits, PRs, and GitHub Pages deployment
    """

    def __init__(self, config: GitConfig):
        """Initialize Git automation system"""
        self.config = config
        self.logger = StructuredLogger('git_automation')
        self.file_handler = FileHandler()

        self.repo_path = Path(config.repository_path).resolve()
        self.current_branch = None
        self.git_available = self._check_git_availability()

        if not self.git_available:
            self.logger.error("Git is not available in PATH")
            return

        self._verify_repository()

    def _check_git_availability(self) -> bool:
        """Check if Git is available in the system"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("Git available", version=result.stdout.strip())
                return True
            else:
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _verify_repository(self):
        """Verify that we're in a Git repository"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info("Git repository verified", path=str(self.repo_path))
                self._update_current_branch()
            else:
                self.logger.error("Not a Git repository or Git error",
                                error=result.stderr,
                                path=str(self.repo_path))

        except subprocess.TimeoutExpired:
            self.logger.error("Git status check timed out")
        except Exception as e:
            self.logger.error("Repository verification failed", error=e)

    def _update_current_branch(self):
        """Update current branch information"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.current_branch = result.stdout.strip()
                self.logger.debug("Current branch updated", branch=self.current_branch)

        except Exception as e:
            self.logger.error("Failed to get current branch", error=e)

    async def deploy_content_batch(self, garden_content: Dict[str, Any]) -> DeploymentResult:
        """
        Deploy batch of garden content with intelligent Git operations

        Args:
            garden_content: Dictionary of content items to deploy

        Returns:
            DeploymentResult with deployment status and details
        """
        if not self.git_available:
            return DeploymentResult(
                success=False,
                errors=["Git is not available"]
            )

        with PerformanceTracker(self.logger, "batch_deployment", items=len(garden_content)) as tracker:
            try:
                self.logger.info("Starting batch deployment", items=len(garden_content))

                # Create deployment branch
                branch_name = await self._create_deployment_branch()
                if not branch_name:
                    return DeploymentResult(
                        success=False,
                        errors=["Failed to create deployment branch"]
                    )

                tracker.add_metric('branch_created', branch_name)

                # Deploy content files
                deployed_files = []
                deployment_errors = []

                for file_path, content_info in garden_content.items():
                    try:
                        deployed_file = await self._deploy_single_content(content_info)
                        if deployed_file:
                            deployed_files.append(deployed_file)
                        else:
                            deployment_errors.append(f"Failed to deploy: {file_path}")

                    except Exception as e:
                        error_msg = f"Error deploying {file_path}: {str(e)}"
                        deployment_errors.append(error_msg)
                        self.logger.error("Content deployment failed", error=e, file=file_path)

                if not deployed_files:
                    return DeploymentResult(
                        success=False,
                        branch_name=branch_name,
                        errors=deployment_errors + ["No files were successfully deployed"]
                    )

                tracker.add_metric('files_deployed', len(deployed_files))

                # Create commit
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                commit_hash = await self._create_batch_commit(deployed_files, session_id)
                if not commit_hash:
                    return DeploymentResult(
                        success=False,
                        branch_name=branch_name,
                        files_deployed=deployed_files,
                        errors=deployment_errors + ["Failed to create commit"]
                    )

                tracker.add_metric('commit_hash', commit_hash)

                # Push branch if configured
                pr_url = None
                if self.config.auto_push:
                    push_success = await self._push_branch(branch_name)
                    if not push_success:
                        deployment_errors.append("Failed to push branch")
                    else:
                        # Create PR if configured
                        if self.config.create_pr:
                            pr_url = await self._create_pull_request(branch_name, deployed_files, session_id)
                            if pr_url:
                                tracker.add_metric('pr_created', pr_url)

                # Get deployment URL if GitHub Pages is enabled
                deployment_url = None
                if self.config.enable_gh_pages:
                    deployment_url = self._get_github_pages_url()

                result = DeploymentResult(
                    success=True,
                    commits_created=1,
                    branch_name=branch_name,
                    pr_url=pr_url,
                    deployment_url=deployment_url,
                    files_deployed=deployed_files,
                    errors=deployment_errors,
                    metadata={
                        'session_id': session_id,
                        'commit_hash': commit_hash,
                        'deployment_time': datetime.now().isoformat(),
                        'total_files': len(garden_content),
                        'successful_files': len(deployed_files)
                    }
                )

                self.logger.info("Batch deployment completed",
                               success=result.success,
                               files=len(deployed_files),
                               branch=branch_name,
                               pr_url=pr_url)

                return result

            except Exception as e:
                self.logger.error("Batch deployment failed", error=e)
                return DeploymentResult(
                    success=False,
                    errors=[f"Deployment failed: {str(e)}"]
                )

    async def _create_deployment_branch(self) -> Optional[str]:
        """Create a new deployment branch"""
        try:
            # Ensure we're on the main branch
            await self._checkout_branch(self.config.main_branch)

            # Pull latest changes
            await self._pull_latest()

            # Create unique branch name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"{self.config.feature_branch_prefix}{timestamp}"

            # Create and checkout new branch
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.current_branch = branch_name
                self.logger.info("Deployment branch created", branch=branch_name)
                return branch_name
            else:
                self.logger.error("Failed to create branch", error=result.stderr)
                return None

        except Exception as e:
            self.logger.error("Branch creation failed", error=e)
            return None

    async def _checkout_branch(self, branch_name: str) -> bool:
        """Checkout specified branch"""
        try:
            result = subprocess.run(
                ['git', 'checkout', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.current_branch = branch_name
                self.logger.debug("Checked out branch", branch=branch_name)
                return True
            else:
                self.logger.warning("Branch checkout failed", branch=branch_name, error=result.stderr)
                return False

        except Exception as e:
            self.logger.error("Branch checkout error", error=e, branch=branch_name)
            return False

    async def _pull_latest(self) -> bool:
        """Pull latest changes from remote"""
        try:
            result = subprocess.run(
                ['git', 'pull', 'origin', self.current_branch or self.config.main_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.logger.debug("Pulled latest changes")
                return True
            else:
                self.logger.warning("Git pull failed", error=result.stderr)
                return False

        except Exception as e:
            self.logger.error("Git pull error", error=e)
            return False

    async def _deploy_single_content(self, content_info: Dict[str, Any]) -> Optional[str]:
        """Deploy a single content file"""
        try:
            target_path = Path(self.repo_path) / content_info['file_path']
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content_info['content'])

            self.logger.debug("Content file deployed", path=str(target_path))
            return str(target_path.relative_to(self.repo_path))

        except Exception as e:
            self.logger.error("Single content deployment failed", error=e)
            return None

    async def _create_batch_commit(self, deployed_files: List[str], session_id: str) -> Optional[str]:
        """Create commit for all deployed files"""
        try:
            # Add files to staging
            for file_path in deployed_files:
                result = subprocess.run(
                    ['git', 'add', file_path],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    self.logger.warning("Failed to add file to staging", file=file_path)

            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                staged_files = result.stdout.strip().split('\n')
                self.logger.debug("Files staged for commit", files=staged_files)
            else:
                self.logger.warning("No changes to commit")
                return None

            # Create commit message
            commit_message = self.config.commit_message_template.format(
                category="mixed" if len(deployed_files) > 1 else "single",
                title=f"{len(deployed_files)} files",
                source_file="batch_processing",
                session_id=session_id
            )

            # Create commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if hash_result.returncode == 0:
                    commit_hash = hash_result.stdout.strip()
                    self.logger.info("Batch commit created",
                                   hash=commit_hash[:8],
                                   files=len(deployed_files))
                    return commit_hash
                else:
                    self.logger.warning("Could not retrieve commit hash")
                    return "unknown"
            else:
                self.logger.error("Commit creation failed", error=result.stderr)
                return None

        except Exception as e:
            self.logger.error("Batch commit failed", error=e)
            return None

    async def _push_branch(self, branch_name: str) -> bool:
        """Push branch to remote repository"""
        try:
            # Push branch with upstream tracking
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.logger.info("Branch pushed successfully", branch=branch_name)
                return True
            else:
                self.logger.error("Branch push failed", branch=branch_name, error=result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Branch push timed out", branch=branch_name)
            return False
        except Exception as e:
            self.logger.error("Branch push error", error=e, branch=branch_name)
            return False

    async def _create_pull_request(self, branch_name: str, deployed_files: List[str], session_id: str) -> Optional[str]:
        """Create pull request using GitHub CLI"""
        try:
            # Check if gh CLI is available
            gh_check = subprocess.run(
                ['gh', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if gh_check.returncode != 0:
                self.logger.warning("GitHub CLI not available, skipping PR creation")
                return None

            # Create PR body
            changes_summary = "\n".join([f"- {file}" for file in deployed_files[:10]])
            if len(deployed_files) > 10:
                changes_summary += f"\n- ... and {len(deployed_files) - 10} more files"

            pr_body = self.config.pr_template.format(
                category="automated_content",
                source_file="automation_pipeline",
                processing_time=0,  # Could be calculated from tracker
                changes_summary=changes_summary
            )

            # Create pull request
            result = subprocess.run(
                [
                    'gh', 'pr', 'create',
                    '--title', f'🤖 Automated Content Update - {session_id}',
                    '--body', pr_body,
                    '--base', self.config.main_branch,
                    '--head', branch_name
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                self.logger.info("Pull request created", url=pr_url, branch=branch_name)
                return pr_url
            else:
                self.logger.error("PR creation failed", error=result.stderr)
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("PR creation timed out")
            return None
        except Exception as e:
            self.logger.error("PR creation error", error=e)
            return None

    def _get_github_pages_url(self) -> Optional[str]:
        """Get GitHub Pages URL for the repository"""
        try:
            # Get remote origin URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                origin_url = result.stdout.strip()

                # Parse GitHub URL
                if 'github.com' in origin_url:
                    # Extract username and repo name
                    if origin_url.startswith('https://github.com/'):
                        repo_path = origin_url.replace('https://github.com/', '').replace('.git', '')
                    elif origin_url.startswith('git@github.com:'):
                        repo_path = origin_url.replace('git@github.com:', '').replace('.git', '')
                    else:
                        return None

                    username, repo_name = repo_path.split('/', 1)
                    gh_pages_url = f"https://{username}.github.io/{repo_name}/"

                    self.logger.debug("GitHub Pages URL generated", url=gh_pages_url)
                    return gh_pages_url

        except Exception as e:
            self.logger.error("Failed to generate GitHub Pages URL", error=e)

        return None

    async def get_repository_status(self) -> Dict[str, Any]:
        """Get current repository status"""
        try:
            # Get status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Get branch info
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Get last commit info
            log_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%s|%ai'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Get remote info
            remote_result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            status_info = {
                "git_available": self.git_available,
                "repository_path": str(self.repo_path),
                "current_branch": branch_result.stdout.strip() if branch_result.returncode == 0 else None,
                "has_changes": bool(status_result.stdout.strip()) if status_result.returncode == 0 else False,
                "remote_url": remote_result.stdout.strip() if remote_result.returncode == 0 else None,
                "last_commit": None
            }

            # Parse last commit info
            if log_result.returncode == 0 and log_result.stdout:
                commit_parts = log_result.stdout.split('|', 2)
                if len(commit_parts) == 3:
                    status_info["last_commit"] = {
                        "hash": commit_parts[0][:8],
                        "message": commit_parts[1],
                        "date": commit_parts[2]
                    }

            return status_info

        except Exception as e:
            self.logger.error("Failed to get repository status", error=e)
            return {
                "git_available": self.git_available,
                "error": str(e)
            }

    async def cleanup_old_branches(self, max_branches: int = 10) -> int:
        """Clean up old automation branches"""
        try:
            # Get list of automation branches
            result = subprocess.run(
                ['git', 'branch', '-r'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return 0

            automation_branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if f'origin/{self.config.feature_branch_prefix}' in line:
                    branch_name = line.replace('origin/', '')
                    automation_branches.append(branch_name)

            # Sort by branch name (which includes timestamp)
            automation_branches.sort()

            # Delete old branches if we have too many
            deleted_count = 0
            if len(automation_branches) > max_branches:
                branches_to_delete = automation_branches[:-max_branches]

                for branch_name in branches_to_delete:
                    try:
                        # Delete remote branch
                        delete_result = subprocess.run(
                            ['git', 'push', 'origin', '--delete', branch_name],
                            cwd=self.repo_path,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if delete_result.returncode == 0:
                            deleted_count += 1
                            self.logger.debug("Deleted old branch", branch=branch_name)

                    except Exception as e:
                        self.logger.warning("Failed to delete branch", branch=branch_name, error=e)

            if deleted_count > 0:
                self.logger.info("Branch cleanup completed", deleted=deleted_count, remaining=len(automation_branches) - deleted_count)

            return deleted_count

        except Exception as e:
            self.logger.error("Branch cleanup failed", error=e)
            return 0

    def get_automation_info(self) -> Dict[str, Any]:
        """Get information about Git automation system"""
        return {
            "git_available": self.git_available,
            "repository_path": str(self.repo_path),
            "current_branch": self.current_branch,
            "main_branch": self.config.main_branch,
            "feature_branch_prefix": self.config.feature_branch_prefix,
            "auto_push": self.config.auto_push,
            "create_pr": self.config.create_pr,
            "enable_gh_pages": self.config.enable_gh_pages
        }