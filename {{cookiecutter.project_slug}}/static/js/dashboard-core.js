(function () {
    const el = document.getElementById('current-theme');
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    el.textContent = current === 'dark' ? el.dataset.dark : el.dataset.light;
  })();

  document.querySelectorAll('.home-video-thumb video').forEach(function (v) {
    v.addEventListener('loadedmetadata', function () {
      try { v.currentTime = 0.1; } catch (e) {}
    });
  });

  function randomKey() {
    const bytes = new Uint8Array(32);
    window.crypto.getRandomValues(bytes);
    return Array.from(bytes, function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }
  const genSecret = document.getElementById('genSecretKey');
  const genJwt = document.getElementById('genJwtKey');
  if (genSecret) {
    genSecret.addEventListener('click', function () {
      document.getElementById('secretKeyInput').value = randomKey();
    });
  }
  if (genJwt) {
    genJwt.addEventListener('click', function () {
      document.getElementById('jwtSecretKeyInput').value = randomKey();
    });
  }

