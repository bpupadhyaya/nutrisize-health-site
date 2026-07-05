/* Nutrisize — per-meal nutrition popup.
 * Tap a meal row → a fixed-overlay popup shows that meal's calories + macros as
 * %DV bars and numbers. Closes on the × button, an outside tap, or Esc.
 * The overlay is position:fixed, so page content never shifts. No dependencies. */
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

  var overlay, card, lastFocus;

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
      '<p class="nm-note">% Daily Value on a 2,000-calorie reference diet. ' +
      "Educational estimate — not medical or dietary advice.</p>" +
      "</div>";
    document.body.appendChild(overlay);
    card = overlay.querySelector(".nm-card");

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close(); // tap outside the card
    });
    overlay.querySelector(".nm-close").addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) close();
    });
  }

  function pct(v, dv) { return Math.round((v / dv) * 100); }

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
      var v = vals[row2.key], p = pct(v, DV[row2.key]);
      var el = document.createElement("div");
      el.className = "nm-bar " + row2.cls;
      el.innerHTML =
        '<div class="nm-bar-top"><span class="nm-bar-label">' + row2.label + "</span>" +
        '<span class="nm-bar-val"><b>' + v.toLocaleString() + "</b> " + row2.unit +
        ' <span class="nm-bar-pct">' + p + "% DV</span></span></div>" +
        '<div class="nm-track"><span class="nm-fill" style="width:' +
        Math.min(p, 100) + '%"></span></div>';
      bars.appendChild(el);
    });

    lastFocus = document.activeElement;
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
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
