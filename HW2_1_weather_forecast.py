"""
HW2-1: 獲取天氣預報資料
目的：使用 CWA API 獲取台灣北部、中部、南部、東北部、東部及東南部地區一週的天氣預報資料
資料集：F-C0032-001（三十六小時天氣預報，含全台各縣市）
         F-A0010-001（一週農業氣象預報，若帳號有授權則使用）
"""

import csv
import json
import requests
import urllib3

# 停用因為 `verify=False` 所造成的 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
# 設定 API 授權碼（Authorization Key）
# 請至 https://opendata.cwa.gov.tw/ 註冊會員後取得
# ============================================================
AUTH_KEY = "CWA-4EE11799-4069-4DF2-A50B-B98BF5478258"

# API 基本設定
BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"

# 資料集設定
# F-A0010-001：一週農業氣象預報（優先嘗試，符合規格需求）
# F-C0032-001：三十六小時天氣預報（若沒有授權或出現 404 則作為備用方案）
TARGET_DATASET_ID = "F-A0010-001"
FALLBACK_DATASET_ID = "F-C0032-001"

# ============================================================
# 台灣六大分區縣市對應表
# 北部：臺北市、新北市、基隆市、桃園市、新竹縣、新竹市
# 中部：苗栗縣、臺中市、彰化縣、南投縣、雲林縣
# 南部：嘉義縣、嘉義市、臺南市、高雄市、屏東縣
# 東北部：宜蘭縣（東北部）
# 東部：花蓮縣、臺東縣
# 東南部：（以屏東縣東部鄉鎮為代表，資料集中無單獨分區，使用臺東縣代替）
# 離島：金門縣、澎湖縣、連江縣
# ============================================================
REGION_MAP = {
    "北部":  ["臺北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市"],
    "中部":  ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部":  ["嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"],
    "東北部": ["宜蘭縣"],
    "東部":  ["花蓮縣"],
    "東南部": ["臺東縣"],
}


# ============================================================
# Step 1：呼叫 CWA API
# ============================================================
def fetch_weather_forecast(auth_key: str, dataset_id: str, location_name: str = None) -> dict:
    """
    呼叫 CWA OpenData API 獲取天氣預報資料（JSON 格式）

    Args:
        auth_key     : CWA API 授權碼
        dataset_id   : 資料集代碼（e.g. F-C0032-001）
        location_name: 欲查詢的縣市名稱；None 表示取得全部縣市

    Returns:
        dict: API 回傳的 JSON 資料（Python dict）
    """
    url = f"{BASE_URL}/{dataset_id}"

    params = {"Authorization": auth_key}
    if location_name:
        params["locationName"] = location_name

    print(f"[INFO] 請求 URL : {url}")
    print(f"[INFO] 查詢縣市 : {location_name if location_name else '全部'}")

    # 根據規格需求：Ensure the app handles SSL verification issues
    # 這裡我們加入 verify=False 以忽略 SSL 憑證檢查
    response = requests.get(url, params=params, timeout=30, verify=False)
    
    # 若回傳非 2xx，則例外處理
    response.raise_for_status()

    return response.json()


# ============================================================
# Step 2：將縣市資料依六大分區分組
# ============================================================
def group_by_region(data: dict, region_map: dict) -> dict:
    """
    依照六大分區對應表，將全台縣市資料分組。

    Args:
        data       : fetch_weather_forecast() 回傳的原始 JSON dict
        region_map : REGION_MAP 常數

    Returns:
        dict: { 分區名稱: [location_dict, ...] }
    """
    all_locations = data.get("records", {}).get("location", [])

    # 建立縣市名稱→資料的 lookup
    location_lookup = {loc["locationName"]: loc for loc in all_locations}

    grouped = {}
    for region, counties in region_map.items():
        grouped[region] = []
        for county in counties:
            if county in location_lookup:
                grouped[region].append(location_lookup[county])
            else:
                print(f"[WARNING] 找不到縣市：{county}（可能不在此資料集中）")

    return grouped


# ============================================================
# Step 3：解析並顯示各分區摘要
# ============================================================
def display_region_summary(grouped: dict) -> None:
    """
    逐一列印六大分區各縣市的天氣預報摘要。

    Args:
        grouped: group_by_region() 回傳的分組 dict
    """
    print(f"\n{'='*70}")
    print("  台灣六大分區天氣預報摘要")
    print(f"{'='*70}")

    for region, locations in grouped.items():
        print(f"\n🗺️  【{region}】")
        if not locations:
            print("   (無資料)")
            continue
        for loc in locations:
            loc_name = loc.get("locationName", "N/A")
            elements = {
                elem["elementName"]: elem.get("time", [])
                for elem in loc.get("weatherElement", [])
            }
            # 取第一個時段資料
            wx   = elements.get("Wx",  [{}])[0].get("parameter", {}).get("parameterName", "N/A")
            pop  = elements.get("PoP", [{}])[0].get("parameter", {}).get("parameterName", "N/A")
            mint = elements.get("MinT",[{}])[0].get("parameter", {}).get("parameterName", "N/A")
            maxt = elements.get("MaxT",[{}])[0].get("parameter", {}).get("parameterName", "N/A")
            print(f"   📍 {loc_name}：{wx}｜降雨機率 {pop}%｜氣溫 {mint}~{maxt}°C")


