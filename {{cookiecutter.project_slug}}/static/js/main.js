/* JavaScript principal de la aplicación (local, sin CDN). */

window.changeLang = async function (langUrl) {
  if (!langUrl) return;

  try {
    const res = await fetch(langUrl);
    if (!res.ok) throw new Error("No se pudo cambiar el idioma");
    const html = await res.text();
    loadPageFromHtml(html);
  } catch (err) {
    console.error("Cambio de idioma fallido:", err);
  }
};

function loadPageFromHtml(html) {
  const parser = new DOMParser();
  const newDoc = parser.parseFromString(html, "text/html");

  if (newDoc.title) document.title = newDoc.title;
  if (newDoc.documentElement.lang) {
    document.documentElement.lang = newDoc.documentElement.lang;
  }

  const newNav = newDoc.querySelector("nav.desktop-nav");
  const oldNav = document.querySelector("nav.desktop-nav");
  if (newNav && oldNav) {
    oldNav.replaceWith(newNav);
  }

  const newMain = newDoc.querySelector("main");
  const oldMain = document.querySelector("main");
  if (!newMain || !oldMain) return;

  const oldVideo = oldMain.querySelector(".home-video-wrapper");
  const newVideo = newMain.querySelector(".home-video-wrapper");
  if (oldVideo && newVideo) {
    newMain.replaceChild(oldVideo, newVideo);
  }
  oldMain.replaceWith(newMain);

  const newBack = newDoc.querySelector(".back-button");
  const oldBack = document.querySelector(".back-button");
  if (newBack && oldBack) {
    oldBack.replaceWith(newBack);
  } else if (newBack && !oldBack) {
    document.body.appendChild(newBack);
  } else if (oldBack && !newBack) {
    oldBack.remove();
  }

  // Reemplazar modal de cierre de sesión si existe
  const newModal = newDoc.getElementById("logoutModal");
  const oldModal = document.getElementById("logoutModal");
  if (newModal && oldModal) {
    oldModal.replaceWith(newModal);
  }
}

/* Confirmaciones consistentes con modal de Bootstrap (nunca confirm()/alert() nativos) */
(function () {
  let confirmModal = null;
  let modalBodyEl = null;
  let confirmBtn = null;
  let pendingAction = null;

  function ensureModal() {
    if (confirmModal) return true;
    const modalEl = document.getElementById("confirmActionModal");
    if (!modalEl || typeof bootstrap === "undefined") return false;
    confirmModal = new bootstrap.Modal(modalEl);
    modalBodyEl = document.getElementById("confirmActionModalBody");
    confirmBtn = document.getElementById("confirmActionModalConfirm");
    confirmBtn.addEventListener("click", function () {
      confirmModal.hide();
      const action = pendingAction;
      pendingAction = null;
      if (action) action();
    });
    return true;
  }

  function requestConfirm(message, onConfirm) {
    if (!ensureModal()) {
      onConfirm();
      return;
    }
    modalBodyEl.textContent = message || "¿Estás seguro?";
    pendingAction = onConfirm;
    confirmModal.show();
  }

  document.addEventListener(
    "submit",
    function (e) {
      const form = e.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (!form.hasAttribute("data-confirm") || form.dataset.confirmBypass === "true") return;
      e.preventDefault();
      requestConfirm(form.getAttribute("data-confirm"), function () {
        form.dataset.confirmBypass = "true";
        if (form.requestSubmit) form.requestSubmit();
        else form.submit();
      });
    },
    true
  );

  document.addEventListener(
    "click",
    function (e) {
      const btn = e.target.closest("button[data-confirm]");
      if (!btn || btn.dataset.confirmBypass === "true") return;
      e.preventDefault();
      requestConfirm(btn.getAttribute("data-confirm"), function () {
        btn.dataset.confirmBypass = "true";
        btn.click();
        btn.dataset.confirmBypass = "false";
      });
    },
    true
  );

  window.requestConfirm = requestConfirm;
})();
