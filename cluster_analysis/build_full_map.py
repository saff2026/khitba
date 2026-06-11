#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""خريطة شاملة: كل المحافظات + المجموعات + أداة قياس المسافة بين أي مدينتين."""
import json, re

recs = json.load(open("/home/user/khitba/cluster_analysis/governorates_geo.json"))["records"]
D = json.load(open("/home/user/khitba/cluster_analysis/data.json"))
clusters = D["clusters"]; COORDS = D["coords"]
summary = {s["Cluster"]: s for s in D["summary"]}
pairs = D["pairs"]

# خريطة اسم المدينة (إنجليزي بملف الكلاستر) -> الاسم العربي بجدول المحافظات
EN2AR = {
 "AlDammam":"الدمام","AlDhahran":"الظهران","AlKhobar":"الخبر","Ras Tanura":"رأس تنورة",
 "Bqaiq":"بقيق","AlQatif":"القطيف","Saihat":"صيهات","Safwa":"صفوى","AlJubail":"الجبيل",
 "Aljarudiyah":"الجارودية","AlAhsa":"الأحساء","Mubarraz":"المبرز","Hafar albatin":"حفر الباطن",
 "AlQaisumah":"القيصومة","AlKhafji":"الخفجي","Riyadh":"الرياض","AlMuzahmiyya":"المزاحمية",
 "AlKharj":"الخرج","AlDilam":"الدلم","Howtat Bani Tamim":"حوطة بني تميم","AlMajma'ah":"المجمعة",
 "Al-Ghat":"الغاط","AlZulfi":"الزلفي","AlQuway'iyah":"القويعية","Afif":"عفيف","AlDuwadimi":"الدوادمي",
 "Shaqra":"شقراء","Wadi Aldwasir":"وادي الدواسر","Makkah":"مكة المكرمة","Jeddah":"جدة","Taif":"الطائف",
 "AlQunfudhah":"القنفذة","AlLith":"الليث","Madinah":"المدينة المنورة","Yanbu":"ينبع","AlUla":"العلا",
 "Buraidah":"بريدة","Unaizah":"عنيزة","Al-Bukiryah":"البكيرية","Al-Badayea":"البدائع","AlRass":"الرس",
 "Al-Mithnab":"المذنب","AlJewa":"الجوا","AlKhabra":"الخبراء","AlAsayah":"الأسياح","Dukhnah":"دخنة",
 "Abha":"أبها","Khamis Mushait":"خميس مشيط","Ahad Rufaidah":"أحد رفيدة","Sarat Abidah":"سراة عبيدة",
 "Rijal Almaa":"رجال ألمع","Muhail Aseer":"محايل عسير","Al-Majardah":"المجاردة","Bisha":"بيشة",
 "Tabuk":"تبوك","Tayma":"تيماء","Hail":"حائل","Arar":"عرعر","Rafha":"رفحاء","Turaif":"طريف",
 "Sakaka":"سكاكا","Dumat AlJandal":"دومة الجندل","Tabarjal":"طبرجل","Jazan":"جازان","Abu Arish":"أبو عريش",
 "Sabya":"صبيا","Samtah":"صامطة","Ahad Al-Masarihah":"أحد المسارحة","Baish":"بيش","Damad":"ضمد",
 "Al-Dayer":"الدائر","Al-Darb":"الدرب","Al-Shuqayq":"الشقيق","Faifa":"فيفاء","Farasan":"فرسان",
 "Najran":"نجران","Hubuna":"حبونا","Khabash":"خباش","Sharura":"شرورة","AlBaha":"الباحة",
 "Al-Aqiq":"العقيق","Al-Mandaq":"المندق","Al-Makhwah":"المخواة",
}

def cl_num(c): return int(re.search(r"\d+", c).group())
ordered = sorted(clusters, key=cl_num)
PALETTE = ["#e6194B","#3cb44b","#4363d8","#f58231","#911eb4","#1ab2c4","#f032e6",
           "#9A6324","#469990","#800000","#808000","#000075","#e07b00","#2e8b57",
           "#c71585","#1e90ff","#b8860b","#008080","#8b008b","#556b2f","#ff4500",
           "#4682b4","#a0522d","#6a5acd","#d2691e","#008b45","#cd5c5c"]
CL_COLOR = {cl: PALETTE[i % len(PALETTE)] for i, cl in enumerate(ordered)}
VERDICT_COLOR = {"ممتاز":"#1a9850","جيد":"#66bd63","مدينة واحدة":"#878787",
                 "مقبول/مراجعة":"#f59e0b","بعيد - يُفضّل الفصل":"#d73027"}

