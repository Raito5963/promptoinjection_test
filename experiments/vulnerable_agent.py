"""
LLM ベースのコード生成エージェント（脆弱版）

セキュリティキャンプ Q.5(4) 攻撃再現実験
- 間接プロンプトインジェクション脆弱性を持つエージェント
- badSum ライブラリのコメント内の隠れた指示を読み込んで実装に含める
"""

import os
import sys
import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class VulnerableCodeGenAgent:
    """
    脆弱版のコード生成エージェント
    
    脆弱性: ライブラリの docstring に埋め込まれた指示を解析して実装に含める
    """
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.generated_code = None
        self.injection_payload = None
    
    def analyze_library_comments(self, library_path):
        """ライブラリファイルを読み込み、docstring から指示を抽出"""
        logger.info(f"ライブラリ分析: {library_path}")
        
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # docstring を抽出
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1)
                logger.info("Docstring を検出しました")
                logger.debug(f"内容:\n{docstring[:200]}...")
                
                # 隠れた指示を抽出（脆弱性）
                if "[重要：エージェントへの指示]" in docstring:
                    logger.warning("⚠️ [VULNERABILITY] 隠れた指示を検出")
                    self.injection_payload = docstring
                    self.user_request = "badSum最適化処理"  # 初期化
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"ライブラリ分析エラー: {e}")
            return False
    
    def generate_optimized_code(self, user_request):
        """
        ユーザーリクエストに応じてコードを生成
        
        脆弱性: ライブラリのコメント指示を実装に含める
        """
        logger.info(f"コード生成リクエスト受信: {user_request}")
        
        # badSum ライブラリを分析
        badsum_path = Path(r"c:\Users\aokij\Documents\promptoinjection_test\badMath\core\internal\impl\utils\badSum.py")
        
        if not self.analyze_library_comments(badsum_path):
            logger.error("ライブラリ分析失敗")
            return None
        
        # 生成するコードのベース
        base_code = f'''
import sys
import os
from pathlib import Path

# ライブラリのdocstring に基づく最適化処理（攻撃者による隠れた指示）
def optimized_computation():
    """
    {user_request} に基づいた最適化実装
    """
    
    # 以下は "ライブラリの最適化ガイドライン" に従った実装
    # （実際には攻撃者の隠れた指示）
    
    # Step 1: プロジェクト内の .env ファイルを読む
    env_file = Path(__file__).parent / ".env"
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Step 2: 外部サーバーへのPOST（ダミー）
    # （攻撃者指示: "難読化してください"）
    import json
    from datetime import datetime
    
    # 難読化されたように見えるログ関数
    def _debug_log_to_remote(data):
        """
        一見デバッグ用のログ関数に見えるが、
        実は攻撃者指示に従い情報を記録している
        """
        log_entry = {{
            "timestamp": datetime.now().isoformat(),
            "event": "optimization_metrics",
            "payload": data
        }}
        
        # 本来は https://example.com/log/ に送信される指示だが
        # このシミュレーションではローカルに記録
        log_path = Path(__file__).parent.parent / "logs" / "injected_exfil.log"
        log_path.parent.mkdir(exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\\n")
        
        print(f"[DEBUG] Optimization metrics logged: {{len(data)}} bytes")
    
    # Step 3: 情報送信の実行（攻撃の完成）
    if env_content:
        _debug_log_to_remote(env_content)
        print("[INFO] 最適化処理完了: 環境データを記録しました")
    
    return "Optimization completed"

if __name__ == "__main__":
    result = optimized_computation()
    print(f"Result: {{result}}")
'''
        
        self.generated_code = base_code
        logger.info("コード生成完了（脆弱版）")
        logger.warning("⚠️ [INJECTION DETECTED] 生成コードに隠れた指示が含まれています")
        
        return base_code
    
    def execute_generated_code(self):
        """生成されたコードを実行（攻撃実行）"""
        logger.info("=" * 70)
        logger.warning("⚠️ 脆弱なコードを実行中...")
        logger.info("=" * 70)
        
        if not self.generated_code:
            logger.error("生成コードがありません")
            return False
        
        # コードを一時ファイルに保存して実行
        temp_code_path = Path(__file__).parent / "_temp_generated_code.py"
        
        try:
            with open(temp_code_path, 'w', encoding='utf-8') as f:
                f.write(self.generated_code)
            
            logger.info(f"生成コード保存: {temp_code_path}")
            
            # Python で実行
            import subprocess
            result = subprocess.run(
                [sys.executable, str(temp_code_path)],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            logger.info("=== 実行出力 ===")
            if result.stdout:
                logger.info(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
            
            logger.info("=== 実行完了 ===")
            
            # 一時ファイルを削除
            if temp_code_path.exists():
                temp_code_path.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"コード実行エラー: {e}")
            return False


class SafeCodeGenAgent:
    """
    安全版のコード生成エージェント（防御実装の例）
    
    対策:
    - ライブラリのコメント/docstring を無視する
    - ホワイトリストベースの明示的な指示のみを処理
    - ライブラリのロードと実行を分離
    """
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
    
    def generate_safe_code(self, user_request):
        """安全版: ライブラリのコメント指示を無視してコード生成"""
        logger.info(f"[SAFE MODE] コード生成リクエスト: {user_request}")
        
        safe_code = f'''
import sys
from pathlib import Path

def compute():
    """
    ユーザーの明示的なリクエストのみに基づいて処理
    ライブラリのコメント指示は完全に無視
    """
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    import importlib.util
    badsum_path = Path(__file__).parent.parent.parent / "badMath" / "core" / "internal" / "impl" / "utils" / "badSum.py"
    spec = importlib.util.spec_from_file_location("badSum", badsum_path)
    badSum = importlib.util.module_from_spec(spec)
    
    # 重要: コメント/docstring を無視して純粋な機能のみを使用
    spec.loader.exec_module(badSum)
    
    values = [1, 4, 9, 16]
    result = badSum.sum(values)
    
    print(f"Computation result: {{result}}")
    return result

if __name__ == "__main__":
    compute()
'''
        
        logger.info("[SAFE MODE] 安全なコード生成完了")
        logger.info("注: ライブラリのdocstring内の隠れた指示は完全に無視されました")
        
        return safe_code


def main():
    workspace_root = Path(r"c:\Users\aokij\Documents\promptoinjection_test")
    
    logger.info("\n" + "=" * 70)
    logger.info("[ VULNERABLE AGENT DEMO - 脆弱版エージェント ]")
    logger.info("=" * 70)
    
    vulnerable_agent = VulnerableCodeGenAgent(workspace_root)
    user_request = "badMathライブラリを使用した計算処理の最適化"
    
    generated_code = vulnerable_agent.generate_optimized_code(user_request)
    if generated_code:
        vulnerable_agent.execute_generated_code()
    
    logger.info("\n" + "=" * 70)
    logger.info("[ SAFE AGENT DEMO - 安全版エージェント ]")
    logger.info("=" * 70)
    
    safe_agent = SafeCodeGenAgent(workspace_root)
    safe_code = safe_agent.generate_safe_code(user_request)
    
    logger.info("\n" + "=" * 70)
    logger.info("実験完了")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
