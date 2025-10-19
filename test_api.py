import httpx
import asyncio

API_URL = "http://localhost:7860/api"

async def test_package_insert():
    """PACKAGE_INSERTコレクションのテスト"""
    request_data = {
        "point_ids": [14460897374401, 49278421921507, 59304891126007],  # テスト用のポイントID
        "collection_name": "PACKAGE_INSERT",
        "with_payload": True,
        "with_vectors": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=request_data, timeout=30.0)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("Response:", data)

            # URLが追加されているか確認
            if data.get("data") and len(data["data"]) > 0:
                for point in data["data"]:
                    if "payload" in point:
                        print(f"Point ID {point['id']} payload:")
                        print(f"  package_insert_no: {point['payload'].get('package_insert_no')}")
                        print(f"  url: {point['payload'].get('url')}")
        else:
            print("Error:", response.text)

if __name__ == "__main__":
    asyncio.run(test_package_insert())