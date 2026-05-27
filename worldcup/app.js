// ===== FIREBASE =====
firebase.initializeApp({
  apiKey:"AIzaSyD4tyQotZeMeh86s5yq9EbRIoXoev10Ajk",
  authDomain:"engagement-cards.firebaseapp.com",
  databaseURL:"https://engagement-cards-default-rtdb.firebaseio.com",
  projectId:"engagement-cards",
  storageBucket:"engagement-cards.firebasestorage.app",
  messagingSenderId:"277478223891",
  appId:"1:277478223891:web:12165a3b3826c436954fe6"
});
var db = firebase.database();
var WC = db.ref('worldcup'); // separate node from the engagement app

// ===== SCORING =====
var PTS_EXACT = 5;   // نتيجة مطابقة تماماً
var PTS_RESULT = 2;  // فوز/تعادل/خسارة صحيحة فقط

// ===== TEAMS (للقوائم المنسدلة) =====
var TEAMS = [
  {n:'الأرجنتين',f:'🇦🇷'},{n:'البرازيل',f:'🇧🇷'},{n:'فرنسا',f:'🇫🇷'},
  {n:'إنجلترا',f:'🏴󠁧󠁢󠁥󠁮󠁧󠁿'},{n:'إسبانيا',f:'🇪🇸'},{n:'ألمانيا',f:'🇩🇪'},
  {n:'البرتغال',f:'🇵🇹'},{n:'هولندا',f:'🇳🇱'},{n:'بلجيكا',f:'🇧🇪'},
  {n:'إيطاليا',f:'🇮🇹'},{n:'كرواتيا',f:'🇭🇷'},{n:'أوروغواي',f:'🇺🇾'},
  {n:'المكسيك',f:'🇲🇽'},{n:'الولايات المتحدة',f:'🇺🇸'},{n:'كندا',f:'🇨🇦'},
  {n:'المغرب',f:'🇲🇦'},{n:'السعودية',f:'🇸🇦'},{n:'قطر',f:'🇶🇦'},
  {n:'مصر',f:'🇪🇬'},{n:'تونس',f:'🇹🇳'},{n:'الجزائر',f:'🇩🇿'},
  {n:'السنغال',f:'🇸🇳'},{n:'غانا',f:'🇬🇭'},{n:'نيجيريا',f:'🇳🇬'},
  {n:'اليابان',f:'🇯🇵'},{n:'كوريا الجنوبية',f:'🇰🇷'},{n:'أستراليا',f:'🇦🇺'},
  {n:'إيران',f:'🇮🇷'},{n:'كولومبيا',f:'🇨🇴'},{n:'الإكوادور',f:'🇪🇨'},
  {n:'سويسرا',f:'🇨🇭'},{n:'الدنمارك',f:'🇩🇰'},{n:'بولندا',f:'🇵🇱'},
  {n:'صربيا',f:'🇷🇸'},{n:'النمسا',f:'🇦🇹'},{n:'الأكوادور',f:'🇪🇨'}
];
function flagOf(name){
  var t=TEAMS.filter(function(x){return x.n===name;})[0];
  return t?t.f:'🏳️';
}

// ===== SEED MATCHES (نقطة بداية، يقدر الأدمن يعدّلها) =====
function seedMatches(){
  var raw=[
    ['المكسيك','كرواتيا','المجموعة A','2026-06-11T19:00','استاد أزتيكا - مكسيكو سيتي'],
    ['كندا','المغرب','المجموعة B','2026-06-12T19:00','استاد تورنتو'],
    ['الولايات المتحدة','أستراليا','المجموعة D','2026-06-12T22:00','استاد لوس أنجلوس'],
    ['الأرجنتين','السعودية','المجموعة C','2026-06-13T19:00','استاد ميامي'],
    ['البرازيل','صربيا','المجموعة E','2026-06-13T22:00','استاد نيويورك'],
    ['فرنسا','الدنمارك','المجموعة F','2026-06-14T16:00','استاد سياتل'],
    ['إسبانيا','المغرب','المجموعة B','2026-06-14T19:00','استاد دالاس'],
    ['إنجلترا','إيران','المجموعة G','2026-06-15T19:00','استاد بوسطن'],
    ['البرتغال','غانا','المجموعة H','2026-06-15T22:00','استاد هيوستن'],
    ['ألمانيا','اليابان','المجموعة I','2026-06-16T19:00','استاد كانساس سيتي'],
    ['هولندا','السنغال','المجموعة J','2026-06-16T22:00','استاد أتلانتا'],
    ['بلجيكا','كرواتيا','المجموعة K','2026-06-17T19:00','استاد فيلادلفيا']
  ];
  var o={};
  raw.forEach(function(r,i){
    o['s'+i]={
      home:r[0],homeFlag:flagOf(r[0]),
      away:r[1],awayFlag:flagOf(r[1]),
      group:r[2],date:new Date(r[3]).getTime(),
      stadium:r[4],status:'upcoming',result:null
    };
  });
  return o;
}

