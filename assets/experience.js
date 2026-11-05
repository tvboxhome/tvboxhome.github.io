(() => {
  const image = document.querySelector('.hero-screen img');
  const buttons = [...document.querySelectorAll('.screen-choice')];
  let requested = 0;
  buttons.forEach(button => button.addEventListener('click', () => {
    if (!image || button.getAttribute('aria-pressed') === 'true') return;
    const ticket = ++requested;
    const candidate = new Image();
    button.disabled = true;
    candidate.onload = () => {
      button.disabled = false;
      if (ticket !== requested) return;
      image.src = candidate.src;
      image.alt = button.dataset.alt;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    };
    candidate.onerror = () => { button.disabled = false; };
    candidate.src = '/assets/screenshots/web/' + button.dataset.screen;
  }));
  const menu = document.querySelector('.mobile-nav');
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { menu.open = false; }));
  menu?.addEventListener('keydown', event => {
    if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); }
  });
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('just-visible');
      observer.unobserve(entry.target);
    }), { threshold: .12 });
    document.querySelectorAll('.benefit,.download-card,.news-card').forEach(el => observer.observe(el));
  }
})();
