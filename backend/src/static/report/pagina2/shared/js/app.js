(function () {
  function getByPath(obj, path) {
    return path.split('.').reduce((acc, k) => (acc == null ? acc : acc[k]), obj);
  }

  function applyTokens(tokens) {
    const root = document.documentElement;
    Object.entries(tokens.colors).forEach(([k, v]) => {
      root.style.setProperty(`--color-${k}`, v);
    });
  }

  function setTextContent(el, value) {
    el.textContent = value;
    // SVG <text> nodes exported from the design tool carry a fixed textLength
    // with lengthAdjust="spacingAndGlyphs", sized for the original placeholder
    // text. Real data rarely matches that width, so without removing these
    // attributes the glyphs get stretched/compressed to fit the old box,
    // making the text render abnormally huge or tiny. Drop the constraint so
    // the text renders at its natural size.
    if (el.hasAttribute('textLength')) {
      el.removeAttribute('textLength');
      el.removeAttribute('lengthAdjust');
    }
  }

  // Chromium's print-to-PDF flattens raster <image> elements that live inside
  // an SVG <pattern> at the (low) print raster resolution, so pattern-filled
  // icons come out blurry/pixelated in the generated PDF. A directly-placed
  // <image>, by contrast, is embedded at its native resolution. We therefore
  // replace the pattern-filled <rect> with a direct <image> of the same
  // geometry, which keeps the icons crisp at maximum quality while respecting
  // the size declared in the layout.
  function promotePatternImage(image) {
    const pattern = image.closest('pattern');
    if (!pattern || !pattern.id) return;
    const rect = document.querySelector(`rect[fill="url(#${pattern.id})"]`);
    if (!rect) return;
    const SVG_NS = 'http://www.w3.org/2000/svg';
    const XLINK_NS = 'http://www.w3.org/1999/xlink';
    const href =
      image.getAttribute('href') || image.getAttributeNS(XLINK_NS, 'href');
    if (!href) return;
    const out = document.createElementNS(SVG_NS, 'image');
    ['x', 'y', 'width', 'height', 'transform'].forEach((attr) => {
      if (rect.hasAttribute(attr)) out.setAttribute(attr, rect.getAttribute(attr));
    });
    out.setAttribute('href', href);
    out.setAttributeNS(XLINK_NS, 'href', href);
    out.setAttribute(
      'preserveAspectRatio',
      image.getAttribute('preserveAspectRatio') || 'xMidYMid slice'
    );
    rect.parentNode.replaceChild(out, rect);
  }

  // Maps each table column (data-bind field) to the row attribute that holds
  // the background color for that cell. Columns absent here keep their static
  // design color (e.g. the "2050"/arrow column and the RISCO/sector column).
  const CELL_COLOR_FIELDS = {
    tempoAtual: 'tempoAtualColor',
    ameaca: 'ameacaColor',
    exposicao: 'exposicaoColor',
    vulnerabilidade: 'vulnerabilidadeColor',
    sensibilidade: 'sensibilidadeColor',
    capacidadeAdaptativa: 'capacidadeAdaptativaColor',
  };

  function applyCellColor(el, data) {
    // data-bind paths look like "rows.<index>.<field>". Color the cell's
    // background rect using the matching *Color attribute from that row.
    const match = /^rows\.(\d+)\.(\w+)$/.exec(el.getAttribute('data-bind') || '');
    if (!match) return;
    const colorField = CELL_COLOR_FIELDS[match[2]];
    if (!colorField) return;
    const row = data.rows && data.rows[Number(match[1])];
    const color = row && row[colorField];
    if (!color) return;
    const svg = el.closest('svg');
    if (!svg) return;
    // Each cell SVG has a single visible background rect (the stroke-only
    // frame-background rects live in <defs> and carry no inline fill).
    const bg = svg.querySelector('rect.frame-background[style*="fill:"]');
    if (bg) bg.style.fill = color;
  }

  function bindFieldToElement(el, value) {
    if (value == null) return;
    if (el.tagName === 'IMG') {
      el.setAttribute('src', String(value));
    } else if (typeof value === 'string' || typeof value === 'number') {
      setTextContent(el, value);
    }
  }

  function renderLists(data) {
    document.querySelectorAll('[data-bind-list]').forEach((container) => {
      const list = getByPath(data, container.getAttribute('data-bind-list'));
      const tplId = container.getAttribute('data-template');
      const tpl = tplId ? document.getElementById(tplId) : null;
      if (!Array.isArray(list) || !tpl) return;
      container.innerHTML = '';
      list.forEach((item) => {
        const node = tpl.content.cloneNode(true);
        node.querySelectorAll('[data-field]').forEach((f) => {
          bindFieldToElement(f, item[f.getAttribute('data-field')]);
        });
        container.appendChild(node);
      });
    });
  }

  function bind() {
    const data = window.PAGE_DATA;
    if (!data) return;

    if (data.tokens) applyTokens(data.tokens);

    renderLists(data);

    document.querySelectorAll('[data-bind]').forEach((el) => {
      const path = el.getAttribute('data-bind');
      if (path === 'location.cityState') {
        setTextContent(el, `${data.location.city}/${data.location.state}`);
        return;
      }
      const value = getByPath(data, path);
      if (typeof value === 'string' || typeof value === 'number') {
        setTextContent(el, value);
      }
      applyCellColor(el, data);
    });

    document.querySelectorAll('[data-bind-src]').forEach((el) => {
      const value = getByPath(data, el.getAttribute('data-bind-src'));
      const isImage = el.tagName.toLowerCase() === 'image';
      // Empty/missing values keep the placeholder icon baked into the template.
      if (typeof value === 'string' && value) {
        if (isImage) {
          // SVG <image> uses href (not src) to reference its source.
          el.setAttribute('href', value);
        } else {
          el.setAttribute('src', value);
        }
      }
      // Promote pattern-filled SVG icons (bound or placeholder) to direct
      // <image> elements so they stay sharp in the print-to-PDF output.
      if (isImage) promotePatternImage(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
