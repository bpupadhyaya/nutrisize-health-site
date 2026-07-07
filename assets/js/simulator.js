/* Nutrisize — What-if weight & energy simulator (/simulator).
 * Projects body weight over time under a chosen daily calorie change, using
 * Mifflin-St Jeor BMR recomputed each week as weight changes — so the curve
 * flattens the way real weight loss plateaus (metabolic adaptation). Draws an
 * interactive SVG chart comparing the realistic (adapting) path to the naive
 * straight-line projection. Runs entirely in memory; inputs mirror to the URL.
 * No dependencies. */
(function () {
  "use strict";

  var KCAL_PER_KG = 7700; // energy in ~1 kg of body-weight change
  var WEEKS = 24;
  var els = {};

  function $(id) { return document.getElementById(id); }
  function num(id) { var v = parseFloat($(id).value); return isFinite(v) ? v : NaN; }

  function bmr(sex, kg, cm, age) {
    return 10 * kg + 6.25 * cm - 5 * age + (sex === "m" ? 5 : -161);
  }

  function readState() {
    var imperial = $("sim-units").value === "imperial";
    var h = num("sim-height"), w = num("sim-weight"), age = num("sim-age");
    if (imperial) { h = h * 2.54; w = w * 0.45359237; }
    return {
      sex: $("sim-sex").value, age: age, cm: h, kg: w, imperial: imperial,
      act: parseFloat($("sim-activity").value),
      delta: parseFloat($("sim-delta").value), // kcal/day vs maintenance
    };
  }

  function project(s) {
    // Week 0..WEEKS. Adaptive: recompute TDEE from current weight each week.
    var adaptive = [], naive = [], kg = s.kg;
    var tdee0 = bmr(s.sex, s.kg, s.cm, s.age) * s.act;
    var naiveKgPerWk = (s.delta * 7) / KCAL_PER_KG; // constant
    for (var wk = 0; wk <= WEEKS; wk++) {
      adaptive.push(kg);
      naive.push(s.kg + naiveKgPerWk * wk);
      var tdee = bmr(s.sex, kg, s.cm, s.age) * s.act;
      // Body defends against a deficit/surplus: the effective daily gap shrinks
      // as weight moves and TDEE tracks it. Model the gap against *current* TDEE
      // by holding intake = starting maintenance + delta.
      var intake = tdee0 + s.delta;
      var gap = intake - tdee; // + surplus, − deficit
      kg += (gap * 7) / KCAL_PER_KG;
      if (kg < 30) kg = 30;
    }
    return { adaptive: adaptive, naive: naive, tdee0: tdee0 };
  }

  function bmiOf(kg, cm) { return cm > 0 ? kg / Math.pow(cm / 100, 2) : NaN; }
  function toDisp(kg, imperial) { return imperial ? kg / 0.45359237 : kg; }
  function unit(imperial) { return imperial ? "lb" : "kg"; }

  function fmt1(n) { return isFinite(n) ? (Math.round(n * 10) / 10).toLocaleString() : "–"; }

  function chart(p, s) {
    var W = 640, H = 300, padL = 44, padR = 16, padT = 16, padB = 28;
    var data = p.adaptive.concat(p.naive);
    var min = Math.min.apply(null, data), max = Math.max.apply(null, data);
    var span = Math.max(max - min, 1);
    min -= span * 0.12; max += span * 0.12;
    var x = function (wk) { return padL + (W - padL - padR) * wk / WEEKS; };
    var y = function (kg) { return padT + (H - padT - padB) * (max - kg) / (max - min); };
    var toPath = function (arr) {
      return arr.map(function (kg, i) { return (i ? "L" : "M") + x(i).toFixed(1) + " " + y(kg).toFixed(1); }).join(" ");
    };

    // Y gridlines / labels (4)
    var grid = "";
    for (var g = 0; g <= 3; g++) {
      var val = min + (max - min) * g / 3;
      var yy = y(val);
      grid += '<line x1="' + padL + '" y1="' + yy.toFixed(1) + '" x2="' + (W - padR) +
        '" y2="' + yy.toFixed(1) + '" stroke="#e6f0ea" stroke-width="1"/>' +
        '<text x="' + (padL - 6) + '" y="' + (yy + 3).toFixed(1) + '" text-anchor="end" ' +
        'font-size="10" fill="#8a9a91">' + fmt1(toDisp(val, s.imperial)) + "</text>";
    }
    // X labels (0, 8, 16, 24 wk)
    var xlab = "";
    [0, 8, 16, 24].forEach(function (wk) {
      xlab += '<text x="' + x(wk).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle" ' +
        'font-size="10" fill="#8a9a91">' + (wk === 0 ? "now" : wk + "w") + "</text>";
    });

    return '<svg viewBox="0 0 ' + W + " " + H + '" role="img" ' +
      'aria-label="Projected weight over ' + WEEKS + ' weeks">' + grid + xlab +
      '<path d="' + toPath(p.naive) + '" fill="none" stroke="#93a29a" stroke-width="2" ' +
      'stroke-dasharray="5 4"/>' +
      '<path d="' + toPath(p.adaptive) + '" fill="none" stroke="#178a5e" stroke-width="3" ' +
      'stroke-linejoin="round"/>' +
      '<circle cx="' + x(WEEKS).toFixed(1) + '" cy="' + y(p.adaptive[WEEKS]).toFixed(1) +
      '" r="4.5" fill="#0b3d2e"/></svg>';
  }

  function render() {
    var s = readState();
    if (!(s.kg > 0 && s.cm > 0 && s.age > 0)) {
      els.out.innerHTML = '<p class="tool-note">Enter your age, height, and weight to see a projection.</p>';
      return;
    }
    var p = project(s);
    var endKg = p.adaptive[WEEKS];
    var deltaKg = endKg - s.kg;
    var endBmi = bmiOf(endKg, s.cm), startBmi = bmiOf(s.kg, s.cm);
    var dir = deltaKg < -0.1 ? "down" : deltaKg > 0.1 ? "up" : "flat";
    var sign = deltaKg > 0 ? "+" : "";

    els.out.innerHTML =
      '<div class="tool-hero">' +
      '<div class="tool-stat"><div class="v">' + fmt1(toDisp(endKg, s.imperial)) + " " + unit(s.imperial) +
      '</div><div class="k">Projected in ' + WEEKS + ' weeks</div></div>' +
      '<div class="tool-stat"><div class="v delta-' + (dir === "up" ? "up" : "down") + '">' +
      (dir === "flat" ? "±0" : sign + fmt1(toDisp(deltaKg, s.imperial))) + " " + unit(s.imperial) +
      '</div><div class="k">Total change</div></div>' +
      '<div class="tool-stat"><div class="v">' + fmt1(endBmi) + '</div><div class="k">BMI (' +
      fmt1(startBmi) + ' today)</div></div>' +
      '<div class="tool-stat"><div class="v">' + Math.round(p.tdee0).toLocaleString() +
      '</div><div class="k">Maintenance kcal/day today</div></div>' +
      "</div>" +
      '<div class="tool-chart">' + chart(p, s) + "</div>" +
      '<div class="tool-legend"><span class="lg"><span class="sw solid"></span>Realistic (metabolism adapts)</span>' +
      '<span class="lg"><span class="sw dash"></span>If nothing adapted</span></div>' +
      '<p class="tool-note">The green curve bends because your body burns less as it changes ' +
      'weight — which is why steady progress plateaus and the straight-line estimate overshoots. ' +
      'A projection from today’s numbers, not a guarantee; real results vary. Educational only, ' +
      'not medical or dietary advice.</p>';

    var q = new URLSearchParams();
    ["sex", "age", "units", "height", "weight", "activity", "delta"].forEach(function (k) {
      var el = $("sim-" + k); if (el && el.value) q.set(k, el.value);
    });
    history.replaceState(null, "", "?" + q.toString());
  }

  function applyURL() {
    var p = new URLSearchParams(location.search);
    ["sex", "age", "units", "height", "weight", "activity", "delta"].forEach(function (k) {
      var v = p.get(k), el = $("sim-" + k);
      if (v != null && el) el.value = v;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    els.out = $("sim-out");
    els.deltaVal = $("sim-delta-val");
    if (!els.out) return;
    applyURL();
    var syncDelta = function () {
      if (els.deltaVal) els.deltaVal.textContent = (parseFloat($("sim-delta").value) > 0 ? "+" : "") + $("sim-delta").value;
    };
    var recompute = function () { syncDelta(); render(); };
    document.addEventListener("input", function (e) { if (e.target.id && e.target.id.indexOf("sim-") === 0) recompute(); });
    document.addEventListener("change", function (e) { if (e.target.id && e.target.id.indexOf("sim-") === 0) recompute(); });
    syncDelta();
    render();
  });
})();
