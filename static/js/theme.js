// Смена темы: тёмная / светлая, с сохранением в localStorage

(function () {
  "use strict";

  var STORAGE_KEY = "tournament_theme";
  var html = document.documentElement;

  function getSavedTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      html.setAttribute("data-theme", "dark");
    } else {
      html.removeAttribute("data-theme");
    }
    updateIcon(theme);
  }

  function updateIcon(theme) {
    var icon = document.getElementById("theme-icon");
    if (!icon) return;
    icon.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  // применить сохранённую (или системную) при загрузке
  var saved = getSavedTheme();
  if (!saved) {
    // определяем системную
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      saved = "dark";
    } else {
      saved = "light";
    }
  }
  applyTheme(saved);

  // обработчик кнопки
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;

    updateIcon(getSavedTheme() || saved);

    btn.addEventListener("click", function () {
      var current =
        html.getAttribute("data-theme") === "dark" ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      saveTheme(next);
      applyTheme(next);
    });
  });
})();
