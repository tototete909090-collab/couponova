/* Code Wafra measurement consent. Loads the Google tag only after explicit accept. */
(function () {
  "use strict";
  var TAG_ID = "G-2K5VH08D0T"; /* replaced with the confirmed G- ID at publish */
  var KEY = "cw-consent-v1";
  var isEN = /^\/en(\/|$)/.test(location.pathname);

  var T = isEN ? {
    text: "We use Google Analytics cookies to understand visits (pages viewed, visit length, device type, approximate country). Accept or reject, your choice applies to the whole site.",
    accept: "Accept",
    reject: "Reject",
    more: "Privacy"
  } : {
    text: "نستخدم كوكيز Google Analytics لفهم الزيارات (الصفحات المعروضة ومدة الزيارة ونوع الجهاز والبلد التقريبي). يمكنك القبول أو الرفض، ويسري اختيارك على الموقع كله.",
    accept: "أوافق",
    reject: "أرفض",
    more: "الخصوصية"
  };

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }
  function write(choice) {
    try { localStorage.setItem(KEY, JSON.stringify({ choice: choice, ts: new Date().toISOString() })); } catch (e) {}
  }
  function deleteAnalyticsCookies() {
    var names = ["_ga"];
    (document.cookie.match(/_ga[^=;]*/g) || []).forEach(function (n) { names.push(n.trim()); });
    names.forEach(function (n) {
      ["", "; domain=" + location.hostname, "; domain=." + location.hostname].forEach(function (d) {
        document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + d;
      });
    });
  }
  function loadTag() {
    if (window.__cwTagLoaded) return;
    window.__cwTagLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + TAG_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    /* strip the entire query and fragment from the address bar BEFORE loading the tag,
       so no event can carry link additions (any value could contain personal data).
       Cost: campaign-level (utm) attribution is lost; visit sources remain visible
       as referring site names (e.g. google.com, instagram.com) via strict-origin. */
    try {
      if (location.search || location.hash) {
        history.replaceState(null, "", location.pathname);
      }
    } catch (e) {}
    window.gtag("js", new Date());
    window.gtag("config", TAG_ID);
  }
  function withdraw() {
    window["ga-disable-" + TAG_ID] = true; /* stops further events for this property */
    deleteAnalyticsCookies();
    write("rejected");
  }
  window.cwConsentWithdraw = withdraw;
  window.cwConsentAccept = function () { write("accepted"); loadTag(); };

  function banner() {
    if (read()) return;
    var css = document.createElement("style");
    css.textContent =
      "#cwConsent{position:fixed;inset-inline:0;bottom:0;z-index:9999;background:#15181c;color:#eee;" +
      "padding:14px 16px;font-size:14px;line-height:1.6;box-shadow:0 -2px 12px rgba(0,0,0,.4)}" +
      "#cwConsent .row{max-width:900px;margin:auto;display:flex;flex-wrap:wrap;gap:10px;align-items:center}" +
      "#cwConsent p{margin:0;flex:1 1 320px}" +
      "#cwConsent button{flex:0 0 auto;padding:10px 26px;border-radius:8px;border:1px solid #8a8f98;" +
      "background:transparent;color:#fff;font-size:15px;cursor:pointer;min-width:110px}" +
      "#cwConsent a{color:#ffd666}";
    document.head.appendChild(css);
    var box = document.createElement("div");
    box.id = "cwConsent";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", isEN ? "Measurement consent" : "إذن القياس");
    var row = document.createElement("div");
    row.className = "row";
    var p = document.createElement("p");
    p.textContent = T.text + " ";
    var a = document.createElement("a");
    a.href = isEN ? "/en/privacy/" : "/privacy/";
    a.textContent = T.more;
    p.appendChild(a);
    var ok = document.createElement("button");
    ok.type = "button";
    ok.textContent = T.accept;
    var no = document.createElement("button");
    no.type = "button";
    no.textContent = T.reject;
    ok.addEventListener("click", function () { write("accepted"); loadTag(); box.remove(); });
    no.addEventListener("click", function () { write("rejected"); box.remove(); });
    row.appendChild(p); row.appendChild(no); row.appendChild(ok);
    box.appendChild(row);
    document.body.appendChild(box);
  }

  var c = read();
  if (c && c.choice === "accepted") loadTag();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", banner);
  } else { banner(); }
})();
