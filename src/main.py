import os
import argparse
from cleanup import identify_old_versions_to_move, move_files_to_old

def main():
    parser = argparse.ArgumentParser(description="ディレクトリ内のファイルを整理し、明らかに古いバージョンのみをoldディレクトリに移動します。")
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
    
    # 最新版を特定するのではなく、「移動すべき古いファイル」を直接特定する
    files_to_move = identify_old_versions_to_move(all_files)
    
    print(f"検出されたファイル総数: {len(all_files)}")
    print(f"移動対象（古いバージョン）: {len(files_to_move)}")
    
    if args.dry_run:
        print("\n--- Dry Run: 以下のファイルが old/ に移動されます ---")
        if not files_to_move:
            print("(移動対象のファイルはありません)")
        else:
            for f in files_to_move:
                print(f"[Move] {f}")
        print("---------------------------------------------------")
        print("※ Dry Run モードのため、実際の移動は行われませんでした。")
    else:
        if not files_to_move:
            print("移動対象のファイルがないため、処理を終了します。")
        else:
            print("\nファイルを整理中...")
            move_files_to_old(target_dir, files_to_move)
            # 完了メッセージは move_files_to_old 内でも出していますが、main側でも終了を通知
            print("全ての処理が完了しました。")

if __name__ == "__main__":
    main()
