/* Alternador de tema claro/oscuro */
(function () {
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-bs-theme", theme);
    localStorage.setItem("theme", theme);
  }

  const stored = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(stored || (prefersDark ? "dark" : "light"));

  window.toggleTheme = function () {
    const current =
      document.documentElement.getAttribute("data-bs-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  };

  window.setTheme = applyTheme;
})();