# نقطة لكل مدينة: نبدأ من جدول المحافظات (154) ونضيف مدن الكلاستر غير الموجودة
points = {}   # name_ar -> {lat,lon,region,cat,cluster}
for r in recs:
    points[r["name"]] = {"lat": r["lat"], "lon": r["lon"], "region": r["region"],
                         "cat": r["cat"], "cluster": None}

# ربط المجموعات
cluster_members = {cl: [] for cl in ordered}
for cl in ordered:
    for city_en in clusters[cl]["cities"]:
        ar = EN2AR.get(city_en, city_en)
        if ar not in points:                      # مدينة كلاستر ليست محافظة مستقلة
            lat, lon = COORDS[city_en]
            points[ar] = {"lat": lat, "lon": lon, "region": clusters[cl]["region"],
                          "cat": "مجموعة", "cluster": None}
        cluster_members[cl].append(ar)

# تعداد سكاني تقريبي (بالآلاف) لاختيار أكبر مدينة تكون اسم الكلاستر
POP = {
 "الدمام":1250,"الظهران":240,"الخبر":410,"رأس تنورة":95,"بقيق":50,
 "الجبيل":470,"القطيف":110,"صيهات":95,"صفوى":50,"الجارودية":20,
 "الأحساء":660,"المبرز":290,"حفر الباطن":390,"القيصومة":30,"الخفجي":100,
 "الرياض":7000,"المزاحمية":45,"الخرج":380,"الدلم":40,"حوطة بني تميم":25,
 "المجمعة":75,"الغاط":20,"الزلفي":70,"القويعية":53,"عفيف":65,"الدوادمي":73,
 "شقراء":40,"وادي الدواسر":106,"مكة المكرمة":2040,"جدة":4000,"الطائف":690,
 "القنفذة":78,"الليث":72,"المدينة المنورة":1490,"ينبع":330,"العلا":60,
 "بريدة":670,"عنيزة":180,"البكيرية":70,"البدائع":50,"الرس":133,"المذنب":60,
 "الجوا":15,"الخبراء":30,"الأسياح":30,"دخنة":10,"أبها":510,"خميس مشيط":630,
 "أحد رفيدة":90,"سراة عبيدة":60,"رجال ألمع":60,"محايل عسير":100,"المجاردة":50,
 "بيشة":110,"تبوك":670,"تيماء":65,"حائل":480,"عرعر":210,"رفحاء":90,"طريف":50,
 "سكاكا":250,"دومة الجندل":50,"طبرجل":60,"جازان":170,"أبو عريش":160,"صبيا":230,
 "صامطة":90,"أحد المسارحة":60,"بيش":80,"ضمد":40,"الدائر":30,"الدرب":50,
 "الشقيق":30,"فيفاء":60,"فرسان":18,"نجران":380,"حبونا":30,"خباش":20,"شرورة":85,
 "الباحة":110,"العقيق":40,"المندق":30,"المخواة":60,
}
import os
_mp = "/home/user/khitba/cluster_analysis/matrix.json"
MX = json.load(open(_mp, encoding="utf-8")) if os.path.exists(_mp) else {}
def _sec(a, b):
    if a == b: return 0
    for k in (a + "|" + b, b + "|" + a):
        if k in MX:
            v = MX[k]; return v["sec"] if v else 9e9
    return 9e9
def fmt_t(sec):
    if sec >= 9e8: return "—"
    m = round(sec / 60); h, m = divmod(m, 60)
    return (f"{h}س {m}د" if h else f"{m}د")
def name_for(cities):
    if len(cities) == 1:
        return "مجموعة " + cities[0]
    rank_pop = {c: i for i, c in enumerate(sorted(cities, key=lambda c: -POP.get(c, 0)))}
    avg = {c: sum(_sec(c, o) for o in cities if o != c) / (len(cities) - 1) for c in cities}
    rank_cen = {c: i for i, c in enumerate(sorted(cities, key=lambda c: avg[c]))}
    best = min(cities, key=lambda c: (rank_pop[c] + rank_cen[c], -POP.get(c, 0)))
    return "مجموعة " + best
def verdict_of(maxsec, n):
    if n <= 1: return "مدينة واحدة"
    m = maxsec / 60
    if m <= 60: return "ممتاز"
    if m <= 90: return "جيد"
    if m <= 150: return "مقبول/مراجعة"
    return "بعيد - يُفضّل الفصل"
