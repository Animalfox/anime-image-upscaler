(() => {
  const DEFAULT_LOCALE = "en";
  const SUPPORTED = new Set(["en", "ru"]);

  const MESSAGES = {
    en: {
      "a11y.skip": "Skip to uploader",
      "brand.sub": "RealESRGAN Anime 6B · 4× · anti-shakal mode",
      "drop.title": "Time to ENHANCE!",
      "drop.hint": "PNG · JPEG · WebP · BMP · GIF · up to 25 MB",
      "drop.pick": "Choose file",
      "drop.secondary": "or drop an image right here",
      "drop.aria": "Upload an image to upscale",
      "compare.beforeAlt": "Before upscale",
      "compare.afterAlt": "After upscale",
      "compare.slider": "Before and after comparison",
      "compare.before": "Before",
      "compare.after": "After",
      "compare.hint": "Drag the divider · click · ← →",
      "actions.again": "New image",
      "actions.download": "Download PNG",
      "busy": "Mining resolution…",
      "busy.sub": "First run can be longer — model is waking up",
      "foot.loading": "model loads on first request",
      "foot.fallback": "server ready · model loads on upscale",
      "credits.legal":
        'Model <span lang="en">RealESRGAN_x4plus_anime_6B</span> — ' +
        '<a href="https://github.com/xinntao/Real-ESRGAN" rel="noopener noreferrer" target="_blank">xinntao/Real-ESRGAN</a>, ' +
        "BSD-3-Clause. Not affiliated. " +
        '<a href="/NOTICE">NOTICE</a> · <a href="/LICENSE">MIT</a>',
      "error.generic": "Upscale failed — maybe VRAM ran out?",
      "error.status": "Error {status}",
      "error.dismiss": "Dismiss",
    },
    ru: {
      "a11y.skip": "К загрузке",
      "brand.sub": "RealESRGAN Anime 6B · 4× · режим антишакалинг",
      "drop.title": "Пора апскейлить!",
      "drop.hint": "PNG · JPEG · WebP · BMP · GIF · до 25 МБ",
      "drop.pick": "Выбрать файл",
      "drop.secondary": "или просто брось картинку сюда",
      "drop.aria": "Загрузить изображение для апскейла",
      "compare.beforeAlt": "До апскейла",
      "compare.afterAlt": "После апскейла",
      "compare.slider": "Сравнение до и после",
      "compare.before": "Было",
      "compare.after": "Стало",
      "compare.hint": "Тяни разделитель · кликай · ← →",
      "actions.again": "Новая картинка",
      "actions.download": "Скачать PNG",
      "busy": "Добываю разрешение…",
      "busy.sub": "Первый запуск подольше — модель просыпается",
      "foot.loading": "модель загрузится при первом запросе",
      "foot.fallback": "сервер готов · модель подгрузится при апскейле",
      "credits.legal":
        'Модель <span lang="en">RealESRGAN_x4plus_anime_6B</span> — ' +
        '<a href="https://github.com/xinntao/Real-ESRGAN" rel="noopener noreferrer" target="_blank">xinntao/Real-ESRGAN</a>, ' +
        "BSD-3-Clause. Не аффилированы. " +
        '<a href="/NOTICE">NOTICE</a> · <a href="/LICENSE">MIT</a>',
      "error.generic": "Не вышло — может, VRAM кончилась?",
      "error.status": "Ошибка {status}",
      "error.dismiss": "Закрыть",
    },
  };

  function detectLocale() {
    const candidates = [
      ...(Array.isArray(navigator.languages) ? navigator.languages : []),
      navigator.language,
      navigator.userLanguage,
    ].filter(Boolean);

    for (const tag of candidates) {
      const primary = String(tag).toLowerCase().split("-")[0];
      if (SUPPORTED.has(primary)) return primary;
    }
    return DEFAULT_LOCALE;
  }

  function t(key, vars = {}) {
    const catalog = MESSAGES[I18n.locale] || MESSAGES[DEFAULT_LOCALE];
    let text = catalog[key] ?? MESSAGES[DEFAULT_LOCALE][key] ?? key;
    for (const [name, value] of Object.entries(vars)) {
      text = text.replaceAll(`{${name}}`, String(value));
    }
    return text;
  }

  function apply() {
    document.documentElement.lang = I18n.locale;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      el.textContent = t(key);
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      if (!key) return;
      el.innerHTML = t(key);
    });

    document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
      const raw = el.getAttribute("data-i18n-attr");
      if (!raw) return;
      for (const pair of raw.split(";")) {
        const [attr, key] = pair.split(":").map((s) => s.trim());
        if (attr && key) el.setAttribute(attr, t(key));
      }
    });
  }

  const I18n = {
    locale: detectLocale(),
    supported: [...SUPPORTED],
    t,
    apply,
    detectLocale,
  };

  window.I18n = I18n;
})();
