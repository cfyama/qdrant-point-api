# Qdrant Point API

Qdrantベクトルデータベースから医学ノート（CUBEC_NOTE）および医薬品添付文書（PACKAGE_INSERT）のデータを取得するためのFastAPI ベースのREST APIサービスです。

## 機能

- **ポイントID指定取得**: 指定したポイントIDのデータを取得
- **CUBEC_NOTE章取得**: 疾患名とメインカテゴリで医学ノートの特定章を検索
- **CUBEC_NOTEページ取得**: 疾患名で医学ノートのすべてのページを検索
- **PACKAGE_INSERT章取得**: YJコードとセクションタイトルで医薬品情報を検索
- **自動URL取得**: PACKAGE_INSERTコレクションの場合、医薬品URLを自動的に取得して付加
  - **複数URL対応**: カンマ区切りのYJコードを持つ医薬品の場合、全ての添付文書URLを配列として取得
  - 重複URLは自動的に削除され、ユニークなURLのみを返す
- **CORS対応**: クロスオリジンリクエストをサポート

## 技術スタック

- **Python**: 3.9+
- **FastAPI**: 高速なWeb APIフレームワーク
- **Qdrant Client**: Qdrantベクトルデータベースクライアント
- **Poetry**: 依存関係管理
- **Docker**: コンテナ化対応

## セットアップ

### 前提条件

- Python 3.9以上
- Poetry
- Qdrantサーバーへのアクセス

### ローカル開発環境

1. **リポジトリをクローン**

```bash
git clone https://github.com/cfyama/qdrant-point-api.git
cd qdrant-point-api
```

2. **依存関係をインストール**

```bash
poetry install
```

3. **環境変数を設定**

`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
# Qdrant設定
QDRANT_URL=http://your-qdrant-server:6333
QDRANT_API_KEY=your-api-key

# コレクション名
COLLECTION_CUBEC_NOTE=20251018_医学ノート_3large
COLLECTION_PACKAGE_INSERT=20250810_医薬品添付文書_3large

# 医薬品URL取得API
DRUG_API_BASE_URL=https://your-api-endpoint.com/

# サーバー設定
PORT=7860

# CORS設定（カンマ区切りで複数指定可能）
CORS_ORIGINS=http://localhost:3001,https://example.com
```

4. **サーバーを起動**

```bash
poetry run python src/app.py
```

サーバーは `http://localhost:7860` で起動します。

### Dockerを使用する場合

1. **Dockerイメージをビルド**

```bash
docker build -t qdrant-point-api .
```

2. **コンテナを起動**

```bash
docker run -p 7860:7860 --env-file .env qdrant-point-api
```

## API エンドポイント

### 1. ポイントID指定取得API

指定したポイントIDのデータを取得します。

**エンドポイント:** `POST /api`

**リクエストボディ:**
```json
{
  "point_ids": [1, 2, 3],
  "collection_name": "CUBEC_NOTE",
  "with_payload": true,
  "with_vectors": false
}
```

**パラメータ:**
- `point_ids` (必須): 取得したいポイントIDのリスト
- `collection_name` (オプション): `CUBEC_NOTE` または `PACKAGE_INSERT` (デフォルト: `CUBEC_NOTE`)
- `with_payload` (オプション): ペイロードを含めるか (デフォルト: `true`)
- `with_vectors` (オプション): ベクトルを含めるか (デフォルト: `false`)

**使用例:**
```bash
curl -X POST http://localhost:7860/api \
  -H "Content-Type: application/json" \
  -d '{
    "point_ids": [0, 1, 2],
    "collection_name": "CUBEC_NOTE",
    "with_payload": true
  }'
```

---

### 2. CUBEC_NOTE章取得API

タイトルと疾患名で医学ノートの特定章を検索します。

**エンドポイント:** `POST /api/cubec-note/chapter`

**リクエストボディ:**
```json
{
  "title": "WPW症候群 -- 概要・推奨",
  "disease": "WPW症候群",
  "with_payload": true,
  "with_vectors": false
}
```

