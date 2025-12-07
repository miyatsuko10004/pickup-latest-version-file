import re
import os
import shutil
from typing import List, Tuple, Optional, Dict

def parse_filename(filename: str) -> Tuple[str, Optional[int], str]:
    """
    ファイル名を解析する。
    戻り値: (ベース名, バージョン番号またはNone, 拡張子)
    """
    name, ext = os.path.splitext(filename)
    
    # パターン 1: 末尾が _v{N} (例: report_v1.txt)
    match_v = re.search(r'_v(\d+)$', name)
    if match_v:
        return name[:match_v.start()], int(match_v.group(1)), ext

    # パターン 2: 末尾が _{Timestamp} (8桁以上) (例: data_20250101.csv)
    match_t = re.search(r'_(\d{8,})$', name)
    if match_t:
        return name[:match_t.start()], int(match_t.group(1)), ext
        
    # パターン 3: バージョン記述なし、または解析不能
    return name, None, ext

def identify_old_versions_to_move(filenames: List[str]) -> List[str]:
    """
    ファイルリストの中から、「明らかに古いバージョンである」と断定できるファイルのみを特定する。
    バージョンが付いていないファイルや、各グループの最新版はリストに含まない。
    """
    # (ベース名, 拡張子) をキーにしてグループ化
    groups: Dict[Tuple[str, str], List[Tuple[int, str]]] = {}
    
    for filename in filenames:
        base, version, ext = parse_filename(filename)
        
        # バージョンが検出できない（怪しい）ファイルは、整理対象外として無視（＝残す）
        if version is None:
            continue

        key = (base, ext)
        if key not in groups:
            groups[key] = []
        groups[key].append((version, filename))
    
    files_to_move = []
    
    for key, variants in groups.items():
        # ファイルが1つしかない場合は、それが最新なので移動しない
        if len(variants) < 2:
            continue

        # バージョン番号で降順ソート (新しい順)
        variants.sort(key=lambda x: x[0], reverse=True)
        
        # 先頭(index 0)は最新なので残す。
        # 2番目以降(index 1~)は「明らかに古い中間バージョン」なので移動リストに追加
        for ver, fname in variants[1:]:
            files_to_move.append(fname)
        
    return files_to_move

def move_files_to_old(directory: str, target_filenames: List[str]) -> None:
    """
    指定されたファイルリスト（古いバージョン）を old ディレクトリに移動する。
    """
    if not target_filenames:
        print("移動対象のファイルはありませんでした。")
        return

    old_dir = os.path.join(directory, "old")
    if not os.path.exists(old_dir):
        os.makedirs(old_dir)
    
    count_moved = 0
    
    for filename in target_filenames:
        src_path = os.path.join(directory, filename)
        dst_path = os.path.join(old_dir, filename)
        
        # 念のためファイルの存在確認
        if not os.path.exists(src_path):
            continue

        # 移動先に同名ファイルがある場合は上書き
        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
            except OSError as e:
                print(f"Warning: 上書き前の削除に失敗しました {dst_path}: {e}")

        try:
            shutil.move(src_path, dst_path)
            print(f"Moved (Old Version): {filename}")
            count_moved += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")

    print(f"--- 完了 ---\n計 {count_moved} 個の中間ファイルを 'old/' に移動しました。")

# --- 実行ブロック ---
if __name__ == "__main__":
    # カレントディレクトリを対象にする場合
    # target_dir = os.getcwd() 
    
    # テスト用ディレクトリを指定する場合
    target_dir = "./test_files" 

    if os.path.exists(target_dir):
        print(f"対象ディレクトリ: {target_dir}")
        
        # ファイルのみをリストアップ
        all_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
        
        # 移動すべき「古いファイル」だけを特定
        move_targets = identify_old_versions_to_move(all_files)
        
        # 実行
        move_files_to_old(target_dir, move_targets)
    else:
        print(f"ディレクトリが見つかりません: {target_dir}")
