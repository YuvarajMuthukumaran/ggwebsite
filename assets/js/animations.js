// Advanced Cinematic Animations with GSAP
(function() {
  // Register GSAP plugins
  gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

  // Enable custom cursor only on desktop without reduced motion
  const enableCursor = !prefersReducedMotion && !isTouchDevice;
  if (enableCursor) {
    document.body.classList.add('cursor-active');
  }

  // ============================================
  // PAGE LOADER
  // ============================================
  const initPageLoader = () => {
    const loader = document.querySelector('.page-loader');
    if (!loader) return;

    const tl = gsap.timeline({
      onComplete: () => {
        loader.classList.add('hidden');
        initHeroAnimations();
      }
    });

    tl.from('.loader-logo', {
      scale: 0,
      rotation: -180,
      opacity: 0,
      duration: 0.6,
      ease: 'back.out(1.7)'
    })
    .from('.loader-text', {
      y: 20,
      opacity: 0,
      duration: 0.4,
      ease: 'power2.out'
    }, '-=0.3')
    .from('.loader-bar', {
      width: 0,
      duration: 0.8,
      ease: 'power2.inOut'
    }, '-=0.2');
  };

  // ============================================
  // CUSTOM CURSOR
  // ============================================
  const initCustomCursor = () => {
    if (!enableCursor) return;

    const cursor = document.querySelector('.custom-cursor');
    const dot = cursor.querySelector('.cursor-dot');
    const ring = cursor.querySelector('.cursor-ring');
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;
    let ringX = 0, ringY = 0;

    // Track mouse position
    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    // Smooth cursor animation - faster
    gsap.ticker.add(() => {
      const dt = 1.0;
      cursorX += (mouseX - cursorX) * 0.95;
      cursorY += (mouseY - cursorY) * 0.95;
      ringX += (mouseX - ringX) * 0.25;
      ringY += (mouseY - ringY) * 0.25;

      gsap.set(dot, { x: cursorX, y: cursorY });
      gsap.set(ring, { x: ringX, y: ringY });
    });

    // Hover effects for interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .card, .btn, details summary');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('hovering'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('hovering'));
    });
  };

  // ============================================
  // HERO SECTION ANIMATIONS
  // ============================================
  const initHeroAnimations = () => {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    const tl = gsap.timeline();

    // Text reveal - faster and snappier
    tl.from('.giant span', {
      y: 60,
      opacity: 0,
      duration: 0.6,
      ease: 'power3.out'
    })
    .from('.qual', {
      x: 30,
      opacity: 0,
      duration: 0.4,
      ease: 'power2.out'
    }, '-=0.3')
    .from('.cut', {
      y: 60,
      opacity: 0,
      scale: 0.95,
      duration: 0.7,
      ease: 'power2.out'
    }, '-=0.4')
    .from('.hero__l', {
      y: 30,
      opacity: 0,
      duration: 0.4,
      ease: 'power2.out'
    }, '-=0.3')
    .from('.stats', {
      y: 30,
      opacity: 0,
      duration: 0.4,
      ease: 'power2.out'
    }, '-=0.2')
    .from('.fl', {
      scale: 0,
      opacity: 0,
      duration: 0.3,
      stagger: 0.1,
      ease: 'back.out(1.7)'
    }, '-=0.2');

    // Parallax effect on scroll - faster scrub
    if (!prefersReducedMotion) {
      gsap.to('.cut', {
        yPercent: 15,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 0.5
        }
      });

      gsap.to('.giant', {
        yPercent: -20,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 0.5
        }
      });
    }
  };

  // ============================================
  // SCROLL-TRIGGERED SECTION REVEALS
  // ============================================
  const initScrollReveals = () => {
    if (prefersReducedMotion) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
      return;
    }

    // Standard reveal animations - much faster
    gsap.utils.toArray('.reveal').forEach((el, i) => {
      gsap.fromTo(el,
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 90%',
            toggleActions: 'play none none reverse'
          },
          delay: i * 0.05
        }
      );
    });

    // Left reveal
    gsap.utils.toArray('.reveal-left').forEach((el, i) => {
      gsap.fromTo(el,
        { x: -50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.5,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 90%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    });

    // Right reveal
    gsap.utils.toArray('.reveal-right').forEach((el, i) => {
      gsap.fromTo(el,
        { x: 50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.5,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 90%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    });

    // Scale reveal
    gsap.utils.toArray('.reveal-scale').forEach((el, i) => {
      gsap.fromTo(el,
        { scale: 0.9, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.5,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 90%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    });
  };

  // ============================================
  // MOSAIC / BENTO GRID ANIMATIONS
  // ============================================
  const initMosaicAnimations = () => {
    const mosaicItems = document.querySelectorAll('.mt');
    if (mosaicItems.length === 0) return;

    mosaicItems.forEach((item, i) => {
      gsap.fromTo(item,
        { y: 50, opacity: 0, scale: 0.95 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.5,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: item,
            start: 'top 90%',
            toggleActions: 'play none none reverse'
          },
          delay: i * 0.06
        }
      );
    });

    // Radar gauge animation - faster
    const radar = document.querySelector('.m-radar');
    if (radar && !prefersReducedMotion) {
      gsap.fromTo('.gauge-line',
        { rotation: -180 },
        {
          rotation: 0,
          duration: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: radar,
            start: 'top 80%'
          }
        }
      );
    }
  };

  // ============================================
  // CARD INTERACTIONS WITH MAGNETIC EFFECT
  // ============================================
  const initCardInteractions = () => {
    if (isTouchDevice || prefersReducedMotion) return;

    const cards = document.querySelectorAll('.card, .rec, .press, .mt');

    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        // Set CSS variable for glow effect
        card.style.setProperty('--x', `${e.clientX - rect.left}px`);
        card.style.setProperty('--y', `${e.clientY - rect.top}px`);

        gsap.to(card, {
          x: x * 0.04,
          y: y * 0.04 - 8,
          duration: 0.15,
          ease: 'power1.out'
        });
      });

      card.addEventListener('mouseleave', () => {
        gsap.to(card, {
          x: 0,
          y: 0,
          duration: 0.3,
          ease: 'power2.out'
        });
      });
    });
  };

  // ============================================
  // MAGNETIC BUTTONS
  // ============================================
  const initMagneticButtons = () => {
    if (isTouchDevice || prefersReducedMotion) return;

    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        // Set CSS variable for glow effect
        btn.style.setProperty('--x', `${e.clientX - rect.left}px`);
        btn.style.setProperty('--y', `${e.clientY - rect.top}px`);

        gsap.to(btn, {
          x: x * 0.25,
          y: y * 0.25,
          duration: 0.15,
          ease: 'power1.out'
        });
      });

      btn.addEventListener('mouseleave', () => {
        gsap.to(btn, {
          x: 0,
          y: 0,
          duration: 0.25,
          ease: 'power2.out'
        });
      });
    });
  };

  // ============================================
  // IMAGE PARALLAX
  // ============================================
  const initImageParallax = () => {
    if (prefersReducedMotion) return;

    const images = document.querySelectorAll('.about figure img, .m-photo img, .m-award img');

    images.forEach(img => {
      gsap.to(img, {
        yPercent: 15,
        ease: 'none',
        scrollTrigger: {
          trigger: img.parentElement,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true
        }
      });
    });
  };

  // ============================================
  // NUMBER COUNTER ANIMATIONS
  // ============================================
  const initCounterAnimations = () => {
    if (prefersReducedMotion) return;

    const counters = document.querySelectorAll('[data-n]');

    counters.forEach(counter => {
      const target = parseFloat(counter.dataset.n);
      const suffix = counter.dataset.s || '';

      gsap.fromTo(counter,
        { textContent: 0 },
        {
          textContent: target,
          duration: 1,
          ease: 'power2.out',
          snap: { textContent: 1 },
          scrollTrigger: {
            trigger: counter,
            start: 'top 85%'
          },
          onUpdate: function() {
            counter.textContent = Math.round(this.targets()[0].textContent) + suffix;
          }
        }
      );
    });
  };

  // ============================================
  // FAQ ACCORDION ANIMATIONS
  // ============================================
  const initFAQAnimations = () => {
    const details = document.querySelectorAll('details');

    details.forEach(detail => {
      const summary = detail.querySelector('summary');
      const content = detail.querySelector('p');

      summary.addEventListener('click', (e) => {
        e.preventDefault();

        const isOpen = detail.hasAttribute('open');

        // Close all other details
        details.forEach(d => {
          if (d !== detail && d.hasAttribute('open')) {
            gsap.to(d.querySelector('p'), {
              height: 0,
              opacity: 0,
              duration: 0.25,
              ease: 'power2.inOut',
              onComplete: () => d.removeAttribute('open')
            });
          }
        });

        if (isOpen) {
          gsap.to(content, {
            height: 0,
            opacity: 0,
            duration: 0.25,
            ease: 'power2.inOut',
            onComplete: () => detail.removeAttribute('open')
          });
        } else {
          detail.setAttribute('open', '');
          gsap.fromTo(content,
            { height: 0, opacity: 0 },
            {
              height: 'auto',
              opacity: 1,
              duration: 0.3,
              ease: 'power2.out'
            }
          );
        }
      });
    });
  };

  // ============================================
  // SMOOTH SCROLL FOR NAVIGATION
  // ============================================
  const initSmoothScroll = () => {
    const navLinks = document.querySelectorAll('.nav nav a[href^="#"]');

    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
          gsap.to(window, {
            duration: 0.8,
            scrollTo: {
              y: target,
              offsetY: 80
            },
            ease: 'power2.inOut'
          });
        }
      });
    });
  };

  // ============================================
  // NAVIGATION SCROLL EFFECTS
  // ============================================
  const initNavEffects = () => {
    const nav = document.querySelector('.nav');
    if (!nav) return;

    ScrollTrigger.create({
      start: 'top -80',
      end: 99999,
      toggleClass: { className: 'on', targets: nav }
    });
  };

  // ============================================
  // TIMELINE ANIMATIONS
  // ============================================
  const initTimelineAnimations = () => {
    const timelineItems = document.querySelectorAll('.tl li');

    timelineItems.forEach((item, i) => {
      gsap.fromTo(item,
        { x: -50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: item,
            start: 'top 85%',
            toggleActions: 'play none none reverse'
          },
          delay: i * 0.08
        }
      );
    });
  };

  // ============================================
  // QUOTE SECTION ANIMATION
  // ============================================
  const initQuoteAnimation = () => {
    const quote = document.querySelector('.quote');
    if (!quote) return;

    gsap.fromTo(quote,
      { scale: 0.95, opacity: 0 },
      {
        scale: 1,
        opacity: 1,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: quote,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        }
      }
    );
  };

  // ============================================
  // PRESS CAROUSEL ENHANCEMENT
  // ============================================
  const initPressCarousel = () => {
    const carousel = document.getElementById('car');
    if (!carousel) return;

    const pressItems = carousel.querySelectorAll('.press');

    pressItems.forEach((item, i) => {
      gsap.fromTo(item,
        { x: 100, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: carousel,
            start: 'top 85%'
          },
          delay: i * 0.05
        }
      );
    });
  };

  // ============================================
  // STAGE CARDS ANIMATION
  // ============================================
  const initStageAnimations = () => {
    const stages = document.querySelectorAll('.stg');

    stages.forEach((stage, i) => {
      gsap.fromTo(stage,
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: stage,
            start: 'top 85%'
          },
          delay: i * 0.08
        }
      );
    });
  };

  // ============================================
  // BACKGROUND PARTICLE EFFECT
  // ============================================
  const initParticleEffect = () => {
    if (prefersReducedMotion) return;

    // Create floating particles
    const hero = document.querySelector('.hero__in');
    if (!hero) return;

    for (let i = 0; i < 15; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.cssText = `
        position: absolute;
        width: ${Math.random() * 6 + 2}px;
        height: ${Math.random() * 6 + 2}px;
        background: rgba(47, 111, 203, ${Math.random() * 0.3 + 0.1});
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        pointer-events: none;
      `;
      hero.appendChild(particle);

      gsap.to(particle, {
        y: -200 - Math.random() * 300,
        x: (Math.random() - 0.5) * 100,
        opacity: 0,
        duration: 8 + Math.random() * 4,
        repeat: -1,
        ease: 'none',
        delay: Math.random() * 2
      });
    }
  };

  // ============================================
  // SECTION HEADER ANIMATIONS
  // ============================================
  const initHeaderAnimations = () => {
    const headers = document.querySelectorAll('.head');

    headers.forEach(header => {
      const eyebrow = header.querySelector('.eyebrow');
      const heading = header.querySelector('h2');

      if (eyebrow) {
        gsap.fromTo(eyebrow,
          { y: 30, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 0.4,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: header,
              start: 'top 85%'
            }
          }
        );
      }

      if (heading) {
        gsap.fromTo(heading,
          { y: 40, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 0.4,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: header,
              start: 'top 85%'
            },
            delay: 0.05
          }
        );
      }
    });
  };

  // ============================================
  // FOOTER ANIMATION
  // ============================================
  const initFooterAnimation = () => {
    const footer = document.querySelector('footer');
    if (!footer) return;

    gsap.fromTo(footer,
      { y: 50, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: footer,
          start: 'top 95%'
        }
      }
    );
  };

  // ============================================
  // INITIALIZE ALL ANIMATIONS
  // ============================================
  const initAll = () => {
    initPageLoader();
    initCustomCursor();
    initScrollReveals();
    initMosaicAnimations();
    initCardInteractions();
    initMagneticButtons();
    initImageParallax();
    initCounterAnimations();
    initFAQAnimations();
    initSmoothScroll();
    initNavEffects();
    initTimelineAnimations();
    initQuoteAnimation();
    initPressCarousel();
    initStageAnimations();
    initParticleEffect();
    initHeaderAnimations();
    initFooterAnimation();
  };

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

})();