// ===== STATE =====
var myName='', myKey='';
var data={matches:{},predictions:{},users:{}};
var currentTab='matches', stageFilter='all', editingMatchId=null;

// ===== HELPERS =====
function show(id){document.querySelectorAll('.screen').forEach(function(s){s.classList.remove('active');});document.getElementById(id).classList.add('active');}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(function(){t.classList.remove('show');},2400);}
function keyify(n){return n.trim().replace(/[.#$\[\]\/\s]+/g,'_');}
function fmtDate(ms){
  if(!ms)return '';
  var d=new Date(ms);
  return d.toLocaleDateString('ar',{day:'numeric',month:'short'})+' • '+
    d.toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit'});
}
function isLocked(m){return m.status==='finished'||Date.now()>=m.date;}

// نقاط توقّع واحد مقابل نتيجة فعلية
function scoreOf(pred,res){
  if(!pred||!res)return null;
  if(pred.home===res.home&&pred.away===res.away)return PTS_EXACT;
  var po=Math.sign(pred.home-pred.away), ro=Math.sign(res.home-res.away);
  if(po===ro)return PTS_RESULT;
  return 0;
}

// ===== LOGIN =====
function doLogin(name){
  name=(name||'').trim();
  if(!name){document.getElementById('loginErr').textContent='اكتب اسمك أول 🙂';return;}
  myName=name; myKey=keyify(name);
  try{localStorage.setItem('wc_name',name);}catch(e){}
  WC.child('users/'+myKey).update({name:myName,joined:Date.now()})
    .then(enterApp)
    .catch(function(e){document.getElementById('loginErr').textContent='تعذّر الاتصال. تأكد من الإنترنت.';console.error(e);});
}
document.getElementById('btnLogin').addEventListener('click',function(){doLogin(document.getElementById('nameInput').value);});
document.getElementById('nameInput').addEventListener('keydown',function(e){if(e.key==='Enter')doLogin(this.value);});

// عرض اللاعبين الموجودين في شاشة الدخول
WC.child('users').on('value',function(snap){
  var users=snap.val()||{};
  var keys=Object.keys(users);
  var box=document.getElementById('playersBox'), list=document.getElementById('playersList');
  if(!keys.length){box.style.display='none';return;}
  box.style.display='flex';list.innerHTML='';
  keys.forEach(function(k){
    var b=document.createElement('button');b.className='player-pill';b.textContent='👤 '+users[k].name;
    b.addEventListener('click',function(){doLogin(users[k].name);});
    list.appendChild(b);
  });
});

// دخول تلقائي
try{var saved=localStorage.getItem('wc_name');if(saved)doLogin(saved);}catch(e){}

// ===== ENTER APP =====
function enterApp(){
  document.getElementById('meChip').textContent='👤 '+myName;
  show('sApp');
  buildTeamSelects();
  listen();
}

function listen(){
  WC.on('value',function(snap){
    var g=snap.val()||{};
    if(!g.matches){WC.child('matches').set(seedMatches());return;}
    data.matches=g.matches||{};
    data.predictions=g.predictions||{};
    data.users=g.users||{};
    render();
  });
}

// ===== TABS =====
document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click',function(){
    currentTab=t.dataset.tab;
    document.querySelectorAll('.tab').forEach(function(x){x.classList.toggle('active',x===t);});
    document.querySelectorAll('.view').forEach(function(v){v.classList.remove('active');});
    document.getElementById('v'+currentTab.charAt(0).toUpperCase()+currentTab.slice(1)).classList.add('active');
    render();
  });
});

function render(){
  if(currentTab==='matches')renderMatches();
  else if(currentTab==='board')renderBoard();
  else if(currentTab==='admin')renderAdmin();
}

// ===== MATCHES =====
function sortedMatches(){
  return Object.keys(data.matches).map(function(id){
    return Object.assign({id:id},data.matches[id]);
  }).sort(function(a,b){return (a.date||0)-(b.date||0);});
}

