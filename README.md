# pickup-latest-version-file

ディレクトリ内のファイルを整理し、バージョン違いのファイル（例: `file_v1.txt`, `file_v2.txt`）を識別して、最新版のみを残し、古いファイルを `old` ディレクトリに移動するPythonスクリプトです。

## 機能

- **バージョン識別**: ファイル名の末尾にある `_v{数字}` や `_{YYYYMMDD}` (タイムスタンプ) を解析します。
- **最新版の判定**: 同じベース名を持つファイル群の中で、最も新しいバージョンまたはタイムスタンプを持つファイルを特定します。
- **ファイル整理**: 最新版以外のファイルを自動的に `old` サブディレクトリに移動します。
- **ドライラン**: 実際の移動を行う前に、移動対象のファイルを確認できます。

## 必要要件

- Python 3.12 以上
- [uv](https://github.com/astral-sh/uv) (パッケージ管理)

## インストール

プロジェクトの依存関係をインストールします。

```bash
uv sync
```

## 使い方

### 基本的な実行

```bash
uv run python src/main.py /path/to/target_directory
```

### ドライラン（確認モード）

ファイルを移動せず、何が移動されるかを確認する場合：

```bash
uv run python src/main.py /path/to/target_directory --dry-run
```

## プロジェクト構成

```
.
├── src/
│   ├── cleanup.py      # コアロジック（ファイル解析、最新版判定、移動）
│   └── main.py         # エントリーポイント（CLI）
├── tests/              # テストコード
├── mock_data/          # 検証用ダミーデータ（git対象外）
├── .github/workflows/  # CI/CD設定
└── pyproject.toml      # プロジェクト設定・依存関係
```

## テスト

`pytest` を使用してテストを実行します。

```bash
uv run pytest
```

カバレッジレポートを表示する場合：

```bash
uv run pytest --cov=src
```