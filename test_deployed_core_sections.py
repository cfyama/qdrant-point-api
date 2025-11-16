#!/usr/bin/env python3
"""
デプロイ環境でのPACKAGE_INSERT core-sections API テストスクリプト
"""

import requests
import json

BASE_URL = "https://3j2q4wuiw4.ap-northeast-1.awsapprunner.com"

def test_deployed_core_sections_api():
    """デプロイ環境でのcore-sections APIテスト"""
    print("=" * 80)
    print("デプロイ環境 - PACKAGE_INSERT core-sections API 動作テスト")
    print(f"テスト対象URL: {BASE_URL}")
    print("=" * 80)

    # テストケース1: イコサペント酸エチル
    print("\n[テスト1] YJコード: 3399004M1425 (イコサペント酸エチル)")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/package-insert/core-sections",
            json={"yj_code": "3399004M1425"},
            timeout=30
        )

        print(f"ステータスコード: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"success: {data['success']}")
            print(f"yj_code: {data['data']['yj_code']}")
            print()

            payload = data['data']['payload']

            # 効能又は効果
            print("【効能又は効果】")
            if payload['indications']:
                lines = payload['indications'].split('\n')
                preview = '\n'.join(lines[:5])
                print(f"取得: ✅ ({len(payload['indications'])}文字)")
                print(f"プレビュー:\n{preview}")
                if len(lines) > 5:
                    print(f"... (残り{len(lines)-5}行)")
            else:
                print("取得: ❌ (データなし)")

            print()

            # 用法及び用量
            print("【用法及び用量】")
            if payload['dosage_and_administration']:
                lines = payload['dosage_and_administration'].split('\n')
                preview = '\n'.join(lines[:5])
                print(f"取得: ✅ ({len(payload['dosage_and_administration'])}文字)")
                print(f"プレビュー:\n{preview}")
                if len(lines) > 5:
                    print(f"... (残り{len(lines)-5}行)")
            else:
                print("取得: ❌ (データなし)")

            print()

            # 禁忌
            print("【禁忌】")
            if payload['contraindications']:
                lines = payload['contraindications'].split('\n')
                preview = '\n'.join(lines[:5])
                print(f"取得: ✅ ({len(payload['contraindications'])}文字)")
                print(f"プレビュー:\n{preview}")
                if len(lines) > 5:
                    print(f"... (残り{len(lines)-5}行)")
            else:
                print("取得: ❌ (データなし)")

            print()

            # 副作用
            print("【副作用】")
            if payload['adverse_reactions']:
                lines = payload['adverse_reactions'].split('\n')
                preview = '\n'.join(lines[:5])
                print(f"取得: ✅ ({len(payload['adverse_reactions'])}文字)")
                print(f"プレビュー:\n{preview}")
                if len(lines) > 5:
                    print(f"... (残り{len(lines)-5}行)")
            else:
                print("取得: ❌ (データなし)")

            print()
            print("結果: ✅ 全セクション取得成功")

        else:
            print(f"結果: ❌ エラー")
            print(f"レスポンス: {response.text}")

    except Exception as e:
        print(f"結果: ❌ 例外発生")
        print(f"エラー: {e}")

    # テストケース2: ハルシオン
    print("\n" + "=" * 80)
    print("[テスト2] YJコード: 1124007F1020 (ハルシオン)")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/package-insert/core-sections",
            json={"yj_code": "1124007F1020"},
            timeout=30
        )

        print(f"ステータスコード: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"success: {data['success']}")
            print(f"yj_code: {data['data']['yj_code']}")
            print()

            payload = data['data']['payload']

            print("セクション取得状況:")
            print(f"  - 効能又は効果: {'✅' if payload['indications'] else '❌'} ({len(payload['indications'])}文字)")
            print(f"  - 用法及び用量: {'✅' if payload['dosage_and_administration'] else '❌'} ({len(payload['dosage_and_administration'])}文字)")
            print(f"  - 禁忌: {'✅' if payload['contraindications'] else '❌'} ({len(payload['contraindications'])}文字)")
            print(f"  - 副作用: {'✅' if payload['adverse_reactions'] else '❌'} ({len(payload['adverse_reactions'])}文字)")

            print()
            all_sections = all([
                payload['indications'],
                payload['dosage_and_administration'],
                payload['contraindications'],
                payload['adverse_reactions']
            ])
            print(f"結果: {'✅ 全セクション取得成功' if all_sections else '⚠️  一部セクションが空'}")

        else:
            print(f"結果: ❌ エラー")
            print(f"レスポンス: {response.text}")

    except Exception as e:
        print(f"結果: ❌ 例外発生")
        print(f"エラー: {e}")

    # テストケース3: 存在しないYJコード
    print("\n" + "=" * 80)
    print("[テスト3] YJコード: 9999999999999 (存在しないコード)")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/package-insert/core-sections",
            json={"yj_code": "9999999999999"},
            timeout=30
        )

        print(f"ステータスコード: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"success: {data['success']}")

            payload = data['data']['payload']
            all_empty = all(v == "" for v in payload.values())

            print(f"全セクションが空文字列: {'✅' if all_empty else '❌'}")
            print(f"結果: {'✅ 正常動作（データなし時の処理）' if all_empty else '❌ 異常'}")

        else:
            print(f"結果: ❌ エラー")
            print(f"レスポンス: {response.text}")

    except Exception as e:
        print(f"結果: ❌ 例外発生")
        print(f"エラー: {e}")

    # テストケース4: レスポンス構造検証
    print("\n" + "=" * 80)
    print("[テスト4] レスポンス構造検証")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/api/package-insert/core-sections",
            json={"yj_code": "3399004M1425"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # 構造チェック
            checks = {
                "success フィールド": "success" in data,
                "data フィールド": "data" in data,
                "data.yj_code フィールド": "yj_code" in data.get("data", {}),
                "data.payload フィールド": "payload" in data.get("data", {}),
                "payload.indications フィールド": "indications" in data.get("data", {}).get("payload", {}),
                "payload.dosage_and_administration フィールド": "dosage_and_administration" in data.get("data", {}).get("payload", {}),
                "payload.contraindications フィールド": "contraindications" in data.get("data", {}).get("payload", {}),
                "payload.adverse_reactions フィールド": "adverse_reactions" in data.get("data", {}).get("payload", {})
            }

            all_valid = all(checks.values())

            for check_name, result in checks.items():
                print(f"  {check_name}: {'✅' if result else '❌'}")

            print()
            print(f"結果: {'✅ 全フィールド存在' if all_valid else '❌ 一部フィールド欠落'}")

        else:
            print(f"結果: ❌ エラー")
            print(f"レスポンス: {response.text}")

    except Exception as e:
        print(f"結果: ❌ 例外発生")
        print(f"エラー: {e}")

    print("\n" + "=" * 80)
    print("テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_deployed_core_sections_api()
