/**
 * pwnage by Butchy — Site JavaScript
 * Author: Steve Bartimote
 * © Steve Bartimote. All rights reserved.
 */

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
