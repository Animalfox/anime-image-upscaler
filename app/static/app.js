(() => {
  const { t } = window.I18n;
  window.I18n.apply();

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file");
  const pickBtn = document.getElementById("pickBtn");
  const compare = document.getElementById("compare");
  const compareFrame = document.getElementById("compareFrame");
  const beforeWrap = document.getElementById("beforeWrap");
  const beforeImg = document.getElementById("beforeImg");
  const afterImg = document.getElementById("afterImg");
  const handle = document.getElementById("handle");
  const meta = document.getElementById("meta");
  const downloadBtn = document.getElementById("downloadBtn");
  const againBtn = document.getElementById("againBtn");
  const busy = document.getElementById("busy");
  const status = document.getElementById("status");
  const toast = document.getElementById("toast");
  const toastText = document.getElementById("toastText");
  const toastClose = document.getElementById("toastClose");

  let ratio = 0.5;
  let dragging = false;

  function apiHeaders(extra = {}) {
    return {
      "Accept-Language": window.I18n.locale,
      ...extra,
    };
  }

  function showToast(message) {
    toastText.textContent = message;
    toast.classList.remove("is-hidden");
  }

  function hideToast() {
    toast.classList.add("is-hidden");
    toastText.textContent = "";
  }

  async function loadHealth() {
    try {
      const res = await fetch("/health", { headers: apiHeaders() });
      if (!res.ok) return;
      const data = await res.json();
      status.textContent = `${data.model} · ${data.scale} · ${data.device}`;
    } catch {
      status.textContent = t("foot.fallback");
    }
  }

  function setBusy(on) {
    busy.classList.toggle("is-hidden", !on);
    dropzone.setAttribute("aria-busy", on ? "true" : "false");
  }

  function syncFrameWidth() {
    beforeImg.style.width = `${compareFrame.clientWidth}px`;
    beforeImg.style.height = `${compareFrame.clientHeight}px`;
    compareFrame.style.setProperty("--frame-w", `${compareFrame.clientWidth}px`);
  }

  function setRatio(value) {
    ratio = Math.min(1, Math.max(0, value));
    const pct = `${ratio * 100}%`;
    const rounded = Math.round(ratio * 100);
    beforeWrap.style.width = pct;
    handle.style.left = pct;
    handle.setAttribute("aria-valuenow", String(rounded));
    handle.setAttribute("aria-valuetext", `${rounded}%`);
  }

  function ratioFromEvent(event) {
    const rect = compareFrame.getBoundingClientRect();
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    return (clientX - rect.left) / rect.width;
  }

  function showResult(payload) {
    hideToast();
    dropzone.classList.add("is-hidden");
    compare.classList.remove("is-hidden");
    beforeImg.src = payload.before_url;
    afterImg.src = payload.after_url;
    downloadBtn.href = `/api/download/${payload.id}`;
    meta.textContent =
      `${payload.before_size.w}×${payload.before_size.h}` +
      ` → ${payload.after_size.w}×${payload.after_size.h}` +
      ` · ${payload.scale}× · ${payload.model}`;

    const onReady = () => {
      syncFrameWidth();
      setRatio(0.5);
      handle.focus({ preventScroll: true });
    };
    if (afterImg.complete) onReady();
    else afterImg.onload = onReady;
  }

  function resetUi() {
    hideToast();
    compare.classList.add("is-hidden");
    dropzone.classList.remove("is-hidden");
    fileInput.value = "";
    beforeImg.removeAttribute("src");
    afterImg.removeAttribute("src");
    pickBtn.focus({ preventScroll: true });
  }

  function detailMessage(detail, statusCode) {
    if (typeof detail === "string" && detail.trim()) return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    return t("error.status", { status: statusCode });
  }

  async function upload(file) {
    if (!file) return;
    hideToast();
    setBusy(true);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch("/api/upscale", {
        method: "POST",
        body,
        headers: apiHeaders(),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(detailMessage(data.detail, res.status));
      }
      showResult(data);
    } catch (err) {
      showToast(err.message || t("error.generic"));
    } finally {
      setBusy(false);
    }
  }

  function openPicker() {
    fileInput.click();
  }

  pickBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    openPicker();
  });
  dropzone.addEventListener("click", (e) => {
    if (e.target === pickBtn || pickBtn.contains(e.target)) return;
    openPicker();
  });
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      openPicker();
    }
  });
  fileInput.addEventListener("change", () => upload(fileInput.files?.[0]));

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("is-drag");
  });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("is-drag"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("is-drag");
    upload(e.dataTransfer?.files?.[0]);
  });

  // Prevent browser from navigating away when a file is dropped outside the zone.
  window.addEventListener("dragover", (e) => e.preventDefault());
  window.addEventListener("drop", (e) => e.preventDefault());

  const startDrag = (e) => {
    dragging = true;
    handle.focus({ preventScroll: true });
    setRatio(ratioFromEvent(e));
  };
  const moveDrag = (e) => {
    if (!dragging) return;
    e.preventDefault();
    setRatio(ratioFromEvent(e));
  };
  const endDrag = () => {
    dragging = false;
  };

  compareFrame.addEventListener("mousedown", startDrag);
  compareFrame.addEventListener("touchstart", startDrag, { passive: true });
  window.addEventListener("mousemove", moveDrag);
  window.addEventListener("touchmove", moveDrag, { passive: false });
  window.addEventListener("mouseup", endDrag);
  window.addEventListener("touchend", endDrag);

  handle.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      setRatio(ratio - 0.05);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      setRatio(ratio + 0.05);
    } else if (e.key === "Home") {
      e.preventDefault();
      setRatio(0);
    } else if (e.key === "End") {
      e.preventDefault();
      setRatio(1);
    }
  });

  againBtn.addEventListener("click", resetUi);
  toastClose.addEventListener("click", hideToast);
  window.addEventListener("resize", syncFrameWidth);

  loadHealth();
})();
