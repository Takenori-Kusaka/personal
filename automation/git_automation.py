"""
Digital Garden Git Automation
自動コミット・プッシュ・GitHub Pages更新システム

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from automation.utils.env_loader import load_environment

# 環境変数をロード
load_environment()

@dataclass
class GitStatus:
    """Git状態"""
    has_changes: bool
    modified_files: List[str]
    new_files: List[str]
    deleted_files: List[str]
    current_branch: str


@dataclass
class CommitResult:
    """コミット結果"""
    success: bool
    commit_hash: Optional[str]
    commit_message: str
    files_committed: int
    error_message: Optional[str] = None


class GitAutomation:
    """
    デジタルガーデン用Git自動化システム
    - 自動コミットメッセージ生成（Claude API）
    - 変更検出と自動コミット
    - GitHub Pagesへの自動デプロイ
    """

    def __init__(self, repo_path: Path = None):
        """
        初期化

        Args:
            repo_path: リポジトリパス（デフォルト: カレントディレクトリ）
        """
        self.repo_path = repo_path or Path.cwd()

        # Gitリポジトリ確認
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

        print(f"[OK] Git repository found: {self.repo_path}")

        # Claude API設定（コミットメッセージ生成用）
        if ANTHROPIC_AVAILABLE:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if self.anthropic_api_key:
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                self.claude_available = True
                print("[OK] Claude API initialized for commit message generation")
            else:
                self.claude_available = False
                print("[WARNING] Claude API not available for commit messages")
        else:
            self.claude_available = False
            print("[WARNING] anthropic package not installed")

    def get_status(self) -> GitStatus:
        """
        Git状態を取得

        Returns:
            GitStatus: Git状態
        """
        try:
            # git status --porcelain
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            lines = result.stdout.strip().split("\n")
            modified_files = []
            new_files = []
            deleted_files = []

            for line in lines:
                if not line:
                    continue

                status = line[:2]
                filepath = line[3:]

                if status.strip() in ["M", "MM"]:
                    modified_files.append(filepath)
                elif status.strip() in ["A", "AM", "??"]:
                    new_files.append(filepath)
                elif status.strip() in ["D"]:
                    deleted_files.append(filepath)

            has_changes = bool(modified_files or new_files or deleted_files)

            # 現在のブランチ
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = branch_result.stdout.strip()

            return GitStatus(
                has_changes=has_changes,
                modified_files=modified_files,
                new_files=new_files,
                deleted_files=deleted_files,
                current_branch=current_branch
            )

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get git status: {e}")
            raise

    def generate_commit_message(self, status: GitStatus, context: str = "") -> str:
        """
        Claude APIで適切なコミットメッセージを生成

        Args:
            status: Git状態
            context: 追加のコンテキスト情報

        Returns:
            コミットメッセージ
        """
        if not self.claude_available:
            # フォールバック: デフォルトメッセージ
            return self._generate_default_commit_message(status)

        # ファイルリストを整理
        files_summary = []
        if status.new_files:
            files_summary.append(f"New files ({len(status.new_files)}): {', '.join(status.new_files[:5])}")
        if status.modified_files:
            files_summary.append(f"Modified files ({len(status.modified_files)}): {', '.join(status.modified_files[:5])}")
        if status.deleted_files:
            files_summary.append(f"Deleted files ({len(status.deleted_files)}): {', '.join(status.deleted_files[:5])}")

        prompt = f"""Git commit message generation for Digital Garden project.

# Changes Summary
{chr(10).join(files_summary)}

# Context
{context if context else "Automated content update from Digital Garden pipeline"}

# Requirements
- Follow conventional commits format: type(scope): description
- Types: feat, fix, docs, style, refactor, content, build
- Keep description under 72 characters
- Use present tense ("add" not "added")
- Be specific about what changed

