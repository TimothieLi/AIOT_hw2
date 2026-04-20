import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium

# Coordinate mapping for the specified regions
REGION_COORDS = {
    "北部地區": [25.0330, 121.5654], # Taipei
    "中部地區": [24.1477, 120.6736], # Taichung
    "南部地區": [22.9997, 120.2270], # Tainan
    "東北部地區": [24.7303, 121.7589], # Yilan
    "東部地區": [23.9872, 121.6016], # Hualien
    "東南部地區": [22.7583, 121.1444] # Taitung
}

def connect_db():
    """Connect precisely to the SQLite database (Part 7)."""
    return sqlite3.connect("weather.db")

def get_regions():
    """Fetch all unique regions actively present in the weather table."""
    conn = connect_db()
    df = pd.read_sql("SELECT DISTINCT region FROM weather", conn)
    conn.close()
    # Sort for clear UI order
    return sorted(df['region'].dropna().tolist())

def get_weather_by_region(region):
    """Retrieve 7-day weather attributes matching the prescribed region."""
    conn = connect_db()
    # Use parameterized filtering for security
    query = "SELECT dataDate, MinT, MaxT FROM weather WHERE region = ?"
    df = pd.read_sql(query, conn, params=(region,))
    conn.close()
    
    # Ensure items are inherently ordered by date (Part 7)
    df = df.sort_values(by="dataDate").reset_index(drop=True)
    return df

def main():
    """Build the Streamlit application layout and orchestration (Part 5, 6, 7)."""
    # Use a clean, wide layout configuration
    st.set_page_config(layout="wide", page_title="Taiwan Weather", page_icon="⛅")
    st.title("⛅ Taiwan 7-Day Weather Forecast Viewer")
    st.markdown("This dashboard reads data generated dynamically from **weather.db**.")

    # Apply columns for Left-Right layout
    col1, col2 = st.columns([1.2, 1])
    
    # ====== LEFT: Taiwan Map (Part 6) ======
    with col1:
        st.subheader("🗺️ Taiwan Map")
        st.markdown("Region markers represent the available reporting zones.")
        
        # Initialize folium map focusing centrally around Taiwan
        m = folium.Map(location=[23.6978, 120.9605], zoom_start=7, tiles='CartoDB positron')
        
        # Plot markers to denote each active region
        all_regions = get_regions()
        for r_name in all_regions:
            if r_name in REGION_COORDS:
                # Basic colored markers
                folium.Marker(
                    location=REGION_COORDS[r_name],
                    popup=folium.Popup(f"<b>{r_name}</b>", max_width=200),
                    tooltip=f"Click to zoom: {r_name}",
                    icon=folium.Icon(color="blue", icon="cloud")
                ).add_to(m)
                
        # Render the Folium mapping embedded
        st_folium(m, width=600, height=600)
        
    # ====== RIGHT: Chart + Table controls (Part 5, 6) ======
    with col2:
        st.subheader("📊 Advanced Analytics")
        
        # Render dropdown for region choices
        if not all_regions:
            st.warning("No regions found! Please ensure 'weather.py' data load succeeded.")
            return
            
        selected_region = st.selectbox("📌 Select a Region", all_regions)
        
        # Fetch the selected dataset using required function
        region_df = get_weather_by_region(selected_region)
        
        if not region_df.empty:
            # Prepare Line Chart: X = dataDate, Y = Temp lines (MinT, MaxT)
            st.markdown("#### 📈 Temperature Trend")
            chart_df = region_df.set_index("dataDate")[["MinT", "MaxT"]]
            st.line_chart(chart_df, color=["#00B4D8", "#FF4B4B"])
            
            # Display detailed Data Table
            st.markdown("#### 📋 Data Table")
            
            # Optional: Apply subtle datatable color gradients while strictly fitting guidelines
            styled_df = region_df.style.background_gradient(subset=["MinT"], cmap="Blues") \
                                       .background_gradient(subset=["MaxT"], cmap="Reds")
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No weather data found for strictly '{selected_region}'.")

if __name__ == "__main__":
    main()
