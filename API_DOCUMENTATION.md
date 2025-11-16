# Qdrant Point API ドキュメント

## 新規追加API

### 1. CUBEC_NOTE章取得API

**エンドポイント:** `POST /api/cubec-note/chapter`

**説明:** CUBEC_NOTEコレクションから、titleとdiseaseの両方が一致するポイントを検索して返します。

**リクエストボディ:**
```json
{
  "title": "string",          // 必須: 検索する章のタイトル
  "disease": "string",         // 必須: 検索する疾患名
  "with_payload": true,        // オプション: payloadを含めるか (デフォルト: true)
  "with_vectors": false        // オプション: vectorを含めるか (デフォルト: false)
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": "point_id",
      "payload": {
        "title": "章タイトル",
        "disease": "疾患名",
        "reviewer": {
          "name": "XX 太郎",
          "affiliated_hospital": "XX病院",
          "board_certified": [
            "XX専門医"
          ]
        }
        // その他のpayloadフィールド
      }
    }
  ],
  "count": 10  // 取得件数
}
```

**注意:** `reviewer`フィールドは現在仮データを返します。実データ準備後に実データに切り替わります。

**使用例:**
```bash
curl -X POST http://localhost:8000/api/cubec-note/chapter \
  -H "Content-Type: application/json" \
  -d '{
    "title": "糖尿病の治療",
    "disease": "2型糖尿病"
  }'
```

---

### 2. CUBEC_NOTEページ取得API

**エンドポイント:** `POST /api/cubec-note/page`

**説明:** CUBEC_NOTEコレクションから、diseaseが一致する全てのポイントを検索して返します。

**リクエストボディ:**
```json
{
  "disease": "string",        // 必須: 検索する疾患名
  "with_payload": true,        // オプション: payloadを含めるか (デフォルト: true)
  "with_vectors": false        // オプション: vectorを含めるか (デフォルト: false)
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": "point_id",
      "payload": {
        "disease": "疾患名",
        "reviewer": {
          "name": "XX 太郎",
          "affiliated_hospital": "XX病院",
          "board_certified": [
            "XX専門医"
          ]
        }
        // その他のpayloadフィールド
      }
    }
  ],
  "count": 25  // 取得件数
}
```

**注意:** `reviewer`フィールドは現在仮データを返します。実データ準備後に実データに切り替わります。

**使用例:**
```bash
curl -X POST http://localhost:8000/api/cubec-note/page \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "2型糖尿病"
  }'
```

---

### 3. PACKAGE_INSERT章取得API

**エンドポイント:** `POST /api/package-insert/chapter`

**説明:** PACKAGE_INSERTコレクションから、package_insert_noとsection_titleの両方が一致するポイントを検索して返します。また、各ポイントに対してURLを自動的に取得して付加します。

**リクエストボディ:**
```json
{
  "package_insert_no": "string",    // 必須: 添付文書番号
  "section_title": "string",        // 必須: セクションタイトル
  "with_payload": true,             // オプション: payloadを含めるか (デフォルト: true)
  "with_vectors": false             // オプション: vectorを含めるか (デフォルト: false)
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": "point_id",
      "payload": {
        "package_insert_no": "2149117F1022_1_01",
        "section_title": "効能又は効果",
        "url": "https://example.com/drug/2149117F1022",  // 自動取得されたURL
        // その他のpayloadフィールド
      }
    }
  ],
  "count": 5  // 取得件数
}
```

**使用例:**
```bash
curl -X POST http://localhost:8000/api/package-insert/chapter \
  -H "Content-Type: application/json" \
  -d '{
    "package_insert_no": "2149117F1022_1_01",
    "section_title": "効能又は効果"
  }'
```

---

### 4. PACKAGE_INSERT主要セクション取得API

**エンドポイント:** `POST /api/package-insert/core-sections`

**説明:** PACKAGE_INSERTコレクションから、YJコードを指定して主要な4つのセクション（効能・効果、用法・用量、禁忌、副作用）を一括取得します。

**リクエストボディ:**
```json
{
  "yj_code": "string"    // 必須: YJコード（医薬品コード）
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "yj_code": "62504A4A1023",
    "payload": {
      "indications": "効能又は効果のテキスト...",
      "dosage_and_administration": "用法及び用量のテキスト...",
      "contraindications": "禁忌のテキスト...",
      "adverse_reactions": "副作用のテキスト..."
    }
  }
}
```

**レスポンスフィールド:**
- `indications`: 効能又は効果（または効能・効果）
- `dosage_and_administration`: 用法及び用量（または用法・用量）
- `contraindications`: 禁忌
- `adverse_reactions`: 副作用

**特記事項:**
- セクションが存在しない場合は空文字列 `""` が返されます
- 同じYJコードで複数の添付文書がある場合、最初の1件が返されます
- 各セクションは複数の表記パターン（例: "効能又は効果" / "効能・効果"）に対応しています
- **メタデータ自動除外**: レスポンスからは販売名、製造販売元、一般名、セクション名などのメタデータが自動的に除外され、実コンテンツのみが返されます

**使用例:**
```bash
curl -X POST http://localhost:8000/api/package-insert/core-sections \
  -H "Content-Type: application/json" \
  -d '{
    "yj_code": "62504A4A1023"
  }'
```

---

## 共通仕様

### エラーレスポンス

全てのAPIで共通のエラーレスポンス形式：

```json
{
  "detail": "エラーメッセージ"
}
```

**主なエラーコード:**
- `400 Bad Request`: Qdrant APIエラーまたは無効なリクエスト
- `500 Internal Server Error`: サーバー内部エラー

### 制限事項

- 最大取得件数: 10,000件
- タイムアウト: 60秒
- フィルター条件は完全一致検索のみ対応

### 環境変数

以下の環境変数が必要です：

- `QDRANT_URL`: Qdrantサーバーのアドレス
- `QDRANT_API_KEY`: Qdrant APIキー
- `COLLECTION_CUBEC_NOTE`: CUBEC_NOTEコレクション名
- `COLLECTION_PACKAGE_INSERT`: PACKAGE_INSERTコレクション名
- `DRUG_API_BASE_URL`: 薬剤URL取得用APIのベースURL（PACKAGE_INSERT用）

### CORS設定

`CORS_ORIGINS`環境変数で許可するオリジンを指定できます（デフォルト: `*`）。
カンマ区切りで複数のオリジンを指定可能です。

例: `CORS_ORIGINS=http://localhost:3000,https://example.com`