document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('nav');
  const toggle = document.querySelector('.menu-toggle');
  if (toggle && nav) toggle.addEventListener('click', () => nav.classList.toggle('open'));

  const reveals = document.querySelectorAll('.reveal, .glass-card, .value-card, .dash-cards div');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });
  reveals.forEach(el => { el.classList.add('reveal'); io.observe(el); });

  document.querySelectorAll('[data-counter]').forEach((el) => {
    const end = Number(el.dataset.counter || el.textContent || 0);
    let start = 0;
    const step = Math.max(1, Math.ceil(end / 38));
    const tick = () => {
      start = Math.min(end, start + step);
      el.textContent = start;
      if (start < end) requestAnimationFrame(tick);
    };
    tick();
  });

  const ratingInput = document.querySelector('input[name="rating_value"]');
  const oldSelect = document.querySelector('select[name="rating"]');
  const ratingButtons = document.querySelectorAll('.rating-widget button');
  function setRating(value) {
    if (ratingInput) ratingInput.value = value;
    if (oldSelect) oldSelect.value = value;
    ratingButtons.forEach(btn => btn.classList.toggle('active', Number(btn.dataset.value) <= Number(value)));
  }
  ratingButtons.forEach(btn => btn.addEventListener('click', (e) => { e.preventDefault(); setRating(btn.dataset.value); }));
  if (ratingButtons.length) setRating(5);

  document.querySelectorAll('textarea[maxlength]').forEach((area) => {
    const counter = document.createElement('div');
    counter.className = 'char-count';
    area.insertAdjacentElement('afterend', counter);
    const update = () => counter.textContent = `${area.value.length}/${area.maxLength}`;
    area.addEventListener('input', update); update();
  });

  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  document.querySelectorAll('[data-href]').forEach((card) => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('a, button, input, textarea, select, form')) return;
      window.location.href = card.dataset.href;
    });
  });
});
