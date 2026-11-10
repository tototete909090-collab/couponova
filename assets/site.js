
(() => {
  "use strict";

  const isArabic = document.documentElement.lang === "ar";

  // نسخ كود الخصم
  async function copyCoupon(code, button) {
    const originalText = button.textContent;

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

      button.textContent = isArabic ? "تم النسخ ✓" : "Copied ✓";
    } catch (error) {
      button.textContent = isArabic ? "انسخ يدوياً" : "Copy manually";
    }

    window.setTimeout(() => {
      button.textContent = originalText;
    }, 1800);
  }

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", () => {
      const code = button.getAttribute("data-copy");
      if (code) copyCoupon(code, button);
    });
  });

  // البحث في الكوبونات
  const searchInput = document.querySelector("[data-coupon-search]");
  const couponCards = Array.from(
    document.querySelectorAll("[data-coupon-card]")
  );
  const emptyMessage = document.querySelector("[data-empty]");

  function filterCoupons() {
    if (!searchInput) return;

    const query = searchInput.value.trim().toLocaleLowerCase();
    let visibleCount = 0;

    couponCards.forEach((card) => {
      const matches = card.textContent.toLocaleLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) visibleCount++;
    });

    if (emptyMessage) {
      emptyMessage.hidden = visibleCount > 0;
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", filterCoupons);

    const searchForm = searchInput.closest("form");
    if (searchForm) {
      searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        filterCoupons();
      });
    }
  }

  // تحديث السنة تلقائياً
  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = new Date().getFullYear();
  });

})();

