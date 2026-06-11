#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""خريطة شاملة: كل المحافظات + الكلاسترات + أداة قياس المسافة بين أي مدينتين."""
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

# ربط الكلاسترات
cluster_members = {cl: [] for cl in ordered}
for cl in ordered:
    for city_en in clusters[cl]["cities"]:
        ar = EN2AR.get(city_en, city_en)
        if ar not in points:                      # مدينة كلاستر ليست محافظة مستقلة
            lat, lon = COORDS[city_en]
            points[ar] = {"lat": lat, "lon": lon, "region": clusters[cl]["region"],
                          "cat": "كلاستر", "cluster": None}
        points[ar]["cluster"] = cl
        cluster_members[cl].append(ar)

# أزواج الكلاستر بأوقات قوقل (بالأسماء العربية)
pair_lines = []
for p in pairs:
    a = EN2AR.get(p["From"], p["From"]); b = EN2AR.get(p["To"], p["To"])
    if a in points and b in points:
        pair_lines.append({"a": a, "b": b, "km": p["Road_km"], "t": p["Drive"],
                           "cl": p["Cluster"]})

# تجهيز JSON للواجهة
P = [{"n": n, "lat": v["lat"], "lon": v["lon"], "region": v["region"],
      "cat": v["cat"], "cl": v["cluster"]} for n, v in points.items()]
CLUSTERS = []
for cl in ordered:
    s = summary[cl]
    CLUSTERS.append({"id": cl, "region": s["Region"], "color": CL_COLOR[cl],
                     "verdict": s["Verdict"], "vcolor": VERDICT_COLOR.get(s["Verdict"], "#888"),
                     "maxdrive": s["MaxDrive"], "cities": cluster_members[cl]})

DATA = {"points": P, "clusters": CLUSTERS, "pairs": pair_lines,
        "cl_color": CL_COLOR, "vcolor": VERDICT_COLOR}

print("نقاط على الخريطة:", len(P), "| محافظات الجدول:", len(recs),
      "| مدن كلاستر إضافية:", len(P) - len(recs))
