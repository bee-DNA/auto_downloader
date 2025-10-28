#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 runs.txt - 將包含逗號的行拆分成單獨的樣本
"""

from pathlib import Path

runs_file = Path("runs.txt")
backup_file = Path("runs.txt.backup")

# 備份原始檔案
if runs_file.exists():
    import shutil
    shutil.copy(runs_file, backup_file)
    print(f"✅ 已備份原始檔案: {backup_file}")

# 讀取並處理
all_runs = []
multi_line_count = 0

with open(runs_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
            
        # 如果包含逗號，拆分
        if ',' in line:
            multi_line_count += 1
            samples = [s.strip() for s in line.split(',')]
            print(f"第 {line_num} 行: {line}")
            print(f"  拆分為: {samples}")
            all_runs.extend(samples)
        else:
            all_runs.append(line)

# 移除重複並排序
original_count = len(all_runs)
all_runs = sorted(set(all_runs))
unique_count = len(all_runs)

print(f"\n統計:")
print(f"  包含逗號的行數: {multi_line_count}")
print(f"  原始樣本數: {original_count}")
print(f"  去重後樣本數: {unique_count}")
print(f"  移除重複數: {original_count - unique_count}")

# 寫入修正後的檔案
with open(runs_file, 'w', encoding='utf-8') as f:
    for run_id in all_runs:
        f.write(f"{run_id}\n")

print(f"\n✅ 已修正 {runs_file}")
print(f"   可以執行: git diff runs.txt 查看變更")
