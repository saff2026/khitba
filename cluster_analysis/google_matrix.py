#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""حساب مصفوفة المسافة/الزمن الحقيقية من Google Distance Matrix API لكل أزواج النقاط."""
import os, json, time, urllib.parse, urllib.request

KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
if not KEY:
    raise SystemExit("ضع المفتاح في GOOGLE_MAPS_API_KEY")

P = json.load(open("/home/user/khitba/cluster_analysis/points.json", encoding="utf-8"))
n = len(P)
coord = [f'{p["lat"]},{p["lon"]}' for p in P]
name = [p["n"] for p in P]
BASE = "https://maps.googleapis.com/maps/api/distancematrix/json"

# استئناف من ملف سابق إن وجد
OUT = "/home/user/khitba/cluster_analysis/matrix.json"
matrix = {}
if os.path.exists(OUT):
    matrix = json.load(open(OUT, encoding="utf-8"))
    print("استئناف، موجود:", len(matrix))

def key(a, b):
    return "|".join(sorted((a, b)))

def req(origin_idx, dest_idxs):
    params = {
        "origins": coord[origin_idx],
        "destinations": "|".join(coord[j] for j in dest_idxs),
        "mode": "driving", "key": KEY,
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                j = json.load(r)
            if j.get("status") != "OK":
                raise RuntimeError(j.get("error_message", j.get("status")))
            return j["rows"][0]["elements"]
        except Exception as e:
            if attempt == 4:
                print("  ! err:", e); return None
            time.sleep(2 ** attempt)

CHUNK = 25
done_elems = 0
for i in range(n):
    rem = [j for j in range(i + 1, n) if key(name[i], name[j]) not in matrix]
    for s in range(0, len(rem), CHUNK):
        block = rem[s:s + CHUNK]
        els = req(i, block)
        if els is None:
            continue
        for j, el in zip(block, els):
            if el.get("status") == "OK":
                matrix[key(name[i], name[j])] = {
                    "km": round(el["distance"]["value"] / 1000, 1),
                    "sec": el["duration"]["value"]}
            else:
                matrix[key(name[i], name[j])] = None  # لا يوجد مسار بري
        done_elems += len(block)
        time.sleep(0.05)
    if i % 15 == 0:
        json.dump(matrix, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  i={i}/{n} عناصر مُنجزة={len(matrix)}")

json.dump(matrix, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
none_cnt = sum(1 for v in matrix.values() if v is None)
print("تم. إجمالي أزواج:", len(matrix), "| بدون مسار بري:", none_cnt)
