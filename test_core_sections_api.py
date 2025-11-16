#!/usr/bin/env python3
"""
PACKAGE_INSERT core-sections API のテストスクリプト
"""

import requests
import json

BASE_URL = "http://localhost:7860"

def test_core_sections_api():
    """core-sections APIのテスト"""
    print("=" * 70)
    print("PACKAGE_INSERT core-sections API テスト")
    print("=" * 70)

    # テストケース1: 全てのセクションが存在するYJコード
    print("\n[テスト1] 全セクション取得 - YJコード: 3399004M1425")
    response = requests.post(
        f"{BASE_URL}/api/package-insert/core-sections",
        json={"yj_code": "3399004M1425"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ ステータス: {response.status_code}")
        print(f"   success: {data['success']}")
        print(f"   yj_code: {data['data']['yj_code']}")

        payload = data['data']['payload']
        print(f"\n   セクション取得状況:")
        print(f"   - 効能又は効果: {'✅ 有' if payload['indications'] else '❌ 無'} ({len(payload['indications'])}文字)")
        print(f"   - 用法及び用量: {'✅ 有' if payload['dosage_and_administration'] else '❌ 無'} ({len(payload['dosage_and_administration'])}文字)")
        print(f"   - 禁忌: {'✅ 有' if payload['contraindications'] else '❌ 無'} ({len(payload['contraindications'])}文字)")
        print(f"   - 副作用: {'✅ 有' if payload['adverse_reactions'] else '❌ 無'} ({len(payload['adverse_reactions'])}文字)")
    else:
        print(f"❌ エラー: ステータスコード {response.status_code}")
        print(f"   {response.text}")

    # テストケース2: 別のYJコード
    print("\n[テスト2] 全セクション取得 - YJコード: 1124007F1020 (ハルシオン)")
    response = requests.post(
        f"{BASE_URL}/api/package-insert/core-sections",
        json={"yj_code": "1124007F1020"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ ステータス: {response.status_code}")
        print(f"   success: {data['success']}")

        payload = data['data']['payload']
        print(f"\n   セクション取得状況:")
        print(f"   - 効能又は効果: {'✅ 有' if payload['indications'] else '❌ 無'} ({len(payload['indications'])}文字)")
        print(f"   - 用法及び用量: {'✅ 有' if payload['dosage_and_administration'] else '❌ 無'} ({len(payload['dosage_and_administration'])}文字)")
        print(f"   - 禁忌: {'✅ 有' if payload['contraindications'] else '❌ 無'} ({len(payload['contraindications'])}文字)")
        print(f"   - 副作用: {'✅ 有' if payload['adverse_reactions'] else '❌ 無'} ({len(payload['adverse_reactions'])}文字)")
    else:
        print(f"❌ エラー: ステータスコード {response.status_code}")

    # テストケース3: 存在しないYJコード
    print("\n[テスト3] 存在しないYJコード - YJコード: 9999999999999")
    response = requests.post(
        f"{BASE_URL}/api/package-insert/core-sections",
        json={"yj_code": "9999999999999"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        payload = data['data']['payload']
        all_empty = all(v == "" for v in payload.values())

        if all_empty:
            print(f"✅ ステータス: {response.status_code}")
            print(f"   全セクションが空文字列: ✅ 正常")
        else:
            print(f"⚠️  一部のセクションにデータが存在")
    else:
        print(f"❌ エラー: ステータスコード {response.status_code}")

    # テストケース4: レスポンス構造の検証
    print("\n[テスト4] レスポンス構造の検証")
    response = requests.post(
        f"{BASE_URL}/api/package-insert/core-sections",
        json={"yj_code": "3399004M1425"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()

        # 必須フィールドのチェック
        has_success = "success" in data
        has_data = "data" in data
        has_yj_code = "yj_code" in data.get("data", {})
        has_payload = "payload" in data.get("data", {})

        payload = data.get("data", {}).get("payload", {})
        has_indications = "indications" in payload
        has_dosage = "dosage_and_administration" in payload
        has_contraindications = "contraindications" in payload
        has_adverse_reactions = "adverse_reactions" in payload

        all_valid = all([
            has_success, has_data, has_yj_code, has_payload,
            has_indications, has_dosage, has_contraindications, has_adverse_reactions
        ])

        if all_valid:
            print("✅ レスポンス構造: 全フィールド存在")
        else:
            print("❌ レスポンス構造: 一部フィールドが欠落")
            print(f"   success: {has_success}")
            print(f"   data: {has_data}")
            print(f"   data.yj_code: {has_yj_code}")
            print(f"   data.payload: {has_payload}")
            print(f"   payload.indications: {has_indications}")
            print(f"   payload.dosage_and_administration: {has_dosage}")
            print(f"   payload.contraindications: {has_contraindications}")
            print(f"   payload.adverse_reactions: {has_adverse_reactions}")
    else:
        print(f"❌ エラー: ステータスコード {response.status_code}")

    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)

if __name__ == "__main__":
    test_core_sections_api()
