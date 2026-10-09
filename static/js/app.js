// Турнир — минимальный JS: валидация, автосохранение, автоскролл, переключение схем

document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  var STORAGE_KEY = "tournament_form";
  var playersArea = document.querySelector('textarea[name="players"]');
  var drawForm = document.querySelector('form[action*="/draw"]');

  // Подсчёт непустых строк участников
  function countPlayers() {
    if (!playersArea) return 0;
    return playersArea.value
      .split("\n")
      .map(function (line) {
        return line.trim();
      })
      .filter(function (line) {
        return line.length > 0;
      }).length;
  }

  // 1. Валидация: минимум 4 участника
  if (drawForm) {
    drawForm.addEventListener("submit", function (event) {
      if (countPlayers() < 4) {
        event.preventDefault();
        alert("Нужно минимум 4 участника");
      }
    });
  }

  // 2. Автосохранение формы
  function saveForm() {
    if (!drawForm) return;
    var data = {};
    drawForm
      .querySelectorAll("input, textarea, select")
      .forEach(function (field) {
        if (!field.name) return;
        if (field.type === "radio") {
          if (field.checked) data[field.name] = field.value;
        } else if (field.type === "checkbox") {
          data[field.name] = field.checked;
        } else {
          data[field.name] = field.value;
        }
      });
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {}
  }

  function restoreForm() {
    if (!drawForm) return;
    var raw;
    try {
      raw = localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return;
    }
    if (!raw) return;
    var data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      return;
    }
    drawForm
      .querySelectorAll("input, textarea, select")
      .forEach(function (field) {
        if (!field.name || !(field.name in data)) return;
        if (field.type === "radio") {
          field.checked = field.value === String(data[field.name]);
        } else if (field.type === "checkbox") {
          field.checked = Boolean(data[field.name]);
        } else {
          field.value = data[field.name];
        }
      });
  }

  if (drawForm) {
    drawForm.addEventListener("change", saveForm);
    drawForm.addEventListener("input", saveForm);
  }

  restoreForm();
});

// ============================================================
// Автоскролл к результату жеребьёвки
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  const drawResult = document.getElementById("draw-result");
  if (drawResult) {
    setTimeout(() => {
      drawResult.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }
});

// ============================================================
// Переключение вариантов схемы (только этап 1)
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  const variantRadios = document.querySelectorAll('input[name="variant"]');
  if (!variantRadios.length) return;

  function updateSchemes() {
    const checked = document.querySelector('input[name="variant"]:checked');
    const variant = checked ? checked.value : "through_one";
    const dataKey = variant === "first_last" ? "first" : "through";

    // меняем ТОЛЬКО схему этапа 1
    const field1 = document.getElementById("scheme1");
    if (field1) {
      field1.value = field1.dataset[dataKey] || "";
    }
    // схема этапа 2 не зависит от варианта
  }

  variantRadios.forEach((r) => r.addEventListener("change", updateSchemes));
  updateSchemes();
});