missing_tbl = [n for n in points if points[n]["cat"] != "كلاستر"]
print("كل محافظات الجدول مرسومة:", len(missing_tbl) == len(recs))

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>خريطة محافظات المملكة — الكلاسترات وقياس المسافات</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Segoe UI',Tahoma,Arial,sans-serif}
 #wrap{display:flex;height:100vh}
 #side{width:340px;background:#0f2540;color:#e9eef5;overflow-y:auto;flex-shrink:0}
 #map{flex:1}
 .hd{background:#0a3d62;padding:12px 14px;font-weight:bold;font-size:15px;position:sticky;top:0;z-index:5}
 .sec{padding:10px 14px;border-bottom:1px solid #1c3a5e}
 .sec h3{margin:0 0 8px;font-size:14px;color:#ffd166}
 select,button{width:100%;padding:8px;border-radius:6px;border:1px solid #2a4a6e;
   background:#16314f;color:#fff;font-size:13px;margin-bottom:6px}
 button{background:#1b6ca8;cursor:pointer;font-weight:bold} button:hover{background:#2980b9}
 .gmaps{background:#2e7d32} .gmaps:hover{background:#388e3c}
 .res{background:#16314f;border-radius:6px;padding:8px;font-size:13px;line-height:1.7}
 .res b{color:#ffd166}
 .cl{padding:7px 9px;border-radius:6px;margin-bottom:5px;cursor:pointer;background:#16314f;
   border-right:5px solid #888;font-size:12.5px}
 .cl:hover{background:#1d3e63} .cl .v{float:left;font-size:11px;padding:1px 6px;border-radius:10px;color:#fff}
 .cl .ct{color:#aac4e0;font-size:11px;margin-top:3px}
 .lbl{font-size:11px;color:#111;font-weight:bold;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff}
 .leg{background:#16314f;font-size:11.5px;line-height:1.8}
 small{color:#9fb6d0}
</style></head><body>
<div id="wrap">
 <div id="side">
  <div class="hd">🗺️ محافظات المملكة — الكلاسترات وقياس المسافات</div>

  <div class="sec">
   <h3>📏 قياس المسافة بين مدينتين</h3>
   <select id="pa"></select>
   <select id="pb"></select>
   <div class="res" id="dres">اختر مدينتين لعرض المسافة.</div>
   <button class="gmaps" id="gbtn" onclick="openGmaps()">احسب الوقت الفعلي على قوقل مابس ↗</button>
   <small>المسافة بالأعلى مباشرة (خط القيادة التقريبي). زر قوقل مابس يفتح المسار بالوقت الفعلي.</small>
  </div>

  <div class="sec">
   <h3>🎛️ خيارات العرض</h3>
   <label><input type="checkbox" id="names" onchange="toggleNames()"> إظهار أسماء كل المدن</label><br>
   <label><input type="checkbox" id="lines" checked onchange="toggleLines()"> خطوط الكلاسترات</label>
  </div>

  <div class="sec"><h3>📋 الكلاسترات (اضغط للتمييز)</h3><div id="cllist"></div></div>

  <div class="sec leg"><h3>دليل الألوان</h3>
   <span style="color:#1a9850">●</span> ممتاز ·
   <span style="color:#66bd63">●</span> جيد ·
   <span style="color:#f59e0b">●</span> مراجعة ·
   <span style="color:#d73027">●</span> بعيد<br>
   <small>كل كلاستر له لون نقاط مميز. النقاط الرمادية = محافظات خارج الكلاسترات.</small>
  </div>
 </div>
 <div id="map"></div>
</div>
<script>
const DATA = __DATA__;
const map = L.map('map').setView([24.2,45.5],6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:18, attribution:'© OpenStreetMap'}).addTo(map);

const byName = {}; DATA.points.forEach(p=>byName[p.n]=p);
const markers = {};
const labelOn = {};
// رسم النقاط
DATA.points.forEach(p=>{
  const col = p.cl ? DATA.cl_color[p.cl] : '#9aa7b4';
  const r = p.cat==='مقر'?8 : (p.cl?6:4.5);
  const m = L.circleMarker([p.lat,p.lon],{radius:r,color:'#222',weight:1,
     fillColor:col,fillOpacity:0.95});
  let info = '<div style="direction:rtl;font-family:Tahoma"><b>'+p.n+'</b><br>'+
     'المنطقة: '+p.region+'<br>الفئة: '+p.cat;
  if(p.cl){const c=DATA.clusters.find(x=>x.id===p.cl);
     info+='<br>الكلاستر: '+p.cl+'<br>التقييم: <b style="color:'+c.vcolor+'">'+c.verdict+'</b>';}
  info+='</div>';
  m.bindPopup(info); m.bindTooltip(p.n,{direction:'top'});
  m.addTo(map); markers[p.n]=m;
});

// خطوط الكلاسترات
const lineLayer = L.layerGroup().addTo(map);
DATA.pairs.forEach(pr=>{
  const a=byName[pr.a],b=byName[pr.b]; if(!a||!b)return;
  const c=DATA.clusters.find(x=>x.id===pr.cl);
  L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:c?c.vcolor:'#666',weight:2,opacity:0.5})
    .bindTooltip(pr.a+' ↔ '+pr.b+': '+pr.km+' كم / '+pr.t).addTo(lineLayer);
});
function toggleLines(){document.getElementById('lines').checked?
  map.addLayer(lineLayer):map.removeLayer(lineLayer);}

// أسماء دائمة
function toggleNames(){const on=document.getElementById('names').checked;
  DATA.points.forEach(p=>{const m=markers[p.n];
    if(on){m.bindTooltip(p.n,{permanent:true,direction:'right',className:'lbl',offset:[6,0]}).openTooltip();}
    else{m.unbindTooltip(); m.bindTooltip(p.n,{direction:'top'});}});}

// قائمة الكلاسترات
const cl = document.getElementById('cllist');
DATA.clusters.forEach(c=>{
  const d=document.createElement('div'); d.className='cl';
  d.style.borderRightColor=c.color;
  d.innerHTML='<span class="v" style="background:'+c.vcolor+'">'+c.verdict+'</span>'+
    '<b>'+c.id+'</b> — '+c.region+'<div class="ct">أقصى زمن: '+c.maxdrive+
    ' · '+c.cities.length+' مدن<br>'+c.cities.join('، ')+'</div>';
  d.onclick=()=>focusCluster(c);
  cl.appendChild(d);
});
let hi=[];
function focusCluster(c){
  hi.forEach(m=>m.setStyle&&m.setStyle({weight:1,radius:m._r0}));
  hi=[];const pts=[];
  c.cities.forEach(n=>{const m=markers[n],p=byName[n]; if(!m)return;
    m._r0=m._r0||m.options.radius; m.setStyle({weight:3,color:'#000',radius:9});
    hi.push(m); pts.push([p.lat,p.lon]);});
  if(pts.length>1) map.fitBounds(pts,{padding:[60,60]});
  else if(pts.length===1) map.setView(pts[0],10);
}

// أداة المسافة
const pa=document.getElementById('pa'), pb=document.getElementById('pb');
const names=DATA.points.map(p=>p.n).sort((a,b)=>a.localeCompare(b,'ar'));
function fill(sel,ph){sel.innerHTML='<option value="">'+ph+'</option>'+
  names.map(n=>'<option>'+n+'</option>').join('');}
fill(pa,'— المدينة الأولى —'); fill(pb,'— المدينة الثانية —');
let measureLine=null;
function haversine(a,b){const R=6371,d=x=>x*Math.PI/180;
  const dla=d(b.lat-a.lat),dlo=d(b.lon-a.lon);
  const h=Math.sin(dla/2)**2+Math.cos(d(a.lat))*Math.cos(d(b.lat))*Math.sin(dlo/2)**2;
  return 2*R*Math.asin(Math.sqrt(h));}
function fmt(min){const h=Math.floor(min/60),m=Math.round(min%60);return h?h+'س '+m+'د':m+'د';}
function calc(){const a=byName[pa.value],b=byName[pb.value];
  const res=document.getElementById('dres');
  if(!a||!b){res.innerHTML='اختر مدينتين لعرض المسافة.';
    if(measureLine){map.removeLayer(measureLine);measureLine=null;}return;}
  const air=haversine(a,b), road=air*1.3;
  const v= road>=150?100: road>=80?90: road>=30?75:50;
  const t=road/v*60;
  res.innerHTML='<b>'+a.n+'</b> ↔ <b>'+b.n+'</b><br>'+
    'خط مستقيم: '+air.toFixed(0)+' كم<br>'+
    'تقدير الطريق: <b>'+road.toFixed(0)+' كم</b><br>'+
    'زمن القيادة التقريبي: <b>'+fmt(t)+'</b>';
  if(measureLine)map.removeLayer(measureLine);
  measureLine=L.polyline([[a.lat,a.lon],[b.lat,b.lon]],
    {color:'#e63946',weight:3,dashArray:'6,6'}).addTo(map);
  map.fitBounds([[a.lat,a.lon],[b.lat,b.lon]],{padding:[80,80]});
}
pa.onchange=calc; pb.onchange=calc;
function openGmaps(){const a=byName[pa.value],b=byName[pb.value];
  if(!a||!b){alert('اختر مدينتين أولاً');return;}
  window.open('https://www.google.com/maps/dir/?api=1&origin='+a.lat+','+a.lon+
    '&destination='+b.lat+','+b.lon+'&travelmode=driving','_blank');}
</script></body></html>"""

HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/governorates_map.html", "w", encoding="utf-8").write(HTML)
print("تم حفظ governorates_map.html")