**パラメータ:**
- `title` (必須): 検索する章のタイトル
- `disease` (必須): 検索する疾患名
- `with_payload` (オプション): ペイロードを含めるか (デフォルト: `true`)
- `with_vectors` (オプション): ベクトルを含めるか (デフォルト: `false`)

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": 0,
      "payload": {
        "title": "WPW症候群 -- 概要・推奨",
        "disease": "WPW症候群",
        "context": "# WPW症候群（循環器）\n## WPW症候群 -- 概要・推奨\n\n### 概要\n\n  * WPW症候群は、心房と心室の間に副伝導路（ケント束）とよばれる、正常な刺激伝導路以外の興奮の通り道が存在する疾患です。\n...",
        "section_title": "概要",
        "main_department": "循環器",
        "supervisor": "せい@循環器内科x製薬",
        "gl_department": "循環器",
        "gl_publisher": "日本循環器学会/日本不整脈心電学会",
        "gl_name": "2024 年JCS/JHRS ガイドラインフォーカスアップデート版不整脈治療",
        "gl_link": "https://www.j-circ.or.jp/cms/wp-content/uploads/2024/03/JCS2024_Iwasaki.pdf",
        "content_length": 379,
        "line_number": 2,
        "section_level": 4
      }
    }
  ],
  "count": 2
}
```

**使用例:**
```bash
curl -X POST http://localhost:7860/api/cubec-note/chapter \
  -H "Content-Type: application/json" \
  -d '{
    "title": "WPW症候群 -- 概要・推奨",
    "disease": "WPW症候群"
  }'
```

---

### 3. CUBEC_NOTEページ取得API

疾患名で医学ノートのすべてのページを検索します。

**エンドポイント:** `POST /api/cubec-note/page`

**リクエストボディ:**
```json
{
  "disease": "WPW症候群",
  "with_payload": true,
  "with_vectors": false
}
```

**パラメータ:**
- `disease` (必須): 検索する疾患名
- `with_payload` (オプション): ペイロードを含めるか (デフォルト: `true`)
- `with_vectors` (オプション): ベクトルを含めるか (デフォルト: `false`)

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": 0,
      "payload": {
        "title": "WPW症候群 -- 概要・推奨",
        "disease": "WPW症候群",
        "context": "# WPW症候群（循環器）\n## WPW症候群 -- 概要・推奨\n\n### 概要\n...",
        "section_title": "概要",
        "main_department": "循環器",
        ...
      }
    },
    {
      "id": 1,
      "payload": {
        "title": "WPW症候群 -- 概要・推奨",
        "disease": "WPW症候群",
        "context": "# WPW症候群（循環器）\n## WPW症候群 -- 概要・推奨\n\n### 推奨\n...",
        "section_title": "推奨",
        ...
      }
    }
  ],
  "count": 10
}
```

**使用例:**
```bash
curl -X POST http://localhost:7860/api/cubec-note/page \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "WPW症候群",
    "with_payload": true
  }'
```

---

### 4. PACKAGE_INSERT章取得API

添付文書番号とセクションタイトルで医薬品情報を検索します。医薬品URLも自動的に取得して付加されます。

**エンドポイント:** `POST /api/package-insert/chapter`

**リクエストボディ:**
```json
{
  "yj_code": "3399004M1425",
  "section_title": "禁忌",
  "with_payload": true,
  "with_vectors": false
}
```

