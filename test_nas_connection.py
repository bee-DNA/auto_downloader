import paramiko
import sys

print("測試 NAS 連線...")
print()

try:
    print("步驟 1: 建立 SSH Transport...")
    t = paramiko.Transport(("bioailab.synology.me", 22))
    t.banner_timeout = 30  # 增加超時時間
    t.window_size = 2147483647
    t.packetizer.REKEY_BYTES = pow(2, 40)
    t.packetizer.REKEY_PACKETS = pow(2, 40)

    print("✅ Transport 建立成功")
    print()

    print("步驟 2: 開始連線...")
    print("  Host: bioailab.synology.me")
    print("  Port: 22")
    print("  User: bioailab")
    print()

    t.connect(username="bioailab", password="Ncueailab403")
    print("✅ SSH 認證成功")
    print()

    print("步驟 3: 建立 SFTP 連線...")
    sftp = paramiko.SFTPClient.from_transport(t)
    print("✅ SFTP 建立成功")
    print()

    print("步驟 4: 測試目錄訪問...")
    files = sftp.listdir("/Bee_metagenomics/Bee_metagenomics/fastq_data")
    print(f"✅ 目錄訪問成功，找到 {len(files)} 個檔案")
    print()

    print("步驟 5: 關閉連線...")
    sftp.close()
    t.close()
    print("✅ 連線正常關閉")
    print()

    print("=" * 70)
    print("✅ 所有測試通過！NAS 連線正常")
    print("=" * 70)

except Exception as e:
    print()
    print("=" * 70)
    print("❌ 錯誤詳情:")
    print("=" * 70)
    print(f"錯誤類型: {type(e).__name__}")
    print(f"錯誤訊息: {str(e)}")
    print()

    import traceback

    print("完整錯誤堆疊:")
    traceback.print_exc()
    print()

    print("可能原因:")
    print("1. 連線超時 - 增加 timeout 參數")
    print("2. SSH 金鑰交換問題 - 更新 paramiko 版本")
    print("3. 網路不穩定 - 檢查網路連線")
    print("4. NAS 伺服器忙碌 - 稍後再試")
    sys.exit(1)
