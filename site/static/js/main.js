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

// Contact form — async submission via Web3Forms
(function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;
  const btn    = form.querySelector('.contact-submit');
  const result = document.getElementById('contact-result');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    btn.disabled = true;
    btn.textContent = 'Sending…';
    result.textContent = '';
    result.className = 'contact-result';

    try {
      const res  = await fetch('https://api.web3forms.com/submit', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body:    JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        result.textContent = 'Message sent — thanks, I\'ll be in touch.';
        result.classList.add('contact-result--success');
        form.reset();
      } else {
        throw new Error(data.message || 'Submission failed.');
      }
    } catch (err) {
      result.textContent = 'Something went wrong. Please try again or reach out on LinkedIn.';
      result.classList.add('contact-result--error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Send Message';
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
