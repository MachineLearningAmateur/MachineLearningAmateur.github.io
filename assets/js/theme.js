(function () {
  var storageKey = "site-theme";
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");

  if (!toggle) {
    return;
  }

  function readStoredTheme() {
    try {
      var storedTheme = localStorage.getItem(storageKey);
      return storedTheme === "light" || storedTheme === "dark" ? storedTheme : null;
    } catch (error) {
      return null;
    }
  }

  function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    toggle.setAttribute("aria-pressed", String(theme === "dark"));
    toggle.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light theme" : "Switch to dark theme"
    );
  }

  function persistTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      return;
    }
  }

  var currentTheme = root.dataset.theme;

  if (currentTheme !== "light" && currentTheme !== "dark") {
    currentTheme = readStoredTheme() || getSystemTheme();
  }

  applyTheme(currentTheme);

  toggle.addEventListener("click", function () {
    var nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    persistTheme(nextTheme);
  });

  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  var handleSystemThemeChange = function (event) {
    if (readStoredTheme()) {
      return;
    }

    applyTheme(event.matches ? "dark" : "light");
  };

  if (typeof mediaQuery.addEventListener === "function") {
    mediaQuery.addEventListener("change", handleSystemThemeChange);
  } else if (typeof mediaQuery.addListener === "function") {
    mediaQuery.addListener(handleSystemThemeChange);
  }
})();
