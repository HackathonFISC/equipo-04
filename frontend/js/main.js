/* ==========================================================================
   AquaAlerta Admin Simple — JavaScript compartido
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  initSmoothScroll();
  initHeaderScroll();
  initTabs();
});

/* --- Partículas de fondo --- */
function initParticles() {
  const container = document.getElementById('particles');
  if (!container) return;

  const count = window.innerWidth < 768 ? 14 : 24;

  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';

    const size = Math.random() * 40 + 10;
    p.style.width = `${size}px`;
    p.style.height = `${size}px`;
    p.style.left = `${Math.random() * 100}%`;
    p.style.top = `${Math.random() * 100}%`;
    p.style.animationDelay = `${Math.random() * 5}s`;
    p.style.animationDuration = `${Math.random() * 20 + 10}s`;

    container.appendChild(p);
  }
}

/* --- Scroll suave --- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
      }
    });
  });
}

/* --- Efecto header --- */
function initHeaderScroll() {
  const header = document.getElementById('header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 100) {
      header.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
    } else {
      header.style.boxShadow = 'none';
    }
  });
}

/* --- Tabs para gestión.html --- */
function initTabs() {
  const btns = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  function selectTab(target) {
    const panel = Array.from(panels).find((item) => item.id === target);
    const button = Array.from(btns).find((item) => item.getAttribute('data-target') === target);
    if (!panel || !button) return false;

    btns.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle('active', isActive);
      item.setAttribute('aria-selected', String(isActive));
    });

    panels.forEach((item) => {
      const isActive = item === panel;
      item.classList.toggle('hidden', !isActive);
      item.style.display = isActive ? 'block' : 'none';
    });
    return true;
  }

  btns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');
      if (selectTab(target)) {
        window.history.replaceState(null, '', `#${target}`);
      }
    });
  });

  if (btns.length && panels.length) {
    const initialTarget = window.location.hash.slice(1);
    if (!selectTab(initialTarget)) {
      selectTab(btns[0].getAttribute('data-target'));
    }
    window.addEventListener('hashchange', () => {
      selectTab(window.location.hash.slice(1));
    });
  }
}

/* --- Toast global --- */
window.showToast = function (type, title, message) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = type === 'success' ? '✔' : type === 'error' ? '✖' : 'ℹ';
  toast.innerHTML = `<strong>${icon} ${title}</strong>${message ? `<br><small style="opacity:0.8;">${message}</small>` : ''}`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};
