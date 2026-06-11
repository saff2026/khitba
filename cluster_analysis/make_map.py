#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""بناء خريطة تفاعلية للكلاسترات."""
import json, math
import folium
from folium.plugins import Fullscreen

D = json.load(open("/home/user/khitba/cluster_analysis/data.json", encoding="utf-8"))
clusters, COORDS = D["clusters"], D["coords"]
summary = {s["Cluster"]: s for s in D["summary"]}
pairs = D["pairs"]

VERDICT_COLOR = {
    "ممتاز": "#1a9850", "جيد": "#66bd63", "مدينة واحدة": "#878787",
    "مقبول/مراجعة": "#fdae61", "بعيد - يُفضّل الفصل": "#d73027",
}

# لون مميز لكل كلاستر للنقاط
PALETTE = ["#e6194B","#3cb44b","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6",
           "#bfef45","#fabed4","#469990","#dcbeff","#9A6324","#800000","#aaffc3",
           "#808000","#ffd8b1","#000075","#a9a9a9","#e6beff","# fffac8".replace(" ",""),
           "#ff4500","#2e8b57","#1e90ff","#daa520","#c71585","#008080","#8b4513"]

def haversine(a,b):
    R=6371.0; lat1,lon1=map(math.radians,a); lat2,lon2=map(math.radians,b)
    dlat,dlon=lat2-lat1,lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(h))

m = folium.Map(location=[24.0, 45.0], zoom_start=6, tiles="OpenStreetMap",
               control_scale=True)
Fullscreen(position="topleft").add_to(m)

import re
def cl_num(c): return int(re.search(r"\d+", c).group())
ordered = sorted(clusters.keys(), key=cl_num)

# خطوط الأزواج داخل كل كلاستر (في طبقة)
pair_layer = folium.FeatureGroup(name="خطوط المسافة/الوقت", show=True).add_to(m)
for p in pairs:
    a, b = COORDS[p["From"]], COORDS[p["To"]]
    s = summary[p["Cluster"]]
    col = VERDICT_COLOR.get(s["Verdict"], "#555")
    folium.PolyLine([a, b], color=col, weight=2, opacity=0.55,
        tooltip=f"{p['From']} ↔ {p['To']}: {p['Road_km']} كم / {p['Drive']}").add_to(pair_layer)

# النقاط
for idx, cl in enumerate(ordered):
    info = clusters[cl]; s = summary[cl]
    color = PALETTE[idx % len(PALETTE)]
    fg = folium.FeatureGroup(name=f"{cl} ({info['region']}) — {s['Verdict']}", show=True).add_to(m)
    for city in info["cities"]:
        lat, lon = COORDS[city]
        popup = (f"<div style='direction:rtl;font-family:Tajawal,sans-serif'>"
                 f"<b>{city}</b><br>الكلاستر: {cl}<br>المنطقة: {info['region']}<br>"
                 f"أقصى مسافة بالكلاستر: {s['MaxRoad_km']} كم<br>"
                 f"أقصى زمن قيادة: {s['MaxDrive']}<br>"
                 f"التقييم: <b>{s['Verdict']}</b></div>")
        folium.CircleMarker(
            [lat, lon], radius=7, color="#222", weight=1,
            fill=True, fill_color=color, fill_opacity=0.95,
            popup=folium.Popup(popup, max_width=260),
            tooltip=f"{city} — {cl}").add_to(fg)
        folium.map.Marker([lat, lon],
            icon=folium.DivIcon(html=f"<div style='font-size:10px;color:#111;font-weight:bold;"
                 f"text-shadow:0 0 3px #fff,0 0 3px #fff;white-space:nowrap'>{city}</div>",
                 icon_anchor=(-6, 8))).add_to(fg)

folium.LayerControl(collapsed=True).add_to(m)

# وسيلة إيضاح
legend = """
<div style="position:fixed;bottom:20px;right:20px;z-index:9999;background:#fff;
 padding:12px 14px;border:1px solid #999;border-radius:8px;direction:rtl;
 font-family:Tajawal,Arial,sans-serif;font-size:13px;box-shadow:0 2px 8px rgba(0,0,0,.2)">
 <b>تقييم الكلاستر (حسب أقصى زمن قيادة بين مدينتين)</b><br>
 <span style="color:#1a9850">●</span> ممتاز (≤ ساعة)<br>
 <span style="color:#66bd63">●</span> جيد (≤ ساعة ونصف)<br>
 <span style="color:#fdae61">●</span> مقبول/مراجعة (≤ ساعتين ونصف)<br>
 <span style="color:#d73027">●</span> بعيد — يُفضّل الفصل (&gt; ساعتين ونصف)<br>
 <span style="color:#878787">●</span> مدينة واحدة<br>
 <hr style="margin:6px 0">
 <small>المسافات والأزمنة <b>حقيقية من Google Maps</b> (Distance Matrix API، وضع القيادة).</small>
</div>"""
m.get_root().html.add_child(folium.Element(legend))

title = """
<div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;
 background:#0a3d62;color:#fff;padding:8px 18px;border-radius:8px;
 font-family:Tajawal,Arial,sans-serif;font-size:16px;font-weight:bold;
 box-shadow:0 2px 8px rgba(0,0,0,.3)">خريطة كلاسترات المدن U11–U14 — مسافات وأزمنة Google Maps</div>"""
m.get_root().html.add_child(folium.Element(title))

m.save("/home/user/khitba/cluster_analysis/clusters_map.html")
print("Saved clusters_map.html")
