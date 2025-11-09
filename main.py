import folium
import pandas as pd
import json
from branca.colormap import LinearColormap

# ----------------------------------------------------------
# 1. Load County Scores CSV
# ----------------------------------------------------------
df = pd.read_csv("texas_county_chs.csv")  # CSV must contain: county, chs


# ----------------------------------------------------------
# 2. Load Texas County GeoJSON
# ----------------------------------------------------------
geojson_path = "tx_counties.geojson"
with open(geojson_path) as f:
    counties = json.load(f)


# ----------------------------------------------------------
# 3. Create Base Map (Texas view)
# ----------------------------------------------------------
m = folium.Map(
    location=[31.0, -99.0],  
    zoom_start=5,
    tiles="cartodbpositron"
)


# ----------------------------------------------------------
# 4. Define Custom Color Scale (T-Mobile theme)
# ----------------------------------------------------------
colors = ["#f2def0", "#ffd2fa", "#f7c1ea", "#f073c6", "#E20074"]  # 0–100 gradient
colormap = LinearColormap(
    colors=colors,
    index=[0, 25, 50, 75, 100],
    vmin=0,
    vmax=100
)
colormap.caption = "Customer Happiness Score"


# ----------------------------------------------------------
# 5. Build lookup dictionary for CHS by county
# ----------------------------------------------------------
county_lookup = df.set_index("county")["chs"].to_dict()


# ----------------------------------------------------------
# 6. Add Counties With Custom Colors and Tooltip
# ----------------------------------------------------------
for feature in counties["features"]:
    county_name = feature["properties"]["COUNTY"]    
    chs = county_lookup.get(county_name, 0)

    color = colormap(chs)

    folium.GeoJson(
        feature,
        style_function=lambda x, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.78
        },
        highlight_function=lambda x: {
            "weight": 3,
            "color": "#666",
            "fillOpacity": 0.9
        },
        tooltip=folium.Tooltip(f"{county_name}: {chs}")
    ).add_to(m)


# ----------------------------------------------------------
# 7. Add Legend to Map
# ----------------------------------------------------------
colormap.add_to(m)


# ----------------------------------------------------------
# 8. CSS hack to FORCE legend to bottom-left corner
# ----------------------------------------------------------
legend_css = '''
<style>
.colorbar, 
.branca-colormap, 
.legend {
    position: fixed !important;
    bottom: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;

    transform: scale(0.7);        /* ✅ Shrinks to 50% */
    transform-origin: bottom left;  /* ✅ Ensures shrinking stays anchored */

    background-color: white !important;
    padding: 10px !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}
</style>
'''

m.get_root().html.add_child(folium.Element(legend_css))


# ----------------------------------------------------------
# 9. Save HTML Map File
# ----------------------------------------------------------
m.save("texas_county_happiness_map.html")
print("✅ Map created: texas_county_happiness_map.html")
