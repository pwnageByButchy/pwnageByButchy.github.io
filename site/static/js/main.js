/**
 * pwnage by Butchy — Site JavaScript
 * Author: Steve Bartimote
 * © Steve Bartimote. All rights reserved.
 */

// Click-toggle dropdown menus; close when clicking outside
(function initDropdowns() {
  const dropdowns = document.querySelectorAll('.nav-item--dropdown');
  dropdowns.forEach((item) => {
    const trigger = item.querySelector('.nav-link-parent');
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const isOpen = item.classList.contains('open');
      // Close all other dropdowns first
      dropdowns.forEach((d) => d.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item--dropdown')) {
      dropdowns.forEach((d) => d.classList.remove('open'));
    }
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
