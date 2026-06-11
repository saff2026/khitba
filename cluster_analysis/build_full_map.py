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

import os
matrix = {}
mpath = "/home/user/khitba/cluster_analysis/matrix.json"
if os.path.exists(mpath):
    matrix = json.load(open(mpath, encoding="utf-8"))
    print("مصفوفة قوقل محمّلة:", len(matrix), "زوج")

DATA = {"points": P, "clusters": CLUSTERS, "pairs": pair_lines,
        "cl_color": CL_COLOR, "vcolor": VERDICT_COLOR, "matrix": matrix}

json.dump(P, open("/home/user/khitba/cluster_analysis/points.json", "w", encoding="utf-8"),
          ensure_ascii=False)
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
   <button class="gmaps" id="gbtn" onclick="openGmaps()">افتح المسار في قوقل مابس ↗</button>
   <small>المسافة والزمن بالأعلى <b>حقيقية من قوقل مابس</b> (محسوبة مسبقًا لكل الأزواج). الزر يفتح المسار المباشر للتأكد/الازدحام اللحظي.</small>
  </div>

  <div class="sec">
   <h3>✏️ تعديل الكلاسترات</h3>
   <select id="ecity"></select>
   <select id="etarget"></select>
   <button onclick="moveCity()">↪️ نقل المدينة للكلاستر المحدد</button>
   <div class="res" id="estat">اختر مدينة، ثم كلاستر الوجهة (أو «كلاستر جديد»)، واضغط نقل. كل شيء يتحدّث فورًا.</div>
   <button class="gmaps" onclick="exportCsv()">⬇️ تصدير التقسيمة المعدّلة (CSV)</button>
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

const byName={}; DATA.points.forEach(p=>byName[p.n]=p);
const markers={};
const VC=DATA.vcolor;
const PALETTE=['#e6194B','#3cb44b','#4363d8','#f58231','#911eb4','#16b2c4','#f032e6','#bf40bf',
 '#1f9e89','#d2691e','#2e8b57','#c71585','#1e90ff','#b8860b','#8b008b','#ff4500','#556b2f',
 '#008b8b','#9932cc','#cd5c5c','#6a5acd','#a0522d','#008b45','#b22222','#4682b4'];

// حالة قابلة للتعديل
let CL={}, ptCl={}, newCount=0;
DATA.clusters.forEach(c=>{CL[c.id]={region:c.region,color:c.color,cities:c.cities.slice()};});
DATA.points.forEach(p=>{ptCl[p.n]=p.cl;});

function getG(a,b){let g=DATA.matrix[a+'|'+b]; if(g===undefined)g=DATA.matrix[b+'|'+a]; return g;}
function fmt(min){const h=Math.floor(min/60),m=Math.round(min%60);return h?h+'س '+m+'د':m+'د';}
function haversine(a,b){const R=6371,d=x=>x*Math.PI/180;const dla=d(b.lat-a.lat),dlo=d(b.lon-a.lon);
  const h=Math.sin(dla/2)**2+Math.cos(d(a.lat))*Math.cos(d(b.lat))*Math.sin(dlo/2)**2;return 2*R*Math.asin(Math.sqrt(h));}
function verdict(min,n){if(n<=1)return['مدينة واحدة',VC['مدينة واحدة']];
  if(min<=60)return['ممتاز',VC['ممتاز']]; if(min<=90)return['جيد',VC['جيد']];
  if(min<=150)return['مقبول/مراجعة',VC['مقبول/مراجعة']]; return['بعيد - يُفضّل الفصل',VC['بعيد - يُفضّل الفصل']];}
function stats(cities){let mx=0,nr=0;for(let i=0;i<cities.length;i++)for(let j=i+1;j<cities.length;j++){
  const g=getG(cities[i],cities[j]); if(g==null){nr++;continue;} if(g.sec>mx)mx=g.sec;} return{mx,nr};}
function clKey(id){const m=id.match(/\d+/);return (id.indexOf('جديد')>=0?1000:0)+(m?parseInt(m[0]):9999);}

// النقاط
function colorOf(n){const id=ptCl[n];return id&&CL[id]?CL[id].color:'#9aa7b4';}
function popupHtml(n){const p=byName[n],id=ptCl[n];
  let s='<div style="direction:rtl;font-family:Tahoma"><b>'+n+'</b><br>المنطقة: '+p.region+'<br>الفئة: '+p.cat;
  if(id&&CL[id]){const st=stats(CL[id].cities);const[v,vc]=verdict(st.mx/60,CL[id].cities.length);
    s+='<br>الكلاستر: '+id+'<br>التقييم: <b style="color:'+vc+'">'+v+'</b>';}else s+='<br>بدون كلاستر';
  return s+'</div>';}
DATA.points.forEach(p=>{const m=L.circleMarker([p.lat,p.lon],{radius:p.cat==='مقر'?8:5.5,
   color:'#222',weight:1,fillColor:colorOf(p.n),fillOpacity:0.95});
  m.bindPopup(()=>popupHtml(p.n)); m.bindTooltip(p.n,{direction:'top'}); m.addTo(map); markers[p.n]=m;});
function renderMarkers(){DATA.points.forEach(p=>markers[p.n].setStyle({fillColor:colorOf(p.n)}));}

