/* Nutrisize — per-meal nutrition popup.
 * Tap a meal row → a fixed-overlay popup shows that meal's calories + macros as
 * %DV bars and numbers, plus fiber/sodium/sugar, a vitamins & minerals section,
 * and a per-food breakdown (every constituent food expands to its own full
 * nutrient panel), all computed from the meal's itemized foods (embedded per
 * page in the #nutri-data JSON blob by scripts/render_plans.py). Closes on the
 * × button, an outside tap, or Esc. The overlay is position:fixed, so page
 * content never shifts. No dependencies. */
(function () {
  "use strict";

  // FDA reference Daily Values (2,000-kcal reference diet).
  var DV = { kcal: 2000, protein: 50, carbs: 275, fat: 78 };
  var ORDER = [
    { key: "kcal", label: "Calories", unit: "kcal", cls: "kcal" },
    { key: "protein", label: "Protein", unit: "g", cls: "protein" },
    { key: "carbs", label: "Carbs", unit: "g", cls: "carbs" },
    { key: "fat", label: "Fat", unit: "g", cls: "fat" },
  ];

  // Extended nutrients from the itemized foods. Index = position in each
  // meal's "t" array — order MUST match NUTRIENT_ORDER in scripts/render_plans.py.
  // dv: FDA adult Daily Value; sugar has no DV (FDA defines one for ADDED sugar
  // only; the food data carries total sugar), so it renders as a value-only row.
  var NUTR = [
    { label: "Fiber", unit: "g", dv: 28, cls: "fiber" },
    { label: "Total sugar", unit: "g", dv: 0, cls: "sugar" },
    { label: "Sodium", unit: "mg", dv: 2300, cls: "sodium" },
    { label: "Vitamin A", unit: "µg", dv: 900, vit: 1 },
    { label: "Vitamin C", unit: "mg", dv: 90, vit: 1 },
    { label: "Vitamin D", unit: "µg", dv: 20, vit: 1 },
    { label: "Vitamin E", unit: "mg", dv: 15, vit: 1 },
    { label: "Vitamin K", unit: "µg", dv: 120, vit: 1 },
    { label: "Thiamin B1", unit: "mg", dv: 1.2, vit: 1 },
    { label: "Riboflavin B2", unit: "mg", dv: 1.3, vit: 1 },
    { label: "Niacin B3", unit: "mg", dv: 16, vit: 1 },
    { label: "Vitamin B6", unit: "mg", dv: 1.7, vit: 1 },
    { label: "Folate B9", unit: "µg", dv: 400, vit: 1 },
    { label: "Vitamin B12", unit: "µg", dv: 2.4, vit: 1 },
    { label: "Calcium", unit: "mg", dv: 1300, vit: 1 },
    { label: "Iron", unit: "mg", dv: 18, vit: 1 },
    { label: "Magnesium", unit: "mg", dv: 420, vit: 1 },
    { label: "Phosphorus", unit: "mg", dv: 1250, vit: 1 },
    { label: "Potassium", unit: "mg", dv: 4700, vit: 1 },
    { label: "Zinc", unit: "mg", dv: 11, vit: 1 },
    { label: "Selenium", unit: "µg", dv: 55, vit: 1 },
  ];

  // Per-food per-100g arrays in the page food table put the four macros first —
  // order MUST match FOOD_NUTRIENT_ORDER in scripts/render_plans.py.
  var FOOD_NUTR = [
    { label: "Calories", unit: "kcal", dv: 2000 },
    { label: "Protein", unit: "g", dv: 50 },
    { label: "Carbs", unit: "g", dv: 275 },
    { label: "Fat", unit: "g", dv: 78 },
  ].concat(NUTR);

  var overlay, card, lastFocus, nutriData;

  function getNutriData() {
    if (nutriData === undefined) {
      var el = document.getElementById("nutri-data");
      nutriData = null;
      if (el) {
        try { nutriData = JSON.parse(el.textContent); } catch (e) { /* stay null */ }
      }
    }
    return nutriData;
  }

  function buildOverlay() {
    overlay = document.createElement("div");
    overlay.className = "nutri-modal";
    overlay.setAttribute("hidden", "");
    overlay.innerHTML =
      '<div class="nm-card" role="dialog" aria-modal="true" aria-labelledby="nm-title">' +
      '<button class="nm-close" type="button" aria-label="Close">&times;</button>' +
      '<div class="nm-head"><span class="nm-eyebrow" id="nm-eyebrow"></span>' +
      '<h3 id="nm-title"></h3><p class="nm-foods" id="nm-foods"></p></div>' +
      '<div class="nm-bars" id="nm-bars"></div>' +
      '<div id="nm-micros"></div>' +
      '<p class="nm-note">% Daily Value on a 2,000-calorie reference diet. ' +
      "Educational estimate — not medical or dietary advice.</p>" +
      '<div class="nm-more" aria-hidden="true">&#8595; scroll for foods &amp; vitamins</div>' +
      "</div>";
    document.body.appendChild(overlay);
    card = overlay.querySelector(".nm-card");

    // Scroll cue: visible only while more popup content is below the fold.
    card.addEventListener("scroll", updateMore);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close(); // tap outside the card
    });
    overlay.querySelector(".nm-close").addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) close();
    });
  }

  function pct(v, dv) { return Math.round((v / dv) * 100); }

  function updateMore() {
    var more = overlay.querySelector(".nm-more");
    var atEnd = card.scrollTop + card.clientHeight >= card.scrollHeight - 24;
    more.classList.toggle("nm-more-hidden", atEnd);
  }

  function fmt(v) {
    if (v >= 100) return Math.round(v).toLocaleString();
    if (v >= 10) return "" + Math.round(v);
    if (v >= 1) return "" + Math.round(v * 10) / 10;
    return "" + Math.round(v * 100) / 100;
  }

  function barHTML(label, v, unit, dv, cls) {
    var valStr = "<b>" + fmt(v) + "</b> " + unit;
    if (!dv) {
      return '<div class="nm-bar ' + cls + ' nm-noDV"><div class="nm-bar-top">' +
        '<span class="nm-bar-label">' + label + "</span>" +
        '<span class="nm-bar-val">' + valStr +
        ' <span class="nm-bar-pct">no %DV*</span></span></div></div>';
    }
    var p = pct(v, dv);
    return '<div class="nm-bar ' + cls + '"><div class="nm-bar-top">' +
      '<span class="nm-bar-label">' + label + "</span>" +
      '<span class="nm-bar-val">' + valStr +
      ' <span class="nm-bar-pct">' + p + "% DV</span></span></div>" +
      '<div class="nm-track"><span class="nm-fill" style="width:' +
      Math.min(p, 100) + '%"></span></div></div>';
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // Compact label/value/%DV rows. specs: [{label, unit, dv, vit}], vals aligned
  // by index. vitOnly limits to the vitamins/minerals subset (meal-level grid);
  // per-food grids pass false and show everything, macros included.
  function microGrid(specs, vals, vitOnly) {
    var rows = "";
    specs.forEach(function (n, i) {
      if (vitOnly && !n.vit) return;
      var v = vals[i];
      var body;
      if (!n.dv) {
        body = '<span class="nm-micro-val"><b>' + fmt(v) + "</b> " + n.unit +
          ' <span class="nm-bar-pct nm-nodv">no DV*</span></span>';
      } else {
        var p = pct(v, n.dv);
        body = '<span class="nm-micro-val"><b>' + fmt(v) + "</b> " + n.unit +
          ' <span class="nm-bar-pct">' + p + "%</span></span>" +
          '<div class="nm-track"><span class="nm-fill" style="width:' +
          Math.min(p, 100) + '%"></span></div>';
      }
      rows += '<div class="nm-micro"><span class="nm-micro-label">' + n.label +
        "</span>" + body + "</div>";
    });
    return rows;
  }

  // "Foods in this meal": one expandable row per constituent food, each with
  // the food's full nutrient panel for its portion in this meal.
  function foodsHTML(foods, meal) {
    if (!foods || !meal.i || !meal.i.length) return "";
    var out = "";
    meal.i.forEach(function (it) {
      var food = foods[it[0]];
      if (!food) return;
      var grams = it[1];
      var per100 = food[1];
      var vals = per100.map(function (v, i) {
        var x = v * grams / 100;
        // fiber (index 4: after the 4 macros) carries the day reconciliation
        // scale so foods sum to their meal and meals sum to the day
        return i === 4 ? x * (meal.s || 1) : x;
      });
      var portion = it[2] ? esc(it[2]) + " · " + fmt(grams) + " g" : fmt(grams) + " g";
      out += '<details class="nm-food"><summary><span class="nm-food-name">' +
        esc(food[0]) + '</span><span class="nm-food-meta">' + portion +
        ' · <b>' + fmt(vals[0]) + '</b> kcal</span></summary>' +
        '<div class="nm-micro-grid">' + microGrid(FOOD_NUTR, vals, false) +
        "</div></details>";
    });
    return '<div class="nm-foods-sec"><h4>Foods in this meal <span class="nm-sum-hint">' +
      "tap a food for its nutrients</span></h4>" + out + "</div>";
  }

  function open(row) {
    if (!overlay) buildOverlay();
    var d = row.dataset;
    var vals = { kcal: +d.kcal, protein: +d.protein, carbs: +d.carbs, fat: +d.fat };

    overlay.querySelector("#nm-eyebrow").textContent = "Nutrition · " + (d.meal || "Meal");
    overlay.querySelector("#nm-title").textContent = d.meal || "Meal";
    overlay.querySelector("#nm-foods").textContent = d.items || "";

    var bars = overlay.querySelector("#nm-bars");
    bars.innerHTML = "";
    ORDER.forEach(function (row2) {
      var v = vals[row2.key];
      bars.insertAdjacentHTML("beforeend",
        barHTML(row2.label, v, row2.unit, DV[row2.key], row2.cls));
    });

    // Extended nutrients for this meal, when the page carries itemized data.
    var micros = overlay.querySelector("#nm-micros");
    micros.innerHTML = "";
    var data = getNutriData();
    var meal = data && data.meals && d.nid ? data.meals[d.nid] : null;
    if (meal) {
      var nvals = meal.t;
      NUTR.forEach(function (n, i) {
        if (!n.vit) bars.insertAdjacentHTML("beforeend",
          barHTML(n.label, nvals[i], n.unit, n.dv, n.cls));
      });
      micros.innerHTML =
        foodsHTML(data.foods, meal) +
        '<details class="nm-micros"><summary>Vitamins &amp; minerals <span class="nm-sum-hint">' +
        "estimated from this meal's foods</span></summary>" +
        '<div class="nm-micro-grid">' + microGrid(NUTR, nvals, true) + "</div></details>" +
        '<p class="nm-note nm-sugar-note">*FDA sets a Daily Value for added sugar only; ' +
        "the value shown is total sugar.</p>";
    }

    lastFocus = document.activeElement;
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    card.scrollTop = 0;
    updateMore();
    overlay.querySelector(".nm-close").focus();
  }

  function close() {
    if (!overlay) return;
    overlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function onActivate(e) {
    var row = e.target.closest(".meal-row");
    if (!row) return;
    if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
    if (e.type === "keydown") e.preventDefault();
    open(row);
  }

  document.addEventListener("click", onActivate);
  document.addEventListener("keydown", onActivate);
})();
