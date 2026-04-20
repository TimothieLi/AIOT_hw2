import requests
import json
import pandas as pd
import sqlite3
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========================
# 📌 Configuration
# ========================
AUTH_KEY = "CWA-4EE11799-4069-4DF2-A50B-B98BF5478258"
# Using F-D0047-091 which provides 7-day forecasts for all counties
API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization={AUTH_KEY}"

# Mapping of specific regions
REGION_MAP = {
    "北部地區": ["臺北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市"],
    "中部地區": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部地區": ["嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"],
    "東北部地區": ["宜蘭縣"],
    "東部地區": ["花蓮縣"],
    "東南部地區": ["臺東縣"]
}

def get_region_for_county(county_name):
    """Map a county name to its macro region."""
    for region, counties in REGION_MAP.items():
        if county_name in counties:
            return region
    return None

def fetch_weather_data():
    """Fetch JSON from CWA API."""
    print("[INFO] Fetching data from CWA API...")
    res = requests.get(API_URL, verify=False, timeout=30)
    res.raise_for_status()
    data = res.json()
    
    # Use json.dumps to print and inspect raw JSON (Part 1.3)
    print("\n[INFO] Inspecting raw JSON data (first 500 characters):")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
    
    return data

def parse_weather_data(data):
    """Parse JSON to extract 7-day data organized by regions."""
    locations = data['records']['Locations'][0]['Location']
    temp_rows = []
    
    # Step 1: Extract MinT and MaxT for each county per day
    for loc in locations:
        county = loc['LocationName']
        region = get_region_for_county(county)
        
        if not region: # Skip islands or unmapped regions
            continue
            
        weather_elements = loc['WeatherElement']
        daily_mint = {}
        daily_maxt = {}
        
        for we in weather_elements:
            if we['ElementName'] == '最低溫度':
                for t in we['Time']:
                    date_str = t['StartTime'][:10]
                    val = t['ElementValue'][0]['MinTemperature']
                    # Keep track of the absolute minimum for the day
                    if date_str not in daily_mint or int(val) < daily_mint[date_str]:
                        daily_mint[date_str] = int(val)
            elif we['ElementName'] == '最高溫度':
                for t in we['Time']:
                    date_str = t['StartTime'][:10]
                    val = t['ElementValue'][0]['MaxTemperature']
                    # Keep track of the absolute maximum for the day
                    if date_str not in daily_maxt or int(val) > daily_maxt[date_str]:
                        daily_maxt[date_str] = int(val)
        
        # Merge dictionary data into list
        for date_str in daily_mint.keys():
            if date_str in daily_maxt:
                temp_rows.append({
                    "county": county,
                    "region": region,
                    "dataDate": date_str,
                    "MinT": daily_mint[date_str],
                    "MaxT": daily_maxt[date_str]
                })

    df_counties = pd.DataFrame(temp_rows)
    
    # Step 2: Group by Region and Date to get the regional extreme limits
    df_regions = df_counties.groupby(["region", "dataDate"], as_index=False).agg({
        "MinT": "min",
        "MaxT": "max"
    })
    
    return df_regions.sort_values(by=["region", "dataDate"])

def save_csv(df):
    """Save parsed DataFrame to CSV (Part 3)"""
    csv_path = "weather_data.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] Saved {len(df)} rows to {csv_path}")

def save_to_sqlite(df):
    """Save parsed DataFrame to SQLite database (Part 4)"""
    db_path = "weather.db"
    conn = sqlite3.connect(db_path)
    
    # Create or replace table using pandas (satisfies requirement 4.4, 4.5)
    # The 'weather' table will have columns: region, dataDate, MinT, MaxT
    df.to_sql("weather", conn, if_exists="replace", index=False, 
              dtype={"region": "TEXT", "dataDate": "TEXT", "MinT": "INTEGER", "MaxT": "INTEGER"})
    
    conn.close()
    print(f"[INFO] Saved {len(df)} rows to SQLite database '{db_path}' table 'weather'")

def main():
    print("="*50)
    print("Starting Weather Data Processing Pipeline")
    print("="*50)
    
    # 1. Fetch data
    raw_data = fetch_weather_data()
    
    # 2. Parse data
    df_parsed = parse_weather_data(raw_data)
    
    # 3. Save CSV for debugging
    save_csv(df_parsed)
    
    # 4. Save to SQLite
    save_to_sqlite(df_parsed)
    
    print("[INFO] Pipeline complete.")

if __name__ == "__main__":
    main()
