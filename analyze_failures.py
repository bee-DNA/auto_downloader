"""
分析下載失敗原因
"""

import json
from collections import Counter


def analyze_failures():
    print("=" * 70)
    print("📊 下載失敗原因分析")
    print("=" * 70)

    with open("download_progress.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    completed = data.get("completed", [])
    failed = data.get("failed", [])

    print(f"\n✅ 已完成: {len(completed)} 個樣本")
    print(f"❌ 失敗: {len(failed)} 個樣本")
    print(f"📊 成功率: {len(completed)/(len(completed)+len(failed))*100:.1f}%")

    if not failed:
        print("\n🎉 沒有失敗的樣本!")
        return

    # 統計失敗原因
    print("\n" + "=" * 70)
    print("❌ 失敗原因統計")
    print("=" * 70)

    error_counts = Counter()
    step_counts = Counter()

    for f in failed:
        error = f.get("error", "Unknown")
        step = f.get("step", "Unknown")
        error_counts[error] += 1
        step_counts[step] += 1

    print("\n📋 按錯誤類型:")
    for error, count in error_counts.most_common():
        print(f"  • {error}")
        print(f"    數量: {count} 次 ({count/len(failed)*100:.1f}%)")

    print("\n📋 按失敗步驟:")
    for step, count in step_counts.most_common():
        print(f"  • {step}: {count} 次")

    # 顯示前 10 個失敗樣本
    print("\n" + "=" * 70)
    print("📝 前 10 個失敗樣本")
    print("=" * 70)

    for i, f in enumerate(failed[:10], 1):
        run_id = f.get("run_id", "Unknown")
        step = f.get("step", "Unknown")
        error = f.get("error", "Unknown")
        time = f.get("time", "Unknown")

        print(f"\n{i}. {run_id}")
        print(f"   步驟: {step}")
        print(f"   錯誤: {error}")
        print(f"   時間: {time}")

    # 主要問題判斷
    print("\n" + "=" * 70)
    print("💡 問題診斷")
    print("=" * 70)

    most_common_error = error_counts.most_common(1)[0][0]

    if "找不到指定的檔案" in most_common_error or "WinError 2" in most_common_error:
        print("\n🔍 主要問題: SRA Toolkit 工具找不到")
        print("\n解決方案:")
        print("  1. 執行: 一鍵安裝_SRA_Toolkit.bat")
        print("  2. 或執行: SETUP.bat")
        print("  3. 確認 prefetch.exe 和 fasterq-dump.exe 存在於:")
        print("     D:\\...\\data_collector\\sratoolkit.3.2.1-win64\\bin\\")

    elif "網路" in most_common_error or "timeout" in most_common_error.lower():
        print("\n🔍 主要問題: 網路連線問題")
        print("\n解決方案:")
        print("  1. 檢查網路連線")
        print("  2. 稍後重試")
        print("  3. 考慮使用 Aspera (更快更穩定)")

    elif "權限" in most_common_error or "permission" in most_common_error.lower():
        print("\n🔍 主要問題: 檔案權限問題")
        print("\n解決方案:")
        print("  1. 以系統管理員身分執行")
        print("  2. 檢查 D 槽寫入權限")

    else:
        print(f"\n🔍 主要問題: {most_common_error}")
        print("\n建議:")
        print("  1. 檢查錯誤訊息")
        print("  2. 確認系統環境")
        print("  3. 查看完整日誌")


if __name__ == "__main__":
    try:
        analyze_failures()
    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
        import traceback

        traceback.print_exc()
