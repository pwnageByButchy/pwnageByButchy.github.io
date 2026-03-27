/**
 * pwnage by Butchy — Site JavaScript
 * Author: Steve Bartimote
 * © Steve Bartimote. All rights reserved.
 */

// Dropdown menus — aria-expanded toggle
(function initDropdowns() {
  const triggers = document.querySelectorAll('.nav-link-parent[aria-expanded]');
  function closeAll() {
    triggers.forEach((t) => t.setAttribute('aria-expanded', 'false'));
  }
  function onTriggerClick() {
    const wasOpen = this.getAttribute('aria-expanded') === 'true';
    closeAll();
    if (!wasOpen) this.setAttribute('aria-expanded', 'true');
  }
  triggers.forEach((t) => t.addEventListener('click', onTriggerClick));
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