function renderStageFilter(){
  var stages=['all'];
  sortedMatches().forEach(function(m){if(m.group&&stages.indexOf(m.group)<0)stages.push(m.group);});
  var row=document.getElementById('stageFilter');row.innerHTML='';
  stages.forEach(function(s){
    var b=document.createElement('button');b.className='fbtn'+(s===stageFilter?' active':'');
    b.textContent=s==='all'?'الكل':s;
    b.addEventListener('click',function(){stageFilter=s;renderMatches();});
    row.appendChild(b);
  });
}

function myPred(matchId){
  var p=data.predictions[matchId];
  return p&&p[myKey]?p[myKey]:null;
}

function renderMatches(){
  renderStageFilter();
  var list=document.getElementById('matchesList');list.innerHTML='';
  var ms=sortedMatches().filter(function(m){return stageFilter==='all'||m.group===stageFilter;});
  if(!ms.length){list.innerHTML='<div class="empty">لا توجد مباريات بعد</div>';return;}
  ms.forEach(function(m){list.appendChild(matchCard(m));});
}

function matchCard(m){
  var card=document.createElement('div');card.className='match-card';
  var locked=isLocked(m), finished=m.status==='finished'&&m.result;
  var pred=myPred(m.id);

  var head=document.createElement('div');head.className='mc-head';
  head.innerHTML='<span class="mc-group">'+(m.group||'')+'</span><span>'+fmtDate(m.date)+'</span>';
  card.appendChild(head);

  var teams=document.createElement('div');teams.className='mc-teams';
  teams.appendChild(teamEl(m.homeFlag,m.home));
  var mid=document.createElement('div');mid.className='mid';

  if(finished){
    var bs=document.createElement('div');bs.className='big-score';
    bs.innerHTML='<span class="gold">'+m.result.home+'</span> - <span class="gold">'+m.result.away+'</span>';
    var lbl=document.createElement('div');lbl.className='vs';lbl.textContent='النتيجة النهائية';
    mid.appendChild(lbl);mid.appendChild(bs);
  } else if(locked){
    var lk=document.createElement('div');lk.className='big-score';lk.textContent='🔒';
    var lbl2=document.createElement('div');lbl2.className='vs';lbl2.textContent='بدأت المباراة';
    mid.appendChild(lbl2);mid.appendChild(lk);
  } else {
    var lbl3=document.createElement('div');lbl3.className='vs';lbl3.textContent='توقّعك';
    var si=document.createElement('div');si.className='score-inputs';
    var hi=numInput(pred?pred.home:'');
    var ai=numInput(pred?pred.away:'');
    var dash=document.createElement('span');dash.className='dash';dash.textContent='-';
    si.appendChild(hi);si.appendChild(dash);si.appendChild(ai);
    mid.appendChild(lbl3);mid.appendChild(si);
    var save=document.createElement('button');save.className='btn btn-green btn-sm';
    save.textContent=pred?'تعديل ✓':'حفظ التوقّع';
    save.addEventListener('click',function(){
      var h=parseInt(hi.value,10), a=parseInt(ai.value,10);
      if(isNaN(h)||isNaN(a)||h<0||a<0){toast('اكتب نتيجة صحيحة 🙂');return;}
      WC.child('predictions/'+m.id+'/'+myKey).set({home:h,away:a,ts:Date.now()}).then(function(){
        toast('تم حفظ توقّعك ✅');
      });
    });
    mid.appendChild(save);
  }
  teams.appendChild(mid);
  teams.appendChild(teamEl(m.awayFlag,m.away));
  card.appendChild(teams);

  // سطر التوقّع + النقاط
  if(finished){
    if(pred){
      var pl=document.createElement('div');pl.className='pred-line';
      pl.innerHTML='توقّعك: <b>'+pred.home+' - '+pred.away+'</b>';
      card.appendChild(pl);
      var pts=scoreOf(pred,m.result);
      var pe=document.createElement('div');
      pe.className='pts '+(pts===PTS_EXACT?'pts-exact':pts>0?'pts-good':'pts-zero');
      pe.textContent=pts===PTS_EXACT?('🎯 نتيجة مطابقة! +'+pts+' نقاط'):
        pts>0?('✅ نتيجة صحيحة +'+pts):'❌ لا نقاط';
      card.appendChild(pe);
    } else {
      var pn=document.createElement('div');pn.className='pts pts-none';pn.textContent='لم تتوقّع هذه المباراة';
      card.appendChild(pn);
    }
  } else if(locked){
    var ll=document.createElement('div');ll.className='lock-line';
    ll.textContent=pred?('توقّعك المُقفل: '+pred.home+' - '+pred.away):'لم تتوقّع — أُقفلت التوقّعات';
    card.appendChild(ll);
  }
  if(m.stadium){
    var st=document.createElement('div');st.className='lock-line';st.textContent='🏟️ '+m.stadium;
    card.appendChild(st);
  }
  return card;
}

