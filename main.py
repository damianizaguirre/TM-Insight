import folium
import pandas as pd
import json

# -------------------------------------
# 1. Load Your CHS County Data
# -------------------------------------
df = pd.read_csv("texas_county_chs.csv")  # county, chs


# -------------------------------------
# 2. Load Texas County GeoJSON
# -------------------------------------
geojson_path = "tx_counties.geojson"

with open(geojson_path) as f:
    counties = json.load(f)


# -------------------------------------
# 3. Create Base Map (Texas Center)
# -------------------------------------
m = folium.Map(
    location=[31.0, -99.0],  # geographic center of Texas
    zoom_start=6,
    tiles="cartodbpositron"
)


# -------------------------------------
# 4. Add Choropleth Layer
# -------------------------------------
folium.Choropleth(
    geo_data=counties,
    name="Texas County CHS",
    data=df,
    columns=["county", "chs"],
    key_on="feature.properties.COUNTY",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name="Customer Happiness Score (0–100)"
).add_to(m)


# -------------------------------------
# 5. Add Hover Tooltips for Each County
# -------------------------------------
county_lookup = df.set_index("county")["chs"].to_dict()

for feature in counties["features"]:
    county_name = feature["properties"]["COUNTY"]    # ✅ FIXED
    chs = county_lookup.get(county_name, "No Data")  # ✅ FIXED

    folium.GeoJson(
        feature,
        style_function=lambda x: {"fillOpacity": 0, "weight": 0},
        tooltip=folium.Tooltip(f"{county_name}: {chs}")
    ).add_to(m)


# -------------------------------------
# 6. Save the Map
# -------------------------------------
m.save("texas_county_happiness_map.html")
print("✅ Map created: texas_county_happiness_map.html")
