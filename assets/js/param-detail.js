/* Nutrisize — parameter detail popup (/parameters/).
 * Tapping a parameter row or chip opens a dual-audience popup: a plain-language
 * view anyone can follow, and a clinical reference. The clinical quick reference
 * (interpretation, pearl, action guidance) is shown for every parameter; the
 * deeper reference (differential diagnosis, drug interactions, lab methodology,
 * codes, age notes, global ranges) is present only for free-tier parameters —
 * premium ones show a Physiology Premium pointer instead (their deep content is
 * never shipped to the browser). Data: assets/data/free/parameter-details.json.
 * Reuses the nm-* modal shell from plans.css. No dependencies. */
(function () {
  "use strict";

  var byId = null, loading = null, overlay, lastFocus, appLinks = { ios: "#", android: "#" };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function titleCase(s) {
    return String(s || "").replace(/[-_]/g, " ")
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function load() {
    if (byId) return Promise.resolve(byId);
    if (loading) return loading;
    loading = fetch("../assets/data/free/parameter-details.json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        byId = {};
        d.parameters.forEach(function (p) { byId[p.id] = p; });
        return byId;
      });
    return loading;
  }

  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.className = "nutri-modal";
    overlay.setAttribute("hidden", "");
    overlay.innerHTML = '<div class="nm-card" role="dialog" aria-modal="true" aria-labelledby="pd-title">' +
      '<button class="nm-close" type="button" aria-label="Close">&times;</button>' +
      '<div class="pd-body"></div></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    overlay.querySelector(".nm-close").addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) close();
    });
    // Tab switching
    overlay.addEventListener("click", function (e) {
      var t = e.target.closest(".pd-tab");
      if (!t) return;
      var which = t.dataset.tab;
      overlay.querySelectorAll(".pd-tab").forEach(function (b) {
        b.setAttribute("aria-selected", b.dataset.tab === which ? "true" : "false");
      });
      overlay.querySelectorAll(".pd-panel").forEach(function (pnl) {
        pnl.hidden = pnl.dataset.panel !== which;
      });
      overlay.querySelector(".nm-card").scrollTop = 0;
    });
  }

  function cell(kind, label, value) {
    if (!value) return "";
    return '<div class="pd-cell ' + kind + '"><span class="pd-k">' + label + "</span>" +
      '<span class="pd-v">' + esc(value) + "</span></div>";
  }

  function laymanPanel(p) {
    var l = p.layman || {};
    var w = l.whenToWorry || {};
    var worry =
      (w.worry ? cell("worry", "When to be concerned", w.worry) : "") +
      (w.dontWorry ? cell("ok", "Usually fine", w.dontWorry) : "");
    return '<div class="pd-panel" data-panel="layman">' +
      (l.simplyPut ? '<p class="pd-lead">' + esc(l.simplyPut) + "</p>" : "") +
      (l.analogy ? '<div class="pd-analogy">' + esc(l.analogy) + "</div>" : "") +
      (l.whatItTells ? '<div class="pd-sec"><h4>What it tells you</h4>' +
        '<p class="pd-row">' + esc(l.whatItTells) + "</p></div>" : "") +
      (p.range ? '<div class="pd-sec"><h4>Typical healthy range</h4>' +
        '<p class="pd-row"><b>' + esc(p.range) + "</b></p></div>" : "") +
      (worry ? '<div class="pd-sec"><h4>When to worry</h4><div class="pd-hl">' + worry + "</div></div>" : "") +
      "</div>";
  }

  function interpBlock(q) {
    var i = q.interpretation || {};
    var hl = (i.high ? cell("high", "If high", i.high) : "") + (i.low ? cell("low", "If low", i.low) : "");
    if (!hl && !i.general) return "";
    return '<div class="pd-sec"><h4>Interpretation</h4>' +
      (hl ? '<div class="pd-hl">' + hl + "</div>" : "") +
      (i.general ? '<p class="pd-row">' + esc(i.general) + "</p>" : "") + "</div>";
  }

  function actionBlock(q) {
    var a = q.actionGuidance || {};
    function one(label, o) {
      if (!o) return "";
      var u = (o.urgency || "").toLowerCase();
      return '<p class="pd-row"><b>' + label + ":</b> " + esc(o.action || "") +
        (o.urgency ? '<span class="pd-urgency ' + esc(u) + '">' + esc(o.urgency) + "</span>" : "") +
        (o.details ? '<br><span style="color:#6b7f74">' + esc(o.details) + "</span>" : "") + "</p>";
    }
    var body = one("If high", a.high) + one("If low", a.low);
    return body ? '<div class="pd-sec"><h4>What to do</h4>' + body + "</div>" : "";
  }

  function detailBlocks(d) {
    var out = "";
    var dd = d.differentialDiagnosis;
    if (Array.isArray(dd) && dd.length) {
      out += '<div class="pd-sec"><h4>Differential diagnosis</h4>' +
        dd.map(function (x) {
          return '<p class="pd-row"><b>' + esc(x.pattern || "") + "</b> &rarr; " +
            esc(x.consider || "") +
            (x.keyDistinguisher ? ' <span style="color:#6b7f74">(' + esc(x.keyDistinguisher) + ")</span>" : "") +
            "</p>";
        }).join("") + "</div>";
    }
    var di = d.drugInteractions;
    if (Array.isArray(di) && di.length) {
      out += '<div class="pd-sec"><h4>Drug interactions</h4>' +
        di.map(function (x) {
          return '<p class="pd-row"><b>' + esc(x.drug || "") + "</b> — " + esc(x.effect || "") +
            (x.mechanism ? '<br><span style="color:#6b7f74">' + esc(x.mechanism) + "</span>" : "") +
            (x.clinicalNote ? '<br><span style="color:#6b7f74">' + esc(x.clinicalNote) + "</span>" : "") +
            "</p>";
        }).join("") + "</div>";
    }
    var lm = d.labMethodology;
    if (lm && typeof lm === "object") {
      var rows = "";
      [["sampleType", "Sample"], ["fasting", "Fasting"], ["stability", "Stability"]].forEach(function (kv) {
        if (lm[kv[0]]) rows += '<p class="pd-row"><b>' + kv[1] + ":</b> " + esc(lm[kv[0]]) + "</p>";
      });
      if (Array.isArray(lm.interferences) && lm.interferences.length) {
        rows += '<p class="pd-row"><b>Interferences:</b> ' + esc(lm.interferences.join("; ")) + "</p>";
      }
      if (rows) out += '<div class="pd-sec"><h4>Lab methodology</h4>' + rows + "</div>";
    }
    var mc = d.medicalCodes;
    if (mc && (mc.loinc || (mc.icd10Related && mc.icd10Related.length))) {
      var codes = "";
      if (mc.loinc) codes += '<span class="pd-code">LOINC ' + esc(mc.loinc) + "</span>";
      (mc.icd10Related || []).forEach(function (c) { codes += '<span class="pd-code">ICD-10 ' + esc(c) + "</span>"; });
      out += '<div class="pd-sec"><h4>Codes</h4><div class="pd-codes">' + codes + "</div></div>";
    }
    var age = d.ageSpecificNotes;
    if (age && typeof age === "object") {
      var ar = Object.keys(age).map(function (k) {
        return '<p class="pd-row"><b>' + esc(titleCase(k)) + ":</b> " + esc(age[k]) + "</p>";
      }).join("");
      if (ar) out += '<div class="pd-sec"><h4>By age</h4>' + ar + "</div>";
    }
    var gr = d.globalRanges;
    if (gr && typeof gr === "object") {
      var grr = Object.keys(gr).map(function (k) {
        return '<p class="pd-row"><b>' + esc(k.toUpperCase()) + ":</b> " + esc(gr[k]) + "</p>";
      }).join("");
      if (grr) out += '<div class="pd-sec"><h4>Global &amp; special ranges</h4>' + grr + "</div>";
    }
    return out;
  }

  function gateBlock() {
    return '<div class="pd-gate"><h4>Full clinical reference is in the app</h4>' +
      "<p>Differential diagnosis, drug interactions, lab methodology, and diagnostic codes " +
      "for this and every one of the 201 parameters — with Physiology Premium in Nutrisize Health.</p>" +
      '<div class="pd-stores">' +
      '<a href="' + appLinks.ios + '" target="_blank" rel="noopener"><img src="../assets/img/app-store-badge.svg" alt="Download on the App Store" height="38"></a>' +
      '<a href="' + appLinks.android + '" target="_blank" rel="noopener"><img src="../assets/img/google-play-badge.png" alt="Get it on Google Play" height="38"></a>' +
      "</div></div>";
  }

  function citeUrl(c) {
    if (c.url) return c.url;
    var q = ('"' + (c.text || "") + '" ' + (c.source || "")).trim();
    return "https://www.google.com/search?q=" + encodeURIComponent(q);
  }

  function citationsBlock(cites) {
    if (!Array.isArray(cites) || !cites.length) return "";
    return '<div class="pd-sec"><h4>References</h4><div class="cx-refs">' +
      cites.map(function (c) {
        var g = (c.evidenceGrade || "").toLowerCase();
        var badge = '<span class="cx-grade ' + (g || "na") + '">' + (g ? g.toUpperCase() : "–") + "</span>";
        var link = '<a href="' + esc(citeUrl(c)) + '" target="_blank" rel="noopener">' + esc(c.text) + "</a>";
        return '<div class="cx-ref">' + badge + "<span>" + link +
          (c.source ? ' <span class="cx-src">— ' + esc(c.source) + "</span>" : "") + "</span></div>";
      }).join("") + "</div></div>";
  }

  function clinicalPanel(p) {
    var q = p.quickRef || {};
    var quick = interpBlock(q) +
      (q.clinicalPearl ? '<div class="pd-pearl"><b>Clinical pearl.</b> ' + esc(q.clinicalPearl) + "</div>" : "") +
      actionBlock(q);
    var deep = p.detail ? detailBlocks(p.detail) : gateBlock();
    return '<div class="pd-panel" data-panel="clinical" hidden>' + quick + deep +
      citationsBlock(p.citations) +
      '<p class="nm-note" style="margin-top:16px">Educational reference — not a substitute for ' +
      "clinical judgement or individual medical advice.</p></div>";
  }

  function render(p) {
    var head = '<div class="nm-head"><span class="nm-eyebrow">' +
      esc(titleCase(p.system || "")) + (p.freq ? " · " + esc(titleCase(p.freq)) + " check" : "") + "</span>" +
      '<h3 id="pd-title">' + esc(p.name) + "</h3>" +
      (p.pronunciation ? '<p class="pd-pron">' + esc(p.pronunciation) + "</p>" : "") + "</div>";
    var tabs = '<div class="pd-tabs" role="tablist">' +
      '<button class="pd-tab" role="tab" data-tab="layman" aria-selected="true">In plain language</button>' +
      '<button class="pd-tab" role="tab" data-tab="clinical" aria-selected="false">Clinical reference</button>' +
      "</div>";
    overlay.querySelector(".pd-body").innerHTML = head + tabs + laymanPanel(p) + clinicalPanel(p);
  }

  function open(id) {
    ensureOverlay();
    lastFocus = document.activeElement;
    overlay.querySelector(".pd-body").innerHTML = '<p class="cx-empty" style="padding:20px">Loading…</p>';
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    overlay.querySelector(".nm-close").focus();
    load().then(function (map) {
      var p = map[id];
      if (!p) { overlay.querySelector(".pd-body").innerHTML =
        '<p class="cx-empty" style="padding:20px">Details for this parameter are in the app.</p>'; return; }
      render(p);
      overlay.querySelector(".nm-card").scrollTop = 0;
    }).catch(function () {
      overlay.querySelector(".pd-body").innerHTML =
        '<p class="cx-empty" style="padding:20px">Couldn’t load details — please refresh.</p>';
    });
  }

  function close() {
    if (!overlay) return;
    overlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function onActivate(e) {
    var el = e.target.closest("[data-param]");
    if (!el) return;
    if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
    if (e.type === "keydown") e.preventDefault();
    open(el.getAttribute("data-param"));
  }

  document.addEventListener("DOMContentLoaded", function () {
    var cfg = document.getElementById("pd-app-links");
    if (cfg) {
      appLinks.ios = cfg.dataset.ios || "#";
      appLinks.android = cfg.dataset.android || "#";
    }
    document.addEventListener("click", onActivate);
    document.addEventListener("keydown", onActivate);
  });
})();
