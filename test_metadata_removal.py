#!/usr/bin/env python3
"""
メタデータ除外機能のテストスクリプト
"""

import requests
import json

BASE_URL = "http://localhost:7860"

def test_metadata_removal():
    """メタデータ除外機能のテスト"""
    print("=" * 80)
    print("メタデータ除外機能テスト")
    print("=" * 80)

    test_cases = [
        {
            "yj_code": "1124007F1020",
            "name": "ハルシオン"
        },
        {
            "yj_code": "3399004M1425",
            "name": "イコサペント酸エチル"
        }
    ]

    for test_case in test_cases:
        yj_code = test_case["yj_code"]
        name = test_case["name"]

        print(f"\n[テスト] YJコード: {yj_code} ({name})")
        print("-" * 80)

        try:
            response = requests.post(
                f"{BASE_URL}/api/package-insert/core-sections",
                json={"yj_code": yj_code},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                payload = data['data']['payload']

                all_sections_clean = True
                metadata_keywords = ['販売名:', '製造販売元:', '一般名:', 'セクション名:']

                print(f"ステータス: ✅ 200 OK\n")

                for section_key in ['indications', 'dosage_and_administration', 'contraindications', 'adverse_reactions']:
                    section_name_map = {
                        'indications': '効能又は効果',
                        'dosage_and_administration': '用法及び用量',
                        'contraindications': '禁忌',
                        'adverse_reactions': '副作用'
                    }

                    section_name = section_name_map[section_key]
                    content = payload[section_key]

                    if not content:
                        print(f"  [{section_name}] データなし")
                        continue

                    # メタデータが含まれているかチェック
                    has_metadata = any(keyword in content for keyword in metadata_keywords)

                    # 実コンテンツが "# 数字" で始まるかチェック
                    starts_with_section = content.strip().startswith('#')

                    if has_metadata:
                        all_sections_clean = False
                        print(f"  [{section_name}] ❌ メタデータが残存")
                        # 最初の3行を表示
                        lines = content.split('\n')[:3]
                        for line in lines:
                            print(f"      {line}")
                    elif starts_with_section:
                        print(f"  [{section_name}] ✅ メタデータ除外成功 ({len(content)}文字)")
                    else:
                        print(f"  [{section_name}] ⚠️  形式が予期せぬもの")
                        lines = content.split('\n')[:2]
                        for line in lines:
                            print(f"      {line}")

                print()
                if all_sections_clean:
                    print("結果: ✅ 全セクションでメタデータ除外成功")
                else:
                    print("結果: ❌ 一部セクションでメタデータが残存")

            else:
                print(f"結果: ❌ エラー (ステータスコード: {response.status_code})")

        except Exception as e:
            print(f"結果: ❌ 例外発生: {e}")

    print("\n" + "=" * 80)
    print("テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_metadata_removal()
