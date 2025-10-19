#!/usr/bin/env python3
"""
新規追加した3つのAPIの動作テストスクリプト
"""

import requests
import json
import time

# APIのベースURL（必要に応じて変更してください）
BASE_URL = "http://localhost:7860"

# テスト結果を表示する関数
def print_test_result(test_name: str, response: requests.Response, expected_fields: list = None):
    print(f"\n{'='*60}")
    print(f"テスト: {test_name}")
    print(f"{'='*60}")
    print(f"ステータスコード: {response.status_code}")

    try:
        data = response.json()
        print(f"レスポンス:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if response.status_code == 200:
            if "success" in data and data["success"]:
                print(f"✅ 成功: {data.get('count', 0)}件のデータを取得")

                # 期待されるフィールドの確認
                if expected_fields and data.get("data") and len(data["data"]) > 0:
                    first_item = data["data"][0]
                    payload = first_item.get("payload", {})
                    missing_fields = [field for field in expected_fields if field not in payload]
                    if missing_fields:
                        print(f"⚠️  警告: 以下のフィールドがpayloadに見つかりません: {missing_fields}")
                    else:
                        print(f"✅ 全ての期待されるフィールドが存在します")
            else:
                print(f"❌ エラー: {data}")
        else:
            print(f"❌ エラー: HTTPステータス {response.status_code}")

    except json.JSONDecodeError:
        print(f"❌ エラー: JSONのパースに失敗")
        print(f"レスポンステキスト: {response.text}")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

# 1. CUBEC_NOTE章取得APIのテスト
def test_cubec_note_chapter():
    endpoint = f"{BASE_URL}/api/cubec-note/chapter"

    # テストケース1: 正常なリクエスト
    test_data = {
        "title": "診断方針(疾患の除外)",  # 実際のデータに合わせて変更してください
        "disease": "感染性心内膜炎",      # 実際のデータに合わせて変更してください
        "with_payload": True,
        "with_vectors": False
    }

    print("\n" + "="*70)
    print("1. CUBEC_NOTE章取得APIテスト")
    print("="*70)

    try:
        response = requests.post(endpoint, json=test_data, timeout=30)
        print_test_result(
            "CUBEC_NOTE章取得（正常ケース）",
            response,
            expected_fields=["title", "disease"]
        )
    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー")
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: APIサーバーが起動していることを確認してください")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

    # テストケース2: 存在しないデータ
    test_data_not_found = {
        "title": "存在しないタイトル_TEST_12345",
        "disease": "存在しない疾患_TEST_12345",
        "with_payload": True
    }

    try:
        response = requests.post(endpoint, json=test_data_not_found, timeout=30)
        print_test_result(
            "CUBEC_NOTE章取得（データなし）",
            response
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("count", 0) == 0:
                print("✅ 期待通り: データが0件")
    except Exception as e:
        print(f"❌ エラー: {e}")

# 2. CUBEC_NOTEページ取得APIのテスト
def test_cubec_note_page():
    endpoint = f"{BASE_URL}/api/cubec-note/page"

    # テストケース1: 正常なリクエスト
    test_data = {
        "disease": "感染性心内膜炎",  # 実際のデータに合わせて変更してください
        "with_payload": True,
        "with_vectors": False
    }

    print("\n" + "="*70)
    print("2. CUBEC_NOTEページ取得APIテスト")
    print("="*70)

    try:
        response = requests.post(endpoint, json=test_data, timeout=30)
        print_test_result(
            "CUBEC_NOTEページ取得（正常ケース）",
            response,
            expected_fields=["disease"]
        )
    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー")
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: APIサーバーが起動していることを確認してください")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

    # # テストケース2: vectorsも取得
    # test_data_with_vectors = {
    #     "disease": "感染性心内膜炎",  # 実際のデータに合わせて変更してください
    #     "with_payload": True,
    #     "with_vectors": True
    # }

    # try:
    #     response = requests.post(endpoint, json=test_data_with_vectors, timeout=30)
    #     print_test_result(
    #         "CUBEC_NOTEページ取得（vectors含む）",
    #         response
    #     )
    #     if response.status_code == 200:
    #         data = response.json()
    #         if data.get("data") and len(data["data"]) > 0:
    #             if "vector" in data["data"][0]:
    #                 print("✅ vectorsが含まれています")
    #             else:
    #                 print("⚠️  vectorsが含まれていません")
    # except Exception as e:
    #     print(f"❌ エラー: {e}")

# 3. PACKAGE_INSERT章取得APIのテスト
def test_package_insert_chapter():
    endpoint = f"{BASE_URL}/api/package-insert/chapter"

    # テストケース1: 正常なリクエスト
    test_data = {
        "package_insert_no": "6250014F1036_2_13",  # 実際のデータに合わせて変更してください
        "section_title": "禁忌",              # 実際のデータに合わせて変更してください
        "with_payload": True,
        "with_vectors": False
    }

    print("\n" + "="*70)
    print("3. PACKAGE_INSERT章取得APIテスト")
    print("="*70)

    try:
        response = requests.post(endpoint, json=test_data, timeout=30)
        print_test_result(
            "PACKAGE_INSERT章取得（正常ケース）",
            response,
            expected_fields=["package_insert_no", "section_title", "url"]
        )

        # URLが自動取得されているか確認
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                first_item = data["data"][0]
                if "url" in first_item.get("payload", {}):
                    print(f"✅ URLが自動取得されています: {first_item['payload']['url'][:50]}...")
                else:
                    print("⚠️  URLが含まれていません（データによっては正常な場合もあります）")

    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー")
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: APIサーバーが起動していることを確認してください")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

    # テストケース2: 存在しないデータ
    test_data_not_found = {
        "package_insert_no": "9999999X9999_9_99",
        "section_title": "存在しないセクション",
        "with_payload": True
    }

    try:
        response = requests.post(endpoint, json=test_data_not_found, timeout=30)
        print_test_result(
            "PACKAGE_INSERT章取得（データなし）",
            response
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("count", 0) == 0:
                print("✅ 期待通り: データが0件")
    except Exception as e:
        print(f"❌ エラー: {e}")

# 4. エラーケースのテスト
def test_error_cases():
    print("\n" + "="*70)
    print("4. エラーケーステスト")
    print("="*70)

    # 必須パラメータ不足のテスト（CUBEC_NOTEページ）
    endpoint = f"{BASE_URL}/api/cubec-note/page"
    test_data_missing = {
        # diseaseが不足
    }

    try:
        response = requests.post(endpoint, json=test_data_missing, timeout=10)
        print_test_result(
            "必須パラメータ不足（disease欠落）",
            response
        )
        if response.status_code == 422:
            print("✅ 期待通り: バリデーションエラー")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 空文字列のテスト（CUBEC_NOTE章）
    endpoint_chapter = f"{BASE_URL}/api/cubec-note/chapter"
    test_data_empty = {
        "title": "",
        "disease": ""
    }

    try:
        response = requests.post(endpoint_chapter, json=test_data_empty, timeout=10)
        print_test_result(
            "空文字列パラメータ",
            response
        )
    except Exception as e:
        print(f"❌ エラー: {e}")

# メイン実行
def main():
    print("="*70)
    print("新規API動作テスト開始")
    print(f"APIベースURL: {BASE_URL}")
    print("="*70)

    print("\n⚠️  注意: テストデータは実際のデータベースの内容に合わせて調整してください")
    print("⚠️  APIサーバーが起動していることを確認してください")

    input("\nEnterキーを押してテストを開始...")

    # 各テストを実行
    test_cubec_note_chapter()
    time.sleep(1)  # APIへの負荷を避けるため少し待機

    test_cubec_note_page()
    time.sleep(1)

    test_package_insert_chapter()
    time.sleep(1)

    test_error_cases()

    print("\n" + "="*70)
    print("テスト完了")
    print("="*70)
    print("\n📝 注記:")
    print("- 実際のデータに合わせてテストデータを調整してください")
    print("- package_insert_noやtitle、diseaseは実在するものを使用してください")
    print("- エラーが発生した場合は、APIサーバーのログも確認してください")

if __name__ == "__main__":
    main()