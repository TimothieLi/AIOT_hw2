"""
HW2-2: 分析資料，提取最高與最低氣溫的資料
目的：分析天氣預報資料的 JSON 格式，找出最高與最低氣溫的資料位置，並提取出來。
"""

import json


def load_json_data(file_path: str) -> dict:
    """
    載入 JSON 檔案

    Args:
        file_path: JSON 檔案路徑

    Returns:
        dict: JSON 內容
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_temperature_data(data: dict) -> dict:
    """
    從區域天氣預報資料中提取最高與最低氣溫 (MaxT, MinT) 資料。

    Args:
        data: 包含六大分區天氣預報的字典

    Returns:
        dict: 整理後僅包含各縣市最高與最低氣溫資料的字典
    """
    extracted = {}

    for region, locations in data.items():
        extracted[region] = []
        for loc in locations:
            loc_name = loc.get("locationName", "")
            
            mint_data = []
            maxt_data = []

            # 在 weatherElement 中尋找 MinT 與 MaxT
            for elem in loc.get("weatherElement", []):
                elem_name = elem.get("elementName")
                if elem_name == "MinT":
                    mint_data = elem.get("time", [])
                elif elem_name == "MaxT":
                    maxt_data = elem.get("time", [])

            extracted[region].append({
                "locationName": loc_name,
                "MinT": mint_data,
                "MaxT": maxt_data
            })

    return extracted


def main():
    print("=" * 70)
    print("  HW2-2：分析並提取最高與最低氣溫 (MaxT, MinT) 資料")
    print("=" * 70)

    # 1. 讀取 HW2-1 產生的 weather_forecast_regions.json
    input_file = "weather_forecast_regions.json"
    print(f"[INFO] 正在載入資料來源：{input_file} ...")
    try:
        data = load_json_data(input_file)
    except FileNotFoundError:
        print(f"[ERROR] 找不到檔案 {input_file}，請確認是否已執行 HW2-1。")
        return

    # 2. 找出並提取最高與最低氣溫的資料
    print("\n[INFO] 正在提取各區域最高氣溫 (MaxT) 與最低氣溫 (MinT) 資料...")
    temp_data = extract_temperature_data(data)

    # 3. 使用 json.dumps 觀察提取的資料
    # 將提取到的資料轉換成具縮排的 JSON 字串以利觀察
    print("\n" + "=" * 70)
    print("  [觀察提取的資料] json.dumps 輸出（顯示北部作為範例）")
    print("=" * 70)
    
    # 這裡可以全部印出，但為了避免印出過多，挑選"北部"來觀察
    if "北部" in temp_data:
        sample_output = json.dumps({"北部": temp_data["北部"]}, ensure_ascii=False, indent=4)
        print(sample_output)
    else:
        full_output = json.dumps(temp_data, ensure_ascii=False, indent=4)
        print(full_output)

    # 也可以考慮將完整提取的結果儲存成新的 JSON 讓使用者檢查整體
    output_file = "extracted_temperatures.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(temp_data, f, ensure_ascii=False, indent=4)
    print(f"\n[INFO] 完整的氣溫提取結果已儲存至：{output_file}")


if __name__ == "__main__":
    main()
