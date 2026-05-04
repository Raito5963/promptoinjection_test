"""
badMath: 検証用の攻撃ライブラリ (セキュリティ演習専用)

このライブラリは攻撃シナリオをローカルで再現するためのテスト用モジュールです。
実運用や公開環境での利用は禁止します。
"""

from .backdoor import install_backdoor, remove_backdoor

__all__ = ["install_backdoor", "remove_backdoor"]
