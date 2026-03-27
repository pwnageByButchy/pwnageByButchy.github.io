/**
 * pwnage by Butchy — Site JavaScript
 * Author: Steve Bartimote
 * © Steve Bartimote. All rights reserved.
 */

// Dropdown menus — class-driven toggle, aria-expanded for accessibility
(function initDropdowns() {
  const items = document.querySelectorAll('.nav-item--dropdown');
  function closeAll() {
    items.forEach((el) => {
      el.classList.remove('open');
      el.querySelector('.nav-link-parent').setAttribute('aria-expanded', 'false');
    });
  }
  items.forEach((item) => {
    const btn = item.querySelector('.nav-link-parent');
    btn.addEventListener('click', () => {
      const wasOpen = item.classList.contains('open');
      closeAll();
      if (!wasOpen) {
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item--dropdown')) closeAll();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAll();
  });
})();

// Highlight active nav link based on current path
(function markActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.site-nav a').forEach((link) => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });
})();
