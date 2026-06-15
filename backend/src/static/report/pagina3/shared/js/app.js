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
    });

    document.querySelectorAll('[data-bind-src]').forEach((el) => {
      const value = getByPath(data, el.getAttribute('data-bind-src'));
      // Empty/missing values keep the placeholder icon baked into the template.
      if (typeof value !== 'string' || !value) return;
      if (el.tagName.toLowerCase() === 'image') {
        // SVG <image> uses href (not src) to reference its source.
        el.setAttribute('href', value);
      } else {
        el.setAttribute('src', value);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
