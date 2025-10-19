# Qdrant Point API ドキュメント

## ポイント取得API

### get_points API

**エンドポイント:** `POST /api`

**説明:** Qdrantベクトルデータベースから指定されたポイントIDのデータを取得します。PACKAGE_INSERTコレクションの場合は、医薬品のURL情報を自動的に取得して付加します。

**リクエストボディ:**
```json
{
  "point_ids": [1, 2, 3],              // 必須: 取得したいポイントのIDリスト
  "collection_name": "PACKAGE_INSERT", // オプション: コレクション名 (デフォルト: "CUBEC_NOTE")
  "with_payload": true,                // オプション: payloadを含めるか (デフォルト: true)
  "with_vectors": false                // オプション: vectorを含めるか (デフォルト: false)
}
```

**collection_name列挙値:**
- `CUBEC_NOTE`: CUBECノートコレクション
- `PACKAGE_INSERT`: 医薬品添付文書コレクション

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "payload": {
        "package_insert_no": "2149117F1022_1_01",
        "url": "https://example.com/drug/2149117F1022",  // PACKAGE_INSERTの場合自動取得
        // その他のpayloadフィールド
      },
      "vector": [0.1, 0.2, ...]  // with_vectors=trueの場合のみ
    }
  ],
  "count": 3  // 取得件数
}
```

**使用例:**
```bash
# 基本的な使用例
curl -X POST http://localhost:8000/api \
  -H "Content-Type: application/json" \
  -d '{
    "point_ids": [100, 101, 102],
    "collection_name": "CUBEC_NOTE"
  }'

# ベクトルデータを含める例
curl -X POST http://localhost:8000/api \
  -H "Content-Type: application/json" \
  -d '{
    "point_ids": [200],
    "collection_name": "PACKAGE_INSERT",
    "with_payload": true,
    "with_vectors": true
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
- `400 Bad Request`: point_idsが空の場合、またはQdrant APIエラー
- `500 Internal Server Error`: サーバー内部エラー

### 特殊処理

#### PACKAGE_INSERTコレクション向けURL取得処理
`collection_name`が`PACKAGE_INSERT`の場合：

1. 各ポイントの`payload.package_insert_no`を収集
2. ユニークな`package_insert_no`に対して並行でURL取得APIを呼び出し
3. 取得したURLを各ポイントの`payload.url`に追加
4. URL取得に失敗した場合でも、その他のデータは正常に返される

**パフォーマンス最適化:**
- 同じ`package_insert_no`を持つ複数のポイントに対しては、URL取得APIを1回のみ呼び出し
- 非同期処理により並行でURL取得を実行

### 制限事項

- タイムアウト: 60秒
- point_idsは空配列不可

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