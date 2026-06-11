#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""إعادة حساب صفوف المصفوفة للنقاط المصحّحة فقط."""
import os, json, time, urllib.parse, urllib.request
KEY = os.environ["GOOGLE_MAPS_API_KEY"]
CORR = ["الأحساء","النعيرية","تبوك","حائل","الباحة","العقيق","رجال ألمع","الأسياح"]

P = json.load(open("/home/user/khitba/cluster_analysis/points.json", encoding="utf-8"))
coord = {p["n"]: f'{p["lat"]},{p["lon"]}' for p in P}
names = [p["n"] for p in P]
M = json.load(open("/home/user/khitba/cluster_analysis/matrix.json", encoding="utf-8"))
BASE = "https://maps.googleapis.com/maps/api/distancematrix/json"
def key(a,b): return "|".join(sorted((a,b)))
def req(o, ds):
    params={"origins":coord[o],"destinations":"|".join(coord[d] for d in ds),
            "mode":"driving","key":KEY}
    url=BASE+"?"+urllib.parse.urlencode(params)
    for a in range(5):
        try:
            j=json.load(urllib.request.urlopen(url,timeout=30))
            if j.get("status")!="OK": raise RuntimeError(j.get("error_message",j["status"]))
            return j["rows"][0]["elements"]
        except Exception as e:
            if a==4: print("err",e); return None
            time.sleep(2**a)

upd=0
for name in CORR:
    others=[x for x in names if x!=name]
    for s in range(0,len(others),25):
        blk=others[s:s+25]
        els=req(name,blk)
        if not els: continue
        for d,el in zip(blk,els):
            M[key(name,d)] = ({"km":round(el["distance"]["value"]/1000,1),
                               "sec":el["duration"]["value"]}
                              if el.get("status")=="OK" else None)
            upd+=1
        time.sleep(0.05)
    print("  حُدّث:",name)
json.dump(M,open("/home/user/khitba/cluster_analysis/matrix.json","w",encoding="utf-8"),ensure_ascii=False)
print("تم. أزواج محدّثة:",upd,"| إجمالي:",len(M))
