import os
import argparse
import re
from dotenv import load_dotenv
from cleanup import group_and_identify_old_for_pattern, move_files_to_old

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="ディレクトリ内のファイルを整理し、明らかに古いバージョンのみをoldディレクトリに移動します。")
    parser.add_argument("directory", nargs="?", help="整理対象のディレクトリパス")
    parser.add_argument("--dry-run", action="store_true", help="実際の移動を行わず、移動されるファイルを表示します。")
    
    args = parser.parse_args()
    target_dir = args.directory or os.getenv("TARGET_DIRECTORY")
    
    if not target_dir:
        print("エラー: ディレクトリが指定されていません。引数で指定するか、.envファイルに TARGET_DIRECTORY を設定してください。")
        return

    if not os.path.exists(target_dir):
        print(f"エラー: ディレクトリが見つかりません: {target_dir}")
        return

    print(f"処理対象ディレクトリ: {target_dir}")

    # 優先順位順の正規表現パターンリスト
    # 各パターンはバージョン文字列のみをキャプチャする
    version_patterns = [
        # パターン1: _v1.2.3 や _1.2 のようなドット区切りのバージョン
        re.compile(r'[_-]v?(\d+\.\d+[\.\d]*)'),
        # パターン2: _20250101 のような日付形式のバージョン
        re.compile(r'[_-](\d{8,})'),
        # パターン3: _v1, _t1, _r1, _1 のようなシンプルな整数バージョン
        re.compile(r'[_-][vtr]?(\d+)'),
    ]

    # 全ファイル取得
    all_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    
    total_files_to_move = set()
    handled_files = set()

    for pattern in version_patterns:
        # まだ処理されていないファイルのみを対象とする
        candidate_files = [f for f in all_files if f not in handled_files]
        
        files_to_move_for_pattern, processed_files_for_pattern = group_and_identify_old_for_pattern(candidate_files, pattern)
        
        # 今回のパターンで処理されたファイルを記録
        handled_files.update(processed_files_for_pattern)
        # 今回のパターンで移動対象となったファイルを追加
        total_files_to_move.update(files_to_move_for_pattern)

    # setをリストに変換
    final_files_to_move = sorted(list(total_files_to_move))

    print(f"検出されたファイル総数: {len(all_files)}")
    print(f"移動対象（古いバージョン）: {len(final_files_to_move)}")
    
    if args.dry_run:
        print("\n--- Dry Run: 以下のファイルが old/ に移動されます ---")
        if not final_files_to_move:
            print("(移動対象のファイルはありません)")
        else:
            for f in final_files_to_move:
                print(f"[Move] {f}")
        print("---------------------------------------------------")
        print("※ Dry Run モードのため、実際の移動は行われませんでした。")
    else:
        if not final_files_to_move:
            print("移動対象のファイルがないため、処理を終了します。")
        else:
            print("\nファイルを整理中...")
            move_files_to_old(target_dir, final_files_to_move)
            # 完了メッセージは move_files_to_old 内でも出していますが、main側でも終了を通知
            print("全ての処理が完了しました。")

if __name__ == "__main__":
    main()
