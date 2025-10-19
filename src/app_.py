from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def get_actual_name(self):
        mapping = {
            "CUBEC_NOTE": os.getenv("COLLECTION_CUBEC_NOTE", "default_cubec_note"),
            "PACKAGE_INSERT": os.getenv("COLLECTION_PACKAGE_INSERT", "default_package_insert")
        }
        return mapping.get(self.value)

class PointRequest(BaseModel):
    point_ids: List[int]
    collection_name: CollectionName = CollectionName.CUBEC_NOTE
    with_payload: Optional[bool] = True
    with_vectors: Optional[bool] = False

app = FastAPI(title="Qdrant Point Retrieval API")

# 軽量CORS設定 - 405エラー対策の最小構成
cors_origins_str = os.environ.get("CORS_ORIGINS", "*")
cors_origins = cors_origins_str.split(",") if cors_origins_str != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # OPTIONSを含む全てのメソッドを許可
    allow_headers=["*"],
)

@app.get("/collections")
async def get_available_collections():
    """利用可能なコレクション一覧を取得"""
    return {
        "collections": [
            {"key": "CUBEC_NOTE", "name": CollectionName.CUBEC_NOTE.get_actual_name()},
            {"key": "PACKAGE_INSERT", "name": CollectionName.PACKAGE_INSERT.get_actual_name()}
        ]
    }

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
    return {"success": True, "data": points, "count": len(points)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
