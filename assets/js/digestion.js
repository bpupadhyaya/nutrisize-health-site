/* Nutrisize — Digestion & sleep-impact tool (/digestion).
 * Build an evening meal from the app's digestion dataset, set your dinner time
 * and bedtime, and see when the meal finishes digesting and whether it's still
 * working at bedtime ("sleep distance"). Client-side only; no dependencies. */
(function () {
  "use strict";

  var foods = [], byName = {}, combos = [], data = null, meal = [];
  var els = {};

  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function fmtH(h) {
    var hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    if (mm === 60) { hh++; mm = 0; }
    return hh + "h" + (mm ? " " + mm + "m" : "");
  }
  function parseTime(t) { var m = /^(\d{1,2}):(\d{2})$/.exec(t || ""); return m ? +m[1] + +m[2] / 60 : NaN; }
  function clock(h) {
    h = ((h % 24) + 24) % 24;
    var hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    if (mm === 60) { hh = (hh + 1) % 24; mm = 0; }
    var ap = hh < 12 ? "am" : "pm", h12 = hh % 12 || 12;
    return h12 + ":" + (mm < 10 ? "0" : "") + mm + ap;
  }

  function totalHours(f) { return (f.digest || 0) + (f.absorb || 0); }

  function compute() {
    var dinner = parseTime(els.dinner.value), bed = parseTime(els.bed.value);
    if (!meal.length || isNaN(dinner) || isNaN(bed)) {
      els.result.innerHTML = '<p class="tool-note" style="padding:8px">Add a food or two and set your times to see the sleep impact.</p>';
      return;
    }
    var slowest = meal.reduce(function (a, b) { return totalHours(b) > totalHours(a) ? b : a; });
    var clear = totalHours(slowest);
    var mixed = meal.length > 1 ? 0.5 : 0; // a mixed meal digests a little slower
    clear += mixed;
    var doneAt = dinner + clear;
    var bedAbs = bed < dinner ? bed + 24 : bed; // bedtime later same night
    var distance = bedAbs - doneAt; // + = digested before bed, − = still digesting

    var verdict, cls, tip;
    if (distance >= 1) { verdict = "Clear before bed"; cls = "ok";
      tip = "Your meal should finish digesting about " + fmtH(distance) + " before you sleep — good for rest."; }
    else if (distance >= -0.25) { verdict = "Cutting it close"; cls = "worry";
      tip = "Digestion wraps up right around bedtime. A slightly earlier dinner would give you more buffer."; }
    else { verdict = "Still digesting at bedtime"; cls = "worry";
      tip = "Your meal is likely still digesting " + fmtH(-distance) + " into the night, which can disturb sleep. " +
        "Try eating earlier or choosing lighter, faster foods in the evening."; }

    var rows = meal.map(function (f, i) {
      return '<div class="cx-rel" style="padding:9px 12px"><div class="cx-rel-head">' +
        '<span class="cx-rel-name">' + esc(f.name) + "</span>" +
        '<span class="cx-badge time">' + fmtH(totalHours(f)) + "</span>" +
        '<button class="fx-reset" data-rm="' + i + '" style="margin-left:auto; color:#b91c1c">Remove</button></div>' +
        (f.note ? '<p class="cx-mech" style="margin-top:4px">' + esc(f.note) + "</p>" : "") + "</div>";
    }).join("");

    els.result.innerHTML =
      '<div class="tool-hero" style="margin-bottom:6px">' +
      '<div class="tool-stat"><div class="v">' + clock(doneAt) + '</div><div class="k">Digestion finishes</div></div>' +
      '<div class="tool-stat"><div class="v ' + (cls === "ok" ? "delta-down" : "delta-up") + '">' +
      (distance >= 0 ? fmtH(distance) : "−" + fmtH(-distance)) + '</div><div class="k">' +
      (distance >= 0 ? "Buffer before bed" : "Overlap with sleep") + "</div></div>" +
      '<div class="tool-stat"><div class="v">' + fmtH(clear) + '</div><div class="k">Total to digest' +
      (mixed ? " (mixed meal)" : "") + "</div></div></div>" +
      '<div class="pd-hl"><div class="pd-cell ' + cls + '"><span class="pd-k">' + verdict +
      '</span><span class="pd-v">' + tip + "</span></div></div>" +
      '<div style="margin-top:14px">' + rows + "</div>";
  }

  function addFood(name) {
    var f = byName[name.toLowerCase()];
    if (f && meal.length < 8) { meal.push(f); compute(); }
    els.search.value = "";
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["search", "list", "add", "dinner", "bed", "result"].forEach(function (k) { els[k] = document.getElementById("dg-" + k); });
    if (!els.result) return;

    fetch("../assets/data/free/digestion.json").then(function (r) { return r.json(); }).then(function (d) {
      data = d; foods = d.foods; combos = d.combinationEffects || [];
      foods.forEach(function (f) { byName[f.name.toLowerCase()] = f; });
      // datalist for the search box
      var dl = document.getElementById("dg-foods");
      if (dl) dl.innerHTML = foods.map(function (f) { return '<option value="' + esc(f.name) + '">'; }).join("");
      compute();
    }).catch(function () {
      els.result.innerHTML = '<p class="tool-note">Couldn’t load the digestion data — please refresh.</p>';
    });

    els.add.addEventListener("click", function () { if (els.search.value) addFood(els.search.value); });
    els.search.addEventListener("change", function () { if (this.value && byName[this.value.toLowerCase()]) addFood(this.value); });
    document.addEventListener("input", function (e) {
      if (e.target === els.dinner || e.target === els.bed) compute();
    });
    els.result.addEventListener("click", function (e) {
      var b = e.target.closest("[data-rm]");
      if (b) { meal.splice(+b.dataset.rm, 1); compute(); }
    });
  });
})();