function teamEl(flag,name){
  var t=document.createElement('div');t.className='team';
  t.innerHTML='<div class="flag">'+(flag||'🏳️')+'</div><div class="tname">'+(name||'')+'</div>';
  return t;
}
function numInput(val){
  var i=document.createElement('input');i.className='num';i.type='number';i.min='0';i.inputMode='numeric';
  i.value=(val===0||val)?val:'';
  return i;
}

// ===== BOARD =====
function renderBoard(){
  var list=document.getElementById('boardList');list.innerHTML='';
  var users=data.users||{};
  var stats={};
  Object.keys(users).forEach(function(k){stats[k]={name:users[k].name,pts:0,exact:0,played:0};});
  // اجمع النقاط من المباريات المنتهية
  Object.keys(data.matches).forEach(function(mid){
    var m=data.matches[mid];
    if(m.status!=='finished'||!m.result)return;
    var preds=data.predictions[mid]||{};
    Object.keys(preds).forEach(function(uk){
      if(!stats[uk])stats[uk]={name:(users[uk]?users[uk].name:uk),pts:0,exact:0,played:0};
      var pts=scoreOf(preds[uk],m.result);
      stats[uk].pts+=pts;stats[uk].played++;
      if(pts===PTS_EXACT)stats[uk].exact++;
    });
  });
  var rows=Object.keys(stats).map(function(k){return Object.assign({key:k},stats[k]);});
  rows.sort(function(a,b){return b.pts-a.pts||b.exact-a.exact;});
  if(!rows.length){list.innerHTML='<div class="empty">لا يوجد لاعبون بعد</div>';return;}
  rows.forEach(function(r,i){
    var row=document.createElement('div');row.className='lb-row'+(r.key===myKey?' me':'');
    var medal=i===0?'🥇':i===1?'🥈':i===2?'🥉':(i+1);
    row.innerHTML='<div class="lb-rank">'+medal+'</div>'+
      '<div class="lb-name">'+r.name+'<div class="lb-sub">🎯 '+r.exact+' مطابقة • '+r.played+' توقّع</div></div>'+
      '<div class="lb-pts">'+r.pts+'<small> نقطة</small></div>';
    list.appendChild(row);
  });
  var finishedCount=Object.keys(data.matches).filter(function(id){return data.matches[id].status==='finished';}).length;
  document.getElementById('boardNote').textContent='المباريات المنتهية: '+finishedCount;
}

// ===== ADMIN =====
function renderAdmin(){
  var list=document.getElementById('adminList');list.innerHTML='';
  var ms=sortedMatches();
  if(!ms.length){list.innerHTML='<div class="empty">لا توجد مباريات</div>';return;}
  ms.forEach(function(m){list.appendChild(adminCard(m));});
}

function adminCard(m){
  var card=document.createElement('div');card.className='admin-card'+(m.status==='finished'?' finished':'');
  var head=document.createElement('div');head.className='mc-head';
  head.innerHTML='<span class="mc-group">'+(m.group||'')+'</span><span>'+fmtDate(m.date)+'</span>';
  card.appendChild(head);

  var t=document.createElement('div');t.className='admin-teams';
  t.textContent=m.homeFlag+' '+m.home+'  ضد  '+m.away+' '+m.awayFlag;
  card.appendChild(t);

  var si=document.createElement('div');si.className='score-inputs';si.style.justifyContent='center';
  var hi=numInput(m.result?m.result.home:'');
  var ai=numInput(m.result?m.result.away:'');
  var dash=document.createElement('span');dash.className='dash';dash.textContent='-';
  si.appendChild(hi);si.appendChild(dash);si.appendChild(ai);
  card.appendChild(si);

  var act=document.createElement('div');act.className='admin-actions';
  var bSave=document.createElement('button');bSave.textContent=m.status==='finished'?'تحديث النتيجة':'حفظ النتيجة ✅';
  bSave.addEventListener('click',function(){
    var h=parseInt(hi.value,10), a=parseInt(ai.value,10);
    if(isNaN(h)||isNaN(a)||h<0||a<0){toast('اكتب نتيجة صحيحة');return;}
    WC.child('matches/'+m.id).update({result:{home:h,away:a},status:'finished'}).then(function(){toast('تم تسجيل النتيجة ✅');});
  });
  act.appendChild(bSave);
  if(m.status==='finished'){
    var bUndo=document.createElement('button');bUndo.textContent='إلغاء النتيجة';
    bUndo.addEventListener('click',function(){
      WC.child('matches/'+m.id).update({result:null,status:'upcoming'}).then(function(){toast('تم إلغاء النتيجة');});
    });
    act.appendChild(bUndo);
  }
  var bEdit=document.createElement('button');bEdit.className='a-edit';bEdit.textContent='✏️ تعديل';
  bEdit.addEventListener('click',function(){openMatchModal(m);});
  var bDel=document.createElement('button');bDel.className='a-del';bDel.textContent='🗑 حذف';
  bDel.addEventListener('click',function(){
    if(!confirm('حذف هذه المباراة؟\n'+m.home+' ضد '+m.away))return;
    WC.child('matches/'+m.id).remove();
    WC.child('predictions/'+m.id).remove();
    toast('تم الحذف 🗑');
  });
  act.appendChild(bEdit);act.appendChild(bDel);
  card.appendChild(act);
  return card;
}

