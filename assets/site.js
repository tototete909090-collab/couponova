(() => {
  "use strict";

  const isArabic = document.documentElement.lang === "ar";
  const resetTimers = new WeakMap();
  const status = document.createElement("p");
  status.className = "sr-only";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  document.body.appendChild(status);

  async function copyCode(code, button) {
    const originalText = button.dataset.originalText || button.textContent;
    button.dataset.originalText = originalText;
    window.clearTimeout(resetTimers.get(button));

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(code);
      } else {
        const field = document.createElement("textarea");
        field.value = code;
        field.setAttribute("readonly", "");
        field.style.position = "fixed";
        field.style.opacity = "0";
        document.body.appendChild(field);
        field.select();
        const copied = document.execCommand("copy");
        field.remove();
        if (!copied) throw new Error("Copy failed");
      }
      button.textContent = isArabic ? "تم النسخ" : "Copied";
      status.textContent = isArabic
        ? `تم نسخ ${code}. الصقه في بحث تطبيق SHEIN.`
        : `${code} copied. Paste it into SHEIN app search.`;
    } catch {
      button.textContent = isArabic ? "انسخ يدويًا" : "Copy manually";
      status.textContent = isArabic
        ? `تعذر النسخ التلقائي. انسخ ${code} يدويًا.`
        : `Automatic copy failed. Copy ${code} manually.`;
    }

    resetTimers.set(button, window.setTimeout(() => {
      button.textContent = originalText;
    }, 1800));
  }

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", () => {
      const code = button.getAttribute("data-copy");
      if (code) copyCode(code, button);
    });
  });

  const searchInput = document.querySelector("[data-coupon-search]");
  const cards = Array.from(document.querySelectorAll("[data-coupon-card]"));
  const emptyMessage = document.querySelector("[data-empty]");

  function filterCards() {
    if (!searchInput) return;
    const query = searchInput.value.trim().toLocaleLowerCase();
    let visibleCount = 0;
    cards.forEach((card) => {
      const matches = card.textContent.toLocaleLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) visibleCount += 1;
    });
    if (emptyMessage) emptyMessage.hidden = visibleCount > 0;
  }

  if (searchInput) {
    searchInput.addEventListener("input", filterCards);
    const form = searchInput.closest("form");
    if (form) form.addEventListener("submit", (event) => {
      event.preventDefault();
      filterCards();
    });
  }

  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = new Date().getFullYear();
  });
})();
