#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يجلب المدة والمسافة الحقيقية من Google Distance Matrix API لكل أزواج المدن
داخل كل كلاستر، ثم يحدّث الإكسل والـ JSON المستخدم في الخريطة.

التشغيل:
    GOOGLE_MAPS_API_KEY=xxxx python3 cluster_analysis/google_durations.py
"""
import os, json, time, math, urllib.parse, urllib.request

KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
if not KEY:
    raise SystemExit("ضع المفتاح في المتغير GOOGLE_MAPS_API_KEY")

D = json.load(open("/home/user/khitba/cluster_analysis/data.json", encoding="utf-8"))
clusters, COORDS = D["clusters"], D["coords"]

BASE = "https://maps.googleapis.com/maps/api/distancematrix/json"

def gmaps(origin, dest):
    """origin/dest = (lat,lon) -> (meters, seconds) أو (None,None)."""
    params = {
        "origins": f"{origin[0]},{origin[1]}",
        "destinations": f"{dest[0]},{dest[1]}",
        "mode": "driving", "language": "ar", "region": "sa", "key": KEY,
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                j = json.load(r)
            if j.get("status") != "OK":
                raise RuntimeError(j.get("error_message", j.get("status")))
            el = j["rows"][0]["elements"][0]
            if el.get("status") != "OK":
                return None, None
            return el["distance"]["value"], el["duration"]["value"]
        except Exception as e:
            if attempt == 3:
                print("  ! error:", e); return None, None
            time.sleep(2 ** attempt)

def fmt_time(sec):
    if sec is None: return ""
    m = round(sec / 60); h, m = divmod(m, 60)
    return f"{h}س {m}د" if h else f"{m}د"

import re
def cl_num(c): return int(re.search(r"\d+", c).group())

rows, summary = [], []
seen = {}  # كاش لتفادي تكرار نفس الزوج
for cl in sorted(clusters, key=cl_num):
    info = clusters[cl]; cities = info["cities"]
    print(f"{cl} ({len(cities)} مدن)...")
    pairs = []
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            a, b = cities[i], cities[j]
            k = tuple(sorted((a, b)))
            if k in seen:
                meters, secs = seen[k]
            else:
                meters, secs = gmaps(COORDS[a], COORDS[b])
                seen[k] = (meters, secs)
                time.sleep(0.05)
            if meters is None:
                print(f"   تعذّر: {a} ↔ {b} (قد تكون جزيرة/لا طريق)")
                continue
            km = round(meters / 1000, 1)
            pairs.append((km, secs))
            rows.append({"Cluster": cl, "Region": info["region"], "From": a, "To": b,
                         "Google_km": km, "Google_min": round(secs / 60),
                         "Google_time": fmt_time(secs)})
    maxd = max((p[0] for p in pairs), default=0)
    maxt = max((p[1] for p in pairs), default=0)
    avgd = round(sum(p[0] for p in pairs) / len(pairs), 1) if pairs else 0
    summary.append({"Cluster": cl, "Region": info["region"], "Cities": len(cities),
                    "CityList": ", ".join(cities),
                    "MaxRoad_km": maxd, "MaxDrive_min": round(maxt / 60),
                    "MaxDrive": fmt_time(maxt), "AvgRoad_km": avgd,
                    "Note": clusters[cl].get("note", "")})

def verdict(mt_min, n):
    if n == 1: return "مدينة واحدة"
    if mt_min <= 60: return "ممتاز"
    if mt_min <= 90: return "جيد"
    if mt_min <= 150: return "مقبول/مراجعة"
    return "بعيد - يُفضّل الفصل"
for s in summary:
    s["Verdict"] = verdict(s["MaxDrive_min"], s["Cities"])

import pandas as pd
sum_df, pair_df = pd.DataFrame(summary), pd.DataFrame(rows)
with pd.ExcelWriter("/home/user/khitba/cluster_analysis/cluster_distances_google.xlsx") as xw:
    sum_df.to_excel(xw, sheet_name="Summary", index=False)
    pair_df.to_excel(xw, sheet_name="Pairwise", index=False)

# تحديث data.json (مع علم أن المصدر قوقل) لإعادة بناء الخريطة
D["summary"] = sum_df.to_dict(orient="records")
D["pairs"] = [{"Cluster": r["Cluster"], "From": r["From"], "To": r["To"],
               "Road_km": r["Google_km"], "Drive_min": r["Google_min"],
               "Drive": r["Google_time"]} for r in rows]
D["source"] = "google"
json.dump(D, open("/home/user/khitba/cluster_analysis/data.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nتم. عدد طلبات قوقل:", len(seen))
print(sum_df[["Cluster", "Cities", "MaxDrive", "Verdict"]].to_string())
