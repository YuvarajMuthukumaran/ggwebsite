(function(){
var h=document.querySelector('.hero__in');
if(h&&'IntersectionObserver' in window)new IntersectionObserver(function(e){document.documentElement.classList.toggle('hero-in',e[0].intersectionRatio>.35)},{threshold:[0,.35,.7]}).observe(h);
if(!matchMedia('(hover:hover) and (pointer:fine)').matches||matchMedia('(prefers-reduced-motion:reduce)').matches)return;
document.querySelectorAll('.card,.svc,.rv,.press,.cta-card,.rec').forEach(function(el){
el.addEventListener('pointermove',function(e){var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
el.style.rotate=(-y).toFixed(3)+' '+x.toFixed(3)+' 0 '+(Math.hypot(x,y)*9).toFixed(2)+'deg'});
el.addEventListener('pointerleave',function(){el.style.rotate=''})})})();
