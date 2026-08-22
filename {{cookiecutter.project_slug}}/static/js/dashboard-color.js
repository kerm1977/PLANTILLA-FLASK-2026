  // Selector de color personalizado (rueda de matiz/saturación + luminosidad + hex + pastel)
  (function () {
    function hslToRgb(h, s, l) {
      s /= 100; l /= 100;
      const k = function (n) { return (n + h / 30) % 12; };
      const a = s * Math.min(l, 1 - l);
      const f = function (n) {
        return l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
      };
      return [Math.round(255 * f(0)), Math.round(255 * f(8)), Math.round(255 * f(4))];
    }

    function hslToHex(h, s, l) {
      const rgb = hslToRgb(h, s, l);
      const toHex = function (x) { return x.toString(16).padStart(2, '0'); };
      return '#' + toHex(rgb[0]) + toHex(rgb[1]) + toHex(rgb[2]);
    }

    function hexToHsl(hex) {
      let h = hex.replace('#', '');
      if (h.length === 3) h = h.split('').map(function (c) { return c + c; }).join('');
      const r = parseInt(h.substr(0, 2), 16) / 255;
      const g = parseInt(h.substr(2, 2), 16) / 255;
      const b = parseInt(h.substr(4, 2), 16) / 255;
      const max = Math.max(r, g, b), min = Math.min(r, g, b);
      let hh = 0, s = 0;
      const l = (max + min) / 2;
      if (max !== min) {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        if (max === r) hh = (g - b) / d + (g < b ? 6 : 0);
        else if (max === g) hh = (b - r) / d + 2;
        else hh = (r - g) / d + 4;
        hh /= 6;
      }
      return [hh * 360, s * 100, l * 100];
    }

    function drawWheel(canvas, lightness) {
      const ctx = canvas.getContext('2d');
      const w = canvas.width, h = canvas.height;
      const cx = w / 2, cy = h / 2, radius = w / 2;
      const img = ctx.createImageData(w, h);
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const dx = x - cx, dy = y - cy;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const idx = (y * w + x) * 4;
          if (dist <= radius) {
            let angle = Math.atan2(dy, dx) * 180 / Math.PI;
            if (angle < 0) angle += 360;
            const sat = Math.min(dist / radius * 100, 100);
            const rgb = hslToRgb(angle, sat, lightness);
            img.data[idx] = rgb[0]; img.data[idx + 1] = rgb[1]; img.data[idx + 2] = rgb[2]; img.data[idx + 3] = 255;
          } else {
            img.data[idx + 3] = 0;
          }
        }
      }
      ctx.putImageData(img, 0, 0);
    }

    function initColorPicker(root) {
      const hidden = root.querySelector('.color-value');
      const trigger = root.querySelector('.color-picker-trigger');
      const popover = root.querySelector('.color-picker-popover');
      const canvas = root.querySelector('.color-wheel');
      const marker = root.querySelector('.color-wheel-marker');
      const lightnessInput = root.querySelector('.color-lightness');
      const hexInput = root.querySelector('.color-hex');
      const pastelSwatches = root.querySelectorAll('.color-pastel-swatch');
      const radius = canvas.width / 2;

      let hsl = hexToHsl(hidden.value || '#ffffff');
      lightnessInput.value = Math.round(hsl[2]);

      function updateMarker() {
        const rad = hsl[0] * Math.PI / 180;
        const dist = (hsl[1] / 100) * radius;
        marker.style.left = (radius + Math.cos(rad) * dist) + 'px';
        marker.style.top = (radius + Math.sin(rad) * dist) + 'px';
      }

      function setColor(hex, skipHexInput) {
        hidden.value = hex;
        trigger.style.background = hex;
        if (!skipHexInput) hexInput.value = hex;
      }

      function redraw() {
        drawWheel(canvas, hsl[2]);
        updateMarker();
      }

      function pickFromPoint(clientX, clientY) {
        const rect = canvas.getBoundingClientRect();
        let dx = clientX - rect.left - radius;
        let dy = clientY - rect.top - radius;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > radius) { dx = dx * radius / dist; dy = dy * radius / dist; dist = radius; }
        let angle = Math.atan2(dy, dx) * 180 / Math.PI;
        if (angle < 0) angle += 360;
        hsl[0] = angle;
        hsl[1] = Math.min(dist / radius * 100, 100);
        const hex = hslToHex(hsl[0], hsl[1], hsl[2]);
        setColor(hex);
        updateMarker();
      }

      let dragging = false;
      canvas.addEventListener('mousedown', function (e) { dragging = true; pickFromPoint(e.clientX, e.clientY); });
      window.addEventListener('mousemove', function (e) { if (dragging) pickFromPoint(e.clientX, e.clientY); });
      window.addEventListener('mouseup', function () { dragging = false; });
      canvas.addEventListener('touchstart', function (e) { dragging = true; pickFromPoint(e.touches[0].clientX, e.touches[0].clientY); e.preventDefault(); }, { passive: false });
      canvas.addEventListener('touchmove', function (e) { if (dragging) { pickFromPoint(e.touches[0].clientX, e.touches[0].clientY); e.preventDefault(); } }, { passive: false });
      window.addEventListener('touchend', function () { dragging = false; });

      lightnessInput.addEventListener('input', function () {
        hsl[2] = parseFloat(lightnessInput.value);
        redraw();
        setColor(hslToHex(hsl[0], hsl[1], hsl[2]));
      });

      hexInput.addEventListener('change', function () {
        let val = hexInput.value.trim();
        if (!/^#?[0-9a-f]{3}([0-9a-f]{3})?$/i.test(val)) { hexInput.value = hidden.value; return; }
        if (val[0] !== '#') val = '#' + val;
        hsl = hexToHsl(val);
        lightnessInput.value = Math.round(hsl[2]);
        redraw();
        setColor(val, true);
      });

      pastelSwatches.forEach(function (sw) {
        sw.addEventListener('click', function () {
          const hex = sw.dataset.color;
          hsl = hexToHsl(hex);
          lightnessInput.value = Math.round(hsl[2]);
          redraw();
          setColor(hex);
        });
      });

      trigger.addEventListener('click', function (e) {
        e.stopPropagation();
        document.querySelectorAll('.color-picker-popover').forEach(function (p) {
          if (p !== popover) p.classList.add('d-none');
        });
        popover.classList.toggle('d-none');
      });

      document.addEventListener('click', function (e) {
        if (!root.contains(e.target)) popover.classList.add('d-none');
      });

      redraw();
    }

    document.querySelectorAll('[data-color-picker]').forEach(initColorPicker);
  })();
