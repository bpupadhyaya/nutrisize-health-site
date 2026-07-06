/* Nutrisize — Food Explorer (/foods).
 * Fetches the free-tier food dataset (assets/data/free/foods.json, generated
 * by scripts/export_free_tier.py) and renders a searchable, sortable,
 * filterable table with a per-food nutrition popup (reusing the nm-* modal
 * styles from plans.css) and a side-by-side compare view (up to 4 foods).
 * Everything runs in memory — nothing is stored in the browser. Filter state
 * mirrors into the URL query string so views are bookmarkable/shareable.
 * No dependencies. */
(function () {
  "use strict";

  // FDA adult Daily Values, keyed by the dataset's nutrientsPer100g keys.
  // dv: 0 → value-only row (FDA defines a DV for added sugar only).
  var SPECS = [
    { key: "calories", label: "Calories", unit: "kcal", dv: 2000, macro: 1 },
    { key: "protein", label: "Protein", unit: "g", dv: 50, macro: 1 },
    { key: "carbohydrates", label: "Carbs", unit: "g", dv: 275, macro: 1 },
    { key: "fat", label: "Fat", unit: "g", dv: 78, macro: 1 },
    { key: "fiber", label: "Fiber", unit: "g", dv: 28, macro: 1 },
    { key: "sugar", label: "Total sugar", unit: "g", dv: 0, macro: 1 },
    { key: "sodium", label: "Sodium", unit: "mg", dv: 2300, macro: 1 },
    { key: "vitaminA", label: "Vitamin A", unit: "µg", dv: 900 },
    { key: "vitaminC", label: "Vitamin C", unit: "mg", dv: 90 },
    { key: "vitaminD", label: "Vitamin D", unit: "µg", dv: 20 },
    { key: "vitaminE", label: "Vitamin E", unit: "mg", dv: 15 },
    { key: "vitaminK", label: "Vitamin K", unit: "µg", dv: 120 },
    { key: "vitaminB1", label: "Thiamin B1", unit: "mg", dv: 1.2 },
    { key: "vitaminB2", label: "Riboflavin B2", unit: "mg", dv: 1.3 },
    { key: "vitaminB3", label: "Niacin B3", unit: "mg", dv: 16 },
    { key: "vitaminB6", label: "Vitamin B6", unit: "mg", dv: 1.7 },
    { key: "vitaminB9", label: "Folate B9", unit: "µg", dv: 400 },
    { key: "vitaminB12", label: "Vitamin B12", unit: "µg", dv: 2.4 },
    { key: "calcium", label: "Calcium", unit: "mg", dv: 1300 },
    { key: "iron", label: "Iron", unit: "mg", dv: 18 },
    { key: "magnesium", label: "Magnesium", unit: "mg", dv: 420 },
    { key: "phosphorus", label: "Phosphorus", unit: "mg", dv: 1250 },
    { key: "potassium", label: "Potassium", unit: "mg", dv: 4700 },
    { key: "zinc", label: "Zinc", unit: "mg", dv: 11 },
    { key: "selenium", label: "Selenium", unit: "µg", dv: 55 },
  ];

  var SORTS = {
    name: function (a, b) { return a.name.localeCompare(b.name); },
    calories: byNutrient("calories"),
    protein: byNutrient("protein"),
    fiber: byNutrient("fiber"),
    density: function (a, b) { return (b.densityScore || 0) - (a.densityScore || 0); },
  };

  var foods = [], state = { q: "", cat: "", gi: "", sort: "name" };
  var compare = []; // food objects, max 4
  var els = {};

  function byNutrient(key) {
    return function (a, b) {
      return (nv(b, key) || 0) - (nv(a, key) || 0);
    };
  }

  function nv(food, key) {
    var n = food.nutrientsPer100g;
    return n && typeof n[key] === "number" ? n[key] : null;
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function fmt(v) {
    if (v == null) return "–";
    if (v >= 100) return Math.round(v).toLocaleString();
    if (v >= 10) return "" + Math.round(v);
    if (v >= 1) return "" + Math.round(v * 10) / 10;
    return "" + Math.round(v * 100) / 100;
  }

  function titleCase(s) {
    return String(s || "").replace(/[-_]/g, " ")
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function densityChip(score) {
    if (score == null) return '<span class="fx-chip na">–</span>';
    var cls = score >= 7 ? "good" : score >= 4 ? "mid" : "low";
    return '<span class="fx-chip ' + cls + '">' + fmt(score) + "</span>";
  }

  // Dataset GI values: low, low-medium, medium-high, high, none, varies.
  function giChip(cat) {
    var c = String(cat || "").toLowerCase();
    if (!c || c === "none" || c === "varies") {
      return '<span class="fx-chip na">' + (c === "varies" ? "Varies" : "–") + "</span>";
    }
    var cls = c === "low" ? "good" : c === "high" ? "low" : "mid";
    return '<span class="fx-chip ' + cls + '">' + esc(titleCase(cat)) + "</span>";
  }

  // ------------------------------------------------------------ filtering

  function visible() {
    var q = state.q.toLowerCase();
    var out = foods.filter(function (f) {
      if (state.cat && f.category !== state.cat) return false;
      if (state.gi && String(f.giCategory || "").toLowerCase() !== state.gi) return false;
      if (q && f.name.toLowerCase().indexOf(q) === -1 &&
          String(f.subcategory || "").toLowerCase().indexOf(q) === -1) return false;
      return true;
    });
    out.sort(SORTS[state.sort] || SORTS.name);
    return out;
  }

  function syncURL() {
    var p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.cat) p.set("cat", state.cat);
    if (state.gi) p.set("gi", state.gi);
    if (state.sort !== "name") p.set("sort", state.sort);
    var qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  function readURL() {
    var p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    state.cat = p.get("cat") || "";
    state.gi = (p.get("gi") || "").toLowerCase();
    state.sort = SORTS[p.get("sort")] ? p.get("sort") : "name";
  }

  // ------------------------------------------------------------ rendering

  function render() {
    var rows = visible();
    els.count.textContent = "Showing " + rows.length + " of " + foods.length +
      " free foods · per 100 g · tap a food for its full nutrition panel";
    var html = rows.map(function (f, i) {
      var checked = compare.indexOf(f) !== -1 ? " checked" : "";
      return '<tr tabindex="0" role="button" data-i="' + foods.indexOf(f) + '"' +
        ' aria-label="' + esc(f.name) + ' — open nutrition panel">' +
        '<td class="fx-name"><b>' + esc(f.name) + "</b>" +
        (f.subcategory ? '<span class="fx-sub">' + esc(titleCase(f.subcategory)) + "</span>" : "") + "</td>" +
        "<td>" + esc(titleCase(f.category)) + "</td>" +
        '<td class="fx-num">' + fmt(nv(f, "calories")) + "</td>" +
        '<td class="fx-num">' + fmt(nv(f, "protein")) + "</td>" +
        '<td class="fx-num">' + fmt(nv(f, "carbohydrates")) + "</td>" +
        '<td class="fx-num">' + fmt(nv(f, "fat")) + "</td>" +
        '<td class="fx-num">' + fmt(nv(f, "fiber")) + "</td>" +
        "<td>" + densityChip(f.densityScore) + "</td>" +
        "<td>" + giChip(f.giCategory) + "</td>" +
        '<td class="fx-cmp"><input type="checkbox" aria-label="Compare ' + esc(f.name) + '"' +
        checked + "></td></tr>";
    }).join("");
    els.tbody.innerHTML = html ||
      '<tr><td colspan="10" style="text-align:center; color:#6b7f74; padding:28px;">' +
      "No foods match — try clearing a filter.</td></tr>";
    syncURL();
  }

  function renderCompareBar() {
    els.cmpBar.hidden = compare.length === 0;
    if (compare.length) {
      els.cmpNames.textContent = compare.map(function (f) { return f.name; }).join(" · ");
      els.cmpGo.textContent = "Compare " + compare.length;
      els.cmpGo.disabled = compare.length < 2;
    }
  }

  // ------------------------------------------------------------ modals

  var overlay;

  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.className = "nutri-modal";
    overlay.setAttribute("hidden", "");
    overlay.innerHTML = '<div class="nm-card" role="dialog" aria-modal="true">' +
      '<button class="nm-close" type="button" aria-label="Close">&times;</button>' +
      '<div class="fx-modal-body"></div></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) closeModal(); });
    overlay.querySelector(".nm-close").addEventListener("click", closeModal);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) closeModal();
    });
  }

  function openModal(html) {
    ensureOverlay();
    overlay.querySelector(".fx-modal-body").innerHTML = html;
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    overlay.querySelector(".nm-card").scrollTop = 0;
    overlay.querySelector(".nm-close").focus();
  }

  function closeModal() {
    if (!overlay) return;
    overlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
  }

  function barHTML(spec, v) {
    if (v == null) return "";
    var val = "<b>" + fmt(v) + "</b> " + spec.unit;
    if (!spec.dv) {
      return '<div class="nm-bar nm-noDV"><div class="nm-bar-top">' +
        '<span class="nm-bar-label">' + spec.label + "</span>" +
        '<span class="nm-bar-val">' + val + ' <span class="nm-bar-pct">no %DV*</span></span></div></div>';
    }
    var p = Math.round((v / spec.dv) * 100);
    return '<div class="nm-bar"><div class="nm-bar-top">' +
      '<span class="nm-bar-label">' + spec.label + "</span>" +
      '<span class="nm-bar-val">' + val + ' <span class="nm-bar-pct">' + p + "% DV</span></span></div>" +
      '<div class="nm-track"><span class="nm-fill" style="width:' + Math.min(p, 100) + '%"></span></div></div>';
  }

  function microHTML(spec, v) {
    if (v == null) return "";
    var p = spec.dv ? Math.round((v / spec.dv) * 100) : null;
    return '<div class="nm-micro"><span class="nm-micro-label">' + spec.label + "</span>" +
      '<span class="nm-micro-val"><b>' + fmt(v) + "</b> " + spec.unit +
      (p == null ? ' <span class="nm-bar-pct nm-nodv">no DV*</span></span>'
        : ' <span class="nm-bar-pct">' + p + "%</span></span>" +
          '<div class="nm-track"><span class="nm-fill" style="width:' + Math.min(p, 100) + '%"></span></div>') +
      "</div>";
  }

  function detailHTML(f) {
    var bars = SPECS.filter(function (s) { return s.macro; })
      .map(function (s) { return barHTML(s, nv(f, s.key)); }).join("");
    var micros = SPECS.filter(function (s) { return !s.macro; })
      .map(function (s) { return microHTML(s, nv(f, s.key)); }).join("");

    var tags = "";
    if (f.densityScore != null) tags += densityChip(f.densityScore).replace('">', '">Density ');
    if (f.giCategory) tags += giChip(f.giCategory).replace('">', '">GI ');
    if (f.isStaple) tags += '<span class="fx-chip good">Staple</span>';
    (Array.isArray(f.allergens) ? f.allergens : []).forEach(function (a) {
      tags += '<span class="fx-chip low">Allergen: ' + esc(titleCase(a)) + "</span>";
    });

    var servings = (f.servingSizes || []).map(function (s) {
      return esc(s.label) + " (<b>" + fmt(s.grams) + " g</b>)";
    }).join(" · ");

    var links = "";
    if (Array.isArray(f.physiologyLinks) && f.physiologyLinks.length) {
      links = '<div class="fx-links"><h4>What it touches in your body</h4>' +
        f.physiologyLinks.map(function (l) {
          return '<p><span class="fx-param">' + esc(titleCase(l.param)) + "</span> — " +
            esc(l.effect) + "</p>";
        }).join("") +
        '<p style="margin-top:8px; font-size:12px; color:#6b7f74;">In the app, each parameter links ' +
        "onward to its healthy range, interpretation, and the exercises that move it.</p></div>";
    }

    return '<div class="nm-head"><span class="nm-eyebrow">Per 100 g · ' +
      esc(titleCase(f.category)) + "</span>" +
      "<h3>" + esc(f.name) + "</h3>" +
      (f.description ? '<p class="nm-foods">' + esc(f.description) + "</p>" : "") +
      '<div class="fx-tags">' + tags + "</div></div>" +
      '<div class="nm-bars">' + bars + "</div>" +
      (servings ? '<p class="fx-serv">Common servings: ' + servings + "</p>" : "") +
      '<details class="nm-micros" open><summary>Vitamins &amp; minerals</summary>' +
      '<div class="nm-micro-grid">' + micros + "</div></details>" +
      links +
      '<p class="nm-note">% Daily Value on a 2,000-calorie reference diet. ' +
      "*FDA sets a Daily Value for added sugar only; the value shown is total sugar. " +
      "Educational reference — not medical or dietary advice.</p>" +
      '<p class="nm-app">This is 1 of 533 free foods. The app carries all 4,995 — with serving-size ' +
      "math, regional names, and your personal daily targets. " +
      '<a href="/#download">Get the app</a></p>';
  }

  function compareHTML() {
    var head = "<tr><th>Nutrient (per 100 g)</th>" + compare.map(function (f) {
      return "<th>" + esc(f.name) + "</th>";
    }).join("") + "</tr>";
    var body = SPECS.map(function (s) {
      var vals = compare.map(function (f) { return nv(f, s.key); });
      var known = vals.filter(function (v) { return v != null; });
      if (!known.length) return "";
      // Highlight the "winner": highest for nutrients, lowest for sodium/sugar.
      var lowIsGood = s.key === "sodium" || s.key === "sugar";
      var best = (lowIsGood ? Math.min : Math.max).apply(null, known);
      return "<tr><td>" + s.label + ' <span class="fx-dim">' + s.unit + "</span></td>" +
        vals.map(function (v) {
          var cls = v != null && v === best && known.length > 1 ? ' class="fx-best"' : "";
          return "<td" + cls + ">" + fmt(v) +
            (v != null && s.dv ? ' <span class="fx-dim">' + Math.round((v / s.dv) * 100) + "%</span>" : "") +
            "</td>";
        }).join("") + "</tr>";
    }).join("");
    return '<div class="nm-head"><span class="nm-eyebrow">Side by side · per 100 g · % of Daily Value</span>' +
      "<h3>Compare foods</h3></div>" +
      '<div class="table-scroll"><table class="fx-cmp-table"><thead>' + head + "</thead><tbody>" +
      body + "</tbody></table></div>" +
      '<p class="nm-note">Bold marks the best value in each row (lowest for sodium and sugar, ' +
      "highest otherwise). Educational reference — not medical or dietary advice.</p>" +
      '<p class="nm-app">Comparing your own meals is one tap in the app — across all 4,995 foods. ' +
      '<a href="/#download">Get the app</a></p>';
  }

  // ------------------------------------------------------------ wiring

  function toggleCompare(f, checked) {
    var i = compare.indexOf(f);
    if (checked && i === -1) {
      if (compare.length >= 4) {
        render(); // uncheck the box that can't be added
        renderCompareBar();
        els.cmpNames.textContent = "Up to 4 foods — remove one first · " + els.cmpNames.textContent;
        return;
      }
      compare.push(f);
    } else if (!checked && i !== -1) {
      compare.splice(i, 1);
    }
    renderCompareBar();
  }

  function init(data) {
    foods = data.foods;

    // Category options from the data itself.
    var cats = {};
    foods.forEach(function (f) { cats[f.category] = 1; });
    Object.keys(cats).sort().forEach(function (c) {
      var o = document.createElement("option");
      o.value = c; o.textContent = titleCase(c);
      els.cat.appendChild(o);
    });

    readURL();
    els.q.value = state.q;
    els.cat.value = state.cat;
    els.gi.value = state.gi;
    els.sort.value = state.sort;

    els.q.addEventListener("input", function () { state.q = this.value.trim(); render(); });
    els.cat.addEventListener("change", function () { state.cat = this.value; render(); });
    els.gi.addEventListener("change", function () { state.gi = this.value; render(); });
    els.sort.addEventListener("change", function () { state.sort = this.value; render(); });
    els.reset.addEventListener("click", function () {
      state = { q: "", cat: "", gi: "", sort: "name" };
      els.q.value = ""; els.cat.value = ""; els.gi.value = ""; els.sort.value = "name";
      render();
    });

    els.tbody.addEventListener("click", function (e) {
      var cb = e.target.closest('input[type="checkbox"]');
      var tr = e.target.closest("tr[data-i]");
      if (!tr) return;
      var f = foods[+tr.dataset.i];
      if (cb) { toggleCompare(f, cb.checked); return; }
      openModal(detailHTML(f));
    });
    els.tbody.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      var tr = e.target.closest("tr[data-i]");
      if (!tr || e.target.closest("input")) return;
      e.preventDefault();
      openModal(detailHTML(foods[+tr.dataset.i]));
    });

    els.cmpGo.addEventListener("click", function () {
      if (compare.length >= 2) openModal(compareHTML());
    });
    els.cmpClear.addEventListener("click", function () {
      compare = [];
      renderCompareBar();
      render();
    });

    render();
    renderCompareBar();
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["q", "cat", "gi", "sort", "reset", "tbody", "count", "cmpBar", "cmpNames", "cmpGo", "cmpClear"]
      .forEach(function (id) { els[id] = document.getElementById("fx-" + id); });
    if (!els.tbody) return;

    fetch("../assets/data/free/foods.json")
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(init)
      .catch(function () {
        els.count.textContent = "The food data couldn’t be loaded — please refresh, " +
          "or browse all 4,995 foods in the app.";
      });
  });
})();
