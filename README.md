# AIOT_hw2

這是一個天氣預報資料的爬取與視覺化專案，使用中央氣象署 (CWA) API 獲取台灣北部、中部、南部、東北部、東部及東南部地區一週的天氣預報資料。專案會對取得的 JSON 格式資料進行解析，儲存為 CSV 與 SQLite 資料庫中，最後透過 Streamlit 網頁應用程式與 Folium 動態地圖介面進行互動式視覺化。

## 專案成果展示
![Streamlit 成果截圖](demo.png)

## 功能特色
- **資料獲取與解析**：使用 Requests 抓取 CWA API (`F-D0047-091`) 氣象資料，並將縣市層級對照至六大區域，擷取最高溫與最低溫資料。
- **資料儲存**：可將解析後的紀錄匯出為 `weather_data.csv`，並寫入本機 `weather.db` SQLite 資料庫。
- **動態視覺化網頁**：基於 Streamlit 打造左右排版的互動式儀表板。
  - 左側提供台灣六大分區的 Folium 動態座標地圖。
  - 右側提供區域氣象分析表、選單與動態氣溫折線圖。

## 如何執行

1. **安裝必要的套件：**
   ```bash
   pip install requests pandas folium streamlit streamlit-folium urllib3
   ```

2. **執行資料獲取與更新資料庫：**
   此腳本會向 CWA 請求最新資料並更新 SQLite 資料庫 (`weather.db`)。
   ```bash
   python weather.py
   ```

3. **啟動互動式網頁儀表板：**
   ```bash
   python -m streamlit run app.py
   ```

## 專案結構
- `weather.py`: 資料撈取、處理與儲存的主程式。
- `app.py`: Streamlit 網頁端主程式。
- `Dev_log.md`: **開發日誌**，詳盡紀錄了專案的開發里程碑、與 AI 的互動過程與版本變更。
- `weather.db` / `weather_data.csv`: 獲取後產生的資料儲存檔。
- 其他測試用或流程紀錄腳本 (`HW2_...`)

---
## 開發日誌 (Development Log)
本專案特別維護了一份 [Dev_log.md](Dev_log.md)，旨在展現開發過程中的問題解決思路與技術演進，包含：
- Git 版本提交軌跡。
- 四大開發階段的詳細技術執行細節。
- 與 AI 協作的關鍵 Session 紀錄。
