import re
src=open('legacy/index.html').read()
T=lambda s:re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s)).strip()
sec=lambda a,b:src[src.index(f'id="{a}"'):src.index(f'id="{b}"')]
work=sec('work','philosophy')
panes=re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*<div class="work__tags">(.*?)</div>',work,re.S)
IC=['<path d="M9 3h6v4H9zM6 7h12l-1 14H7z"/>','<path d="M12 4v16M4 12h16"/><circle cx="12" cy="12" r="9"/>','<circle cx="12" cy="9" r="4"/><path d="M5 21c1-5 4-6 7-6s6 1 7 6"/>','<path d="M3 12c3-8 6 8 9 0s6 8 9 0"/>','<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>','<path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z"/>','<path d="M8 4a4 4 0 0 0-4 4v1a3 3 0 0 0 1 5 3 3 0 0 0 3 4h1V4zM16 4a4 4 0 0 1 4 4v1a3 3 0 0 1-1 5 3 3 0 0 1-3 4h-1V4z"/>']
svg=lambda i:f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IC[i%7]}</svg>'
cards=''.join(f'<article class="card svc reveal" style="--i:{i%4}"><span class="ico">{svg(i)}</span><h3>{t}</h3><p>{" ".join(p.split())}</p><div class="tags">{"".join(f"<span>{T(x)}</span>" for x in re.findall(r"<span>(.*?)</span>",tg))}</div></article>' for i,(t,p,tg) in enumerate(panes))
jr=sec('journey','work')
jl=''.join(f'<li class="reveal"><i></i><b>{T(y)}</b><h4>{h}</h4><p>{" ".join(p.split())}</p></li>' for y,h,p in re.findall(r'class="journey__year"[^>]*>(.*?)</[^>]+>.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>',jr,re.S))
rec=sec('impact','insights')
cols=''.join(f'<div class="rec reveal" style="--i:{i}">{c}</div>' for i,c in enumerate(re.findall(r'<div class="impact__col"[^>]*>(.*?)</div>',rec,re.S)))
ins=sec('insights','pathway')
def _p(m):
    h,b=m
    t=T(re.search(r'<h[34][^>]*>(.*?)</h[34]>',b,re.S).group(1)); sp=[T(x) for x in re.findall(r"<span>(.*?)</span>",b) if T(x)]
    return f'<a class="press reveal" href="{h}" target="_blank" rel="noopener"><small>{" · ".join(sp[:3])}</small><h4>{t}</h4><em>{"Watch" if "YouTube" in sp[0] else "Read"} →</em></a>'
