(function () {
  var d = document, w = window;
  var reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* header state, scroll progress, back-to-top */
  var nav = d.querySelector('header.nav'), bar = d.querySelector('.progress'), topBtn = d.querySelector('.top');
  function onScroll() {
    var y = w.scrollY, h = d.documentElement;
    if (nav) nav.classList.toggle('scrolled', y > 40);
    if (bar) bar.style.width = (y / Math.max(1, h.scrollHeight - h.clientHeight)) * 100 + '%';
    if (topBtn) topBtn.classList.toggle('show', y > 600);
  }
  onScroll();
  w.addEventListener('scroll', onScroll, { passive: true });
  if (topBtn) topBtn.addEventListener('click', function () { w.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });

  /* mobile drawer menu */
  var burger = d.querySelector('.burger'), menu = d.getElementById('menu');
  var scrim = d.createElement('div');
  scrim.className = 'scrim';
  d.body.appendChild(scrim);
  function setMenu(open) {
    if (!menu || !burger) return;
    menu.classList.toggle('open', open);
    burger.classList.toggle('on', open);
    scrim.classList.toggle('on', open);
    d.body.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', open);
  }
  if (burger) burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
  scrim.addEventListener('click', function () { setMenu(false); });
  if (menu) menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  w.addEventListener('resize', function () { if (w.innerWidth > 1080) setMenu(false); });

  /* scroll reveal (fade-in-up) with sibling stagger */
  var rvs = [].slice.call(d.querySelectorAll('.rv'));
  function settle(el) {
    // drop reveal classes so the element's own hover transitions take over
    el.classList.remove('rv', 'in', 'left', 'right', 'zoom');
    el.style.removeProperty('--d');
  }
  if (reduce || !('IntersectionObserver' in w)) {
    rvs.forEach(settle);
  } else {
    rvs.forEach(function (el) {
      var sibs = [].filter.call(el.parentElement.children, function (c) { return c.classList.contains('rv'); });
      el.style.setProperty('--d', Math.min(sibs.indexOf(el), 6));
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target, delay = +el.style.getPropertyValue('--d') || 0;
        io.unobserve(el);
        el.classList.add('in');
        setTimeout(function () { settle(el); }, 950 + delay * 110);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    rvs.forEach(function (el) { io.observe(el); });
  }

  /* animated counters */
  var counters = d.querySelectorAll('[data-count]');
  function finish(el) { el.textContent = el.dataset.count + (el.dataset.suffix || ''); }
  if (reduce || !('IntersectionObserver' in w)) {
    [].forEach.call(counters, finish);
  } else {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, end = +el.dataset.count, suf = el.dataset.suffix || '', t0 = null;
        (function step(t) {
          t0 = t0 || t;
          var p = Math.min((t - t0) / 1800, 1);
          el.textContent = Math.floor(end * (1 - Math.pow(1 - p, 3))) + suf;
          if (p < 1) requestAnimationFrame(step);
        })(performance.now());
      });
    }, { threshold: 0.5 });
    [].forEach.call(counters, function (el) { co.observe(el); });
  }

  /* ---------- premium layer ---------- */
  var html = d.documentElement, fine = w.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // preloader: hide after load (min 1.4s so the logo animation can finish, max 3s)
  if (!html.classList.contains('no-pre')) {
    var t0 = Date.now(), hide = function () { setTimeout(function () { html.classList.add('loaded'); }, Math.max(0, 1400 - (Date.now() - t0))); };
    if (d.readyState === 'complete') hide(); else w.addEventListener('load', hide);
    setTimeout(function () { html.classList.add('loaded'); }, 3000);
  }

  // hero headline: word-by-word mask reveal
  var h1 = d.querySelector('.hero h1');
  if (h1 && !reduce) {
    var i = 0;
    (function wrap(node, grad) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 1) return wrap(n, grad || n.classList.contains('grad-text'));
        if (n.nodeType !== 3) return;
        var frag = d.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) return frag.appendChild(d.createTextNode(part));
          var o = d.createElement('span'), inner = d.createElement('span');
          o.className = 'w'; inner.textContent = part; inner.style.setProperty('--i', i++);
          if (grad) inner.className = 'grad-text';
          o.appendChild(inner); frag.appendChild(o);
        });
        n.parentNode.replaceChild(frag, n);
      });
    })(h1, false);
    h1.querySelectorAll(':scope > .grad-text').forEach(function (s) { s.classList.remove('grad-text'); });
    h1.classList.remove('ld'); h1.classList.add('split-w');
  }

  if (fine && !reduce) {
    // mouse spotlight on dark bands
    d.querySelectorAll('.hero, .page-hero, section.dark, .auth, .dash').forEach(function (el) {
      el.setAttribute('data-spot', '');
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top) + 'px');
        el.classList.add('spot-on');
      });
      el.addEventListener('mouseleave', function () { el.classList.remove('spot-on'); });
    });
    // 3D tilt
    d.querySelectorAll('.qcard, .art').forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = 'perspective(1000px) rotateY(' + (x * 6) + 'deg) rotateX(' + (-y * 6) + 'deg)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
    // magnetic call-to-action buttons
    d.querySelectorAll('.hero-btns .btn, .cta .btn, .menu > .btn').forEach(function (b) {
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .25) + 'px,' + ((e.clientY - r.top - r.height / 2) * .35) + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }

  /* ---------- home audit card: two-step wizard ---------- */
  var qa = d.getElementById('quickAudit');
  if (qa) {
    var panes = qa.querySelectorAll('.q-pane'), qNext = qa.querySelector('.q-next'), qBack = qa.querySelector('.q-back'),
        qSubmit = qa.querySelector('.q-submit'), qCount = qa.querySelector('.q-count b');
    var go = function (n) {
      [].forEach.call(panes, function (p, i) { p.classList.toggle('on', i === n - 1); });
      qa.classList.toggle('step2', n === 2);
      qNext.hidden = n !== 1; qSubmit.hidden = n !== 2; qBack.hidden = n !== 2;
      qCount.textContent = '0' + n;
    };
    qa.classList.add('wiz'); go(1);
    qNext.addEventListener('click', function () { go(2); });
    qBack.addEventListener('click', function () { go(1); });
    // picking a service moves on automatically, like a guided funnel
    qa.querySelectorAll('input[name=service]').forEach(function (r) {
      r.addEventListener('change', function () { setTimeout(function () { go(2); }, 350); });
    });
  }

  /* ---------- login dropdown ---------- */
  var dd = d.getElementById('account');
  if (dd) {
    var ddBtn = dd.querySelector('.dd-btn');
    ddBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !dd.classList.contains('open');
      dd.classList.toggle('open', open); ddBtn.setAttribute('aria-expanded', open);
    });
    d.addEventListener('click', function (e) { if (!dd.contains(e.target)) { dd.classList.remove('open'); ddBtn.setAttribute('aria-expanded', false); } });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') dd.classList.remove('open'); });
  }

  /* ---------- API helpers ---------- */
  function api(path, body) {
    return fetch(path, body === undefined ? { credentials: 'same-origin' } : {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().catch(function () { throw new Error('offline'); }).then(function (j) { j._status = r.status; return j; });
    }, function () { throw new Error('offline'); });
  }
  var OFFLINE = 'Accounts need the Raventon server. Start it with: python server.py';
  function showMsg(form, text, good) {
    var m = form.querySelector('.form-msg');
    if (!m) return;
    m.textContent = text; m.hidden = !text; m.classList.toggle('good', !!good);
  }
  function busy(btn, on) {
    btn.classList.toggle('loading', on); btn.disabled = on;
    var sp = btn.querySelector('.spinner');
    if (on && !sp) { sp = d.createElement('span'); sp.className = 'spinner'; btn.appendChild(sp); }
    if (!on && sp) sp.remove();
  }
  function formData(form) {
    var o = {};
    [].forEach.call(form.elements, function (el) {
      if (!el.name || (el.type === 'radio' && !el.checked)) return;
      o[el.name] = el.type === 'checkbox' ? el.checked : el.value;
    });
    return o;
  }

  // signed-in state in the header
  var me = null;
  api('/api/me').then(function (j) {
    if (!j.user) return;
    me = j.user;
    if (dd) {
      dd.querySelector('.dd-label').textContent = me.full_name.split(' ')[0];
      dd.querySelector('.dd-guest').hidden = true;
      dd.querySelector('.dd-user').hidden = false;
    }
  }).catch(function () {}).then(renderDashboard);

  d.addEventListener('click', function (e) {
    if (!e.target.closest('.js-logout')) return;
    api('/api/logout', {}).catch(function () {}).then(function () { location.href = 'index.html'; });
  });

  // password visibility toggles
  d.querySelectorAll('.pw-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var inp = b.parentNode.querySelector('input'), show = inp.type === 'password';
      inp.type = show ? 'text' : 'password'; b.classList.toggle('on', show);
      b.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });

  // login + register forms
  d.querySelectorAll('form[data-auth]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = formData(form), btn = form.querySelector('button[type=submit]');
      data.role = form.dataset.role;
      form.querySelectorAll('.bad').forEach(function (x) { x.classList.remove('bad'); });
      var bad = [].filter.call(form.querySelectorAll('input[required], select[required]'), function (el) { return !el.checkValidity(); });
      bad.forEach(function (el) { el.classList.add('bad'); });
      if (bad.length) return showMsg(form, bad[0].type === 'checkbox' ? 'Please accept the terms to continue.' : 'Please fill in the highlighted fields correctly.');
      if (form.dataset.auth === 'register' && data.password !== data.confirm) {
        form.querySelector('[name=confirm]').classList.add('bad');
        return showMsg(form, 'Passwords do not match.');
      }
      showMsg(form, ''); busy(btn, true);
      api('/api/' + (form.dataset.auth === 'login' ? 'login' : 'register'), data).then(function (j) {
        if (j.ok) { showMsg(form, form.dataset.auth === 'login' ? 'Signed in. Redirecting…' : 'Account created. Redirecting…', true); location.href = j.redirect || 'dashboard.html'; return; }
        busy(btn, false); showMsg(form, j.error || 'Something went wrong. Please try again.');
      }, function () { busy(btn, false); showMsg(form, OFFLINE); });
    });
  });

  // dashboard
  function renderDashboard() {
    var app = d.getElementById('dashApp');
    if (!app) return;
    d.getElementById('dashLoading').hidden = true;
    if (!me) { d.getElementById('dashGuest').hidden = false; return; }
    var pub = me.role === 'publisher', since = new Date((me.created_at || '').replace(' ', 'T') + 'Z');
    var f = {
      role_label: (pub ? 'Publisher' : 'Advertiser') + ' account', first_name: me.full_name.split(' ')[0],
      since: isNaN(since) ? '' : since.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' }),
      details_label: pub ? 'Traffic source' : 'Monthly budget'
    };
    ['full_name', 'company', 'email', 'phone', 'website', 'details', 'account_type'].forEach(function (k) { f[k] = me[k] || '—'; });
    f.location = [me.address, me.city, me.state, me.country].filter(Boolean).join(', ') || '—';
    app.querySelectorAll('[data-f]').forEach(function (el) { el.textContent = f[el.dataset.f]; });
    app.hidden = false;
  }

  /* contact form: prefill from the home quick-audit card, save to the database */
  var form = d.getElementById('contactForm');
  if (form) {
    var q = new URLSearchParams(location.search);
    ['service', 'budget'].forEach(function (k) {
      var v = q.get(k), sel = form.querySelector('[name="' + k + '"]');
      if (!v || !sel) return;
      [].forEach.call(sel.options, function (o) { if (o.text === v) sel.value = o.value; });
    });
    form.setAttribute('novalidate', '');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = d.getElementById('formOk'), btn = form.querySelector('button[type=submit]');
      form.querySelectorAll('.bad').forEach(function (x) { x.classList.remove('bad'); });
      var bad = [].filter.call(form.querySelectorAll('[required]'), function (el) { return !el.checkValidity(); });
      bad.forEach(function (el) { el.classList.add('bad'); });
      if (bad.length) return showMsg(form, 'Please fill in the highlighted fields correctly.');
      showMsg(form, ''); ok.style.display = 'none'; busy(btn, true);
      api('/api/contact', formData(form)).then(function (j) {
        busy(btn, false);
        if (j.ok) { ok.style.display = 'block'; form.reset(); } else showMsg(form, j.error || 'Something went wrong.');
      }, function () { busy(btn, false); showMsg(form, OFFLINE); });
    });
  }
})();
