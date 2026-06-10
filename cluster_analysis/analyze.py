#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحليل منطقية تقسيم الكلاسترات (U11-U14) من حيث المسافة والوقت بين مراكز المدن.
المسافة على الطريق = مسافة الخط المستقيم (Haversine) * معامل التواء الطرق.
الوقت = تقدير بسرعات واقعية حسب طول الرحلة.
"""
import math, json

# ---------------------------------------------------------------------------
# إحداثيات مراكز المدن (lat, lon)
# ---------------------------------------------------------------------------
COORDS = {
    # Eastern Province
    "AlDammam": (26.4207, 50.0888), "AlDhahran": (26.2886, 50.1140),
    "AlKhobar": (26.2794, 50.2083), "Ras Tanura": (26.7000, 50.1628),
    "Bqaiq": (25.9344, 49.6677), "AlQatif": (26.5196, 50.0115),
    "Saihat": (26.4595, 50.0466), "Safwa": (26.6494, 49.9514),
    "AlJubail": (27.0046, 49.6583), "Aljarudiyah": (26.5536, 49.9856),
    "AlAhsa": (25.3833, 49.5867), "Mubarraz": (25.4119, 49.5917),
    "Hafar albatin": (28.4326, 45.9636), "AlQaisumah": (28.3090, 46.1270),
    "AlKhafji": (28.4392, 48.4914),
    # Riyadh
    "Riyadh": (24.7136, 46.6753), "AlMuzahmiyya": (24.4667, 46.2667),
    "AlKharj": (24.1556, 47.3120), "AlDilam": (23.9904, 47.1611),
    "Howtat Bani Tamim": (23.5226, 46.8460), "AlMajma'ah": (25.9039, 45.3450),
    "Al-Ghat": (26.0289, 44.9617), "AlZulfi": (26.2994, 44.8147),
    "AlQuway'iyah": (24.0500, 45.2667), "Afif": (23.9061, 42.9170),
    "AlDuwadimi": (24.5076, 44.3924), "Shaqra": (25.2439, 45.2520),
    "Wadi Aldwasir": (20.4581, 44.7919),
    # Makkah
    "Makkah": (21.3891, 39.8579), "Jeddah": (21.4858, 39.1925),
    "Taif": (21.2854, 40.4183), "AlQunfudhah": (19.1264, 41.0789),
    "AlLith": (20.1500, 40.2667),
    # Madinah
    "Madinah": (24.5247, 39.5692), "Yanbu": (24.0895, 38.0618),
    "AlUla": (26.6167, 37.9167),
    # Qassim
    "Buraidah": (26.3260, 43.9750), "Unaizah": (26.0843, 43.9935),
    "Al-Bukiryah": (26.1378, 43.6583), "Al-Badayea": (26.0167, 43.7667),
    "AlRass": (25.8694, 43.4972), "Al-Mithnab": (25.8667, 44.2167),
    "AlJewa": (25.9500, 44.1300), "AlKhabra": (26.1167, 43.5333),
    "AlAsayah": (26.4050, 43.9500), "Dukhnah": (26.0200, 43.4800),
    # Asir
    "Abha": (18.2169, 42.5053), "Khamis Mushait": (18.3000, 42.7333),
    "Ahad Rufaidah": (18.1936, 42.8500), "Sarat Abidah": (18.0500, 42.8800),
    "Rijal Almaa": (18.1989, 42.2961), "Muhail Aseer": (18.5500, 42.0500),
    "Al-Majardah": (19.1167, 41.9167), "Bisha": (19.9833, 42.6000),
    # Tabuk
    "Tabuk": (28.3838, 36.5550), "Tayma": (27.6333, 38.5500),
    # Hail
    "Hail": (27.5114, 41.7208),
    # Northern Borders
    "Arar": (30.9753, 41.0381), "Rafha": (29.6266, 43.4983),
    "Turaif": (31.6725, 38.6637),
    # Al-Jawf
    "Sakaka": (29.9697, 40.2064), "Dumat AlJandal": (29.8117, 39.8675),
    "Tabarjal": (30.4983, 38.2197),
    # Jazan
    "Jazan": (16.8892, 42.5611), "Abu Arish": (16.9689, 42.8328),
    "Sabya": (17.1494, 42.6258), "Samtah": (16.5969, 42.9456),
    "Ahad Al-Masarihah": (16.7100, 42.9550), "Baish": (17.3833, 42.5500),
    "Damad": (17.0667, 42.7000), "Al-Dayer": (17.3833, 43.0500),
    "Al-Darb": (17.7236, 42.2486), "Al-Shuqayq": (17.6917, 42.0500),
    "Faifa": (17.2500, 43.1000), "Farasan": (16.7000, 42.1167),
    # Najran
    "Najran": (17.4933, 44.1277), "Hubuna": (17.9389, 43.9656),
    "Khabash": (17.7000, 44.0000), "Sharura": (17.4869, 47.1167),
    # Al-Baha
    "AlBaha": (20.0129, 41.4677), "Al-Aqiq": (20.2667, 41.6500),
    "Al-Mandaq": (20.1667, 41.2833), "Al-Makhwah": (19.7667, 41.4333),
}

# ---------------------------------------------------------------------------
# تركيب الكلاسترات من ملف الإكسل
# ---------------------------------------------------------------------------
import pandas as pd
df = pd.read_excel("/root/.claude/uploads/96ed5203-3895-59d2-9405-1c6ffc5c13cf/ae7321fb-U11U14_Clusters.xlsx",
                   header=0).iloc[:, 1:]
df.columns = ["Region", "ClusterRaw", "City"]
df = df.dropna(subset=["City"])
df = df[df["City"] != "City"]

def cluster_key(s):
    # نطبّع "Cluster 5 (Based on logistics)" -> "Cluster 5"
    import re
    m = re.search(r"Cluster\s*\d+", str(s))
    return m.group(0) if m else str(s)

df["Cluster"] = df["ClusterRaw"].apply(cluster_key)
df["Note"] = df["ClusterRaw"].apply(lambda s: str(s).replace(cluster_key(s), "").strip(" -()") )

# ---------------------------------------------------------------------------
def haversine(a, b):
    R = 6371.0
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(h))

CIRCUITY = 1.30  # معامل التواء الطرق

def road_km(a, b):
    return haversine(a, b) * CIRCUITY

def drive_minutes(road):
    # سرعات فعّالة واقعية (تشمل الخروج/الدخول من المدن)
    if road >= 150:   v = 100
    elif road >= 80:  v = 90
    elif road >= 30:  v = 75
    else:             v = 50
    return road / v * 60

def fmt_time(mins):
    h = int(mins // 60); m = int(round(mins % 60))
    return (f"{h}س {m}د" if h else f"{m}د")

# ---------------------------------------------------------------------------
# تحليل كل كلاستر
# ---------------------------------------------------------------------------
missing = [c for c in df["City"] if c not in COORDS]
if missing:
    print("WARNING: missing coords:", missing)

clusters = {}
for cl, g in df.groupby("Cluster"):
    cities = list(g["City"])
    region = g["Region"].iloc[0]
    note = next((n for n in g["Note"] if n), "")
    clusters[cl] = {"region": region, "cities": cities, "note": note}

rows = []          # تفاصيل الأزواج
summary = []       # ملخص كل كلاستر
for cl, info in clusters.items():
    cities = info["cities"]
    pairs = []
    for i in range(len(cities)):
        for j in range(i+1, len(cities)):
            a, b = cities[i], cities[j]
            if a in COORDS and b in COORDS:
                d = road_km(COORDS[a], COORDS[b])
                t = drive_minutes(d)
                pairs.append((a, b, d, t))
                rows.append({"Cluster": cl, "Region": info["region"],
                             "From": a, "To": b,
                             "Road_km": round(d, 1), "Drive_min": round(t),
                             "Drive": fmt_time(t)})
    maxd = max((p[2] for p in pairs), default=0)
    maxt = max((p[3] for p in pairs), default=0)
    avgd = sum(p[2] for p in pairs)/len(pairs) if pairs else 0
    # المدينة الأبعد عن البقية
    summary.append({"Cluster": cl, "Region": info["region"],
                    "Cities": len(cities), "CityList": ", ".join(cities),
                    "MaxRoad_km": round(maxd, 1), "MaxDrive_min": round(maxt),
                    "MaxDrive": fmt_time(maxt), "AvgRoad_km": round(avgd, 1),
                    "Note": info["note"]})

sum_df = pd.DataFrame(summary)
def cl_num(c):
    import re; return int(re.search(r"\d+", c).group())
sum_df = sum_df.sort_values("Cluster", key=lambda s: s.map(cl_num)).reset_index(drop=True)
pair_df = pd.DataFrame(rows)

# تقييم منطقية: عتبة الوقت 90 دقيقة للذهاب بين أبعد مدينتين تعتبر معقولة لفئة ناشئين
def verdict(mt, n):
    if n == 1: return "مدينة واحدة"
    if mt <= 60:  return "ممتاز"
    if mt <= 90:  return "جيد"
    if mt <= 150: return "مقبول/مراجعة"
    return "بعيد - يُفضّل الفصل"
sum_df["Verdict"] = [verdict(m, n) for m, n in zip(sum_df["MaxDrive_min"], sum_df["Cities"])]

with pd.ExcelWriter("/home/user/khitba/cluster_analysis/cluster_distances.xlsx") as xw:
    sum_df.to_excel(xw, sheet_name="Summary", index=False)
    pair_df.to_excel(xw, sheet_name="Pairwise", index=False)

print(sum_df.to_string())
print("\nTotal cities:", len(df), "Clusters:", len(clusters))

# حفظ JSON للخريطة
out = {"clusters": clusters, "coords": COORDS,
       "summary": sum_df.to_dict(orient="records"),
       "pairs": pair_df.to_dict(orient="records")}
with open("/home/user/khitba/cluster_analysis/data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
