/* Registro del Service Worker y acceso a servicios del dispositivo */

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js')
    .then(() => console.log('Service Worker registrado'))
    .catch((err) => console.error('Error registrando SW:', err));
}

function show(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

function getLocation() {
  if (!('geolocation' in navigator)) {
    show('gps-result', 'La geolocalización no está disponible en este dispositivo.');
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude, accuracy } = pos.coords;
      show('gps-result', `Latitud: ${latitude}<br>Longitud: ${longitude}<br>Precisión: ${accuracy} m`);
    },
    (err) => show('gps-result', `Error GPS: ${err.message}`),
    { enableHighAccuracy: true }
  );
}

let cameraStream = null;

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    const video = document.getElementById('camera-video');
    if (video) {
      video.srcObject = cameraStream;
      video.classList.remove('d-none');
    }
    show('camera-result', 'Cámara activa. Pulsa <b>Capturar</b> para tomar una foto.');
  } catch (err) {
    show('camera-result', `Error cámara: ${err.message}`);
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
  const video = document.getElementById('camera-video');
  if (video) {
    video.srcObject = null;
    video.classList.add('d-none');
  }
  show('camera-result', 'Cámara detenida.');
}

function capturePhoto() {
  const video = document.getElementById('camera-video');
  const canvas = document.getElementById('camera-canvas');
  if (!video || !canvas || !cameraStream) {
    show('camera-result', 'Primero activa la cámara.');
    return;
  }
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const dataUrl = canvas.toDataURL('image/png');
  const preview = document.getElementById('photo-preview');
  if (preview) {
    preview.src = dataUrl;
    preview.classList.remove('d-none');
  }
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = `foto_${Date.now()}.png`;
  link.innerHTML = '<br><i class="bi bi-download"></i> Descargar foto';
  show('camera-result', 'Foto capturada.');
  const result = document.getElementById('camera-result');
  if (result) result.appendChild(link);
}

async function checkBiometric() {
  if (!window.PublicKeyCredential) {
    show('bio-result', 'WebAuthn no está soportado.');
    return;
  }
  try {
    const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    if (available) {
      show('bio-result', 'El dispositivo dispone de autenticación biométrica (huella / rostro).');
    } else {
      show('bio-result', 'No se detecta autenticador biométrico en este dispositivo.');
    }
  } catch (err) {
    show('bio-result', `Error biometría: ${err.message}`);
  }
}

async function registerBiometric() {
  if (!window.PublicKeyCredential) {
    show('bio-result', 'WebAuthn no está soportado.');
    return;
  }
  try {
    const challenge = new Uint8Array(32);
    window.crypto.getRandomValues(challenge);
    const id = new Uint8Array(16);
    window.crypto.getRandomValues(id);
    const publicKey = {
      challenge,
      rp: { name: 'Flask PWA' },
      user: {
        id,
        name: 'usuario@flask.local',
        displayName: 'Usuario Flask'
      },
      pubKeyCredParams: [{ type: 'public-key', alg: -7 }],
      authenticatorSelection: {
        authenticatorAttachment: 'platform',
        userVerification: 'required'
      },
      timeout: 60000,
      attestation: 'none'
    };
    const credential = await navigator.credentials.create({ publicKey });
    show('bio-result', `Credencial registrada: <code>${credential.id}</code>`);
  } catch (err) {
    show('bio-result', `Error registro: ${err.message}`);
  }
}

async function shareApp() {
  if (!navigator.share) {
    show('share-result', 'La función Compartir no está soportada.');
    return;
  }
  try {
    await navigator.share({
      title: 'Flask PWA',
      text: 'Mira esta PWA con acceso a servicios del dispositivo.',
      url: window.location.origin
    });
    show('share-result', 'Compartido correctamente.');
  } catch (err) {
    show('share-result', `Error compartir: ${err.message}`);
  }
}

function vibrate() {
  if (!('vibrate' in navigator)) {
    show('vib-result', 'La vibración no está soportada.');
    return;
  }
  navigator.vibrate([200, 100, 200]);
  show('vib-result', 'Vibración enviada.');
}
