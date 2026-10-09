(function(){
  var root=document.getElementById('films');if(!root)return;
  var pl=root.querySelector('.player'),vs=[].slice.call(pl.querySelectorAll('video')),
      items=[].slice.call(root.querySelectorAll('.reel li')),glow=root.querySelector('.films__glow'),
      seek=pl.querySelector('.pl__seek'),snd=pl.querySelector('.pl__snd'),tap=pl.querySelector('.pl__tap'),
      reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,cur=0,visible=false,wantSound=false;
  function v(){return vs[cur]}
  function setP(p){pl.style.setProperty('--p',p);items[cur].style.setProperty('--p',p);seek.setAttribute('aria-valuenow',Math.round(p*100))}
  function sync(){pl.classList.toggle('playing',!v().paused);pl.classList.toggle('muted',v().muted);snd.setAttribute('aria-pressed',!v().muted)}
  function play(){var p=v().play();if(p&&p.catch)p.catch(function(){sync()});sync()}
  function go(n,user){
    if(n===cur&&!user)return;var o=v();o.pause();o.classList.remove('on');items[cur].classList.remove('act');items[cur].querySelector('button').removeAttribute('aria-current');
    cur=(n+vs.length)%vs.length;var c=v();c.currentTime=0;c.muted=!wantSound;c.classList.add('on');items[cur].classList.add('act');items[cur].querySelector('button').setAttribute('aria-current','true');
    setP(0);glow.classList.add('sw');setTimeout(function(){glow.style.backgroundImage='url('+c.poster+')';glow.classList.remove('sw')},500);
    if(visible&&(user||!reduce))play();else sync();
  }
  vs.forEach(function(el,i){
    el.addEventListener('timeupdate',function(){if(i===cur&&el.duration)setP(el.currentTime/el.duration)});
    el.addEventListener('ended',function(){go(cur+1)});
    el.addEventListener('play',sync);el.addEventListener('pause',sync);
  });
  items.forEach(function(li,i){li.querySelector('button').addEventListener('click',function(){go(i,true)})});
  tap.addEventListener('click',function(){var e=v();if(e.paused){if(wantSound)e.muted=false;play()}else{e.pause()}});
  snd.addEventListener('click',function(){wantSound=v().muted;v().muted=!wantSound;if(v().paused)play();sync()});
  function seekTo(x){var r=seek.getBoundingClientRect(),p=Math.min(1,Math.max(0,(x-r.left)/r.width));if(v().duration)v().currentTime=p*v().duration}
  seek.addEventListener('pointerdown',function(e){seek.setPointerCapture(e.pointerId);seekTo(e.clientX);seek.onpointermove=function(m){seekTo(m.clientX)}});
  seek.addEventListener('pointerup',function(){seek.onpointermove=null});
  seek.addEventListener('keydown',function(e){var d=v().duration||0;if(e.key==='ArrowRight'){v().currentTime=Math.min(d,v().currentTime+5)}if(e.key==='ArrowLeft'){v().currentTime=Math.max(0,v().currentTime-5)}});
  new IntersectionObserver(function(es){visible=es[0].isIntersecting&&es[0].intersectionRatio>.45;
    if(visible){if(!reduce)play()}else{v().pause()}},{threshold:[0,.45,.6]}).observe(pl);
  document.addEventListener('visibilitychange',function(){if(document.hidden)v().pause();else if(visible&&!reduce)play()});
  glow.style.backgroundImage='url('+vs[0].poster+')';vs[0].classList.add('on');sync();
})();
