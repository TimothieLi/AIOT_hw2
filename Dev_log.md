# AIOT_HW2 開發日誌 (Development Log)

本文件詳盡紀錄了「AIOT HW2：天氣預報資料爬取與視覺化」專案的開發歷程、版本變更以及與 AI 的互動細節。

---

## 📅 版本紀錄 (Version Record - Git History)

以下為本專案在 Git 中的開發軌跡，紀錄了核心功能的加入順序：

| 版本 Hash | 日期 | 提交訊息 (Commit Message) | 核心變更內容 |
| :--- | :--- | :--- | :--- |
| `5c24e36` | 2026-04-21 | Update screenshot with fully rendered Streamlit map | 更新 README 的 Streamlit 成果截圖。 |
| `8922545` | 2026-04-21 | Add Streamlit demo screenshot to README | 初次加入專案成果展示圖。 |
| `c79f848` | 2026-04-21 | Merge remote main and keep local README | 合併遠端儲存庫並保留本地文件。 |
| `41d86c7` | 2026-04-21 | Homework 2 Initial commit: Weather Fetcher and Streamlit Map | **核心功能上線**：實作天氣抓取、SQLite 存儲與 Streamlit 地圖展示。 |
| `d111920` | 2026-04-20 | Initial commit | 專案初始化，建立基礎目錄結構。 |

---

## 🛠️ 詳細開發歷程 (Detailed Development Process)

本專案採階段式開發 (Phase-based Development)，從資料源頭抓取到最終的視覺化呈現，共分為四個主要階段：

### 階段 1：CWA API 資料獲取與解析 (HW2-1)
*   **使用者請求**：
    > 「請幫我寫一個 Python 腳本，使用中央氣象署 (CWA) API `F-D0047-091` 獲取台灣各縣市一週的天氣預報，並將縣市依六大分區（北部、中部、南部、東北部、東部、東南部）進行分組，最後輸出為 JSON 與 CSV 格式。」
*   **AI 執行動作**：
    1.  實作 `fetch_weather_forecast` 函數，使用 `requests` 呼叫 API 並處理 SSL 憑證檢查問題。
    2.  定義 `REGION_MAP` 將台灣縣市對應至六大區域。
    3.  開發解析邏輯，提取每個縣市的氣象元素（Wx, PoP, MinT, MaxT）。
    4.  實作資料儲存功能，產生 `weather_forecast_all.json` 與 `weather_data.csv`。
*   **主要產出**：`HW2_1_weather_forecast.py`

### 階段 2：氣溫特徵提取與資料清洗 (HW2-2)
*   **使用者請求**：
    > 「我需要進一步從天氣資料中提取每天的最高溫與最低溫，並依分區彙整出該區每天的氣溫範圍。請確保能處理資料中的時間格式，並將結果儲存為結構化的格式。」
*   **AI 執行動作**：
    1.  建立 `parse_weather_data` 邏輯，精確比對 API 返回的多個時段，找出每日的絕對最高溫與最低溫。
    2.  使用 `pandas` 進行 `groupby` 操作，彙整各分區的氣溫極端值。
*   **主要產出**：`HW2_2_extract_temperatures.py`

### 階段 3：SQLite 資料庫整合 (HW2-3)
*   **使用者請求**：
    > 「請將處理好的天氣資料存入 SQLite 資料庫中，資料表應包含區域、日期、最低溫與最高溫。若資料已存在，應支援覆蓋更新。」
*   **AI 執行動作**：
    1.  實作 `save_to_sqlite` 函數，使用 `sqlite3` 與 `pandas.to_sql` 進行資料持久化。
    2.  設計資料庫 Schema，確保 `region` 與 `dataDate` 的正確性。
*   **主要產出**：`HW2_3_save_to_sqlite.py` 與整合後的 `weather.py`

### 階段 4：Streamlit 互動式儀表板開發
*   **使用者請求**：
    > 「最後，請建立一個 Streamlit 網頁應用程式。左側要顯示台灣地圖並標註分區座標，右側要讓使用者可以選擇分區，並動態顯示該區的一週氣溫折線圖與詳細資料表。」
*   **AI 執行動作**：
    1.  實作 `app.py`，使用 `st.set_page_config` 設定寬屏版面。
    2.  整合 `folium` 與 `streamlit_folium` 在左側欄位顯示動態座標地圖。
    3.  在右側欄位建立 `st.selectbox` 選單，從 `weather.db` 讀取即時資料。
    4.  使用 `st.line_chart` 繪製氣溫趨勢圖，並使用 `dataframe.style` 為資料表添加熱力圖背景（藍色表示低溫，紅色表示高溫）。
*   **主要產出**：`app.py`

---

## 💬 近期對話紀錄 (Recent Interactions)

### Session: fbeac4cc-3ccc-4867-abf4-aba9ac31cda7 (2026-04-28)

*   **使用者請求**：
    > 「請幫我加一個檔案，裡面包含聊天記錄。我想要關於 AIOT_HW2 的版本紀錄的所有內容，請改名成 Dev_log.md，且要包含詳細的對話細節（如 Request、AI 回應等）。」
*   **AI 執行動作**：
    1.  掃描系統內 30 個 Session 的日誌，識別與 `AIOT`, `HW2`, `weather` 相關的對話。
    2.  過濾掉無關的「專題 (Movie Recommender)」歷史紀錄。
    3.  根據 Git 歷史與程式碼結構，重新整理出 AIOT_HW2 的完整開發里程碑。
    4.  自動彙整本份 `Dev_log.md` 檔案。

---

> [!NOTE]
> 本日誌已根據您的要求進行了深度過濾，移除了與 AIOT_HW2 無關的專題開發歷史。
> 若未來有新的開發對話，建議再次更新此檔案以維持記錄完整性。
