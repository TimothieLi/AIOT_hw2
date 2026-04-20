"""
HW2-3: 將氣溫資料儲存到 SQLite3 資料庫
目的：將氣溫資料儲存到 SQLite3 資料庫，以便後續查詢。
方法：
- 建立 SQLite3 資料庫，取名為 "data.db"
- 創建資料庫 Table，取名為 "TemperatureForecasts"
- 將氣溫資料存到資料庫
- 從資料庫查詢以下資料：
  1. 列出所有地區名稱
  2. 列出中部地區的氣溫資料
"""

import json
import sqlite3

# 中部地區的縣市列表，用於查詢過濾
CENTRAL_REGION_COUNTIES = ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"]


def setup_database(db_name: str = "data.db"):
    """
    建立 SQLite 資料庫連線並創建 Table
    資料欄位包含：id, regionName, dataDate, mint, maxt
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 為了避免重複執行塞入相同資料，先嘗試清除舊的 Table（若存在）
    cursor.execute("DROP TABLE IF EXISTS TemperatureForecasts")

    # 建立 Table
    create_table_sql = """
    CREATE TABLE TemperatureForecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regionName TEXT NOT NULL,
        dataDate TEXT NOT NULL,
        mint INTEGER NOT NULL,
        maxt INTEGER NOT NULL
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()

    return conn, cursor


def parse_and_insert_data(cursor, json_file: str = "extracted_temperatures.json"):
    """
    讀取包含 JSON 氣溫資料的檔案，並將其插入資料庫
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    insert_sql = """
    INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
    VALUES (?, ?, ?, ?)
    """

    # 遍歷資料 (第一層為六大分區、第二層為各縣市、第三層為清單)
    for region, locations in data.items():
        for loc in locations:
            region_name = loc["locationName"]
            
            # 分別取得最低溫與最高溫的清單
            mint_list = loc.get("MinT", [])
            maxt_list = loc.get("MaxT", [])

            # 假設兩邊時段長度與順序一致，透過 zip 同時提取
            for mint_data, maxt_data in zip(mint_list, maxt_list):
                # 取 startTime 作為 dataDate，或者你可以結合 startTime 與 endTime
                start_time = mint_data.get("startTime", "")
                end_time = mint_data.get("endTime", "")
                data_date = f"{start_time} 至 {end_time}"
                
                mint_val = int(mint_data.get("parameter", {}).get("parameterName", 0))
                maxt_val = int(maxt_data.get("parameter", {}).get("parameterName", 0))

                cursor.execute(insert_sql, (region_name, data_date, mint_val, maxt_val))


def check_database_data(cursor):
    """
    從資料庫查詢以檢查：
    1. 列出所有地區名稱
    2. 列出中部地區的氣溫資料
    """
    print("\n" + "=" * 50)
    print("  資料庫檢查：1. 列出所有地區名稱")
    print("=" * 50)
    
    # 透過 DISTINCT 排除重複查詢所有存在於資料庫裡的 regionName
    cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts;")
    all_regions = cursor.fetchall()
    # fetchall 回傳的格式是 list of tuples 例如 [('臺北市',), ('新北市',)]
    region_names = [row[0] for row in all_regions]
    print(f"資料庫中的總地區數: {len(region_names)}")
    print(f"地區清單: {', '.join(region_names)}")
    
    print("\n" + "=" * 50)
    print("  資料庫檢查：2. 列出中部地區的氣溫資料")
    print("=" * 50)

    # 動態產生 sql IN 參數的 ?, ?, ?
    placeholders = ",".join("?" * len(CENTRAL_REGION_COUNTIES))
    query_sql = f"""
    SELECT id, regionName, dataDate, mint, maxt 
    FROM TemperatureForecasts 
    WHERE regionName IN ({placeholders})
    ORDER BY regionName, dataDate;
    """
    
    cursor.execute(query_sql, CENTRAL_REGION_COUNTIES)
    central_data = cursor.fetchall()

    if central_data:
        # 印出表格表頭 (Markdown 格式)
        print(f"| {'ID':<4} | {'地區':<4} | {'日期時間區間':<40} | {'最低氣溫(°C)':<12} | {'最高氣溫(°C)':<12} |")
        print(f"|{'-'*6}|{'-'*8}|{'-'*42}|{'-'*16}|{'-'*16}|")
        for row in central_data:
            id_, r_name, d_date, mint, maxt = row
            print(f"| {id_:<4} | {r_name:<4} | {d_date:<40} | {mint:<14} | {maxt:<14} |")
    else:
        print("未查找到任何中部地區氣溫資料")


def main():
    print("[INFO] 開始將資料寫入 SQLite3 資料庫...")
    
    # 建立與設定資料庫
    conn, cursor = setup_database("data.db")
    
    try:
        # 讀取並插入 JSON 資料
        parse_and_insert_data(cursor, "extracted_temperatures.json")
        conn.commit()
        print("[INFO] 氣溫資料已成功插入至 data.db。")
        
        # 檢查與查詢資料
        check_database_data(cursor)
        
    except FileNotFoundError:
        print("[ERROR] 找不到檔案 extracted_temperatures.json，請確認是前一個步驟否有正確產出。")
    except Exception as e:
        print(f"[ERROR] 處理資料庫時發生異常：{e}")
        conn.rollback() # 出錯的話不存檔
    finally: # 確保最後資料庫有被正確關閉
        conn.close() 

if __name__ == "__main__":
    main()