**パラメータ:**
- `yj_code` (必須): YJコード（医薬品コード）
- `section_title` (必須): セクションタイトル
- `with_payload` (オプション): ペイロードを含めるか (デフォルト: `true`)
- `with_vectors` (オプション): ベクトルを含めるか (デフォルト: `false`)

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1234,
      "payload": {
        "yj_code": "3399004M1425",
        "section_title": "禁忌",
        "url": [
          "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/480187_3399004M1425_1_06"
        ],
        ...
      }
    }
  ],
  "count": 5
}
```

**複数URL対応:**
- カンマ区切りのYJコード（例: `"2399009F1092, 2399009F2064"`）を持つ医薬品の場合、全てのYJコードに対応する添付文書URLを取得し、`url`フィールドに配列として返します
- 重複するURLは自動的に削除されます
- 例: 3つの異なる添付文書URLがある場合
  ```json
  "url": [
    "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/530213_2399009F1092_1_16",
    "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/530213_2399009F1092_4_05",
    "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/530213_2399009F1092_3_05"
  ]
  ```

**使用例:**
```bash
curl -X POST http://localhost:7860/api/package-insert/chapter \
  -H "Content-Type: application/json" \
  -d '{
    "yj_code": "3399004M1425",
    "section_title": "禁忌"
  }'
```

---

### 5. コレクション一覧取得API

利用可能なコレクション一覧を取得します。

**エンドポイント:** `GET /collections`

**使用例:**
```bash
curl http://localhost:7860/collections
```

**レスポンス:**
```json
{
  "collections": [
    {
      "key": "CUBEC_NOTE",
      "name": "20251018_医学ノート_3large"
    },
    {
      "key": "PACKAGE_INSERT",
      "name": "20250810_医薬品添付文書_3large"
    }
  ]
}
```

## データ構造

### CUBEC_NOTEコレクション

APIレスポンスでは、内部のネスト構造をフラット化して返します：

```json
{
  "id": 0,
  "payload": {
    "title": "WPW症候群 -- 概要・推奨",
    "disease": "WPW症候群",
    "context": "# WPW症候群（循環器）\n## WPW症候群 -- 概要・推奨\n\n### 概要\n...",
    "section_title": "概要",
    "main_department": "循環器",
    "sub_department": "",
    "supervisor": "せい@循環器内科x製薬",
    "supervision_condition": "匿名",
    "draft_chars": "4,537",
    "gl_department": "循環器",
    "gl_publisher": "日本循環器学会/日本不整脈心電学会",
    "gl_name": "2024 年JCS/JHRS ガイドラインフォーカスアップデート版不整脈治療",
    "gl_link": "https://www.j-circ.or.jp/cms/wp-content/uploads/2024/03/JCS2024_Iwasaki.pdf",
    "gl_free_or_paid": "無料",
    "gl_count": 1,
    "file_name": "WPW症候群_draft_251012.md",
    "source": "医学ノート",
    "publicationDate": "2025-10-12",
    "section_level": 4,
    "line_number": 2,
    "content_length": 379,
    "is_split": false,
    "id": 496
  }
}
```

**主要フィールド:**
- `title`: 章のタイトル（メインカテゴリ）
- `disease`: 疾患名
- `context`: マークダウン形式の本文内容

### PACKAGE_INSERTコレクション

```json
{
  "id": 1234,
  "payload": {
    "package_insert_no": "添付文書番号",
    "section_title": "セクションタイトル",
    "url": "医薬品URL（自動取得）",
    ...
  }
}
```

## エラーレスポンス

すべてのAPIで共通のエラーレスポンス形式：

```json
{
  "detail": "エラーメッセージ"
}
```

**主なHTTPステータスコード:**
- `200 OK`: 成功
- `400 Bad Request`: リクエストが不正、またはQdrant APIエラー
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバー内部エラー

## テスト

### ローカル環境のテスト

```bash
# APIサーバーを起動
poetry run python src/app.py

# 別のターミナルでテストを実行
python test_new_apis.py
```

### AWS環境のテスト

```bash
# AWS環境の包括的なテストを実行
poetry run python test_aws_apis.py
```

**AWSエンドポイント**: `https://3j2q4wuiw4.ap-northeast-1.awsapprunner.com`

**テスト結果**: 全ての機能が正常に動作しています（詳細は `AWS_TEST_RESULTS.md` を参照）

### 手動テスト例

#### ローカル環境