def cluster_maxsec(cities):
    mx = 0
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            s = _sec(cities[i], cities[j])
            if s < 9e8 and s > mx: mx = s
    return mx
def build_dataset(groups):
    out = []
    for i, (region, cities_en) in enumerate(groups):
        cities = [EN2AR.get(c, c) for c in cities_en]
        mx = cluster_maxsec(cities)
        v = verdict_of(mx, len(cities))
        out.append({"id": name_for(cities), "region": region, "color": PALETTE[i % len(PALETTE)],
                    "verdict": v, "vcolor": VERDICT_COLOR.get(v, "#888"),
                    "maxdrive": fmt_t(mx) if len(cities) > 1 else "—", "cities": cities})
    ids = [c["id"] for c in out]
    assert len(set(ids)) == len(ids), "أسماء مكررة: " + str([x for x in ids if ids.count(x) > 1])
    return out

# تجميعة 11-14 (من ملف المجموعات الأصلي)
groups_1114 = [(clusters[cl]["region"], clusters[cl]["cities"]) for cl in ordered]
# تجميعة 5-9 (من الجدول الجديد — نفس المدن بتجميع أدق)
groups_59 = [
 ("Eastern Province", ["AlDammam","AlDhahran","AlKhobar","AlQatif","Saihat","Safwa","Aljarudiyah"]),
 ("Eastern Province", ["AlAhsa","Mubarraz"]),
 ("Eastern Province", ["AlJubail"]),
 ("Eastern Province", ["Ras Tanura"]),
 ("Eastern Province", ["Bqaiq"]),
 ("Eastern Province", ["Hafar albatin","AlQaisumah"]),
 ("Eastern Province", ["AlKhafji"]),
 ("Riyadh Region", ["Riyadh"]),
 ("Riyadh Region", ["AlKharj","AlDilam"]),
 ("Riyadh Region", ["AlMuzahmiyya"]),
 ("Riyadh Region", ["Howtat Bani Tamim"]),
 ("Riyadh Region", ["AlMajma'ah"]),
 ("Riyadh Region", ["Al-Ghat"]),
 ("Riyadh Region", ["AlZulfi"]),
 ("Riyadh Region", ["AlQuway'iyah"]),
 ("Riyadh Region", ["Afif"]),
 ("Riyadh Region", ["AlDuwadimi"]),
 ("Riyadh Region", ["Shaqra"]),
 ("Riyadh Region", ["Wadi Aldwasir"]),
 ("Makkah Region", ["Makkah"]),
 ("Makkah Region", ["Jeddah"]),
 ("Makkah Region", ["Taif"]),
 ("Makkah Region", ["AlQunfudhah"]),
 ("Makkah Region", ["AlLith"]),
 ("Madinah Region", ["Madinah"]),
 ("Madinah Region", ["Yanbu"]),
 ("Madinah Region", ["AlUla"]),
 ("Al-Qassim Region", ["Buraidah","Unaizah"]),
 ("Al-Qassim Region", ["Al-Bukiryah","Al-Badayea","AlKhabra"]),
 ("Al-Qassim Region", ["AlRass"]),
 ("Al-Qassim Region", ["Al-Mithnab"]),
 ("Al-Qassim Region", ["AlJewa","AlAsayah","Dukhnah"]),
 ("Asir Region", ["Abha","Khamis Mushait"]),
 ("Asir Region", ["Ahad Rufaidah"]),
 ("Asir Region", ["Muhail Aseer"]),
 ("Asir Region", ["Rijal Almaa","Sarat Abidah"]),
 ("Asir Region", ["Al-Majardah"]),
 ("Asir Region", ["Bisha"]),
 ("Tabuk Region", ["Tabuk"]),
 ("Tabuk Region", ["Tayma"]),
 ("Hail Region", ["Hail"]),
 ("Northern Borders", ["Arar"]),
 ("Northern Borders", ["Rafha"]),
 ("Northern Borders", ["Turaif"]),
 ("Al-Jawf Region", ["Sakaka"]),
 ("Al-Jawf Region", ["Dumat AlJandal"]),
 ("Al-Jawf Region", ["Tabarjal"]),
 ("Jazan Region", ["Jazan","Ahad Al-Masarihah"]),
 ("Jazan Region", ["Abu Arish","Samtah"]),
 ("Jazan Region", ["Sabya","Damad"]),
 ("Jazan Region", ["Baish"]),
 ("Jazan Region", ["Al-Dayer","Al-Darb","Al-Shuqayq"]),
 ("Jazan Region", ["Faifa"]),
 ("Jazan Region", ["Farasan"]),
 ("Najran Region", ["Najran"]),
 ("Najran Region", ["Hubuna","Khabash"]),
 ("Najran Region", ["Sharura"]),
 ("Al-Baha Region", ["AlBaha"]),
 ("Al-Baha Region", ["Al-Aqiq"]),
 ("Al-Baha Region", ["Al-Mandaq"]),
 ("Al-Baha Region", ["Al-Makhwah"]),
]
DATASETS = {"11-14": build_dataset(groups_1114), "5-9": build_dataset(groups_59)}

