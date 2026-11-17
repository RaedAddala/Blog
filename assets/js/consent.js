// Google Analytics consent gate.
// GA is never loaded until the visitor accepts. The choice is stored with a date and asked again
// after about 6 months. Do Not Track (if enabled in hugo.toml) and Global Privacy Control count as
// a refusal, so those visitors never see the banner. Cloudflare Web Analytics is cookieless and is
// not handled here.
(() => {
  const script = document.currentScript;
  const gaId = script.dataset.gaId;
  const respectDnt = script.dataset.respectDnt === "true";
  const STORAGE_KEY = "analytics-consent";
  const MAX_AGE_MS = 182 * 24 * 60 * 60 * 1000;

  const dntValues = [navigator.doNotTrack, window.doNotTrack, navigator.msDoNotTrack];
  const dnt = respectDnt && dntValues.some((v) => v === "1" || v === "yes");
  const gpc = navigator.globalPrivacyControl === true;

  const clearGaCookies = () => {
    const host = location.hostname;
    const domains = ["", host, "." + host];
    document.cookie.split(";").forEach((c) => {
      const name = c.split("=")[0].trim();
      if (!/^_g(a|id)/.test(name)) return;
      domains.forEach((d) => {
        document.cookie = `${name}=; Max-Age=0; path=/${d ? "; domain=" + d : ""}`;
      });
    });
  };

  if (dnt || gpc) {
    clearGaCookies();
    return;
  }

  const read = () => {
    try {
      const c = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (c && (c.value === "granted" || c.value === "denied") && Date.now() - c.time < MAX_AGE_MS) {
        return c.value;
      }
    } catch (_) {
      // Storage blocked or malformed: treat as no decision.
    }
    return null;
  };

  const write = (value) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ value, time: Date.now() }));
    } catch (_) {
      // Storage blocked: the choice applies to this page view only.
    }
  };

  let loaded = false;
  const loadGa = () => {
    window["ga-disable-" + gaId] = false;
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("consent", "default", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    });
    window.gtag("js", new Date());
    window.gtag("config", gaId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(gaId);
    document.head.appendChild(s);
  };

  const stopGa = () => {
    window["ga-disable-" + gaId] = true;
    if (loaded) window.gtag("consent", "update", { analytics_storage: "denied" });
    clearGaCookies();
  };

  let banner = null;
  const closeBanner = () => {
    if (banner) banner.remove();
    banner = null;
  };

  const decide = (value) => {
    write(value);
    closeBanner();
    if (value === "granted") loadGa();
    else stopGa();
  };

  const showBanner = () => {
    if (banner) return;
    banner = document.createElement("section");
    banner.className = "consent-banner";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-label", "Analytics consent");
    banner.innerHTML =
      '<p>May I use <strong>Google Analytics</strong> to count visits and see which pages are read? ' +
      "It sets cookies only if you accept, and you can change your choice anytime from " +
      "&ldquo;Cookie settings&rdquo; in the footer. Cookieless Cloudflare visit counts run either way.</p>" +
      '<div class="consent-actions">' +
      '<button type="button" data-consent="denied">Reject</button>' +
      '<button type="button" data-consent="granted">Accept</button>' +
      "</div>";
    banner.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-consent]");
      if (btn) decide(btn.dataset.consent);
    });
    document.body.appendChild(banner);
  };

  const addFooterLink = () => {
    const footer = document.querySelector(".footer");
    if (!footer) return;
    const wrap = document.createElement("span");
    wrap.append(" · ");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "consent-link";
    btn.textContent = "Cookie settings";
    btn.addEventListener("click", () => {
      showBanner();
      banner.querySelector("button").focus();
    });
    wrap.appendChild(btn);
    footer.appendChild(wrap);
  };

  addFooterLink();
  const choice = read();
  if (choice === "granted") loadGa();
  else if (choice === null) {
    clearGaCookies();
    showBanner();
  }
})();