# ============================================================
# Step 4：儲存為 CSV
# ============================================================
def save_to_csv(grouped: dict, csv_path: str = "weather_data.csv") -> None:
    """
    將六大分區資料攤平後儲存為 CSV 檔案。

    CSV 欄位：
        region | locationName | elementName | startTime | endTime |
        parameterName | parameterValue | parameterUnit

    Args:
        grouped : group_by_region() 回傳的分組 dict
        csv_path: 輸出 CSV 檔案路徑
    """
    fieldnames = [
        "region", "locationName", "elementName",
        "startTime", "endTime",
        "parameterName", "parameterValue", "parameterUnit",
    ]
    rows = []

    for region, locations in grouped.items():
        for loc in locations:
            loc_name = loc.get("locationName", "")
            for elem in loc.get("weatherElement", []):
                elem_name = elem.get("elementName", "")
                for slot in elem.get("time", []):
                    param = slot.get("parameter", {})
                    rows.append({
                        "region":         region,
                        "locationName":   loc_name,
                        "elementName":    elem_name,
                        "startTime":      slot.get("startTime", ""),
                        "endTime":        slot.get("endTime", ""),
                        "parameterName":  param.get("parameterName", ""),
                        "parameterValue": param.get("parameterValue", ""),
                        "parameterUnit":  param.get("parameterUnit", ""),
                    })

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] CSV 已儲存至 {csv_path}（共 {len(rows)} 筆資料）")


# ============================================================
# 主程式
# ============================================================
def main():
    print("=" * 70)
    print("  HW2-1：CWA API 一週天氣預報資料爬取")
    print(f"  目標資料集：{TARGET_DATASET_ID}")
    print("=" * 70)

    # ----------------------------------------------------------
    # Step 1：呼叫 CWA API 取得全部縣市天氣預報
    # ----------------------------------------------------------
    print(f"\n[STEP 1] 呼叫 CWA API 獲取全台天氣預報資料 ({TARGET_DATASET_ID})...")
    try:
        all_data = fetch_weather_forecast(auth_key=AUTH_KEY, dataset_id=TARGET_DATASET_ID)
    except Exception as e:
        print(f"[WARNING] 獲取 {TARGET_DATASET_ID} 失敗 ({e})，正在自動切換至備用資料集 {FALLBACK_DATASET_ID}...")
        all_data = fetch_weather_forecast(auth_key=AUTH_KEY, dataset_id=FALLBACK_DATASET_ID)

    # 使用 json.dumps 觀察原始資料結構
    print("\n[STEP 1] json.dumps 觀察原始 JSON 資料（前 2000 字元）：")
    raw_json_str = json.dumps(all_data, ensure_ascii=False, indent=2)
    print(raw_json_str[:2000])
    print("\n... (資料截斷，完整資料已儲存至 weather_forecast_all.json)")

    # 儲存完整 JSON
    with open("weather_forecast_all.json", "w", encoding="utf-8") as f:
        f.write(raw_json_str)
    print("[INFO] 完整 JSON 已寫入 weather_forecast_all.json")

    # ----------------------------------------------------------
    # Step 2：將全台資料依六大分區分組
    # ----------------------------------------------------------
    print("\n[STEP 2] 依六大分區分組資料...")
    grouped = group_by_region(all_data, REGION_MAP)

    # 逐區 json.dumps 觀察
    for region, locations in grouped.items():
        region_json = json.dumps({region: locations}, ensure_ascii=False, indent=2)
        print(f"\n[{region}] json.dumps 輸出（前 400 字元）：")
        print(region_json[:400])

    # ----------------------------------------------------------
    # Step 3：顯示各分區天氣摘要
    # ----------------------------------------------------------
    print("\n[STEP 3] 各分區天氣預報摘要：")
    display_region_summary(grouped)

    # ----------------------------------------------------------
    # Step 4：儲存六大分區 JSON
    # ----------------------------------------------------------
    with open("weather_forecast_regions.json", "w", encoding="utf-8") as f:
        json.dump(grouped, f, ensure_ascii=False, indent=2)
    print("\n[INFO] 六大分區 JSON 已儲存至 weather_forecast_regions.json")

    # ----------------------------------------------------------
    # Step 5：攤平資料儲存為 CSV
    # ----------------------------------------------------------
    print("\n[STEP 5] 儲存結構化資料至 weather_data.csv...")
    save_to_csv(grouped, csv_path="weather_data.csv")

    print("\n✅ 資料爬取完成！")
    print("   - weather_forecast_all.json    : 全台縣市原始 JSON")
    print("   - weather_forecast_regions.json : 六大分區分組 JSON")
    print("   - weather_data.csv             : 攤平後的結構化 CSV 資料")


if __name__ == "__main__":
    main()