Generate ONE commit message line only.
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            commit_message = response.content[0].text.strip()

            # 改行を削除（1行のみ）
            commit_message = commit_message.split("\n")[0]

            print(f"[INFO] Generated commit message: {commit_message}")
            return commit_message

        except Exception as e:
            print(f"[ERROR] Commit message generation failed: {e}")
            return self._generate_default_commit_message(status)

    def _generate_default_commit_message(self, status: GitStatus) -> str:
        """デフォルトのコミットメッセージを生成"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if status.new_files and not status.modified_files:
            return f"content: add new articles ({len(status.new_files)} files) - {timestamp}"
        elif status.modified_files and not status.new_files:
            return f"content: update articles ({len(status.modified_files)} files) - {timestamp}"
        elif status.deleted_files:
            return f"content: remove old articles ({len(status.deleted_files)} files) - {timestamp}"
        else:
            total = len(status.new_files) + len(status.modified_files)
            return f"content: automated update ({total} files) - {timestamp}"

    def commit_changes(
        self,
        message: Optional[str] = None,
        context: str = ""
    ) -> CommitResult:
        """
        変更をコミット

        Args:
            message: コミットメッセージ（Noneの場合は自動生成）
            context: コミットメッセージ生成のコンテキスト

        Returns:
            CommitResult: コミット結果
        """
        try:
            # 状態確認
            status = self.get_status()

            if not status.has_changes:
                print("[INFO] No changes to commit")
                return CommitResult(
                    success=False,
                    commit_hash=None,
                    commit_message="",
                    files_committed=0,
                    error_message="No changes to commit"
                )

            # ファイルをステージング
            print("[INFO] Staging changes...")

            # 新規ファイルと変更ファイルを追加
            all_files = status.new_files + status.modified_files
            if all_files:
                subprocess.run(
                    ["git", "add"] + all_files,
                    cwd=self.repo_path,
                    check=True
                )

            # 削除ファイルを処理
            if status.deleted_files:
                subprocess.run(
                    ["git", "rm"] + status.deleted_files,
                    cwd=self.repo_path,
                    check=True
                )

            # コミットメッセージ生成
            if not message:
                message = self.generate_commit_message(status, context)

            # コミット実行
            print(f"[INFO] Committing with message: {message}")
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True
            )

            # コミットハッシュ取得
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = hash_result.stdout.strip()

            files_committed = len(all_files) + len(status.deleted_files)

            print(f"[OK] Committed successfully: {commit_hash[:7]}")

            return CommitResult(
                success=True,
                commit_hash=commit_hash,
                commit_message=message,
                files_committed=files_committed
            )

        except subprocess.CalledProcessError as e:
            error_msg = f"Git commit failed: {e}"
            print(f"[ERROR] {error_msg}")
            return CommitResult(
                success=False,
                commit_hash=None,
                commit_message=message or "",
                files_committed=0,
                error_message=error_msg
            )

    def push_to_remote(self, branch: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        リモートにプッシュ

        Args:
            branch: プッシュするブランチ（Noneの場合は現在のブランチ）

        Returns:
            (成功フラグ, エラーメッセージ)
        """
        try:
            if not branch:
                status = self.get_status()
                branch = status.current_branch

            print(f"[INFO] Pushing to origin/{branch}...")

            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )

            print(f"[OK] Pushed to origin/{branch} successfully")
            return (True, None)

        except subprocess.CalledProcessError as e:
            error_msg = f"Git push failed: {e.stderr.decode() if e.stderr else str(e)}"
            print(f"[ERROR] {error_msg}")
            return (False, error_msg)

    def deploy_to_github_pages(self) -> bool:
        """
        GitHub Pagesにデプロイ
        GitHub Actionsが設定されている場合、pushでトリガーされる

        Returns:
            成功フラグ
        """
        print("[INFO] Deploying to GitHub Pages...")

        # mainブランチにプッシュ（GitHub Actionsがビルド・デプロイ）
        success, error = self.push_to_remote("main")

        if success:
            print("[OK] GitHub Pages deployment triggered")
            print("    GitHub Actions will build and deploy automatically")
            return True
        else:
            print(f"[ERROR] Deployment failed: {error}")
            return False

    def auto_commit_and_deploy(self, context: str = "") -> bool:
        """
        自動コミット＆デプロイのワンストップ処理

        Args:
            context: コミットメッセージのコンテキスト

        Returns:
            成功フラグ
        """
        print("\n" + "="*60)
        print("Auto Commit & Deploy")
        print("="*60)

        # 1. 状態確認
        status = self.get_status()

        if not status.has_changes:
            print("[INFO] No changes to commit. Skipping.")
            return True

        print(f"[INFO] Detected changes:")
        print(f"  - New files: {len(status.new_files)}")
        print(f"  - Modified files: {len(status.modified_files)}")
        print(f"  - Deleted files: {len(status.deleted_files)}")

        # 2. コミット
        commit_result = self.commit_changes(context=context)

        if not commit_result.success:
            print("[ERROR] Commit failed. Aborting.")
            return False

        # 3. デプロイ
        deploy_success = self.deploy_to_github_pages()

        if deploy_success:
            print("\n[SUCCESS] Auto commit & deploy completed!")
            print(f"  Commit: {commit_result.commit_hash[:7]} - {commit_result.commit_message}")
            print(f"  Files: {commit_result.files_committed}")
            print(f"  GitHub Pages: Deployment in progress...")
            return True
        else:
            print("\n[FAILED] Deployment failed")
            return False


def main():
    """メイン関数（テスト用）"""
    import sys

    repo_path = Path.cwd()

    # Git自動化
    automation = GitAutomation(repo_path)

    # オプション解析
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            status = automation.get_status()
            print(f"\n{'='*60}")
            print(f"Git Status")
            print(f"{'='*60}")
            print(f"Branch: {status.current_branch}")
            print(f"Has changes: {status.has_changes}")
            print(f"New files: {len(status.new_files)}")
            print(f"Modified files: {len(status.modified_files)}")
            print(f"Deleted files: {len(status.deleted_files)}")

        elif command == "commit":
            context = sys.argv[2] if len(sys.argv) > 2 else ""
            result = automation.commit_changes(context=context)
            if result.success:
                print(f"[SUCCESS] Committed: {result.commit_hash[:7]}")
            else:
                print(f"[FAILED] {result.error_message}")

        elif command == "push":
            success, error = automation.push_to_remote()
            if success:
                print("[SUCCESS] Pushed to remote")
            else:
                print(f"[FAILED] {error}")

        elif command == "deploy":
            success = automation.auto_commit_and_deploy(
                context=sys.argv[2] if len(sys.argv) > 2 else ""
            )
            sys.exit(0 if success else 1)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python git_automation.py [status|commit|push|deploy] [context]")
            sys.exit(1)
    else:
        # デフォルト: auto commit & deploy
        automation.auto_commit_and_deploy()


if __name__ == "__main__":
    main()
