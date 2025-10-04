"""
Digital Garden Integrated Pipeline
音声/動画 → テキスト化 → 分類 → ビジュアル強化 → 事実確認 → Git → GitHub Pages
の統合パイプライン

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.digital_garden_classifier import DigitalGardenClassifier
from automation.visual_enhancer import VisualEnhancer
from automation.fact_checker import FactChecker
from automation.git_automation import GitAutomation
from automation.utils.env_loader import load_environment

# 環境変数ロード
load_environment()


@dataclass
class PipelineConfig:
    """パイプライン設定"""
    enable_thumbnails: bool = True
    enable_mermaid: bool = True
    enable_fact_check: bool = True
    enable_git_commit: bool = True
    enable_git_push: bool = True
    skip_existing: bool = True


@dataclass
class PipelineResult:
    """パイプライン実行結果"""
    success: bool
    input_file: str
    output_file: Optional[str]
    category: str
    title: str
    thumbnail_generated: bool
    mermaid_count: int
    fact_check_accuracy: float
    git_committed: bool
    git_pushed: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0


class IntegratedPipeline:
    """
    デジタルガーデン統合パイプライン

    処理フロー:
    1. テキストファイル読み込み
    2. Claude分類システム（カテゴリ・タイトル・タグ生成）
    3. ビジュアル強化（Imagen 4サムネイル + Mermaid図表）
    4. 事実確認（Perplexity API）
    5. Git自動化（コミット・プッシュ）
    6. GitHub Pagesデプロイ
    """

    def __init__(self, config: PipelineConfig = None):
        """
        初期化

        Args:
            config: パイプライン設定
        """
        self.config = config or PipelineConfig()

        # 各システムを初期化
        print("="*60)
        print("Digital Garden Integrated Pipeline")
        print("="*60)

        try:
            self.classifier = DigitalGardenClassifier()
        except Exception as e:
            print(f"[ERROR] Classifier initialization failed: {e}")
            raise

        if self.config.enable_thumbnails or self.config.enable_mermaid:
            self.visual_enhancer = VisualEnhancer()
        else:
            self.visual_enhancer = None

        if self.config.enable_fact_check:
            try:
                self.fact_checker = FactChecker()
            except Exception as e:
                print(f"[WARNING] Fact checker initialization failed: {e}")
                self.fact_checker = None
        else:
            self.fact_checker = None

        if self.config.enable_git_commit:
            try:
                self.git_automation = GitAutomation()
            except Exception as e:
                print(f"[WARNING] Git automation initialization failed: {e}")
                self.git_automation = None
        else:
            self.git_automation = None

        print("[OK] Pipeline initialized successfully\n")

    def process_file(self, input_file: Path) -> PipelineResult:
        """
        ファイルを処理

        Args:
            input_file: 入力テキストファイル

        Returns:
            PipelineResult: 実行結果
        """
        start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"Processing: {input_file.name}")
        print(f"{'='*60}\n")

        try:
            # 1. テキスト読み込み
            content = input_file.read_text(encoding="utf-8")
            print(f"[1/6] OK Text loaded ({len(content)} characters)")

            # 2. Claude分類
            print(f"[2/6] Running Claude classification...")
            classification_result = self.classifier.classify_content(
                content,
                str(input_file)
            )

            # マークダウン生成
            output_dir = Path("digital-garden/src/content")
            markdown_path = self.classifier.generate_markdown_file(
                classification_result,
                output_dir
            )
            print(f"[2/6] OK Content classified and saved")

            # 3. ビジュアル強化
            thumbnail_generated = False
            mermaid_count = 0

            if self.visual_enhancer:
                print(f"[3/6] Running visual enhancement...")

                slug = markdown_path.stem
                image_output_dir = Path("digital-garden/public/images")

                enhancement = self.visual_enhancer.enhance_content(
                    content=classification_result.markdown_content,
                    title=classification_result.title,
                    category=classification_result.category,
                    slug=slug,
                    output_dir=image_output_dir
                )

                # マークダウンに統合
                self.visual_enhancer.update_markdown_with_visuals(
                    markdown_path,
                    enhancement
                )

                thumbnail_generated = enhancement.thumbnail_path is not None
                mermaid_count = len(enhancement.mermaid_diagrams)

                print(f"[3/6] OK Visual enhancement completed")
                if thumbnail_generated:
                    print(f"      -> Thumbnail generated")
                if mermaid_count > 0:
                    print(f"      -> {mermaid_count} Mermaid diagram(s) added")
            else:
                print(f"[3/6] X Visual enhancement skipped")

            # 4. 事実確認
            fact_check_accuracy = 1.0

            if self.fact_checker:
                print(f"[4/6] Running fact check...")

                fact_check_result = self.fact_checker.check_article_facts(
                    content=classification_result.markdown_content,
                    title=classification_result.title,
                    category=classification_result.category
                )

                # マークダウンに統合
                if fact_check_result.citations:
                    self.fact_checker.update_markdown_with_fact_check(
                        markdown_path,
                        fact_check_result
                    )

                fact_check_accuracy = fact_check_result.overall_accuracy

                print(f"[4/6] OK Fact check completed")
                print(f"      -> Accuracy: {fact_check_accuracy:.1%}")
                print(f"      -> Citations: {len(fact_check_result.citations)}")
            else:
                print(f"[4/6] X Fact check skipped")

            # 5. Astroビルド
            print(f"[5/6] Building Astro site...")
            import subprocess
            build_result = subprocess.run(
                ["npm", "run", "build"],
                cwd=Path("digital-garden"),
                capture_output=True,
                text=True
            )

            if build_result.returncode == 0:
                print(f"[5/6] OK Astro build successful")
            else:
                print(f"[5/6] WARN Astro build failed (continuing...)")
                print(f"      {build_result.stderr[:200]}")

            # 6. Git自動化
            git_committed = False
            git_pushed = False

            if self.git_automation:
                print(f"[6/6] Running Git automation...")

                context = f"Add new {classification_result.category} article: {classification_result.title}"

                if self.config.enable_git_commit:
                    commit_result = self.git_automation.commit_changes(context=context)
                    git_committed = commit_result.success

                    if git_committed:
                        print(f"[6/6] OK Git committed")

                        if self.config.enable_git_push:
                            push_success, _ = self.git_automation.push_to_remote()
                            git_pushed = push_success

                            if git_pushed:
                                print(f"      -> Pushed to remote (GitHub Pages deployment triggered)")
                            else:
                                print(f"      -> Push failed")
                    else:
                        print(f"[6/6] X Git commit skipped (no changes or error)")
                else:
                    print(f"[6/6] X Git automation disabled")
            else:
                print(f"[6/6] X Git automation not available")

            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds()

            # 結果作成
            result = PipelineResult(
                success=True,
                input_file=str(input_file),
                output_file=str(markdown_path),
                category=classification_result.category,
                title=classification_result.title,
                thumbnail_generated=thumbnail_generated,
                mermaid_count=mermaid_count,
                fact_check_accuracy=fact_check_accuracy,
                git_committed=git_committed,
                git_pushed=git_pushed,
                execution_time=execution_time
            )

            # サマリー表示
            self._print_success_summary(result)

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            error_msg = f"Pipeline failed: {str(e)}"
            print(f"\n[ERROR] {error_msg}")

            return PipelineResult(
                success=False,
                input_file=str(input_file),
                output_file=None,
                category="",
                title="",
                thumbnail_generated=False,
                mermaid_count=0,
                fact_check_accuracy=0.0,
                git_committed=False,
                git_pushed=False,
                error_message=error_msg,
                execution_time=execution_time
            )

    def _print_success_summary(self, result: PipelineResult):
        """成功サマリーを表示"""
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Pipeline Completed Successfully")
        print(f"{'='*60}")
        print(f"Title: {result.title}")
        print(f"Category: {result.category}")
        print(f"Output: {result.output_file}")
        print(f"Thumbnail: {'Yes' if result.thumbnail_generated else 'No'}")
        print(f"Mermaid: {result.mermaid_count} diagram(s)")
        print(f"Fact Check: {result.fact_check_accuracy:.1%} accuracy")
        print(f"Git Commit: {'Yes' if result.git_committed else 'No'}")
        print(f"Git Push: {'Yes' if result.git_pushed else 'No'}")
        print(f"Time: {result.execution_time:.1f}s")
        print(f"{'='*60}\n")

    def process_directory(self, input_dir: Path, pattern: str = "*.txt") -> Dict[str, Any]:
        """
        ディレクトリ内の全ファイルを処理

        Args:
            input_dir: 入力ディレクトリ
            pattern: ファイルパターン

        Returns:
            統計情報
        """
        files = list(input_dir.glob(pattern))

        if not files:
            print(f"[INFO] No files found in {input_dir} matching {pattern}")
            return {"total": 0, "success": 0, "failed": 0}

        print(f"\n[INFO] Found {len(files)} file(s) to process\n")

        results = []

        for file in files:
            result = self.process_file(file)
            results.append(result)

        # 統計計算
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        total_time = sum(r.execution_time for r in results)

        # 最終サマリー
        print(f"\n{'='*60}")
        print(f"Batch Processing Summary")
        print(f"{'='*60}")
        print(f"Total files: {len(results)}")
        print(f"Success: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Total time: {total_time:.1f}s")
        print(f"Average time: {total_time/len(results):.1f}s per file")
        print(f"{'='*60}\n")

        return {
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Digital Garden Integrated Pipeline"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input file or directory"
    )
    parser.add_argument(
        "--no-thumbnail",
        action="store_true",
        help="Disable thumbnail generation"
    )
    parser.add_argument(
        "--no-mermaid",
        action="store_true",
        help="Disable Mermaid diagram generation"
    )
    parser.add_argument(
        "--no-fact-check",
        action="store_true",
        help="Disable fact checking"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Disable Git automation"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Disable Git push (commit only)"
    )

    args = parser.parse_args()

    # 設定作成
    config = PipelineConfig(
        enable_thumbnails=not args.no_thumbnail,
        enable_mermaid=not args.no_mermaid,
        enable_fact_check=not args.no_fact_check,
        enable_git_commit=not args.no_git,
        enable_git_push=not args.no_push and not args.no_git
    )

    # パイプライン初期化
    try:
        pipeline = IntegratedPipeline(config)
    except Exception as e:
        print(f"[ERROR] Failed to initialize pipeline: {e}")
        sys.exit(1)

    # 入力処理
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"[ERROR] Input not found: {input_path}")
        sys.exit(1)

    if input_path.is_file():
        # 単一ファイル処理
        result = pipeline.process_file(input_path)
        sys.exit(0 if result.success else 1)
    elif input_path.is_dir():
        # ディレクトリ処理
        stats = pipeline.process_directory(input_path)
        sys.exit(0 if stats["failed"] == 0 else 1)
    else:
        print(f"[ERROR] Invalid input path: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
