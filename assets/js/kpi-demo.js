/* Nutrisize — KPI dashboard demo (/coach, embedded).
 * A live illustration of the app's 10-KPI scoring: move sliders for a few daily
 * behaviours and watch all ten scores, statuses, and sparklines recompute — the
 * same ten dimensions the app scores from your real logged data. The formulas
 * here are a plausible illustration, not the production engine. No dependencies,
 * client-side only. */
(function () {
  "use strict";

  var KPIS = [
    "Nutrition Quality", "Nutrition Adequacy", "Hydration & Meal Timing",
    "Activity Volume", "Strength & Mobility", "Recovery & Sedentary Time",
    "Vitals & Sleep", "Biofeedback Signals", "Body Composition", "Adherence & Safety",
  ];

  var INPUTS = [
    { id: "sleep", label: "Sleep", unit: "h/night", min: 4, max: 10, step: 0.5, val: 7 },
    { id: "steps", label: "Steps", unit: "k/day", min: 0, max: 20, step: 1, val: 8 },
    { id: "cardio", label: "Cardio sessions", unit: "/week", min: 0, max: 7, step: 1, val: 3 },
    { id: "strength", label: "Strength sessions", unit: "/week", min: 0, max: 5, step: 1, val: 2 },
    { id: "veg", label: "Veg & fruit", unit: "servings/day", min: 0, max: 10, step: 1, val: 4 },
    { id: "water", label: "Water", unit: "glasses/day", min: 0, max: 12, step: 1, val: 6 },
    { id: "sedentary", label: "Sitting", unit: "h/day", min: 4, max: 14, step: 1, val: 9 },
    { id: "rhr", label: "Resting heart rate", unit: "bpm", min: 45, max: 90, step: 1, val: 66 },
    { id: "logging", label: "Days logged", unit: "/week", min: 0, max: 7, step: 1, val: 5 },
  ];

  var v = {};
  function clamp(n) { return Math.max(0, Math.min(100, n)); }

  function sleepScore(s) {
    if (s >= 7 && s <= 9) return 100;
    return s < 7 ? clamp(40 + (s - 4) / 3 * 60) : clamp(100 - (s - 9) * 15);
  }
  function rhrScore(r) { return clamp(100 - (r - 55) * 2); }

  function scores() {
    var nutQ = clamp(v.veg / 8 * 100);
    var adeq = clamp((v.veg / 8 * 100 + v.logging / 7 * 100) / 2);
    var hyd = clamp(v.water / 8 * 100);
    var act = clamp(0.6 * Math.min(v.steps / 12, 1) * 100 + 0.4 * Math.min(v.cardio / 5, 1) * 100);
    var str = clamp(Math.min(v.strength / 4, 1) * 100);
    var sed = clamp((12 - v.sedentary) / 6 * 100);
    var slp = sleepScore(v.sleep);
    var rec = clamp(0.5 * sed + 0.5 * slp);
    var vit = clamp(0.5 * slp + 0.5 * rhrScore(v.rhr));
    var bio = clamp(0.5 * rhrScore(v.rhr) + 0.5 * slp);
    var body = clamp(0.5 * act + 0.5 * nutQ);
    var adh = clamp(v.logging / 7 * 100);
    return [nutQ, adeq, hyd, act, str, rec, vit, bio, body, adh];
  }

  function statusOf(s) {
    return s >= 85 ? ["Excellent", "excellent"] : s >= 70 ? ["Good", "good"]
      : s >= 55 ? ["Fair", "fair"] : ["Needs attention", "attention"];
  }

  function spark(score, idx) {
    // 7 deterministic points settling toward the current score.
    var W = 120, H = 34, pts = [];
    for (var i = 0; i < 7; i++) {
      var wig = Math.sin(i * 1.25 + idx * 0.9) * 7 - (6 - i) * 1.4;
      pts.push(clamp(score + wig));
    }
    var x = function (i) { return (W - 4) * i / 6 + 2; };
    var y = function (s) { return H - 3 - (H - 6) * s / 100; };
    var d = pts.map(function (s, i) { return (i ? "L" : "M") + x(i).toFixed(1) + " " + y(s).toFixed(1); }).join(" ");
    var st = statusOf(score)[1];
    var col = { excellent: "#14684c", good: "#178a5e", fair: "#b45309", attention: "#b91c1c" }[st];
    return '<svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="2" ' +
      'stroke-linejoin="round" stroke-linecap="round"/></svg>';
  }

  function render() {
    var s = scores();
    document.getElementById("kpi-cards").innerHTML = s.map(function (score, i) {
      var st = statusOf(score);
      return '<div class="kpi-card"><div class="kpi-name">' + KPIS[i] + "</div>" +
        '<div class="kpi-score kpi-s-' + st[1] + '">' + Math.round(score) + "</div>" +
        '<div class="kpi-status kpi-s-' + st[1] + '">' + st[0] + "</div>" +
        '<div class="kpi-spark">' + spark(score, i) + "</div>" +
        '<div class="kpi-band"><span class="kpi-dot" style="left:' + Math.round(score) + '%"></span></div>' +
        "</div>";
    }).join("");
    var avg = Math.round(s.reduce(function (a, b) { return a + b; }, 0) / s.length);
    var el = document.getElementById("kpi-overall");
    if (el) el.textContent = avg;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var panel = document.getElementById("kpi-inputs");
    if (!panel) return;
    panel.innerHTML = INPUTS.map(function (n) {
      return '<div class="tool-field tool-slider"><div class="tool-slabel">' +
        '<label for="kpi-' + n.id + '" style="margin:0">' + n.label + "</label>" +
        '<span class="tool-sval"><span id="kpi-' + n.id + '-v">' + n.val + "</span> " + n.unit + "</span></div>" +
        '<input id="kpi-' + n.id + '" type="range" min="' + n.min + '" max="' + n.max +
        '" step="' + n.step + '" value="' + n.val + '"></div>';
    }).join("");
    INPUTS.forEach(function (n) { v[n.id] = n.val; });
    panel.addEventListener("input", function (e) {
      var m = e.target.id && e.target.id.match(/^kpi-(\w+)$/);
      if (!m) return;
      v[m[1]] = parseFloat(e.target.value);
      var lab = document.getElementById("kpi-" + m[1] + "-v");
      if (lab) lab.textContent = e.target.value;
      render();
    });
    render();
  });
})();
