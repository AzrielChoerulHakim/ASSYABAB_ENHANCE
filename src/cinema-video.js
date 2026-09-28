/* ASSYABAB / CAHAYA — paused, scroll-scrubbed video. No WebGL or runtime dependency. */
(() => {
  'use strict';
  const clamp = n => Math.max(0, Math.min(1, Number(n) || 0));
  const chapter = p => p < 0.24 ? 0 : p < 0.57 ? 1 : 2;
  const FRAME = 1 / 24;

  class AssyababVideoCinema {
    constructor(video, { reduced = false } = {}) {
      if (!(video instanceof HTMLVideoElement)) throw new TypeError('Cinematic video is missing');
      this.video = video;
      this.section = video.closest('.cinema-section');
      this.poster = this.section.querySelector('#cinema-poster');
      this.note = this.section.querySelector('#render-note');
      this.retry = this.section.querySelector('#cinema-retry');
      this.posters = [this.poster.dataset.source, this.poster.dataset.light, this.poster.dataset.creation];
      this.target = 0;
      this.progress = 0;
      this.reduced = reduced;
      this.ready = false;
      this.loaded = false;
      this.failed = false;
      this.near = false;
      this.disposed = false;
      this.raf = 0;
      this.lastSeek = 0;
      this.posterIndex = 0;
      this.maxTime = 0;
      this.metrics = { frames: 0, seeks: 0, mode: 'poster', currentTime: 0, source: null };
      this.cleanups = [];
      const params = new URLSearchParams(location.search);
      this.forcedStatic = params.get('media') === 'off' || params.get('graphics') === 'off';
      this.saveData = Boolean(navigator.connection?.saveData);
      video.muted = true;
      video.defaultMuted = true;
      video.playsInline = true;
      video.pause();
      this.listen(video, 'loadedmetadata', () => {
        if (Number.isFinite(video.duration) && video.duration > FRAME) {
          this.maxTime = Math.max(0, video.duration - FRAME);
        } else this.fail('Durasi video tidak tersedia.');
      });
      this.listen(video, 'loadeddata', () => this.onReady());
      this.listen(video, 'canplay', () => this.onReady());
      this.listen(video, 'seeked', () => {
        clearTimeout(this.seekTimer);
        if (this.staticMode || this.disposed) return;
        this.ready = true;
        this.failed = false;
        this.publishFrame();
        this.queue();
      });
      this.listen(video, 'error', () => this.fail('Video belum dapat dimuat.'));
      this.listen(video, 'play', () => video.pause());
      this.listen(this.retry, 'click', () => {
        if (this.staticMode) return;
        this.failed = false;
        this.load(true);
      });
      this.listen(document, 'visibilitychange', () => {
        if (document.hidden) this.cancel();
        else if (!this.staticMode && this.near) { this.load(); this.queue(); }
      });
      if ('IntersectionObserver' in window) {
        this.observer = new IntersectionObserver(entries => {
          this.near = entries[0].isIntersecting;
          if (this.near) { this.load(); this.queue(); }
          else this.cancel();
        }, { rootMargin: '480px 0px' });
        this.observer.observe(this.section);
      } else { this.near = true; this.load(); }
      this.setReducedMotion(reduced);
    }

    get staticMode() { return this.reduced || this.saveData || this.forcedStatic; }
    listen(target, event, callback) {
      target?.addEventListener(event, callback);
      this.cleanups.push(() => target?.removeEventListener(event, callback));
    }
    state(mode, message = '') {
      this.metrics.mode = mode;
      this.section.dataset.mediaState = mode;
      const text = message || (mode === 'static'
        ? (this.saveData ? 'Mode hemat data · tiga gambar dari film.' : 'Mode minim gerak · tiga gambar dari film.')
        : mode === 'loading' ? 'Menyiapkan film…'
        : mode === 'error' ? 'Film belum tersedia. Gambar dan informasi tetap dapat dijelajahi.' : '');
      if (this.note.textContent !== text) this.note.textContent = text;
      this.note.hidden = !text;
      this.retry.hidden = mode !== 'error';
      this.video.dispatchEvent(new CustomEvent('cinema-state', { detail: { mode, message: text } }));
    }
    showPoster(p) {
      const index = chapter(p);
      if (index !== this.posterIndex) {
        this.posterIndex = index;
        this.poster.src = this.posters[index];
      }
      this.section.classList.remove('video-ready');
      this.progress = p;
      this.emitProgress();
    }
    emitProgress() {
      this.video.dispatchEvent(new CustomEvent('cinema-frame', {
        detail: { progress: this.progress, time: this.video.currentTime || 0, mode: this.metrics.mode }
      }));
    }
    setReducedMotion(value) {
      const previous = this.staticMode;
      this.reduced = Boolean(value);
      if (this.staticMode) {
        this.cancel();
        this.video.pause();
        this.state('static');
        this.showPoster(this.target);
      } else if (previous || this.metrics.mode === 'poster') {
        this.state(this.ready ? 'ready' : 'poster');
        if (this.near) this.load();
        this.queue();
      }
    }
    load(force = false) {
      if (this.disposed || this.staticMode || (!force && this.loaded)) return;
      this.loaded = true;
      this.ready = false;
      this.failed = false;
      this.cancel();
      this.state('loading');
      const mobile = matchMedia('(max-width: 760px)').matches;
      // Choose once per load. Resizing never causes repeated multi-megabyte downloads.
      const source = mobile ? this.video.dataset.mobileSrc : this.video.dataset.src;
      if (!source) { this.fail('Sumber video belum tersedia.'); return; }
      this.metrics.source = mobile ? 'mobile' : 'desktop';
      this.video.preload = 'auto';
      this.video.src = source;
      this.video.load();
      clearTimeout(this.loadTimer);
      this.loadTimer = setTimeout(() => {
        if (!this.ready) this.fail('Koneksi lambat. Gambar ditampilkan sementara; video dapat dicoba lagi.');
      }, 15000);
    }
    onReady() {
      if (this.disposed || this.video.readyState < 2 || !this.maxTime) return;
      clearTimeout(this.loadTimer);
      this.ready = true;
      this.failed = false;
      if (this.staticMode) { this.state('static'); return; }
      this.state('ready');
      this.publishFrame();
      this.queue();
    }
    publishFrame() {
      if (this.staticMode || this.video.readyState < 2 || this.disposed) return;
      this.progress = clamp(this.video.currentTime / (this.maxTime || 1));
      this.metrics.currentTime = this.video.currentTime;
      this.metrics.frames += 1;
      this.section.classList.add('video-ready');
      if (this.metrics.mode !== 'ready') this.state('ready');
      this.emitProgress();
    }
    render(p) {
      this.target = clamp(p);
      if (this.staticMode || this.failed) {
        this.showPoster(this.target);
        return;
      }
      if (this.near) this.load();
      this.queue();
    }
    queue() {
      if (this.raf || !this.ready || this.failed || this.staticMode || !this.near || document.hidden || this.disposed) return;
      const desired = Math.min(this.maxTime, Math.round(this.target * this.maxTime / FRAME) * FRAME);
      if (Math.abs(desired - this.video.currentTime) < FRAME * 0.55) return;
      this.raf = requestAnimationFrame(now => this.seek(now));
    }
    seek(now) {
      this.raf = 0;
      if (this.disposed || document.hidden || this.staticMode || !this.near || !this.ready || this.failed) return;
      // One outstanding seek only. The seeked event drains the newest target.
      if (this.video.seeking) return;
      if (now - this.lastSeek < 1000 / 30) { this.queue(); return; }
      const desired = Math.min(this.maxTime, Math.round(this.target * this.maxTime / FRAME) * FRAME);
      if (Math.abs(desired - this.video.currentTime) < FRAME * 0.55) return;
      try {
        this.lastSeek = now;
        this.video.currentTime = desired;
        this.metrics.seeks += 1;
        clearTimeout(this.seekTimer);
        this.seekTimer = setTimeout(() => {
          if (this.video.seeking && !this.staticMode) this.fail('Video tersendat. Gambar ditampilkan sementara.');
        }, 5000);
      } catch (error) {
        this.fail('Browser belum dapat menampilkan film.');
      }
    }
    fail(message) {
      if (this.disposed) return;
      clearTimeout(this.loadTimer);
      clearTimeout(this.seekTimer);
      this.failed = true;
      this.cancel();
      this.video.pause();
      this.state(this.staticMode ? 'static' : 'error', message);
      this.showPoster(this.target);
    }
    resize() { /* CSS owns the layout; keep the loaded video and current scroll target. */ }
    cancel() { cancelAnimationFrame(this.raf); this.raf = 0; }
    dispose() {
      this.disposed = true;
      this.cancel();
      clearTimeout(this.loadTimer);
      clearTimeout(this.seekTimer);
      this.observer?.disconnect();
      this.cleanups.forEach(cleanup => cleanup());
      this.video.pause();
    }
  }
  window.AssyababVideoCinema = AssyababVideoCinema;
})();
