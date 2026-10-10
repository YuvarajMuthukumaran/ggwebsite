/* calm.js — Breathe & Ground widget + three-step request form. No dependencies. */
(function(){
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---- Breathe & Ground: in 4s, hold 2s, out 6s, six rounds ---- */
var w=document.createElement('div');w.className='bg';
w.innerHTML='<button class="bg__fab" type="button" aria-expanded="false" aria-controls="bgp"><span class="bg__dot" aria-hidden="true"></span>Breathe</button>'+
'<div class="bg__panel" id="bgp" role="dialog" aria-label="Breathing guide" hidden><button class="bg__x" type="button" aria-label="Close">\u00d7</button>'+
'<div class="bg__ring"><i aria-hidden="true"></i><span class="bg__lbl">Ready when you are</span></div>'+
'<p class="bg__tip">Breathing out a little longer than you breathe in can help you feel steadier.</p>'+
'<button class="btn bg__go" type="button">Begin</button></div>';
document.body.appendChild(w);
var fab=w.querySelector('.bg__fab'),panel=w.querySelector('.bg__panel'),ring=w.querySelector('.bg__ring i'),
lbl=w.querySelector('.bg__lbl'),go=w.querySelector('.bg__go'),t=null,round=0,running=false;
var P=[['Breathe in',4,1],['Hold',2,1],['Breathe out',6,.55]];
function set(s,d){ring.style.setProperty('--d',(reduce?0:d)+'s');ring.style.setProperty('--s',s)}
function stop(msg){running=false;clearTimeout(t);set(.55,1.2);lbl.textContent=msg||'Ready when you are';go.textContent='Begin'}
function step(i){
  if(!running)return;
  if(i===0&&round===6){stop('Well done. Take your time.');return}
  var p=P[i];lbl.textContent=p[0];set(p[2],p[1]);
  t=setTimeout(function(){if(i===2)round++;step((i+1)%3)},p[1]*1000);
}
go.addEventListener('click',function(){
  if(running){stop();return}
  running=true;round=0;go.textContent='Stop';step(0);
});
function open(o){panel.hidden=!o;fab.setAttribute('aria-expanded',o);if(o)go.focus();else{stop();fab.focus()}}
fab.addEventListener('click',function(){open(panel.hidden)});
w.querySelector('.bg__x').addEventListener('click',function(){open(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!panel.hidden)open(false)});

/* ---- Gentle reminder: a small bubble beside the Breathe button.
   First after ~45s, then about every 4 minutes, at most 3 times per visit.
   Never while someone is typing or the guide is open; off for the visit after two dismissals. ---- */
var nudge=document.createElement('div');nudge.className='bg__nudge';nudge.setAttribute('role','status');nudge.hidden=true;
nudge.innerHTML='<p>Remember to breathe</p><div class="bg__nb"><button class="bg__yes" type="button">Breathe with me</button><button class="bg__no" type="button">Not now</button></div>';
w.appendChild(nudge);
var NK='gg-breathe-nudge',ns={shown:0,dismissed:0},lastKey=0,nTimer=null,hideT=null;
try{var sv=JSON.parse(sessionStorage.getItem(NK)||'null');if(sv)ns=sv}catch(e){}
function saveN(){try{sessionStorage.setItem(NK,JSON.stringify(ns))}catch(e){}}
function nDone(){return ns.shown>=3||ns.dismissed>=2}
function typing(){
  var a=document.activeElement,tag=a&&a.tagName;
  if(tag==='INPUT'||tag==='TEXTAREA'||tag==='SELECT'||(a&&a.isContentEditable))return true;
  return Date.now()-lastKey<6000;
}
document.addEventListener('keydown',function(){lastKey=Date.now()},true);
function hideN(){nudge.hidden=true;clearTimeout(hideT)}
function sched(ms){clearTimeout(nTimer);if(nDone())return;nTimer=setTimeout(tryShow,ms)}
function tryShow(){
  if(nDone())return;
  if(document.hidden||typing()||!panel.hidden||!nudge.hidden){sched(15000);return}
  nudge.hidden=false;ns.shown++;saveN();
  hideT=setTimeout(hideN,16000);
  sched(240000);
}
nudge.querySelector('.bg__no').addEventListener('click',function(){hideN();ns.dismissed++;saveN();if(nDone())clearTimeout(nTimer)});
nudge.querySelector('.bg__yes').addEventListener('click',function(){hideN();open(true);if(!running)go.click()});
fab.addEventListener('click',hideN);
sched(ns.shown?240000:45000);

/* ---- Request form: composes a WhatsApp message; nothing is stored or sent by this site ---- */
var f=document.getElementById('rq');if(!f)return;
var sets=f.querySelectorAll('fieldset'),dots=f.querySelectorAll('.rq__p li'),
status=f.querySelector('.rq__s'),back=f.querySelector('.rq__b'),next=f.querySelector('.rq__n'),done=f.querySelector('.rq__done'),
cur=0,N=sets.length;
function show(n){
  cur=n;
  sets.forEach(function(s,i){s.hidden=i!==n;s.classList.toggle('in',i===n)});
  dots.forEach(function(d,i){d.classList.toggle('on',i<=n)});
  status.textContent='Step '+(n+1)+' of '+N;
  back.hidden=n===0;next.textContent=n===N-1?'Open in WhatsApp':'Continue';
}
function val(name){var c=f.querySelector('input[name="'+name+'"]:checked');return c?c.value:''}
function url(){
  var nm=f.elements.nm.value.trim(),note=f.elements.note.value.trim();
  var msg='Hello Dr. Gupta\u2019s team, '+(nm?'this is '+nm+'. ':'')+'I\u2019d like to request a consultation for '+val('who')+'. '+
  'Preferred setting: '+val('mode')+'. Preferred time: '+val('time')+'.'+(note?' '+note:'');
  return 'https://wa.me/918800000255?text='+encodeURIComponent(msg);
}
next.addEventListener('click',function(){
  if(cur<N-1){show(cur+1);return}
  var u=url();window.open(u,'_blank','noopener');
  sets.forEach(function(s){s.hidden=true});f.querySelector('.rq__a').hidden=true;status.hidden=true;
  dots.forEach(function(d){d.classList.add('on')});
  done.hidden=false;done.querySelector('a').href=u;done.querySelector('h3').focus();
});
back.addEventListener('click',function(){if(cur>0)show(cur-1)});
f.addEventListener('submit',function(e){e.preventDefault()});
show(0);
})();
