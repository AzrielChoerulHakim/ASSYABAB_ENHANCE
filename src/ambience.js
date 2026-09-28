/* A little wind and a quiet stream. All audio is synthesized locally, not a field recording. */
(() => {
  'use strict';
  if (window.AssyababAmbience) return;

  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const layers = [];
  const leafPath = 'M2 15C4 5 14 2 25 3C23 14 15 21 2 15ZM2 15L21 6';
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3C9 7 6 10 6 14a6 6 0 0 0 12 0c0-4-3-7-6-11Z"/><path d="M9 14a3 3 0 0 0 3 3"/><path class="ambience-sound-slash" d="m4 4 16 16"/></svg>';

  function leaf(layer, x, y, size, delay, duration, direction = 1) {
    const item = document.createElement('span');
    item.className = 'ambience-leaf';
    item.style.cssText = `left:${x}%;top:${y}%;width:${size}px;--ambience-delay:${delay}s;--ambience-duration:${duration}s;--ambience-direction:${direction}`;
    item.innerHTML = `<svg viewBox="0 0 28 24"><path d="${leafPath}"/></svg>`;
    layer.append(item);
  }

  function decorate(section, kind) {
    if (!section) return;
    const layer = document.createElement('div');
    layer.className = `ambience-layer ambience-${kind}`;
    layer.setAttribute('aria-hidden', 'true');
    if (kind === 'hero') {
      leaf(layer, 8, 52, 17, -9, 29);
      leaf(layer, 87, 43, 12, -20, 33, -1);
      leaf(layer, 79, 65, 15, -3, 37, -1);
    } else {
      leaf(layer, 12, 44, 13, -14, 36);
      leaf(layer, 85, 25, 10, -8, 41, -1);
      const ripple = document.createElement('span');
      ripple.className = 'ambience-ripples';
      ripple.innerHTML = '<i></i><i></i><i></i>';
      layer.append(ripple);
    }
    section.append(layer);
    layers.push(layer);
  }

  decorate(document.getElementById('beranda'), 'hero');
  decorate(document.getElementById('kehidupan'), 'daily');

  function syncMotion() {
    const quiet = motionPreference.matches || document.body.classList.contains('reduced-motion');
    layers.forEach(layer => {
      layer.classList.toggle('ambience-still', quiet);
      layer.classList.toggle('ambience-page-hidden', document.hidden);
    });
  }
  const bodyObserver = new MutationObserver(syncMotion);
  bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });
  motionPreference.addEventListener?.('change', syncMotion);
  if ('IntersectionObserver' in window) {
    const visibleObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.target.classList.toggle('ambience-offscreen', !entry.isIntersecting));
    });
    layers.forEach(layer => visibleObserver.observe(layer));
  }
  syncMotion();

  const dock = document.createElement('div');
  dock.className = 'ambience-dock';
  dock.setAttribute('role', 'group');
  dock.setAttribute('aria-label', 'Suasana suara');
  dock.innerHTML = `
    <button class="ambience-toggle" type="button" aria-pressed="false" aria-label="Putar suara air">
      ${icon}<span>Suara air</span><i class="ambience-live-dot" aria-hidden="true"></i>
    </button>
    <button class="ambience-settings" type="button" aria-label="Atur volume suara air" aria-controls="ambience-panel" aria-expanded="false">
      <svg viewBox="0 0 18 18" aria-hidden="true"><path d="m5 11 4-4 4 4"/></svg>
    </button>
    <div class="ambience-panel" id="ambience-panel" hidden>
      <div class="ambience-panel-heading"><span>Gemericik pelan.</span><span class="ambience-volume-value">35%</span></div>
      <label for="ambience-volume">Volume suara air</label>
      <input id="ambience-volume" type="range" min="0" max="100" step="1" value="35" aria-valuetext="35 persen">
      <p>Teman tenang untuk menjelajah.</p>
    </div>
    <span class="ambience-status" role="status" aria-live="polite"></span>`;
  document.body.append(dock);

  const toggle = dock.querySelector('.ambience-toggle');
  const settings = dock.querySelector('.ambience-settings');
  const panel = dock.querySelector('.ambience-panel');
  const volume = dock.querySelector('input');
  const status = dock.querySelector('.ambience-status');
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  let context = null;
  let master = null;
  let source = null;
  let enabled = false;
  let suspendedByPage = false;
  let level = 0.35;
  let suspendTimer = 0;
  let epoch = 0;
  let error = null;

  // Seeded noise keeps this an original, offline soundscape with no downloaded audio.
  function random(seed) {
    return () => {
      seed = (Math.imul(seed, 1664525) + 1013904223) | 0;
      return (seed >>> 0) / 4294967296;
    };
  }

  function streamBuffer(audioContext) {
    const duration = 18;
    const rate = audioContext.sampleRate;
    const count = Math.floor(duration * rate);
    const buffer = audioContext.createBuffer(2, count, rate);
    for (let channel = 0; channel < 2; channel++) {
      const data = buffer.getChannelData(channel);
      const next = random(4819 + channel * 691);
      let low = 0;
      let soft = 0;
      for (let i = 0; i < count; i++) {
        const noise = next() * 2 - 1;
        low = (low + noise * 0.026) / 1.026;
        soft = soft * 0.73 + noise * 0.27;
        const t = i / rate;
        // Slow, periodic swells are seamless over the loop and avoid a static hiss.
        const swell = 0.83 + Math.sin(t * Math.PI * 2 / 6 + channel) * 0.09
          + Math.sin(t * Math.PI * 2 / 9 + channel * 1.5) * 0.08;
        data[i] = (soft * 0.40 + low * 2.5) * swell;
      }
      // Very quiet resonant splashes within the water bed, not isolated notification-like beeps.
      for (let drop = 0; drop < 68; drop++) {
        const at = Math.floor(next() * (count - rate * 0.23));
        const length = Math.floor(rate * (0.035 + next() * 0.09));
        const frequency = 450 + next() * 950;
        const strength = 0.009 + next() * 0.020;
        let phase = 0;
        for (let j = 0; j < length; j++) {
          const t = j / length;
          phase += Math.PI * 2 * frequency * (1 - 0.28 * t) / rate;
          const envelope = Math.sin(Math.PI * t) * Math.exp(-t * 4.2);
          data[at + j] += (Math.sin(phase) * 0.7 + (next() * 2 - 1) * 0.3) * envelope * strength;
        }
      }
      // Overlap the end and start so the noise never clicks at the loop boundary.
      const crossfade = Math.floor(rate * 0.04);
      const first = data[0];
      for (let i = 0; i < crossfade; i++) {
        const mix = i / (crossfade - 1);
        data[count - crossfade + i] = data[count - crossfade + i] * (1 - mix) + first * mix;
      }
      // Retain headroom across device sample rates before the filters and volume gain.
      let peak = 0;
      for (let i = 0; i < count; i++) peak = Math.max(peak, Math.abs(data[i]));
      if (peak > 0.72) {
        const headroom = 0.72 / peak;
        for (let i = 0; i < count; i++) data[i] *= headroom;
      }
    }
    return buffer;
  }

  function createAudio() {
    if (context && context.state !== 'closed') return;
    context = new AudioContextClass({ latencyHint: 'playback' });
    master = context.createGain();
    master.gain.value = 0;
    const lowpass = context.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 3300;
    lowpass.Q.value = 0.45;
    const highpass = context.createBiquadFilter();
    highpass.type = 'highpass';
    highpass.frequency.value = 180;
    source = context.createBufferSource();
    source.buffer = streamBuffer(context);
    source.loop = true;
    source.connect(highpass).connect(lowpass).connect(master).connect(context.destination);
    source.start();
  }

  function fadeTo(value) {
    if (!context || !master || context.state === 'closed') return;
    const now = context.currentTime;
    master.gain.cancelScheduledValues(now);
    master.gain.setTargetAtTime(value, now, 0.12);
  }

  function updateControl() {
    const active = enabled && !suspendedByPage && context?.state === 'running';
    dock.classList.toggle('ambience-playing', Boolean(active));
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.setAttribute('aria-label', enabled ? 'Matikan suara air' : 'Putar suara air');
    toggle.title = enabled ? 'Matikan suara air' : 'Putar suara air';
  }

  function audioFailure(reason) {
    error = reason?.message || 'Audio unavailable';
    enabled = false;
    fadeTo(0);
    if (context && context.state !== 'closed') context.suspend().catch(() => {});
    status.textContent = 'Suara belum dapat diputar. Coba tekan Suara air sekali lagi.';
    updateControl();
  }

  async function syncAudio() {
    const request = ++epoch;
    clearTimeout(suspendTimer);
    suspendedByPage = document.hidden;
    if (!context || context.state === 'closed') {
      updateControl();
      return;
    }
    if (enabled && !suspendedByPage) {
      // resume() is reached directly from the click, preserving browser user activation.
      try {
        await context.resume();
        if (request !== epoch) return;
        fadeTo(level * 0.60);
      } catch (reason) {
        if (request === epoch) audioFailure(reason);
      }
    } else {
      fadeTo(0);
      if (suspendedByPage) {
        try { await context.suspend(); } catch (reason) { if (request === epoch) audioFailure(reason); }
      } else {
        suspendTimer = window.setTimeout(() => {
          if (request === epoch && !enabled && context?.state !== 'closed') {
            context.suspend().then(updateControl).catch(audioFailure);
          }
        }, 500);
      }
    }
    updateControl();
  }

  toggle.addEventListener('click', () => {
    if (!AudioContextClass) return;
    enabled = !enabled;
    error = null;
    status.textContent = enabled ? 'Suara air diaktifkan.' : 'Suara air dimatikan.';
    if (enabled) {
      try { createAudio(); } catch (reason) { audioFailure(reason); return; }
    }
    updateControl();
    void syncAudio();
  });

  volume.addEventListener('input', () => {
    level = Number(volume.value) / 100;
    volume.setAttribute('aria-valuetext', `${volume.value} persen`);
    dock.querySelector('.ambience-volume-value').textContent = `${volume.value}%`;
    if (enabled && !document.hidden) fadeTo(level * 0.60);
  });

  function closePanel(returnFocus = false) {
    panel.hidden = true;
    settings.setAttribute('aria-expanded', 'false');
    if (returnFocus) settings.focus();
  }

  // The chapter navigation is a custom overlay, so explicitly include this
  // body-level dock in its focus boundary. Native dialogs also close the panel.
  const chapterMenu = document.getElementById('chapter-menu');
  function syncOverlays() {
    const overlayOpen = Boolean((chapterMenu && !chapterMenu.hidden) || document.querySelector('dialog[open]'));
    dock.inert = overlayOpen;
    if (overlayOpen) closePanel();
  }
  const overlayObserver = new MutationObserver(syncOverlays);
  if (chapterMenu) overlayObserver.observe(chapterMenu, { attributes: true, attributeFilter: ['hidden'] });
  document.querySelectorAll('dialog').forEach(dialog => {
    overlayObserver.observe(dialog, { attributes: true, attributeFilter: ['open'] });
  });
  syncOverlays();

  settings.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    settings.setAttribute('aria-expanded', String(!panel.hidden));
    if (!panel.hidden) volume.focus({ preventScroll: true });
  });
  dock.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) {
      event.stopPropagation();
      closePanel(true);
    }
  });
  document.addEventListener('pointerdown', event => {
    if (!dock.contains(event.target)) closePanel();
  });
  document.addEventListener('focusin', event => {
    if (!dock.contains(event.target)) closePanel();
  });
  document.addEventListener('visibilitychange', () => {
    syncMotion();
    void syncAudio();
  });
  window.addEventListener('pagehide', () => {
    ++epoch;
    clearTimeout(suspendTimer);
    if (context && context.state !== 'closed') context.suspend().catch(() => {});
  });
  window.addEventListener('pageshow', () => { if (enabled) void syncAudio(); });

  if (!AudioContextClass) {
    toggle.disabled = true;
    settings.disabled = true;
    toggle.setAttribute('aria-label', 'Suara air tidak didukung browser ini');
    status.textContent = 'Browser ini belum mendukung suara air.';
  }

  // Read-only diagnostics for smoke checks. No autoplay, analytics, or persisted sound preference.
  window.AssyababAmbience = Object.freeze({
    get enabled() { return enabled; },
    get volume() { return level; },
    get contextState() { return context?.state || 'uninitialized'; },
    get suspendedByPage() { return suspendedByPage; },
    get error() { return error; },
    get decorativeLayers() { return layers.length; },
    get reducedMotion() { return motionPreference.matches || document.body.classList.contains('reduced-motion'); }
  });
})();
