import folium
import pandas as pd
import json
from branca.colormap import LinearColormap

# ----------------------------------------------------------
# 1. Load Updated County Scores CSV
# ----------------------------------------------------------
df = pd.read_csv("county_happiness_with_reddit_feedback_normalized.csv")

# Clean column names (removes accidental spaces)
df.columns = df.columns.str.strip()

# Ensure county name format matches GeoJSON
df["County"] = df["County"].str.strip() + " County"

# Build lookup dictionary
county_lookup = df.set_index("County")["HappinessScore"].to_dict()

# ----------------------------------------------------------
# 2. Load Texas County GeoJSON
# ----------------------------------------------------------
geojson_path = "tx_counties.geojson"
with open(geojson_path) as f:
    counties = json.load(f)

# ----------------------------------------------------------
# 3. Create Base Map
# ----------------------------------------------------------
m = folium.Map(
    location=[31.0, -99.0],
    zoom_start=5,
    tiles="cartodbpositron"
)

# ----------------------------------------------------------
# 4. T-Mobile Color Scale (unchanged)
# ----------------------------------------------------------
colors = ["#f2def0", "#ffd2fa", "#f7c1ea", "#f073c6", "#E20074"]
colormap = LinearColormap(colors, index=[0,25,50,75,100], vmin=0, vmax=100)
colormap.caption = "Customer Happiness Score"

# ----------------------------------------------------------
# 5. Add counties with coloring
# ----------------------------------------------------------
for feature in counties["features"]:
    county_name = feature["properties"]["COUNTY"]
    score = county_lookup.get(county_name)

    color = colormap(score) if score is not None else "#d9d9d9"

    folium.GeoJson(
        feature,
        style_function=lambda x, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.78,
        },
        highlight_function=lambda x: {
            "weight": 3,
            "color": "#666",
            "fillOpacity": 0.9,
        },
        tooltip=folium.Tooltip(f"{county_name}: {score if score is not None else 'No Data'}")
    ).add_to(m)

# ----------------------------------------------------------
# 6. Legend
# ----------------------------------------------------------
colormap.add_to(m)

# ----------------------------------------------------------
# 7. Styling Legend
# ----------------------------------------------------------
legend_css = '''
<style>
.colorbar, .branca-colormap, .legend {
    position: fixed !important;
    bottom: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
    transform: scale(0.7);
    transform-origin: bottom left;
    background-color: white !important;
    padding: 10px !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}
</style>
'''
m.get_root().html.add_child(folium.Element(legend_css))

# ----------------------------------------------------------
# 8. Save Map
# ----------------------------------------------------------
m.save("texas_county_happiness_map.html")
print("✅ Map updated successfully!")
