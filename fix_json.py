"""
修復 download_progress.json 格式問題
"""

import json
import shutil
from datetime import datetime


def fix_json():
    json_file = "download_progress.json"
    backup_file = (
        f"download_progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    print("🔧 修復 JSON 檔案格式...")

    # 備份原始檔案
    try:
        shutil.copy(json_file, backup_file)
        print(f"✅ 已備份至: {backup_file}")
    except Exception as e:
        print(f"⚠️  備份失敗: {e}")

    # 讀取並修復 JSON
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 找到第一個完整的 JSON 物件結尾
        # 尋找最後一個 "remaining": []
        first_end = content.find('"remaining": []')
        if first_end != -1:
            # 找到這個 remaining 後的第一個 }
            bracket_pos = content.find("}", first_end)
            if bracket_pos != -1:
                # 截取到第一個完整 JSON 結束
                fixed_content = content[: bracket_pos + 1]

                # 驗證是否為有效 JSON
                data = json.loads(fixed_content)

                # 寫回檔案
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print(f"✅ JSON 格式已修復!")
                print(f"   已完成樣本: {len(data.get('completed', []))}")
                print(f"   失敗記錄: {len(data.get('failed', []))}")

                return True

        print("❌ 無法自動修復,請檢查檔案內容")
        return False

    except Exception as e:
        print(f"❌ 修復失敗: {e}")
        print(f"   請使用備份檔案: {backup_file}")
        return False


if __name__ == "__main__":
    success = fix_json()
    if success:
        print("\n✅ 現在可以重新執行下載程式了!")
    else:
        print("\n❌ 需要手動修復 JSON 檔案")
