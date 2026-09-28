/* A paused film, scrubbed by native page scroll. No scroll interception. */
(() => {
  'use strict';
  const clamp = n => Math.max(0, Math.min(1, n));
  class ScrollFilm {
    constructor(video, section) {
      this.video = video;
      this.section = section;
      this.target = 0;
      this.progress = 0;
      this.ready = false;
      this.failed = false;
      this.loaded = false;
      this.metrics = { seeks: 0, frames: 0 };
      this.note = section.querySelector('#render-note');
      this.retry = section.querySelector('[data-video-retry]');
      video.muted = true;
      video.defaultMuted = true;
      this.onReady = () => {
        if (!(Number.isFinite(video.duration) && video.duration > 0)) return;
        this.ready = true;
        this.failed = false;
        section.classList.remove('video-unavailable');
        section.classList.add('video-ready');
        this.note.hidden = true;
        this.retry.hidden = true;
        this.seek();
      };
      video.addEventListener('loadeddata', this.onReady);
      video.addEventListener('seeked', () => { this.metrics.frames++; this.seek(); });
      video.addEventListener('error', () => {
        this.failed = true;
        this.ready = false;
        section.classList.add('video-unavailable');
        section.classList.remove('video-ready');
        this.note.textContent = 'Film belum dapat dimuat. Cerita tetap bisa dijelajahi.';
        this.note.hidden = false;
        this.retry.hidden = false;
      });
      this.retry.addEventListener('click', () => this.load(true));
      // Download only when approaching the film. Small screens/save-data get
      // a smaller encode, selected once to prevent redownload on rotation.
      if ('IntersectionObserver' in window) {
        this.observer = new IntersectionObserver(entries => {
          if (entries.some(e => e.isIntersecting)) {
            this.load();
            this.observer.disconnect();
          }
        }, { rootMargin: '600px' });
        this.observer.observe(section);
      } else this.load();
    }
    load(retry = false) {
      if (this.loaded && !retry) return;
      this.loaded = true;
      this.failed = false;
      this.retry.hidden = true;
      const small = matchMedia('(max-width: 760px)').matches || navigator.connection?.saveData;
      this.video.src = small ? this.video.dataset.mobileSrc : this.video.dataset.src;
      this.video.preload = 'auto';
      this.video.load();
    }
    update(target, dt, enabled) {
      this.target = clamp(target);
      if (enabled) {
        // Time-based smoothing settles in ~0.45s regardless of display Hz.
        this.progress += (this.target - this.progress) * (1 - Math.exp(-dt / .10));
        if (Math.abs(this.target - this.progress) < .0005) this.progress = this.target;
      }
      if (this.ready && enabled) this.seek();
      this.section.style.setProperty('--film-progress', this.progress);
      return this.progress;
    }
    seek() {
      const v = this.video;
      if (!this.ready || v.seeking) return;
      const time = this.progress * Math.max(0, v.duration - 1 / 24);
      // Coalesce outstanding seeks. H264 with six-frame GOP also makes reverse
      // scrubbing cheap; fastSeek is deliberately avoided (keyframe snapping).
      if (Math.abs(v.currentTime - time) < 1 / 48) return;
      try { v.currentTime = time; this.metrics.seeks++; }
      catch { /* Metadata can be invalidated during a media retry. */ }
    }
    seekProgress(p) {
      this.progress = this.target = clamp(p);
      this.load();
      this.seek();
    }
    resize() {}
  }
  window.AssyababScrollFilm = ScrollFilm;
})();
