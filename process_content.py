#!/usr/bin/env python3
"""
Digital Garden Content Processor
メインエントリーポイント

使用方法:
    python process_content.py input/text/article.txt
    python process_content.py input/text/  # ディレクトリ全体
    python process_content.py input/text/article.txt --no-thumbnail --no-git

Author: Claude Code Assistant
Date: 2025-10-04
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from automation.integrated_pipeline import main

if __name__ == "__main__":
    main()
