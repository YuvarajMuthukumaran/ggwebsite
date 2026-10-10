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
