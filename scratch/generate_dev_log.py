import json
import os

brain_dir = "/Users/timothy/.gemini/antigravity/brain/"
output_file = "/Users/timothy/AIOT bullshit/AIOT HW2/Dev_log.md"

sessions = sorted(os.listdir(brain_dir), key=lambda x: os.path.getmtime(os.path.join(brain_dir, x)), reverse=True)

with open(output_file, "w") as f:
    f.write("# 開發日誌 (Development Log)\n\n")
    f.write(f"本檔案自動彙整了來自系統中的 {len(sessions)} 個對話 Session 的詳細內容。\n\n")
    
    for i, session_id in enumerate(sessions):
        log_path = os.path.join(brain_dir, session_id, ".system_generated/logs/overview.txt")
        if not os.path.exists(log_path):
            continue
            
        # 讀取內容進行預判斷，確認是否與 AIOT HW2 相關
        is_relevant = False
        temp_content = []
        try:
            with open(log_path, "r") as log_f:
                for line in log_f:
                    if not line.strip(): continue
                    data = json.loads(line)
                    content = data.get("content", "")
                    # 檢查路徑或關鍵字
                    if "AIOT" in content or "HW2" in content or "weather" in content or "AIOT bullshit" in content:
                        is_relevant = True
                    temp_content.append(data)
        except:
            continue
            
        if not is_relevant:
            continue

        f.write(f"## Session {session_id}\n\n")
        
        for data in temp_content:
            source = data.get("source")
            content = data.get("content", "")
            
            if source == "USER_EXPLICIT":
                if "<USER_REQUEST>" in content:
                    request = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                    f.write(f"### 使用者請求 (User Request)\n```\n{request}\n```\n\n")
                else:
                    # 如果不是請求，可能是系統動作紀錄，這裡選擇性忽略以保持簡潔
                    pass
            elif source == "MODEL" and data.get("type") == "PLANNER_RESPONSE" and content:
                f.write(f"### AI 回應 (AI Response)\n{content}\n\n")
        
        f.write("---\n\n")

print(f"Successfully generated {output_file}")