press=''.join(_p(m) for m in re.findall(r'<a class="media__(?:feature|item)" href="(.*?)"[^>]*>(.*?)</a>',ins,re.S))
pw=sec('pathway','calm')
steps=''.join(f'<div class="step reveal" style="--i:{i}"><b>0{i+1}</b><h3>{h}</h3><p>{" ".join(p.split())}</p></div>' for i,(h,p) in enumerate(re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>',pw,re.S)))
faq=''.join(f'<details class="reveal"{" open" if i==0 else ""}><summary>{T(q)}</summary><p>{" ".join(a.split())}</p></details>' for i,(q,a) in enumerate(re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>',src,re.S)))
who=sec('who','journey')
ps=[" ".join(x.split()) for x in re.findall(r'<p[^>]*>\s*((?:Dr\. Gorav Gupta is|He works).*?)</p>',who,re.S)]
facts=''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>',who))
TEL='tel:+918800000255';MAIL='mailto:drgoravgupta@tulasihealthcare.com'
nav=[('who','About'),('work','Expertise'),('journey','Journey'),('insights','Insights'),('questions','Questions'),('contact','Contact')]
links=''.join(f'<a href="#{a}">{b}</a>' for a,b in nav)
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dr. Gorav Gupta — Psychiatrist, New Delhi &amp; Gurugram</title>
<meta name="description" content="Dr. Gorav Gupta, M.B.B.S., M.D. Psychiatry — de-addiction, rehabilitation and dual diagnosis. Consulting in New Delhi and Gurugram.">
<link rel="preload" as="image" href="assets/img/portrait-cutout.webp?v1" fetchpriority="high">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v6"></head><body>
<div class="bar" id="bar"></div>
<div class="ann"><span>Consultations available online</span><a href="{TEL}">Call +91 88000 00255 <i>→</i></a></div>
<header class="nav" id="nav"><a class="brand" href="#top"><span class="logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z"/><path d="M7 11h3l1.5-2.5L13 13l1-2h3"/></svg></span><span>Dr. Gorav Gupta<small>Psychiatrist</small></span></a>
<nav id="links">{links}</nav><a class="btn ghost" href="#appoint">Book Consultation</a><button id="burger" aria-label="Menu"><i></i><i></i></button></header>
<main id="top"><section class="hero"><div class="hero__in">
<h1 class="giant"><span>Dr. Gorav Gupta</span></h1>
<p class="qual">M.B.B.S. · M.D. Psychiatry<small>De-addiction · Rehabilitation · Dual diagnosis<br>New Delhi · Gurugram</small></p>
<img class="cut" src="assets/img/portrait-cutout.webp?v1" alt="Dr. Gorav Gupta in a grey suit and tie." width="680" height="951">
<div class="fl fl1"><b>★</b><span>Economic Times “Psychiatrist of the Year”</span></div><div class="fl fl2"><b>◔</b><span>Consultations available online</span></div>
<div class="hero__l"><p><strong>Your mind deserves care.</strong> Four decades spent with the illnesses that take the longest — and the conviction that treatment is finished only when a person can live their life again.</p><a class="btn" href="#appoint">Book Consultation <svg viewBox="0 0 12 12" width="12" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 10 10 2M4 2h6v6"/></svg></a></div>
<div class="stats"><div><b data-count="40">40+</b><span>Years in practice</span></div><div><b>2</b><span>Consulting rooms</span></div></div>
</div></section>
<section class="strip"><span>Institutions &amp; memberships</span><div class="mq"><div class="mqt"><p>Tulasi Psychiatric &amp; Rehabilitation Centre</p><p>Tulasi Home</p><p>Delhi Psychiatry Society</p><p>Indian Association of Private Psychiatry</p><p>Indian Association of Psychiatry</p><p>NITI Aayog — National Task Force on Brain Health</p><p>Department of Social Welfare, Delhi</p><p>Tulasi Psychiatric &amp; Rehabilitation Centre</p><p>Tulasi Home</p><p>Delhi Psychiatry Society</p><p>Indian Association of Private Psychiatry</p><p>Indian Association of Psychiatry</p><p>NITI Aayog — National Task Force on Brain Health</p><p>Department of Social Welfare, Delhi</p></div></div></section>
<section class="sec bento-s"><div class="head reveal"><span class="eyebrow">By the numbers</span><h2>Four decades, one steady focus</h2></div>
<div class="bento">
<div class="bt big reveal"><b data-n="40" data-s="+">40+</b><h3>Years in practice</h3><p>A senior psychiatrist in New Delhi and Gurugram, working with a team of psychiatrists, psychologists, addiction counsellors and paramedical staff.</p></div>
<div class="bt reveal" style="--i:1"><b data-n="7">7</b><h3>Areas of care</h3><p>From de-addiction to personality disorders.</p></div>
<div class="bt reveal" style="--i:2"><b data-n="4">4</b><h3>Countries beyond India</h3><p>United Kingdom, Nepal, Bhutan and Afghanistan.</p></div>
<div class="bt award reveal" style="--i:1"><span class="medal">★</span><h3>Psychiatrist of the Year</h3><p>Economic Times, National</p></div>
<div class="bt reveal" style="--i:2"><b data-n="2">2</b><h3>Consulting rooms</h3><p>Hauz Khas, New Delhi · Sector 64, Gurugram</p></div>
<div class="bt wide reveal" style="--i:3"><h3>Online or in person</h3><p>Consultations are available online as well as at both consulting rooms.</p><a class="btn" href="#appoint">Book Consultation</a></div>
</div></section>
<section class="sec" id="work"><div class="head reveal"><span class="eyebrow">Areas of care</span><h2>What he treats</h2></div><div class="grid4">{cards}<a class="card svc cta-card reveal" href="#appoint"><h3>Not sure where to begin?</h3><p>Speaking to someone is not a last resort.</p><span class="btn">Book a consultation</span></a></div></section>
<section class="sec about" id="who"><div class="about__l"><div class="head reveal"><span class="eyebrow">About the doctor</span><h2>A steady hand</h2></div>
<p class="lead reveal">A practice built around the illnesses that take the longest to heal.</p>{"".join(f'<p class="reveal">{p}</p>' for p in ps)}
<figure class="reveal"><img src="assets/img/portrait-wide-col.webp?v6" alt="Dr. Gorav Gupta standing in his garden with arms folded, smiling." loading="lazy"></figure>
<dl class="facts reveal">{facts}</dl></div>
<div class="about__r"><div class="head reveal"><span class="eyebrow">The journey</span><h2>Five chapters</h2></div><ol class="tl">{jl}</ol></div></section>
<section class="quote"><blockquote class="reveal">“The objective of treatment is to make this patient functional so as to integrate them into society.”<cite>Dr. Gorav Gupta — on the objective of rehabilitation</cite></blockquote></section>
<section class="sec"><div class="head reveal"><span class="eyebrow">The record</span><h2>Credentials &amp; service</h2></div><div class="recs">{cols}</div></section>
<section class="sec" id="insights"><div class="head reveal row"><div><span class="eyebrow">Insights</span><h2>In the press</h2></div><div class="arrows"><button id="prev" aria-label="Previous">←</button><button id="next" aria-label="Next">→</button></div></div><div class="presses" id="car">{press}</div></section>
<section class="sec tint" id="pathway"><div class="head reveal"><span class="eyebrow">What to expect</span><h2>Coming in</h2></div><div class="steps">{steps}</div></section>
<section class="calm" id="contact"><div class="orb" aria-hidden="true"><span></span></div><div><span class="eyebrow">Talk to us</span><h2>You do not have to work it out on your own.</h2><p>Tulasi Healthcare is a phone call away. Call <a href="{TEL}">+91 88000 00255</a> to speak with the team about a consultation — for yourself or for someone close to you. In an emergency, contact local emergency services.</p></div></section>
<section class="sec faqs" id="questions"><div class="head reveal"><span class="eyebrow">Common questions</span><h2>Before you come in</h2></div><div class="faq">{faq}</div></section>
<section class="sec" id="appoint"><div class="book reveal"><div><span class="eyebrow">Book a consultation</span><h2>Your mind deserves care.</h2><p>Consultations available online</p><div class="cta"><a class="btn" href="{TEL}">Call +91 88000 00255</a><a class="btn ghost" href="{MAIL}">Write to us</a></div></div>
<div class="rooms"><div><h4>New Delhi</h4><p>2/6 Sarvapriya Vihar, New Delhi 110016</p></div><div><h4>Gurugram</h4><p>Gurjar Samrat Mihir Bhoj Rd, near Shriram Millennium School, Sector 64, Gurugram, Haryana 122102</p></div></div></div></section></main>
<footer><div class="f1"><b>Dr. Gorav Gupta</b><span>M.B.B.S. · M.D. Psychiatry</span><p>Senior psychiatrist — de-addiction, rehabilitation and dual diagnosis. New Delhi · Gurugram.</p></div>
<div><h5>Explore</h5>{links}</div>
<div><h5>Contact</h5><a href="{TEL}">+91 88000 00255</a><a href="{MAIL}">drgoravgupta@tulasihealthcare.com</a><a href="https://www.youtube.com/@tulasihealthcare" target="_blank" rel="noopener">YouTube</a></div>
<div><h5>Consulting rooms</h5><p>2/6 Sarvapriya Vihar, New Delhi 110016</p><p>Sector 64, Gurugram, Haryana 122102</p></div>
<div class="fb"><span>© 2026 Dr. Gorav Gupta</span><p>This website is for general information about Dr. Gupta’s practice and is not medical advice, diagnosis or treatment. If you or someone you know is in immediate danger, contact local emergency services. To reach Tulasi Healthcare, call +91 88000 00255.</p></div></footer>
<a class="sticky" href="{TEL}">Book a consultation</a><script src="assets/js/site.js?v5"></script></body></html>'''
open('index.html','w').write(page)
print(len(page),len(panes),len(ps),jl.count('<li'),press.count('<a'),faq.count('<details'),steps.count('step'))