matrix = MX
print("مصفوفة قوقل محمّلة:", len(matrix), "زوج")
print("مجموعات 11-14:", len(DATASETS["11-14"]), "| مجموعات 5-9:", len(DATASETS["5-9"]))

P = [{"n": n, "lat": v["lat"], "lon": v["lon"], "region": v["region"],
      "cat": v["cat"]} for n, v in points.items()]
DATA = {"points": P, "datasets": DATASETS, "vcolor": VERDICT_COLOR, "matrix": matrix}

json.dump(P, open("/home/user/khitba/cluster_analysis/points.json", "w", encoding="utf-8"),
          ensure_ascii=False)
print("نقاط على الخريطة:", len(P), "| محافظات الجدول:", len(recs),
      "| مدن كلاستر إضافية:", len(P) - len(recs))
missing_tbl = [n for n in points if points[n]["cat"] != "مجموعة"]
print("كل محافظات الجدول مرسومة:", len(missing_tbl) == len(recs))

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>خريطة محافظات المملكة — المجموعات وقياس المسافات</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif}
 .leaflet-container{font-family:'Tajawal',sans-serif}
 #wrap{display:flex;height:100vh}
 #side{width:340px;background:#0f2540;color:#e9eef5;overflow-y:auto;flex-shrink:0}
 #map{flex:1}
 .hd{background:#0a3d62;padding:12px 14px;font-weight:bold;font-size:15px;position:sticky;top:0;z-index:5}
 .sec{padding:10px 14px;border-bottom:1px solid #1c3a5e}
 .sec h3{margin:0 0 8px;font-size:14px;color:#ffd166}
 select,button,input{width:100%;padding:8px;border-radius:6px;border:1px solid #2a4a6e;
   background:#16314f;color:#fff;font-size:13px;margin-bottom:6px}
 button{background:#1b6ca8;cursor:pointer;font-weight:bold} button:hover{background:#2980b9}
 .gmaps{background:#2e7d32} .gmaps:hover{background:#388e3c}
 .dsbtn{flex:1;background:#16314f;border:1px solid #2a4a6e;font-size:14px}
 .dsbtn.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 .res{background:#16314f;border-radius:6px;padding:8px;font-size:13px;line-height:1.7}
 .res b{color:#ffd166}
 .cl{padding:7px 9px;border-radius:6px;margin-bottom:5px;cursor:pointer;background:#16314f;
   border-right:5px solid #888;font-size:12.5px}
 .cl:hover{background:#1d3e63} .cl .v{float:left;font-size:11px;padding:1px 6px;border-radius:10px;color:#fff}
 .cl .cbx{float:right;width:auto;margin:2px 6px 0 0;cursor:pointer}
 .cl .ct{color:#aac4e0;font-size:11px;margin-top:3px}
 .lbl{font-size:11px;color:#111;font-weight:bold;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff}
 .leg{background:#16314f;font-size:11.5px;line-height:1.8}
 small{color:#9fb6d0}
</style></head><body>
<div id="wrap">
 <div id="side">
  <div class="hd">🗺️ محافظات المملكة — المجموعات وقياس المسافات</div>

  <div class="sec" style="display:flex;gap:8px">
   <button id="btn1114" class="dsbtn on" onclick="switchDataset('11-14')">تحت 11 – 14</button>
   <button id="btn59" class="dsbtn" onclick="switchDataset('5-9')">تحت 5 – 9</button>
  </div>

  <div class="sec">
   <h3>📏 قياس المسافة بين مدينتين</h3>
   <select id="pa"></select>
   <select id="pb"></select>
   <div class="res" id="dres">اختر مدينتين لعرض المسافة.</div>
   <button class="gmaps" id="gbtn" onclick="openGmaps()">افتح المسار في قوقل مابس ↗</button>
   <small>المسافة والزمن بالأعلى <b>حقيقية من قوقل مابس</b> (محسوبة مسبقًا لكل الأزواج). الزر يفتح المسار المباشر للتأكد/الازدحام اللحظي.</small>
  </div>

  <div class="sec">
   <h3>✏️ تعديل المجموعات</h3>
   <select id="ecity"></select>
   <select id="etarget"></select>
   <button onclick="moveCity()">↪️ نقل المدينة للمجموعة المحددة</button>
   <div class="res" id="estat">اختر مدينة، ثم مجموعة الوجهة (أو «مجموعة جديدة»)، واضغط نقل. كل شيء يتحدّث فورًا.</div>
   <hr style="border-color:#1c3a5e">
   <h3 style="margin-top:4px">✒️ إعادة تسمية مجموعة</h3>
   <select id="rcl"></select>
   <input id="rname" placeholder="الاسم الجديد للمجموعة" />
   <button onclick="renameCluster()">✒️ تغيير الاسم</button>
   <button class="gmaps" onclick="exportCsv()">⬇️ تصدير التقسيمة المعدّلة (CSV)</button>
  </div>

  <div class="sec">
   <h3>🎛️ خيارات العرض</h3>
   <label><input type="checkbox" id="names" onchange="toggleNames()"> إظهار أسماء كل المدن</label><br>
   <label><input type="checkbox" id="lines" checked onchange="toggleLines()"> خطوط المجموعات</label>
  </div>

  <div class="sec"><h3>📋 المجموعات (✓ للإظهار · اضغط الصف للتمييز)</h3>
   <div style="display:flex;gap:6px">
     <button style="flex:1" onclick="showAll(true)">إظهار الكل</button>
     <button style="flex:1" onclick="showAll(false)">إخفاء الكل</button>
   </div>
   <label style="font-size:12px;display:block;margin-bottom:6px"><input type="checkbox" id="vnone" checked onchange="toggleNone()" style="width:auto"> إظهار المحافظات خارج المجموعات</label>
   <div id="cllist"></div></div>

  <div class="sec leg"><h3>دليل الألوان</h3>
   <b>الخطوط (زمن القيادة بين مدينتين):</b><br>
   <span style="color:#1a9850">▬</span> أخضر: أقل من ساعة ·
   <span style="color:#f5b301">▬</span> أصفر: ساعة – ساعتين ·
   <span style="color:#d73027">▬</span> أحمر: أكثر من ساعتين<br>
   <small>الخط المتقطّع = زمن تقديري (لا يتوفر مسار قوقل). النقاط الرمادية = محافظات خارج المجموعات.</small>
  </div>
 </div>
 <div id="map"></div>
</div>
<script>
const DATA = __DATA__;
const map = L.map('map').setView([24.2,45.5],6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:18, attribution:'© OpenStreetMap'}).addTo(map);

const byName={}; DATA.points.forEach(p=>byName[p.n]=p);
const markers={};
const VC=DATA.vcolor;
const PALETTE=['#e6194B','#3cb44b','#4363d8','#f58231','#911eb4','#16b2c4','#f032e6','#bf40bf',
 '#1f9e89','#d2691e','#2e8b57','#c71585','#1e90ff','#b8860b','#8b008b','#ff4500','#556b2f',
 '#008b8b','#9932cc','#cd5c5c','#6a5acd','#a0522d','#008b45','#b22222','#4682b4'];

// حالة قابلة للتعديل
const DS=DATA.datasets;
let CL={}, ptCl={}, hidden=new Set(), newCount=0, hideNone=false, curKey='11-14';
const store={};
function buildLive(key){const cl={},pt={};
  DS[key].forEach(c=>cl[c.id]={region:c.region,color:c.color,cities:c.cities.slice()});
  DATA.points.forEach(p=>pt[p.n]=null);
  DS[key].forEach(c=>c.cities.forEach(x=>pt[x]=c.id));
  return {CL:cl,ptCl:pt,hidden:new Set(),newCount:0};}
function switchDataset(key){if(key===curKey)return;
  store[curKey]={CL,ptCl,hidden,newCount};curKey=key;
  if(!store[key])store[key]=buildLive(key);
  const s=store[key];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;
  updateDsUI();renderAll();refreshSelectors();}
function updateDsUI(){document.getElementById('btn1114').className=curKey==='11-14'?'dsbtn on':'dsbtn';
  document.getElementById('btn59').className=curKey==='5-9'?'dsbtn on':'dsbtn';}
function isVisible(n){const id=ptCl[n];return id?!hidden.has(id):!hideNone;}
function showAll(v){if(v)hidden.clear();else hidden=new Set(Object.keys(CL));renderAll();}
function toggleNone(){hideNone=!document.getElementById('vnone').checked;renderMarkers();}

function getG(a,b){let g=DATA.matrix[a+'|'+b]; if(g===undefined)g=DATA.matrix[b+'|'+a]; return g;}
// زمن/مسافة: قوقل إن توفّر، وإلا تقدير (خط مستقيم ×1.3) حتى لا تظهر «لا يوجد مسار»
function gd(a,b){const g=getG(a,b); if(g)return{km:g.km,sec:g.sec,est:false};
  const A=byName[a],B=byName[b]; if(!A||!B)return{km:0,sec:0,est:true};
  const air=haversine(A,B),road=air*1.3,v=road>=150?100:road>=80?90:road>=30?75:50;
  return{km:Math.round(road),sec:road/v*3600,est:true};}
function fmt(min){const h=Math.floor(min/60),m=Math.round(min%60);return h?h+'س '+m+'د':m+'د';}
function haversine(a,b){const R=6371,d=x=>x*Math.PI/180;const dla=d(b.lat-a.lat),dlo=d(b.lon-a.lon);
  const h=Math.sin(dla/2)**2+Math.cos(d(a.lat))*Math.cos(d(b.lat))*Math.sin(dlo/2)**2;return 2*R*Math.asin(Math.sqrt(h));}
function verdict(min,n){if(n<=1)return['مدينة واحدة',VC['مدينة واحدة']];
  if(min<=60)return['ممتاز',VC['ممتاز']]; if(min<=90)return['جيد',VC['جيد']];
  if(min<=150)return['مقبول/مراجعة',VC['مقبول/مراجعة']]; return['بعيد - يُفضّل الفصل',VC['بعيد - يُفضّل الفصل']];}
function stats(cities){let mx=0,nr=0;for(let i=0;i<cities.length;i++)for(let j=i+1;j<cities.length;j++){
  const g=gd(cities[i],cities[j]); if(g.est)nr++; if(g.sec>mx)mx=g.sec;} return{mx,nr};}
function clKey(id){const m=id.match(/\d+/);return (id.indexOf('جديد')>=0?1000:0)+(m?parseInt(m[0]):9999);}

// النقاط
function colorOf(n){const id=ptCl[n];return id&&CL[id]?CL[id].color:'#9aa7b4';}
function popupHtml(n){const p=byName[n],id=ptCl[n];
  let s='<div style="direction:rtl;font-family:Tajawal,sans-serif"><b>'+n+'</b><br>المنطقة: '+p.region+'<br>الفئة: '+p.cat;
  if(id&&CL[id]){const st=stats(CL[id].cities);const[v,vc]=verdict(st.mx/60,CL[id].cities.length);
    s+='<br>المجموعة: '+id+'<br>التقييم: <b style="color:'+vc+'">'+v+'</b>';}else s+='<br>بدون مجموعة';
  return s+'</div>';}
DATA.points.forEach(p=>{const m=L.circleMarker([p.lat,p.lon],{radius:p.cat==='مقر'?8:5.5,
   color:'#222',weight:1,fillColor:colorOf(p.n),fillOpacity:0.95});
  m.bindPopup(()=>popupHtml(p.n)); m.bindTooltip(p.n,{direction:'top'}); m.addTo(map); markers[p.n]=m;
  m.on('click',()=>{ec.value=p.n; ec.dispatchEvent(new Event('change'));
    document.getElementById('estat').innerHTML='📍 اخترت <b>'+p.n+'</b> — حدّد مجموعة الوجهة واضغط نقل';});});
function renderMarkers(){DATA.points.forEach(p=>{const m=markers[p.n];m.setStyle({fillColor:colorOf(p.n)});
  if(isVisible(p.n)){if(!map.hasLayer(m))m.addTo(map);}else if(map.hasLayer(m))map.removeLayer(m);});}

// خطوط المجموعات
const lineLayer=L.layerGroup().addTo(map);
function lineColor(min){return min>120?'#d73027':min>=60?'#f5b301':'#1a9850';}
function renderLines(){lineLayer.clearLayers();
  Object.keys(CL).forEach(id=>{if(hidden.has(id))return;const c=CL[id],ct=c.cities;
    for(let i=0;i<ct.length;i++)for(let j=i+1;j<ct.length;j++){const a=byName[ct[i]],b=byName[ct[j]];if(!a||!b)continue;
      const g=gd(ct[i],ct[j]);const lbl=ct[i]+' ↔ '+ct[j]+': '+g.km+' كم / '+fmt(g.sec/60)+(g.est?' ≈ تقديري':'');
      L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:lineColor(g.sec/60),weight:3,opacity:0.75,
        dashArray:g.est?'5,5':null}).bindTooltip(lbl).addTo(lineLayer);}});
  document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}
function toggleLines(){document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}

// أسماء دائمة
function toggleNames(){const on=document.getElementById('names').checked;
  DATA.points.forEach(p=>{const m=markers[p.n];
    if(on)m.bindTooltip(p.n,{permanent:true,direction:'right',className:'lbl',offset:[6,0]}).openTooltip();
    else{m.unbindTooltip();m.bindTooltip(p.n,{direction:'top'});}});}

// قائمة المجموعات
function renderList(){const cl=document.getElementById('cllist');cl.innerHTML='';
  Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b)).forEach(id=>{const c=CL[id],st=stats(c.cities);
    const[v,vc]=verdict(st.mx/60,c.cities.length);
    const d=document.createElement('div');d.className='cl';d.style.borderRightColor=c.color;
    const cb=document.createElement('input');cb.type='checkbox';cb.className='cbx';cb.checked=!hidden.has(id);
    cb.onclick=e=>e.stopPropagation();cb.onchange=()=>toggleCluster(id,cb.checked);
    const body=document.createElement('div');
    body.innerHTML='<span class="v" style="background:'+vc+'">'+v+'</span><b>'+id+'</b> — '+c.region+
      '<div class="ct">أقصى زمن: '+(c.cities.length>1?fmt(st.mx/60):'—')+' · '+c.cities.length+' مدن'+
      (st.nr?' · '+st.nr+' تقديري':'')+'<br>'+c.cities.join('، ')+'</div>';
    d.appendChild(cb);d.appendChild(body);d.onclick=()=>focusCluster(id);cl.appendChild(d);});}
function toggleCluster(id,show){if(show)hidden.delete(id);else hidden.add(id);renderMarkers();renderLines();}
let hi=[];
function focusCluster(id){hi.forEach(m=>m.setStyle&&m.setStyle({weight:1,radius:m._r0||5.5}));hi=[];const pts=[];
  (CL[id]?CL[id].cities:[]).forEach(n=>{const m=markers[n],p=byName[n];if(!m)return;
    m._r0=m._r0||m.options.radius;m.setStyle({weight:3,color:'#000',radius:9});hi.push(m);pts.push([p.lat,p.lon]);});
  if(pts.length>1)map.fitBounds(pts,{padding:[60,60]});else if(pts.length===1)map.setView(pts[0],10);}

function renderAll(){renderMarkers();renderLines();renderList();}

// أداة المسافة
const pa=document.getElementById('pa'),pb=document.getElementById('pb');
const names=DATA.points.map(p=>p.n).sort((a,b)=>a.localeCompare(b,'ar'));
function fill(sel,ph){sel.innerHTML='<option value="">'+ph+'</option>'+names.map(n=>'<option>'+n+'</option>').join('');}
fill(pa,'— المدينة الأولى —');fill(pb,'— المدينة الثانية —');
let measureLine=null;
function calc(){const a=byName[pa.value],b=byName[pb.value],res=document.getElementById('dres');
  if(!a||!b){res.innerHTML='اختر مدينتين لعرض المسافة.';if(measureLine){map.removeLayer(measureLine);measureLine=null;}return;}
  const g=gd(a.n,b.n);let html='<b>'+a.n+'</b> ↔ <b>'+b.n+'</b><br>';
  html+='المسافة'+(g.est?' (تقديرية)':' (قوقل مابس)')+': <b>'+g.km+' كم</b><br>'+
        'زمن القيادة'+(g.est?' (تقديري)':' (قوقل مابس)')+': <b style="color:#7CFC00">'+fmt(g.sec/60)+'</b>'+
        (g.est?'<br><small style="color:#ffd6a0">لا يتوفر مسار من قوقل لهذه النقطة (منطقة نائية/جزيرة) — الرقم تقديري.</small>':'');
  res.innerHTML=html;if(measureLine)map.removeLayer(measureLine);
  measureLine=L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:'#e63946',weight:3,dashArray:'6,6'}).addTo(map);
  map.fitBounds([[a.lat,a.lon],[b.lat,b.lon]],{padding:[80,80]});}
pa.onchange=calc;pb.onchange=calc;
function openGmaps(){const a=byName[pa.value],b=byName[pb.value];if(!a||!b){alert('اختر مدينتين أولاً');return;}
  window.open('https://www.google.com/maps/dir/?api=1&origin='+a.lat+','+a.lon+'&destination='+b.lat+','+b.lon+'&travelmode=driving','_blank');}

// تعديل المجموعات
const ec=document.getElementById('ecity'),et=document.getElementById('etarget'),rcl=document.getElementById('rcl');
function refreshCity(){const cur=ec.value;ec.innerHTML='<option value="">— اختر مدينة —</option>'+
  names.map(n=>'<option value="'+n+'">'+n+' ('+(ptCl[n]||'بدون')+')</option>').join('');ec.value=cur;}
function refreshTarget(){et.innerHTML=Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b))
  .map(id=>'<option value="'+id+'">'+id+' — '+CL[id].region+'</option>').join('')+
  '<option value="__none__">— بدون مجموعة —</option><option value="__new__">+ مجموعة جديدة</option>';}
function refreshRcl(){const cur=rcl.value;rcl.innerHTML=Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b))
  .map(id=>'<option value="'+id+'">'+id+'</option>').join('');if(CL[cur])rcl.value=cur;}
function refreshSelectors(){refreshCity();refreshTarget();refreshRcl();}
ec.onchange=function(){const c=ec.value;if(c&&ptCl[c]&&CL[ptCl[c]])et.value=ptCl[c];};
function renameCluster(){const old=rcl.value,nn=document.getElementById('rname').value.trim();
  if(!old){alert('اختر مجموعة');return;} if(!nn){alert('اكتب الاسم الجديد');return;}
  if(nn===old){document.getElementById('rname').value='';return;}
  if(CL[nn]){alert('الاسم مستخدم بالفعل');return;}
  // أعد بناء CL مع الحفاظ على الترتيب وتغيير المفتاح القديم للجديد
  const entries=Object.keys(CL).map(k=>k===old?[nn,CL[old]]:[k,CL[k]]);
  CL={};entries.forEach(([k,v])=>CL[k]=v);
  CL[nn].cities.forEach(x=>ptCl[x]=nn);
  document.getElementById('rname').value='';
  renderAll();refreshSelectors();rcl.value=nn;
  document.getElementById('estat').innerHTML='✒️ تغيّر الاسم إلى <b>'+nn+'</b>';}
function moveCity(){const city=ec.value;if(!city){alert('اختر مدينة أولاً');return;}let tgt=et.value;
  // 1) أزلها من كل المجموعات (يمنع بقاءها في الأول عند تكرار النقل)
  Object.keys(CL).forEach(id=>{CL[id].cities=CL[id].cities.filter(x=>x!==city);});
  // 2) أضفها للوجهة
  if(tgt==='__none__')ptCl[city]=null;
  else{if(tgt==='__new__'){newCount++;tgt='مجموعة جديدة '+newCount;
      CL[tgt]={region:byName[city].region,color:PALETTE[(Object.keys(CL).length+newCount)%PALETTE.length],cities:[]};}
    if(!CL[tgt])CL[tgt]={region:byName[city].region,color:'#888',cities:[]};
    CL[tgt].cities.push(city);ptCl[city]=tgt;}
  // 3) احذف المجموعات الفارغة
  Object.keys(CL).forEach(id=>{if(CL[id].cities.length===0)delete CL[id];});
  renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='✓ نُقلت <b>'+city+'</b> إلى <b>'+(tgt==='__none__'?'بدون مجموعة':tgt)+'</b>';}
function exportCsv(){let rows=[['City','Region','Group']];
  DATA.points.forEach(p=>rows.push([p.n,p.region,ptCl[p.n]||'']));
  const csv='﻿'+rows.map(r=>r.map(x=>'"'+x+'"').join(',')).join('\\r\\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='clusters_edited.csv';a.click();}

store['11-14']=buildLive('11-14');
{const s=store['11-14'];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;}
updateDsUI();refreshSelectors();renderAll();
</script></body></html>"""

HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/governorates_map.html", "w", encoding="utf-8").write(HTML)
print("تم حفظ governorates_map.html")
