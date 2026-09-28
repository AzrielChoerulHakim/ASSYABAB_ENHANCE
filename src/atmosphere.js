/* One landscape, carried through the page. Driven exclusively by app.js's shared clock. */
(() => {
  'use strict';
  const clamp = (value, low = 0, high = 1) => Math.max(low, Math.min(high, value));
  const smooth = value => { const t = clamp(value); return t * t * (3 - 2 * t); };
  const round = value => Math.round(value * 1000) / 1000;

  function documentTop(element) {
    let top = 0;
    for (let node = element; node; node = node.offsetParent) top += node.offsetTop;
    return top;
  }

  function ornament(parent, name, contents = '') {
    if (!parent) return null;
    const element = document.createElement('div');
    element.className = `atmosphere-decoration ${name}`;
    element.setAttribute('aria-hidden', 'true');
    element.innerHTML = contents;
    parent.append(element);
    return element;
  }

  class Atmosphere {
    constructor() {
      this.hero = document.getElementById('beranda');
      this.film = document.getElementById('cahaya');
      this.manifesto = document.getElementById('tentang');
      this.art = document.querySelector('.program-art');
      this.wordmark = document.querySelector('.hero-wordmark');
      this.svg = document.querySelector('.program-symbol svg');
      this.quiet = false;
      this.wind = 0;
      this.geometryProgress = -1;
      this.geometryRotation = 0;
      this.wordmarkOffset = [0, 0];
      this.entryVisible = false;
      this.exitVisible = false;
      this.updates = 0;
      this.visibleSections = [];
      this.leafLayers = [];
      this.quietApplied = null;
      this.shapes = [];

      this.wordmark?.classList.add('atmosphere-wordmark');
      this.manifesto?.classList.add('atmosphere-manifesto');
      this.entry = ornament(this.film, 'atmosphere-entry-fog', '<i class="atmosphere-fog-bank"></i><i class="atmosphere-fog-bank atmosphere-fog-bank-near"></i>');
      this.exit = ornament(this.manifesto, 'atmosphere-exit-glow', '<i class="atmosphere-light-haze"></i><i class="atmosphere-light-paper"></i>');
      this.mist = ornament(this.hero, 'atmosphere-wordmark-mist', '<i class="atmosphere-mist-back"></i><i class="atmosphere-mist-front"></i>');
      if (this.svg) {
        this.orbit = this.svg.querySelector('g');
        this.orbit?.classList.add('atmosphere-geometry-orbit');
        this.shapes = [...this.svg.querySelectorAll('g > circle, g > rect')];
        this.shapes.forEach(shape => {
          shape.setAttribute('pathLength', '1000');
          shape.classList.add('atmosphere-geometry-stroke');
          shape.style.strokeDasharray = '1000 1000';
          shape.style.strokeDashoffset = '0';
        });
        this.svg.classList.add('atmosphere-geometry');
      }
      this.resize();
      Object.defineProperty(window, 'AssyababAtmosphereDebug', {
        configurable: true,
        get: () => this.diagnostics
      });
    }

    resize() {
      this.viewport = Math.max(1, window.innerHeight);
      this.layout = {};
      for (const [name, element] of [['hero', this.hero], ['film', this.film], ['manifesto', this.manifesto], ['art', this.art]]) {
        if (element) this.layout[name] = { top: documentTop(element), height: element.offsetHeight };
      }
      if (this.mist && this.wordmark) {
        // Only the lower strokes of the lettering disappear into this foreground bank.
        this.mist.style.top = `${this.wordmark.offsetTop + this.wordmark.offsetHeight * 0.47}px`;
        this.mist.style.height = `${Math.max(58, this.wordmark.offsetHeight * 0.61)}px`;
      }
      this.leafLayers = [...document.querySelectorAll('.ambience-layer')];
      this.leafBounds = this.leafLayers.map(layer => ({
        top: documentTop(layer.parentElement),
        height: layer.parentElement.offsetHeight
      }));
    }

    visible(bounds, y, margin = 0) {
      return Boolean(bounds && bounds.top + bounds.height > y - margin && bounds.top < y + this.viewport + margin);
    }

    drawGeometry(progress) {
      const p = clamp(progress);
      if (Math.abs(p - this.geometryProgress) < 0.0005) return;
      this.geometryProgress = p;
      this.shapes.forEach((shape, index) => {
        // Rings lead, followed by interlocking squares. Reverse scroll retraces the drawing.
        const start = index * 0.075;
        const local = smooth((p - start) / (1 - start));
        shape.style.strokeDashoffset = String(round(1000 * (1 - local)));
      });
    }

    update({ time = 0, wind = 0, quiet = false, day = 0 } = {}) {
      if (document.hidden) return;
      const finiteTime = Number.isFinite(time) ? time : 0;
      this.quiet = Boolean(quiet);
      this.wind = this.quiet ? 0 : clamp(Number(wind) || 0, -1, 1);
      this.day = clamp(Number(day) || 0, 0, 3);
      if (!this.leafLayers.length && document.querySelector('.ambience-layer')) this.resize();
      if (this.quietApplied !== this.quiet) {
        // Reduced-motion collapses the film section; refresh all following chapter offsets.
        this.resize();
        for (const layer of [this.entry, this.exit, this.mist]) {
          if (layer) layer.classList.toggle('atmosphere-quiet', this.quiet);
        }
        if (this.wordmark && this.quiet) this.wordmark.style.translate = '0px 0px';
        if (this.quiet) this.leafLayers.forEach(layer => { layer.style.transform = 'translate3d(0px, 0px, 0px)'; });
        if (this.quiet) this.drawGeometry(1);
        this.quietApplied = this.quiet;
      }

      const y = window.scrollY;
      const heroVisible = this.visible(this.layout.hero, y);
      const artVisible = this.visible(this.layout.art, y);
      const entryY = (this.layout.film?.top ?? -10000) - y;
      const exitY = (this.layout.manifesto?.top ?? -10000) - y;
      this.entryVisible = !this.quiet && entryY > -220 && entryY < this.viewport + 220;
      this.exitVisible = !this.quiet && exitY > -240 && exitY < this.viewport + 240;
      this.visibleSections = [heroVisible && 'hero', this.entryVisible && 'entry', this.exitVisible && 'exit', artVisible && 'geometry'].filter(Boolean);
      if (!this.visibleSections.length && !this.leafBounds?.some(bounds => this.visible(bounds, y))) return;
      this.updates++;

      if (heroVisible && this.wordmark) {
        const progress = clamp((y - this.layout.hero.top) / this.layout.hero.height);
        const x = this.quiet ? 0 : this.wind * 10;
        const rise = this.quiet ? 0 : progress * 27 + Math.sin(finiteTime * 0.18) * 2.2;
        this.wordmarkOffset = [round(x), round(rise)];
        // Individual translate composes with the existing entrance animation's transform.
        this.wordmark.style.translate = `${round(x)}px ${round(rise)}px`;
        if (!this.quiet && this.mist) {
          const drift = Math.sin(finiteTime * 0.09) * 35 + this.wind * 22;
          this.mist.style.setProperty('--atmosphere-drift', `${round(drift)}px`);
          this.mist.style.setProperty('--atmosphere-drift-back', `${round(-drift * 0.48)}px`);
          this.mist.style.opacity = String(round(0.66 + Math.sin(finiteTime * 0.13) * 0.1));
        }
      }

      if (this.entryVisible && this.entry) {
        const edge = smooth((this.viewport + 100 - entryY) / (this.viewport * 0.52));
        this.entry.style.opacity = String(round(edge * 0.9));
        this.entry.style.setProperty('--atmosphere-drift', `${round(Math.sin(finiteTime * 0.075) * 35 + this.wind * 24)}px`);
        this.entry.style.setProperty('--atmosphere-drift-back', `${round(Math.cos(finiteTime * 0.057) * -28 + this.wind * 9)}px`);
      }
      if (this.exitVisible && this.exit) {
        this.exit.style.setProperty('--atmosphere-drift', `${round(Math.sin(finiteTime * 0.085) * 46 + this.wind * 16)}px`);
        this.exit.style.setProperty('--atmosphere-light', String(round(0.6 + Math.sin(finiteTime * 0.16) * 0.09)));
      }

      if (artVisible && this.art) {
        const top = this.layout.art.top - y;
        this.drawGeometry(this.quiet ? 1 : smooth((this.viewport * 0.94 - top) / (this.viewport * 0.67)));
        if (!this.quiet && this.orbit && this.geometryProgress > 0.03) {
          this.geometryRotation = round(finiteTime * 1.05 + this.wind * 1.5);
          this.orbit.style.transform = `rotate(${this.geometryRotation}deg)`;
        }
      }

      this.leafLayers.forEach((layer, index) => {
        if (this.visible(this.leafBounds[index], y) || this.quiet) {
          layer.style.transform = `translate3d(${round(this.wind * (index ? 12 : 18))}px, 0px, 0px)`;
        }
      });
    }

    get diagnostics() {
      return Object.freeze({
        quiet: this.quiet,
        wind: this.wind,
        day: this.day || 0,
        geometryProgress: this.geometryProgress,
        geometryRotation: this.geometryRotation,
        geometryShapeCount: this.shapes.length,
        wordmarkOffset: [...this.wordmarkOffset],
        entryVisible: this.entryVisible,
        exitVisible: this.exitVisible,
        updates: this.updates,
        visibleSections: [...this.visibleSections]
      });
    }
  }

  window.AssyababAtmosphere = Atmosphere;
})();
