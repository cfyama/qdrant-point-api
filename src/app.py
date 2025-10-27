from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, MatchText
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import logging
import httpx
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qdrant Point Retrieval API")

# CORS設定
cors_origins_str = os.environ.get("CORS_ORIGINS", "*")
cors_origins = cors_origins_str.split(",") if cors_origins_str != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # レスポンスヘッダーを公開
)

def get_points_from_ids(point_ids, collection_name, with_payload=True, with_vectors=False):
    try:
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),    
            timeout=60,
        )
        
        if not point_ids:
            raise ValueError("point_ids cannot be empty")
        
        points = client.retrieve(
            collection_name=collection_name,
            ids=point_ids,
            with_payload=with_payload,
            with_vectors=with_vectors
        )
        
        result = []
        for point in points:
            point_dict = {
                "id": point.id,
                "payload": point.payload if point.payload else {},
            }
            if with_vectors and point.vector:
                point_dict["vector"] = point.vector
            result.append(point_dict)
        
        return result
    
    except ResponseHandlingException as e:
        logger.error(f"Qdrant API error: {e}")
        raise HTTPException(status_code=400, detail=f"Qdrant API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_points_from_ids: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class CollectionName(str, Enum):
    CUBEC_NOTE = "CUBEC_NOTE"
    PACKAGE_INSERT = "PACKAGE_INSERT"
    GUIDELINE = "GUIDELINE"
    
    def get_actual_name(self):
        mapping = {
            "CUBEC_NOTE": os.getenv("COLLECTION_CUBEC_NOTE", "default_cubec_note"),
            "PACKAGE_INSERT": os.getenv("COLLECTION_PACKAGE_INSERT", "default_package_insert"),
            "GUIDELINE": os.getenv("COLLECTION_GUIDELINE", "default_gl")
        }
        return mapping.get(self.value)

class PointRequest(BaseModel):
    point_ids: List[int]
    collection_name: CollectionName = CollectionName.CUBEC_NOTE
    with_payload: Optional[bool] = True
    with_vectors: Optional[bool] = False

@app.options("/api")
async def options_api():
    return {"message": "OK"}

@app.get("/collections")
async def get_available_collections():
    """利用可能なコレクション一覧を取得"""
    return {
        "collections": [
            {"key": "CUBEC_NOTE", "name": CollectionName.CUBEC_NOTE.get_actual_name()},
            {"key": "PACKAGE_INSERT", "name": CollectionName.PACKAGE_INSERT.get_actual_name()},
            {"key": "GUIDELINE", "name": CollectionName.GUIDELINE.get_actual_name()}
        ]
    }

async def fetch_drug_url(package_insert_no: str) -> Optional[str]:
    """package_insert_noからURLを取得する（旧バージョン・互換性のため残す）"""
    try:
        # 末尾の_XX部分を除去してdrug_codeを作成
        parts = package_insert_no.rsplit('_', 1)
        if len(parts) == 2:
            drug_code = parts[0]
        else:
            drug_code = package_insert_no

        # 環境変数からAPIベースURLを取得
        api_base_url = os.getenv("DRUG_API_BASE_URL", "https://oma7a27ol6.execute-api.ap-northeast-1.amazonaws.com/Prod/")
        url = f"{api_base_url}api/v1/code-to-url/{drug_code}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("url")
            else:
                logger.warning(f"Failed to fetch URL for drug_code {drug_code}: status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error fetching drug URL for {package_insert_no}: {e}")
        return None

async def fetch_drug_url_by_yj_code(yj_code: str) -> Optional[str]:
    """YJコード（医薬品コード）からURLを取得する

    Args:
        yj_code: YJコード（カンマ区切りの場合は最初のコードを使用）

    Returns:
        添付文書のHTML URL、取得できない場合はNone
    """
    try:
        # カンマ区切りの場合は最初のコードを使用
        first_yj_code = yj_code.split(',')[0].strip() if ',' in yj_code else yj_code.strip()

        if not first_yj_code:
            logger.warning(f"Invalid yj_code: {yj_code}")
            return None

        # 環境変数からAPIベースURLを取得
        api_base_url = os.getenv("DRUG_API_BASE_URL", "https://oma7a27ol6.execute-api.ap-northeast-1.amazonaws.com/Prod/")
        url = f"{api_base_url}api/v1/documents/by-code/{first_yj_code}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # HTML形式のURLを優先的に取得
                document_links = data.get("document_links", {})
                html_links = document_links.get("html", [])

                if html_links and len(html_links) > 0:
                    return html_links[0].get("url")

                # HTMLがない場合はPDFのURLを取得
                pdf_links = document_links.get("pdf", [])
                if pdf_links and len(pdf_links) > 0:
                    return pdf_links[0].get("url")

                logger.warning(f"No document links found for yj_code {first_yj_code}")
                return None
            else:
                logger.warning(f"Failed to fetch URL for yj_code {first_yj_code}: status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error fetching drug URL for yj_code {yj_code}: {e}")
        return None

def transform_cubec_note_response(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """CUBEC_NOTEのレスポンスを元の形式に変換する"""
    transformed = []
    for point in points:
        payload = point.get("payload", {})
        metadata = payload.get("metadata", {})

        # metadataをフラット化し、フィールド名を元の名前にマッピング
        new_payload = {
            "context": payload.get("page_content", ""),
        }

        # GL関連のフィールドを一時保存
        gl_names = None
        gl_links = None
        gl_publishers = None
        gl_departments = None
        gl_free_or_paid = None

        # その他のmetadataフィールドをコピー
        for key, value in metadata.items():
            if key == "main_category":
                new_payload["title"] = value
            elif key == "disease_name":
                new_payload["disease"] = value
            elif key == "date":
                # dateフィールドをpublicationDateにそのままコピー
                new_payload["publicationDate"] = value
            elif key == "source":
                # "医学ノート" を "Cubec医学ノート" に変更
                if value == "医学ノート":
                    new_payload["source"] = "Cubec医学ノート"
                else:
                    new_payload["source"] = value
            elif key == "gl_names":
                gl_names = value
            elif key == "gl_links":
                gl_links = value
            elif key == "gl_publishers":
                gl_publishers = value
            elif key == "gl_departments":
                gl_departments = value
            elif key == "gl_free_or_paid":
                gl_free_or_paid = value
            elif key == "gl_count":
                # gl_countは配列から計算できるため除外
                pass
            else:
                # その他のフィールドはそのままコピー
                new_payload[key] = value

        # GL情報を配列のオブジェクトにまとめる
        if gl_names and isinstance(gl_names, list):
            gl_array = []
            for i in range(len(gl_names)):
                gl_item = {
                    "name": gl_names[i] if i < len(gl_names) else None,
                    "link": gl_links[i] if gl_links and i < len(gl_links) else None,
                    "publisher": gl_publishers[i] if gl_publishers and i < len(gl_publishers) else None,
                    "department": gl_departments[i] if gl_departments and i < len(gl_departments) else None,
                    "access": gl_free_or_paid[i] if gl_free_or_paid and i < len(gl_free_or_paid) else None,
                }
                gl_array.append(gl_item)
            new_payload["gl"] = gl_array

        transformed_point = {
            "id": point.get("id"),
            "payload": new_payload
        }

        # vectorがあれば追加
        if "vector" in point:
            transformed_point["vector"] = point["vector"]

        transformed.append(transformed_point)

    return transformed

def transform_gl_response(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """GLのレスポンスを整形する"""
    transformed = []
    for point in points:
        payload = point.get("payload", {})
        metadata = payload.get("metadata", {})

        # metadataをフラット化
        new_payload = {
            "context": payload.get("page_content", ""),
        }

        # メタデータフィールドをコピー
        for key, value in metadata.items():
            if key == "gl_name":
                new_payload["guideline_name"] = value
            elif key == "heading_1":
                new_payload["heading1"] = value
            elif key == "heading_2":
                new_payload["heading2"] = value
            elif key == "heading_3":
                new_payload["heading3"] = value
            elif key == "source":
                # "GL" を "GUIDELINE" に変更
                if value == "GL":
                    new_payload["source"] = "GUIDELINE"
                else:
                    new_payload["source"] = value
            else:
                # その他のフィールドはそのままコピー
                new_payload[key] = value

        # 存在しないフィールドに対して一時的に空データを追加
        if "publication_date" not in new_payload:
            new_payload["publication_date"] = ""
        if "author" not in new_payload:
            new_payload["author"] = ""
        if "link" not in new_payload:
            new_payload["link"] = ""
        if "bibliographic_information" not in new_payload:
            new_payload["bibliographic_information"] = ""

        transformed_point = {
            "id": point.get("id"),
            "payload": new_payload
        }

        # vectorがあれば追加
        if "vector" in point:
            transformed_point["vector"] = point["vector"]

        transformed.append(transformed_point)

    return transformed

def transform_package_insert_response(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """PACKAGE_INSERTのレスポンスを旧API互換形式に変換する"""
    transformed = []
    for point in points:
        payload = point.get("payload", {})
        metadata = payload.get("metadata", {})

        # metadataをフラット化して旧API形式にマッピング
        new_payload = {
            "context": payload.get("page_content", ""),
            "section_title": metadata.get("section_title", ""),
            "generic_name": metadata.get("generic_name", ""),
            "brand_name": metadata.get("product_name", ""),
            "company_name": metadata.get("manufacturer", ""),
            "revision_date": metadata.get("revision_date", ""),
            "source": metadata.get("source", ""),
        }

        # URLからpackage_insert_noを抽出
        url = payload.get("url")
        if url:
            # URLの最後の部分（パス）を取得
            # 例: https://www.pmda.go.jp/PmdaSearch/iyakuDetail/166272_6250014F1036_2_13
            # → 166272_6250014F1036_2_13 → 6250014F1036_2_13
            try:
                path_parts = url.rstrip('/').split('/')
                if path_parts:
                    last_part = path_parts[-1]
                    # 最初のアンダースコアの後の部分を取得
                    if '_' in last_part:
                        package_insert_no = '_'.join(last_part.split('_')[1:])
                        new_payload["package_insert_no"] = package_insert_no
                    else:
                        new_payload["package_insert_no"] = None
                else:
                    new_payload["package_insert_no"] = None
            except Exception as e:
                logger.warning(f"Failed to extract package_insert_no from URL {url}: {e}")
                new_payload["package_insert_no"] = None
        else:
            new_payload["package_insert_no"] = None

        # URLを追加
        new_payload["url"] = url

        # 旧APIには存在したが新コレクションにはないフィールド（互換性のためnullで設定）
        new_payload["product_number"] = None
        new_payload["sccj_no"] = None
        new_payload["source_row_index"] = None
        new_payload["source_file"] = None
        new_payload["source_file_path"] = None
        new_payload["therapeutic_class"] = None
        new_payload["company_id"] = None
        new_payload["import_timestamp"] = None

        # 新コレクションにしか存在しないフィールドを追加
        new_payload["yj_code"] = metadata.get("yj_code", "")
        new_payload["document_id"] = metadata.get("document_id", "")
        new_payload["specification"] = metadata.get("specification", "")
        new_payload["classification_number"] = metadata.get("classification_number", None)
        new_payload["section_number"] = metadata.get("section_number", None)
        new_payload["branch_number"] = metadata.get("branch_number", None)
        new_payload["common_name"] = metadata.get("common_name", "")

        transformed_point = {
            "id": point.get("id"),
            "payload": new_payload
        }

        # vectorがあれば追加
        if "vector" in point:
            transformed_point["vector"] = point["vector"]

        transformed.append(transformed_point)

    return transformed

def search_points_by_filters(collection_name: str, filters: List[Dict[str, Any]], with_payload: bool = True, with_vectors: bool = False):
    """フィルター条件に基づいてポイントを検索する"""
    try:
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60,
        )

        # フィルター条件を構築
        conditions = []
        for filter_item in filters:
            field = filter_item.get("field")
            value = filter_item.get("value")
            field_type = filter_item.get("type", "keyword")  # デフォルトはkeyword

            if field and value is not None:
                if field_type == "text":
                    # text型インデックスの場合
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchText(text=value)
                        )
                    )
                else:
                    # keyword型インデックスの場合
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(value=value)
                        )
                    )

        if not conditions:
            raise ValueError("No valid filter conditions provided")

        # 検索を実行
        search_filter = Filter(must=conditions)

        points = client.scroll(
            collection_name=collection_name,
            scroll_filter=search_filter,
            with_payload=with_payload,
            with_vectors=with_vectors,
            limit=10000  # 最大10000件まで取得
        )[0]  # scroll returns tuple (points, next_page_offset)

        result = []
        for point in points:
            point_dict = {
                "id": point.id,
                "payload": point.payload if point.payload else {},
            }
            if with_vectors and point.vector:
                point_dict["vector"] = point.vector
            result.append(point_dict)

        return result

    except ResponseHandlingException as e:
        logger.error(f"Qdrant API error: {e}")
        raise HTTPException(status_code=400, detail=f"Qdrant API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in search_points_by_filters: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class CubecNoteChapterRequest(BaseModel):
    title: str
    disease: str
    with_payload: Optional[bool] = True
    with_vectors: Optional[bool] = False

class CubecNotePageRequest(BaseModel):
    disease: str
    with_payload: Optional[bool] = True
    with_vectors: Optional[bool] = False

class PackageInsertChapterRequest(BaseModel):
    yj_code: str
    section_title: str
    with_payload: Optional[bool] = True
    with_vectors: Optional[bool] = False

@app.post("/api/cubec-note/chapter")
async def get_cubec_note_chapter(request: CubecNoteChapterRequest):
    """CUBEC_NOTEの章取得API - titleとdiseaseで検索"""
    filters = [
        {"field": "metadata.main_category", "value": request.title, "type": "text"},
        {"field": "metadata.disease_name", "value": request.disease, "type": "text"}
    ]

    points = search_points_by_filters(
        collection_name=CollectionName.CUBEC_NOTE.get_actual_name(),
        filters=filters,
        with_payload=request.with_payload,
        with_vectors=request.with_vectors
    )

    # レスポンスを元の形式に変換
    transformed_points = transform_cubec_note_response(points)

    return {"success": True, "data": transformed_points, "count": len(transformed_points)}

@app.post("/api/cubec-note/page")
async def get_cubec_note_page(request: CubecNotePageRequest):
    """CUBEC_NOTEのページ取得API - diseaseで検索"""
    filters = [
        {"field": "metadata.disease_name", "value": request.disease, "type": "text"}
    ]

    points = search_points_by_filters(
        collection_name=CollectionName.CUBEC_NOTE.get_actual_name(),
        filters=filters,
        with_payload=request.with_payload,
        with_vectors=request.with_vectors
    )

    # レスポンスを元の形式に変換
    transformed_points = transform_cubec_note_response(points)

    return {"success": True, "data": transformed_points, "count": len(transformed_points)}

@app.post("/api/package-insert/chapter")
async def get_package_insert_chapter(request: PackageInsertChapterRequest):
    """PACKAGE_INSERTの章取得API - yj_codeとsection_titleで検索"""
    filters = [
        {"field": "metadata.yj_code", "value": request.yj_code, "type": "text"},
        {"field": "metadata.section_title", "value": request.section_title, "type": "keyword"}
    ]

    points = search_points_by_filters(
        collection_name=CollectionName.PACKAGE_INSERT.get_actual_name(),
        filters=filters,
        with_payload=request.with_payload,
        with_vectors=request.with_vectors
    )

    # URLを取得して追加
    if points:
        # 各ポイントのyj_codeを収集
        yj_codes = []
        for point in points:
            metadata = point.get("payload", {}).get("metadata", {})
            if metadata and "yj_code" in metadata:
                yj_codes.append(metadata["yj_code"])
            else:
                yj_codes.append(None)

        # ユニークなyj_codeだけを抽出してAPIを呼ぶ
        unique_yj_codes = list(set(filter(None, yj_codes)))
        url_cache = {}

        if unique_yj_codes:
            # 並行してユニークなyj_codeに対してのみURL取得を実行
            tasks = [fetch_drug_url_by_yj_code(yj_code) for yj_code in unique_yj_codes]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 結果をキャッシュに格納
            for yj_code, result in zip(unique_yj_codes, results):
                if not isinstance(result, Exception) and result:
                    url_cache[yj_code] = result

        # キャッシュされた結果を各ポイントに追加
        for point, yj_code in zip(points, yj_codes):
            if yj_code and yj_code in url_cache:
                point["payload"]["url"] = url_cache[yj_code]

    # レスポンスを旧API互換形式に変換
    transformed_points = transform_package_insert_response(points)

    return {"success": True, "data": transformed_points, "count": len(transformed_points)}

@app.post("/api")
async def get_points(request: PointRequest):
    if not request.point_ids:
        raise HTTPException(status_code=400, detail="point_ids cannot be empty")

    points = get_points_from_ids(
        point_ids=request.point_ids,
        collection_name=request.collection_name.get_actual_name(),
        with_payload=request.with_payload,
        with_vectors=request.with_vectors
    )

    # CUBEC_NOTEコレクションの場合、レスポンスを変換
    if request.collection_name == CollectionName.CUBEC_NOTE:
        points = transform_cubec_note_response(points)

    # GLコレクションの場合、レスポンスを変換
    if request.collection_name == CollectionName.GUIDELINE:
        points = transform_gl_response(points)

    # PACKAGE_INSERTコレクションの場合、URLを取得して追加し、レスポンスを変換
    if request.collection_name == CollectionName.PACKAGE_INSERT:
        # 各ポイントのyj_codeを収集
        yj_codes = []
        for point in points:
            metadata = point.get("payload", {}).get("metadata", {})
            if metadata and "yj_code" in metadata:
                yj_codes.append(metadata["yj_code"])
            else:
                yj_codes.append(None)

        # ユニークなyj_codeだけを抽出してAPIを呼ぶ
        unique_yj_codes = list(set(filter(None, yj_codes)))
        url_cache = {}

        if unique_yj_codes:
            # 並行してユニークなyj_codeに対してのみURL取得を実行
            tasks = [fetch_drug_url_by_yj_code(yj_code) for yj_code in unique_yj_codes]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 結果をキャッシュに格納
            for yj_code, result in zip(unique_yj_codes, results):
                if not isinstance(result, Exception) and result:
                    url_cache[yj_code] = result

        # キャッシュされた結果を各ポイントに追加
        for point, yj_code in zip(points, yj_codes):
            if yj_code and yj_code in url_cache:
                point["payload"]["url"] = url_cache[yj_code]

        # レスポンスを旧API互換形式に変換
        points = transform_package_insert_response(points)

    return {"success": True, "data": points, "count": len(points)}

@app.middleware("http")
async def debug_requests(request: Request, call_next):
    logger.info(f"Method: {request.method}, URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


