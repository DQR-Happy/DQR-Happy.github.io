(() => {
  'use strict';
  document.documentElement.classList.replace('no-js', 'js');
  const english = document.documentElement.lang === 'en';
  const themeButton = document.querySelector('.theme-toggle');
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem('qd-theme'); } catch (_) { /* storage optional */ }
  function applyTheme(dark) {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    const browserColor = document.querySelector('meta[name="theme-color"]');
    if (browserColor) browserColor.content = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
    if (themeButton) {
      themeButton.setAttribute('aria-label', english ? (dark ? 'Switch to light theme' : 'Switch to dark theme') : (dark ? '切换浅色主题' : '切换深色主题'));
      themeButton.setAttribute('aria-pressed', String(dark));
    }
  }
  applyTheme(preference ? preference === 'dark' : media.matches);
  themeButton?.addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme !== 'dark';
    preference = dark ? 'dark' : 'light';
    try { localStorage.setItem('qd-theme', preference); } catch (_) { /* storage optional */ }
    applyTheme(dark);
  });
  media.addEventListener('change', e => { if (!preference) applyTheme(e.matches); });

  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  function closeMenu() { if (nav && menu) { nav.dataset.open = 'false'; menu.setAttribute('aria-expanded', 'false'); } }
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.dataset.open = String(open);
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav?.dataset.open === 'true') { closeMenu(); menu.focus(); } });
  nav?.addEventListener('click', e => { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('click', e => { if (!e.target.closest('.header-inner')) closeMenu(); });

  const search = document.querySelector('#project-search');
  const filters = Array.from(document.querySelectorAll('.filter'));
  const projects = Array.from(document.querySelectorAll('.project-detail'));
  const status = document.querySelector('#filter-status');
  if (projects.length) {
    const params = new URLSearchParams(location.search);
    let category = params.get('category') || 'all';
    if (!filters.some(b => b.dataset.filter === category)) category = 'all';
    search.value = params.get('q') || '';
    function filter(updateUrl = true) {
      const query = search.value.trim().toLocaleLowerCase();
      let count = 0;
      projects.forEach(project => {
        const shown = (category === 'all' || project.dataset.category === category) && project.textContent.toLocaleLowerCase().includes(query);
        project.hidden = !shown;
        if (shown) count++;
      });
      filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === category)));
      status.textContent = english ? `${count} of ${projects.length} projects` : `显示 ${count} / ${projects.length} 个项目`;
      document.querySelector('#empty-projects').hidden = count !== 0;
      if (updateUrl) {
        const url = new URL(location.href);
        category === 'all' ? url.searchParams.delete('category') : url.searchParams.set('category', category);
        query ? url.searchParams.set('q', search.value.trim()) : url.searchParams.delete('q');
        history.replaceState(null, '', url);
      }
    }
    filters.forEach(b => b.addEventListener('click', () => { category = b.dataset.filter; filter(); }));
    search.addEventListener('input', e => { if (!e.isComposing) filter(); });
    search.addEventListener('compositionend', () => filter());
    document.querySelector('#clear-filters')?.addEventListener('click', () => { category = 'all'; search.value = ''; filter(); search.focus(); });
    filter(false);
  }

  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const content = document.getElementById(button.dataset.copy);
      const feedback = button.nextElementSibling;
      try {
        await navigator.clipboard.writeText(content.textContent);
        feedback.textContent = english ? 'Copied to clipboard.' : '已复制到剪贴板。';
      } catch (_) {
        feedback.textContent = english ? 'Select and copy the text below.' : '请选中下方文本手动复制。';
      }
    });
  });
  document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
})();