```bash
# CUBEC_NOTEページ取得
curl -X POST http://localhost:7860/api/cubec-note/page \
  -H "Content-Type: application/json" \
  -d '{"disease": "WPW症候群", "with_payload": true}' \
  -s | python3 -m json.tool

# CUBEC_NOTE章取得
curl -X POST http://localhost:7860/api/cubec-note/chapter \
  -H "Content-Type: application/json" \
  -d '{"title": "WPW症候群 -- 概要・推奨", "disease": "WPW症候群"}' \
  -s | python3 -m json.tool

# PACKAGE_INSERT章取得
curl -X POST http://localhost:7860/api/package-insert/chapter \
  -H "Content-Type: application/json" \
  -d '{"yj_code": "1124023F1029", "section_title": "禁忌"}' \
  -s | python3 -m json.tool
```

#### AWS環境

```bash
# CUBEC_NOTEページ取得
curl -X POST https://3j2q4wuiw4.ap-northeast-1.awsapprunner.com/api/cubec-note/page \
  -H "Content-Type: application/json" \
  -d '{"disease": "WPW症候群", "with_payload": true}' \
  -s | python3 -m json.tool

# PACKAGE_INSERT章取得
curl -X POST https://3j2q4wuiw4.ap-northeast-1.awsapprunner.com/api/package-insert/chapter \
  -H "Content-Type: application/json" \
  -d '{"yj_code": "1124023F1029", "section_title": "禁忌"}' \
  -s | python3 -m json.tool
```

## パフォーマンス最適化

### レスポンス変換

CUBEC_NOTEコレクションでは、Qdrantの新しいデータ構造（`page_content`と`metadata`のネスト構造）を、APIの互換性を保つため元のフラット構造に変換して返します：

- `metadata.main_category` → `title`
- `metadata.disease_name` → `disease`
- `page_content` → `context`

これにより、データベース構造が変更されても、APIクライアントは変更なしで使用できます。

### URL取得の最適化

PACKAGE_INSERTコレクションでは、以下の最適化を実施しています：

1. **重複排除**: 同じ`package_insert_no`に対するURL取得APIは1回のみ呼び出し
2. **並行処理**: 複数の異なる`package_insert_no`に対して並行でURL取得を実行
3. **キャッシング**: 取得したURLをキャッシュして各ポイントに効率的に付加

### 制限事項

- 最大取得件数: 10,000件（scrollのlimit）
- Qdrantクライアントタイムアウト: 60秒
- フィルター検索は完全一致のみ対応

## 環境変数一覧

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `QDRANT_URL` | ✓ | - | QdrantサーバーのURL |
| `QDRANT_API_KEY` | ✓ | - | Qdrant APIキー |
| `COLLECTION_CUBEC_NOTE` | ✓ | - | CUBEC_NOTEコレクション名 |
| `COLLECTION_PACKAGE_INSERT` | ✓ | - | PACKAGE_INSERTコレクション名 |
| `DRUG_API_BASE_URL` | ✓ | - | 医薬品URL取得APIのベースURL |
| `PORT` | - | `8000` | APIサーバーのポート番号 |
| `CORS_ORIGINS` | - | `*` | 許可するCORSオリジン（カンマ区切り） |

## プロジェクト構造

```
qdrant_point_api/
├── src/
│   ├── app.py              # メインアプリケーション
│   └── app_.py             # 旧バージョン（参考用）
├── test_api.py             # テストスクリプト（旧）
├── test_new_apis.py        # テストスクリプト（新）
├── API_DOCUMENTATION.md    # 詳細APIドキュメント
├── API_SPECIFICATION.md    # API仕様書
├── Dockerfile              # Dockerイメージ定義
├── pyproject.toml          # Poetry設定
├── poetry.lock             # 依存関係ロックファイル
└── README.md               # このファイル
```

## ライセンス

このプロジェクトは内部使用のみを目的としています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssuesで受け付けています。

## サポート

問題が発生した場合は、以下を確認してください：

1. 環境変数が正しく設定されているか
2. Qdrantサーバーにアクセスできるか
3. APIサーバーのログを確認（`INFO`レベルでリクエスト/レスポンスをログ出力）

---

Generated with [Claude Code](https://claude.com/claude-code)