// ===== MATCH MODAL (add / edit) =====
function buildTeamSelects(){
  var opts='<option value="">— اختر —</option>'+TEAMS.map(function(t){
    return '<option value="'+t.n+'">'+t.f+' '+t.n+'</option>';
  }).join('');
  document.getElementById('mHome').innerHTML=opts;
  document.getElementById('mAway').innerHTML=opts;
}
function openMatchModal(m){
  editingMatchId=m?m.id:null;
  document.getElementById('modalTitle').textContent=m?'✏️ تعديل المباراة':'＋ أضف مباراة';
  document.getElementById('mHome').value=m?m.home:'';
  document.getElementById('mAway').value=m?m.away:'';
  document.getElementById('mGroup').value=m?(m.group||''):'';
  document.getElementById('mStadium').value=m?(m.stadium||''):'';
  document.getElementById('mDate').value=m&&m.date?toLocalInput(m.date):'';
  document.getElementById('modalMsg').textContent='';
  document.getElementById('overlay').classList.add('show');
}
function toLocalInput(ms){
  var d=new Date(ms-d0Offset(ms));
  return d.toISOString().slice(0,16);
}
function d0Offset(ms){return new Date(ms).getTimezoneOffset()*60000;}

document.getElementById('btnAddMatch').addEventListener('click',function(){openMatchModal(null);});
document.getElementById('btnModalClose').addEventListener('click',function(){document.getElementById('overlay').classList.remove('show');});
document.getElementById('overlay').addEventListener('click',function(e){if(e.target===this)this.classList.remove('show');});

document.getElementById('btnSaveMatch').addEventListener('click',function(){
  var home=document.getElementById('mHome').value, away=document.getElementById('mAway').value;
  var group=document.getElementById('mGroup').value.trim();
  var dateVal=document.getElementById('mDate').value;
  var stadium=document.getElementById('mStadium').value.trim();
  if(!home||!away){document.getElementById('modalMsg').style.color='#fca5a5';document.getElementById('modalMsg').textContent='اختر الفريقين';return;}
  if(home===away){document.getElementById('modalMsg').style.color='#fca5a5';document.getElementById('modalMsg').textContent='لا يمكن نفس الفريق';return;}
  if(!dateVal){document.getElementById('modalMsg').style.color='#fca5a5';document.getElementById('modalMsg').textContent='اختر التاريخ والوقت';return;}
  var obj={
    home:home,homeFlag:flagOf(home),away:away,awayFlag:flagOf(away),
    group:group,date:new Date(dateVal).getTime(),stadium:stadium
  };
  var op;
  if(editingMatchId){op=WC.child('matches/'+editingMatchId).update(obj);}
  else{obj.status='upcoming';obj.result=null;op=WC.child('matches').push(obj);}
  Promise.resolve(op).then(function(){
    document.getElementById('modalMsg').style.color='';
    document.getElementById('modalMsg').textContent=editingMatchId?'✅ تم التعديل':'✅ تمت الإضافة';
    toast(editingMatchId?'تم تعديل المباراة ✅':'تمت إضافة المباراة ✅');
    editingMatchId=null;
    setTimeout(function(){document.getElementById('overlay').classList.remove('show');},900);
  });
});
