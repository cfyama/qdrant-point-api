#!/usr/bin/env python3
"""
医学ノートAPI - reviewerフィールド追加テスト
"""

import requests
import json

BASE_URL = "http://localhost:7860"

def test_reviewer_field():
    """全ての医学ノートAPIエンドポイントでreviewerフィールドをテスト"""
    print("=" * 80)
    print("医学ノートAPI - reviewer フィールド追加テスト")
    print("=" * 80)

    expected_reviewer = {
        "name": "XX 太郎",
        "affiliated_hospital": "XX病院",
        "board_certified": ["XX専門医"]
    }

    # テスト1: /api/cubec-note/page
    print("\n[テスト1] /api/cubec-note/page")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/cubec-note/page",
            json={"disease": "WPW症候群", "with_payload": True},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                payload = data['data'][0]['payload']

                if 'reviewer' in payload:
                    reviewer = payload['reviewer']
                    if reviewer == expected_reviewer:
                        print("✅ reviewer フィールドが正しく追加されています")
                        print(f"   内容: {json.dumps(reviewer, ensure_ascii=False)}")
                    else:
                        print("⚠️  reviewer フィールドは存在しますが、内容が期待値と異なります")
                        print(f"   期待値: {expected_reviewer}")
                        print(f"   実際値: {reviewer}")
                else:
                    print("❌ reviewer フィールドが見つかりません")
            else:
                print("❌ データが取得できませんでした")
        else:
            print(f"❌ エラー: ステータスコード {response.status_code}")
    except Exception as e:
        print(f"❌ 例外発生: {e}")

    # テスト2: /api/cubec-note/chapter
    print("\n[テスト2] /api/cubec-note/chapter")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/cubec-note/chapter",
            json={
                "title": "WPW症候群 -- 概要・推奨",
                "disease": "WPW症候群",
                "with_payload": True
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                payload = data['data'][0]['payload']

                if 'reviewer' in payload:
                    reviewer = payload['reviewer']
                    if reviewer == expected_reviewer:
                        print("✅ reviewer フィールドが正しく追加されています")
                        print(f"   内容: {json.dumps(reviewer, ensure_ascii=False)}")
                    else:
                        print("⚠️  reviewer フィールドは存在しますが、内容が期待値と異なります")
                else:
                    print("❌ reviewer フィールドが見つかりません")
            else:
                print("❌ データが取得できませんでした")
        else:
            print(f"❌ エラー: ステータスコード {response.status_code}")
    except Exception as e:
        print(f"❌ 例外発生: {e}")

    # テスト3: /api (point_ids指定)
    print("\n[テスト3] /api (point_ids指定、CUBEC_NOTE)")
    print("-" * 80)

    # まず実際のIDを取得
    try:
        response = requests.post(
            f"{BASE_URL}/api/cubec-note/page",
            json={"disease": "WPW症候群"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                point_id = data['data'][0]['id']

                # point_idsでリクエスト
                response = requests.post(
                    f"{BASE_URL}/api",
                    json={
                        "point_ids": [point_id],
                        "collection_name": "CUBEC_NOTE",
                        "with_payload": True
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        payload = data['data'][0]['payload']

                        if 'reviewer' in payload:
                            reviewer = payload['reviewer']
                            if reviewer == expected_reviewer:
                                print("✅ reviewer フィールドが正しく追加されています")
                                print(f"   内容: {json.dumps(reviewer, ensure_ascii=False)}")
                            else:
                                print("⚠️  reviewer フィールドは存在しますが、内容が期待値と異なります")
                        else:
                            print("❌ reviewer フィールドが見つかりません")
                    else:
                        print("❌ データが取得できませんでした")
                else:
                    print(f"❌ エラー: ステータスコード {response.status_code}")
            else:
                print("❌ IDの取得に失敗しました")
        else:
            print(f"❌ IDの取得に失敗しました: ステータスコード {response.status_code}")
    except Exception as e:
        print(f"❌ 例外発生: {e}")

    print("\n" + "=" * 80)
    print("テスト完了")
    print("=" * 80)
    print()
    print("まとめ:")
    print("  - /api/cubec-note/page: reviewerフィールド追加")
    print("  - /api/cubec-note/chapter: reviewerフィールド追加")
    print("  - /api (CUBEC_NOTE): reviewerフィールド追加")
    print()
    print("現在は仮データ (XX 太郎 / XX病院 / XX専門医) が返されています。")
    print("実データが準備でき次第、データソースから取得するように変更できます。")

if __name__ == "__main__":
    test_reviewer_field()