// خطوط الكلاسترات
const lineLayer=L.layerGroup().addTo(map);
function renderLines(){lineLayer.clearLayers();
  Object.keys(CL).forEach(id=>{const c=CL[id],ct=c.cities;
    for(let i=0;i<ct.length;i++)for(let j=i+1;j<ct.length;j++){const a=byName[ct[i]],b=byName[ct[j]];if(!a||!b)continue;
      const g=getG(ct[i],ct[j]);const lbl=ct[i]+' ↔ '+ct[j]+': '+(g?g.km+' كم / '+fmt(g.sec/60):'لا يوجد مسار بري');
      L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:c.color,weight:1.5,opacity:0.5}).bindTooltip(lbl).addTo(lineLayer);}});
  document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}
function toggleLines(){document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}

// أسماء دائمة
function toggleNames(){const on=document.getElementById('names').checked;
  DATA.points.forEach(p=>{const m=markers[p.n];
    if(on)m.bindTooltip(p.n,{permanent:true,direction:'right',className:'lbl',offset:[6,0]}).openTooltip();
    else{m.unbindTooltip();m.bindTooltip(p.n,{direction:'top'});}});}

// قائمة الكلاسترات
function renderList(){const cl=document.getElementById('cllist');cl.innerHTML='';
  Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b)).forEach(id=>{const c=CL[id],st=stats(c.cities);
    const[v,vc]=verdict(st.mx/60,c.cities.length);
    const d=document.createElement('div');d.className='cl';d.style.borderRightColor=c.color;
    d.innerHTML='<span class="v" style="background:'+vc+'">'+v+'</span><b>'+id+'</b> — '+c.region+
      '<div class="ct">أقصى زمن: '+(c.cities.length>1?fmt(st.mx/60):'—')+' · '+c.cities.length+' مدن'+
      (st.nr?' · '+st.nr+' بلا طريق':'')+'<br>'+c.cities.join('، ')+'</div>';
    d.onclick=()=>focusCluster(id);cl.appendChild(d);});}
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
  const g=getG(a.n,b.n);let html='<b>'+a.n+'</b> ↔ <b>'+b.n+'</b><br>';
  if(g)html+='المسافة (قوقل مابس): <b>'+g.km+' كم</b><br>زمن القيادة (قوقل مابس): <b style="color:#7CFC00">'+fmt(g.sec/60)+'</b>';
  else if(g===null){const air=haversine(a,b);html+='<span style="color:#ffb4b4">لا يوجد مسار بري على قوقل (جزيرة/عبّارة).</span><br>خط مستقيم: '+air.toFixed(0)+' كم';}
  else{const air=haversine(a,b),road=air*1.3,v=road>=150?100:road>=80?90:road>=30?75:50;html+='تقدير الطريق: <b>'+road.toFixed(0)+' كم</b><br>زمن تقريبي: <b>'+fmt(road/v*60)+'</b>';}
  res.innerHTML=html;if(measureLine)map.removeLayer(measureLine);
  measureLine=L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:'#e63946',weight:3,dashArray:'6,6'}).addTo(map);
  map.fitBounds([[a.lat,a.lon],[b.lat,b.lon]],{padding:[80,80]});}
pa.onchange=calc;pb.onchange=calc;
function openGmaps(){const a=byName[pa.value],b=byName[pb.value];if(!a||!b){alert('اختر مدينتين أولاً');return;}
  window.open('https://www.google.com/maps/dir/?api=1&origin='+a.lat+','+a.lon+'&destination='+b.lat+','+b.lon+'&travelmode=driving','_blank');}

// تعديل الكلاسترات
const ec=document.getElementById('ecity'),et=document.getElementById('etarget');
function refreshCity(){const cur=ec.value;ec.innerHTML='<option value="">— اختر مدينة —</option>'+
  names.map(n=>'<option value="'+n+'">'+n+' ('+(ptCl[n]||'بدون')+')</option>').join('');ec.value=cur;}
function refreshTarget(){et.innerHTML=Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b))
  .map(id=>'<option value="'+id+'">'+id+' — '+CL[id].region+'</option>').join('')+
  '<option value="__none__">— بدون كلاستر —</option><option value="__new__">+ كلاستر جديد</option>';}
ec.onchange=function(){const c=ec.value;if(c&&ptCl[c]&&CL[ptCl[c]])et.value=ptCl[c];};
function moveCity(){const city=ec.value;if(!city){alert('اختر مدينة أولاً');return;}let tgt=et.value;
  const old=ptCl[city];
  if(old&&CL[old]){CL[old].cities=CL[old].cities.filter(x=>x!==city);if(CL[old].cities.length===0)delete CL[old];}
  if(tgt==='__none__')ptCl[city]=null;
  else{if(tgt==='__new__'){newCount++;tgt='كلاستر جديد '+newCount;
      CL[tgt]={region:byName[city].region,color:PALETTE[(Object.keys(CL).length+newCount)%PALETTE.length],cities:[]};}
    if(!CL[tgt])CL[tgt]={region:byName[city].region,color:'#888',cities:[]};
    CL[tgt].cities.push(city);ptCl[city]=tgt;}
  renderAll();refreshCity();refreshTarget();
  document.getElementById('estat').innerHTML='✓ نُقلت <b>'+city+'</b> إلى <b>'+(tgt==='__none__'?'بدون كلاستر':tgt)+'</b>';}
function exportCsv(){let rows=[['City','Region','Cluster']];
  DATA.points.forEach(p=>rows.push([p.n,p.region,ptCl[p.n]||'']));
  const csv='﻿'+rows.map(r=>r.map(x=>'"'+x+'"').join(',')).join('\\r\\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='clusters_edited.csv';a.click();}

refreshCity();refreshTarget();renderAll();
</script></body></html>"""

HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/governorates_map.html", "w", encoding="utf-8").write(HTML)
print("تم حفظ governorates_map.html")
