import re
import os
import shutil

def parse_filename(filename):
    """
    ファイル名を解析して、ベース名、バージョン/タイムスタンプ、拡張子を抽出する。
    戻り値はタプル: (base_name, version, extension)
    version は整数 (vN) または整数 (タイムスタンプ) または None。
    """
    name, ext = os.path.splitext(filename)
    
    # パターン 1: 末尾が _v{N}
    match_v = re.search(r'_v(\d+)$', name)
    if match_v:
        version = int(match_v.group(1))
        base_name = name[:match_v.start()]
        return base_name, version, ext

    # パターン 2: 末尾が _{Timestamp} (例: 20251114...)
    # タイムスタンプは少なくとも8桁 (YYYYMMDD) と仮定
    match_t = re.search(r'_(\d{8,})$', name)
    if match_t:
        version = int(match_t.group(1))
        base_name = name[:match_t.start()]
        return base_name, version, ext
        
    # パターン 3: バージョンサフィックスなし
    return name, None, ext


def determine_latest_files(filenames):
    """
    ファイルリストの中で最新バージョンを特定する。
    最新バージョンのファイル名のリストを返す。
    """
    groups = {}
    for filename in filenames:
        base, version, ext = parse_filename(filename)
        key = (base, ext)
        if key not in groups:
            groups[key] = []
        groups[key].append((version, filename))
    
    latest_files = []
    for key, variants in groups.items():
        # バージョンでソートする。None は -1 として扱う。
        # バージョンが None のケースを考慮する必要がある。
        variants.sort(key=lambda x: x[0] if x[0] is not None else -1, reverse=True)
        # 最初の要素が最新
        latest_files.append(variants[0][1])
        
    return latest_files




def move_old_files(directory, keep_filenames):
    """
    指定されたディレクトリ内のファイルを整理する。
    keep_filenames に含まれないファイルは old ディレクトリに移動する。
    """
    old_dir = os.path.join(directory, "old")
    
    # ディレクトリ内の全ファイルを取得
    all_files = os.listdir(directory)
    
    # keep_filenames をセットに変換して検索を高速化
    keep_set = set(keep_filenames)
    
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        
        # ディレクトリや、すでに old ディレクトリにあるものはスキップ
        if os.path.isdir(file_path):
            continue
            
        # 保持するファイルならスキップ
        if filename in keep_set:
            continue
            
        # old ディレクトリがなければ作成
        if not os.path.exists(old_dir):
            os.makedirs(old_dir)
            
        # 移動
        shutil.move(file_path, os.path.join(old_dir, filename))





