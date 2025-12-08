import re
import os
import shutil
from typing import List, Tuple, Optional, Dict

def group_and_identify_old_for_pattern(
    filenames: List[str], 
    pattern: re.Pattern
) -> Tuple[List[str], List[str]]:
    """
    指定された正規表現パターンに基づき、ファイルリストをグループ化し、古いバージョンを特定する。
    ファイル名内で最後にパターンに一致した箇所をバージョンとして解釈する。

    Args:
        filenames: 処理対象のファイル名リスト。
        pattern: バージョン情報を抽出するためのコンパイル済み正規表現オブジェクト。
                 この正規表現は1つのグループ（バージョン文字列）をキャプチャする必要がある。

    Returns:
        A tuple containing:
        - list[str]: 移動対象と判断された古いバージョンのファイル名リスト。
        - list[str]: このパターンによってグループ化されたすべてのファイル名リスト（最新版も含む）。
    """
    
    groups: Dict[Tuple[str, str], List[Tuple[Tuple[int, ...], str]]] = {}
    processed_files_in_pattern = set()

    for filename in filenames:
        name, ext = os.path.splitext(filename)
        matches = list(pattern.finditer(name))
        
        if not matches:
            continue

        last_match = matches[-1]
        
        base_name = name[:last_match.start()]
        version_str = last_match.group(1)
        
        try:
            version_tuple = tuple(map(int, version_str.split('.')))
        except (ValueError, TypeError):
            continue

        key = (base_name, ext)
        if key not in groups:
            groups[key] = []
        
        groups[key].append((version_tuple, filename))
        processed_files_in_pattern.add(filename)

    files_to_move = []
    for _, variants in groups.items():
        if len(variants) < 2:
            continue

        variants.sort(key=lambda x: x[0], reverse=True)
        
        for _, fname in variants[1:]:
            files_to_move.append(fname)
            
    return files_to_move, list(processed_files_in_pattern)

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
