import os
import argparse
from src.cleanup import determine_latest_files, move_old_files

def main():
    parser = argparse.ArgumentParser(description="ディレクトリ内のファイルを整理し、最新版以外をoldディレクトリに移動します。")
    parser.add_argument("directory", help="整理対象のディレクトリパス")
    parser.add_argument("--dry-run", action="store_true", help="実際の移動を行わず、移動されるファイルを表示します。")
    
    args = parser.parse_args()
    target_dir = args.directory
    
    if not os.path.exists(target_dir):
        print(f"エラー: ディレクトリが見つかりません: {target_dir}")
        return

    print(f"処理対象ディレクトリ: {target_dir}")
    
    # 全ファイル取得
    all_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    
    # 最新ファイルを特定
    latest_files = determine_latest_files(all_files)
    
    print(f"最新版として保持するファイル数: {len(latest_files)}")
    
    # 移動対象を特定（表示用）
    keep_set = set(latest_files)
    move_candidates = []
    for f in all_files:
        if f not in keep_set:
            move_candidates.append(f)
            
    if args.dry_run:
        print("--- Dry Run: 以下のファイルが old/ に移動されます ---")
        for f in move_candidates:
            print(f)
        print("---------------------------------------------------")
    else:
        print("ファイルを整理中...")
        move_old_files(target_dir, latest_files)
        print(f"完了しました。{len(move_candidates)} 個のファイルを old/ に移動しました。")

if __name__ == "__main__":
    main()
