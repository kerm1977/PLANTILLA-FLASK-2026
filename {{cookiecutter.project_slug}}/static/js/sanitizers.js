/**
 * Sanitizadores de formularios centralizados.
 *
 * Cualquier cambio en las reglas de formateo debe hacerse en este archivo.
 * Los inputs con el atributo `data-sanitize` se actualizan automáticamente:
 *   data-sanitize="name"  -> Nombre/Apellido (Title Case)
 *   data-sanitize="email" -> Correo en minúsculas
 *   data-sanitize="digits" -> Solo dígitos
 */
(function () {
  'use strict';

  var Sanitizers = {
    name: function (value) {
      return value
        .toLowerCase()
        .replace(/(?:^|\s)\S/g, function (match) { return match.toUpperCase(); });
    },
    email: function (value) {
      return value.toLowerCase();
    },
    digits: function (value) {
      return value.replace(/\D/g, '');
    }
  };

  function applySanitizer(input) {
    var rule = input.getAttribute('data-sanitize');
    var fn = Sanitizers[rule];
    if (!fn) return;
    input.addEventListener('input', function () {
      input.value = fn(input.value);
    });
  }

  function init() {
    document.querySelectorAll('[data-sanitize]').forEach(applySanitizer);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
