// Mobile menu toggle
const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');

menuToggle.addEventListener('click', () => {
  const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  menuToggle.setAttribute('aria-expanded', String(!isOpen));
  mobileMenu.hidden = isOpen;
  document.body.style.overflow = isOpen ? '' : 'hidden';
});

mobileMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    menuToggle.setAttribute('aria-expanded', 'false');
    mobileMenu.hidden = true;
    document.body.style.overflow = '';
  });
});

// FAQ accordion
document.querySelectorAll('.faq-item').forEach(item => {
  const btn = item.querySelector('.faq-q');
  btn.addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(open => {
      if (open !== item) {
        open.classList.remove('open');
        open.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
      }
    });
    item.classList.toggle('open', !isOpen);
    btn.setAttribute('aria-expanded', String(!isOpen));
  });
});

// Subtle scroll reveal, respects reduced motion
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReducedMotion && 'IntersectionObserver' in window) {
  const revealTargets = document.querySelectorAll(
    '.recognition-head, .rq, .definition-statement, .method-step, .lib-num, .faq-item, .final-statement'
  );
  revealTargets.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(14px)';
    el.style.transition = 'opacity 600ms ease, transform 600ms ease';
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2, rootMargin: '0px 0px -60px 0px' });

  revealTargets.forEach(el => observer.observe(el));
}

// Timeline fill: animate width in on view (05:00 sliver)
const timelineFill = document.querySelector('.timeline-fill');
if (timelineFill && !prefersReducedMotion && 'IntersectionObserver' in window) {
  const targetWidth = timelineFill.style.width;
  timelineFill.style.width = '0%';
  const tObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        timelineFill.style.transition = 'width 900ms ease';
        timelineFill.style.width = targetWidth;
        tObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  tObserver.observe(timelineFill);
}
