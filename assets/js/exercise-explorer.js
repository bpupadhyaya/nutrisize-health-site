/* Nutrisize — Exercise Explorer (/exercises).
 * Loads the free-tier exercise index (assets/data/free/exercises-index.json)
 * for a searchable, sortable, filterable table; the per-exercise detail popup
 * lazy-loads that exercise's category file for the full how-to, and includes a
 * MET-based calorie-burn calculator that works for any bodyweight and duration.
 * Runs in memory — nothing stored in the browser. Filter state mirrors into the
 * URL. No dependencies. */
(function () {
  "use strict";

  var index = [], catCache = {}, els = {};
  var state = { q: "", cat: "", muscle: "", equip: "", diff: "", sort: "name" };

  var DIFF_ORDER = { beginner: 1, intermediate: 2, advanced: 3 };
  var SORTS = {
    name: function (a, b) { return a.name.localeCompare(b.name); },
    met: function (a, b) { return (metOf(b) || 0) - (metOf(a) || 0); },
    burn: function (a, b) { return (b.burnScore || 0) - (a.burnScore || 0); },
    difficulty: function (a, b) {
      return (DIFF_ORDER[a.difficulty] || 9) - (DIFF_ORDER[b.difficulty] || 9) ||
        a.name.localeCompare(b.name);
    },
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function titleCase(s) {
    return String(s || "").replace(/[-_]/g, " ")
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }
  function metOf(e) { return typeof e.met === "number" ? e.met : parseFloat(e.met) || null; }

  function diffChip(d) {
    var c = d === "beginner" ? "good" : d === "advanced" ? "low" : "mid";
    return d ? '<span class="fx-chip ' + c + '">' + esc(titleCase(d)) + "</span>"
      : '<span class="fx-chip na">–</span>';
  }

  // --------------------------------------------------------------- filtering

  function visible() {
    var q = state.q.toLowerCase();
    var out = index.filter(function (e) {
      if (state.cat && e.category !== state.cat) return false;
      if (state.muscle && e.musclePrimary !== state.muscle) return false;
      if (state.equip && e.equipment !== state.equip) return false;
      if (state.diff && e.difficulty !== state.diff) return false;
      if (q && e.name.toLowerCase().indexOf(q) === -1 &&
          String(e.subcategory || "").toLowerCase().indexOf(q) === -1) return false;
      return true;
    });
    out.sort(SORTS[state.sort] || SORTS.name);
    return out;
  }

  function syncURL() {
    var p = new URLSearchParams();
    ["q", "cat", "muscle", "equip", "diff"].forEach(function (k) {
      if (state[k]) p.set(k, state[k]);
    });
    if (state.sort !== "name") p.set("sort", state.sort);
    var qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }
  function readURL() {
    var p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    state.cat = p.get("cat") || "";
    state.muscle = p.get("muscle") || "";
    state.equip = p.get("equip") || "";
    state.diff = p.get("diff") || "";
    state.sort = SORTS[p.get("sort")] ? p.get("sort") : "name";
  }

  // --------------------------------------------------------------- table

  function render() {
    var rows = visible();
    els.count.textContent = "Showing " + rows.length + " of " + index.length +
      " free exercises · tap one for how-to and a calorie-burn calculator";
    els.tbody.innerHTML = rows.map(function (e) {
      return '<tr tabindex="0" role="button" data-id="' + esc(e.id) +
        '" data-cat="' + esc(e.category) + '" aria-label="' + esc(e.name) + ' — details">' +
        '<td class="fx-name"><b>' + esc(e.name) + "</b>" +
        (e.subcategory ? '<span class="fx-sub">' + esc(titleCase(e.subcategory)) + "</span>" : "") + "</td>" +
        "<td>" + esc(titleCase(e.category)) + "</td>" +
        "<td>" + esc(titleCase(e.musclePrimary) || "–") + "</td>" +
        "<td>" + esc(titleCase(e.equipment) || "–") + "</td>" +
        "<td>" + diffChip(e.difficulty) + "</td>" +
        '<td class="fx-num">' + (metOf(e) != null ? metOf(e) : "–") + "</td></tr>";
    }).join("") ||
      '<tr><td colspan="6" style="text-align:center; color:#6b7f74; padding:28px;">' +
      "No exercises match — try clearing a filter.</td></tr>";
    syncURL();
  }

  // --------------------------------------------------------------- detail modal

  var overlay;
  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.className = "nutri-modal";
    overlay.setAttribute("hidden", "");
    overlay.innerHTML = '<div class="nm-card" role="dialog" aria-modal="true">' +
      '<button class="nm-close" type="button" aria-label="Close">&times;</button>' +
      '<div class="ex-modal-body"></div></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) closeModal(); });
    overlay.querySelector(".nm-close").addEventListener("click", closeModal);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) closeModal();
    });
    // Live calorie-burn recompute
    overlay.addEventListener("input", function (e) {
      if (e.target.classList.contains("ex-burn-in")) recomputeBurn();
    });
  }
  function openModal(html) {
    ensureOverlay();
    overlay.querySelector(".ex-modal-body").innerHTML = html;
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    overlay.querySelector(".nm-card").scrollTop = 0;
    overlay.querySelector(".nm-close").focus();
    recomputeBurn();
  }
  function closeModal() {
    if (!overlay) return;
    overlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
  }

  function recomputeBurn() {
    if (!overlay) return;
    var box = overlay.querySelector(".ex-burn");
    if (!box) return;
    var met = +box.dataset.met;
    var w = +overlay.querySelector('.ex-burn-in[name="w"]').value;
    var unit = overlay.querySelector('.ex-burn-in[name="unit"]').value;
    var mins = +overlay.querySelector('.ex-burn-in[name="mins"]').value;
    var kg = unit === "lb" ? w * 0.45359 : w;
    if (!(met > 0) || !(kg > 0) || !(mins > 0)) return;
    // kcal = MET × 3.5 × kg / 200 per minute
    var perMin = met * 3.5 * kg / 200;
    var total = Math.round(perMin * mins);
    overlay.querySelector(".ex-burn-out").innerHTML =
      "≈ <b>" + total.toLocaleString() + "</b> kcal in " + mins + " min " +
      '<span class="fx-dim">(' + (Math.round(perMin * 10) / 10) + " kcal/min)</span>";
  }

  function detailHTML(e, category) {
    var met = metOf(e);
    var sub = titleCase(e.category || category) +
      (e.musclePrimary ? " · " + titleCase(e.musclePrimary) : "") +
      (e.equipment && e.equipment !== "none" ? " · " + titleCase(e.equipment) : "");

    var tags = diffChip(e.difficulty);
    if (met != null) tags += '<span class="fx-chip mid">MET ' + met + "</span>";
    if (e.muscleSecondary) tags += '<span class="fx-chip na">Also: ' + esc(titleCase(e.muscleSecondary)) + "</span>";

    // Calorie-burn calculator (MET-based)
    var burn = "";
    if (met != null) {
      burn = '<div class="ex-burn" data-met="' + met + '">' +
        "<h4>Calories burned — for your body</h4>" +
        '<div class="ex-burn-row">' +
        '<label>Weight <input class="ex-burn-in" name="w" type="number" min="20" max="400" value="70" inputmode="decimal"></label>' +
        '<select class="ex-burn-in" name="unit"><option value="kg">kg</option><option value="lb">lb</option></select>' +
        '<label>Minutes <input class="ex-burn-in" name="mins" type="number" min="1" max="240" value="30" inputmode="numeric"></label>' +
        "</div>" +
        '<p class="ex-burn-out"></p>' +
        '<p class="cx-why">Estimated from this exercise’s MET value ' +
        "(metabolic equivalent). Actual burn varies with intensity, fitness, and body composition.</p>" +
        "</div>";
    }

    // How-to
    var how = e.howTo ? '<div class="cx-block"><h3>How to perform it</h3><p class="ex-prose">' +
      esc(e.howTo) + "</p></div>" : "";

    // Sets/reps by level
    var sr = "";
    if (e.setsReps && typeof e.setsReps === "object") {
      var levels = ["beginner", "intermediate", "advanced"].filter(function (k) { return e.setsReps[k]; });
      if (levels.length) {
        sr = '<div class="cx-block"><h3>Sets &amp; reps</h3><div class="ex-sr">' +
          levels.map(function (k) {
            return '<div class="ex-sr-col"><span class="ex-sr-lvl">' + titleCase(k) + "</span>" +
              "<b>" + esc(e.setsReps[k]) + "</b></div>";
          }).join("") + "</div></div>";
      }
    }

    // Common mistakes
    var mistakes = "";
    var mlist = e.commonMistakes && e.commonMistakes.mistakes;
    if (Array.isArray(mlist) && mlist.length) {
      mistakes = '<div class="cx-block"><h3>Common mistakes</h3>' +
        mlist.map(function (m) {
          var risk = (m.injury_risk || "").toUpperCase();
          var rc = risk === "HIGH" ? "avoid" : risk === "MODERATE" || risk === "MEDIUM" ? "time" : "mag";
          return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
            esc(m.error || "") + "</span>" +
            (risk ? '<span class="cx-badge ' + rc + '">' + esc(risk) + " risk</span>" : "") + "</div>" +
            (m.consequence ? '<p class="cx-rel-eff">' + esc(m.consequence) + "</p>" : "") +
            (m.correction ? '<p class="cx-mech">Fix: ' + esc(m.correction) + "</p>" : "") + "</div>";
        }).join("") + "</div>";
    }

    // Breathing + contraindications
    var extra = "";
    if (e.breathingCues) {
      var bc = Array.isArray(e.breathingCues) ? e.breathingCues.join(" ") :
        (typeof e.breathingCues === "object" ? JSON.stringify(e.breathingCues) : e.breathingCues);
      extra += '<p class="ex-note-line"><b>Breathing:</b> ' + esc(bc) + "</p>";
    }
    if (e.contraindications) {
      var ci = Array.isArray(e.contraindications) ? e.contraindications.join("; ") : e.contraindications;
      extra += '<p class="ex-note-line"><b>Take care if:</b> ' + esc(ci) + "</p>";
    }
    if (extra) extra = '<div class="cx-block">' + extra + "</div>";

    // Physiology links → cross-link to Connections
    var physio = "";
    if (Array.isArray(e.physiologyLinks) && e.physiologyLinks.length) {
      physio = '<div class="cx-block"><h3>What it changes in your body</h3>' +
        e.physiologyLinks.slice(0, 5).map(function (l) {
          var meta = [];
          if (l.direction) meta.push('<span class="cx-badge ' + (l.direction === "increase" ? "up" : "down") +
            '">' + (l.direction === "increase" ? "▲ " : "▼ ") + titleCase(l.direction) + "</span>");
          if (l.magnitude) meta.push('<span class="cx-badge mag">' + esc(l.magnitude) + "</span>");
          if (l.duration) meta.push('<span class="cx-badge time">' + esc(l.duration) + "</span>");
          return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
            esc(titleCase(l.param)) + "</span></div>" +
            '<p class="cx-rel-eff">' + esc(l.effect || "") + "</p>" +
            (meta.length ? '<div class="cx-rel-meta">' + meta.join("") + "</div>" : "") + "</div>";
        }).join("") +
        '<p class="cx-hint" style="margin-top:10px"><a href="../connections/?lens=exercise&id=' +
        encodeURIComponent(e.id) + '">See this exercise in the Connections Explorer →</a> ' +
        "— parameters it moves, plus how to fuel it.</p></div>";
    }

    return '<div class="nm-head"><span class="nm-eyebrow">' + esc(sub) + "</span>" +
      "<h3>" + esc(e.name) + "</h3>" +
      (e.simplyPut ? '<p class="nm-foods">' + esc(e.simplyPut) + "</p>" : "") +
      '<div class="fx-tags">' + tags + "</div></div>" +
      burn + how + sr + mistakes + extra + physio +
      '<p class="nm-note">Educational reference — not medical or fitness advice. ' +
      "Consult a professional before starting new exercise.</p>" +
      '<p class="nm-app">This is 1 of 2,504 free exercises. The app carries all 5,404 — with ' +
      "video demos, progressions, and your own logging. " +
      '<a href="/#download">Get the app</a></p>';
  }

  function loadCategory(cat, cb) {
    if (catCache[cat]) return cb(catCache[cat]);
    fetch("../assets/data/free/exercises/" + cat + ".json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var map = {};
        data.exercises.forEach(function (x) { map[x.id] = x; });
        catCache[cat] = map;
        cb(map);
      })
      .catch(function () { cb(null); });
  }

  function openExercise(id, cat) {
    openModal('<p class="cx-empty">Loading…</p>');
    loadCategory(cat, function (map) {
      var e = map && map[id];
      if (!e) { overlay.querySelector(".ex-modal-body").innerHTML =
        '<p class="cx-empty">Couldn’t load this exercise — please try again.</p>'; return; }
      overlay.querySelector(".ex-modal-body").innerHTML = detailHTML(e, cat);
      overlay.querySelector(".nm-card").scrollTop = 0;
      recomputeBurn();
    });
  }

  // --------------------------------------------------------------- init

  function fillSelect(sel, values, current) {
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v; o.textContent = titleCase(v);
      sel.appendChild(o);
    });
    if (current) sel.value = current;
  }

  function init(data) {
    index = data.exercises;

    var cats = {}, muscles = {}, equips = {};
    index.forEach(function (e) {
      if (e.category) cats[e.category] = 1;
      if (e.musclePrimary) muscles[e.musclePrimary] = 1;
      if (e.equipment) equips[e.equipment] = 1;
    });
    fillSelect(els.cat, Object.keys(cats).sort());
    fillSelect(els.muscle, Object.keys(muscles).sort());
    fillSelect(els.equip, Object.keys(equips).sort());

    readURL();
    els.q.value = state.q; els.cat.value = state.cat; els.muscle.value = state.muscle;
    els.equip.value = state.equip; els.diff.value = state.diff; els.sort.value = state.sort;

    els.q.addEventListener("input", function () { state.q = this.value.trim(); render(); });
    ["cat", "muscle", "equip", "diff", "sort"].forEach(function (k) {
      els[k].addEventListener("change", function () { state[k] = this.value; render(); });
    });
    els.reset.addEventListener("click", function () {
      state = { q: "", cat: "", muscle: "", equip: "", diff: "", sort: "name" };
      els.q.value = ""; els.cat.value = ""; els.muscle.value = ""; els.equip.value = "";
      els.diff.value = ""; els.sort.value = "name";
      render();
    });

    els.tbody.addEventListener("click", function (e) {
      var tr = e.target.closest("tr[data-id]");
      if (tr) openExercise(tr.dataset.id, tr.dataset.cat);
    });
    els.tbody.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      var tr = e.target.closest("tr[data-id]");
      if (tr) { e.preventDefault(); openExercise(tr.dataset.id, tr.dataset.cat); }
    });

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["q", "cat", "muscle", "equip", "diff", "sort", "reset", "tbody", "count"]
      .forEach(function (id) { els[id] = document.getElementById("ex-" + id); });
    if (!els.tbody) return;
    fetch("../assets/data/free/exercises-index.json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(init)
      .catch(function () {
        els.count.textContent = "The exercise data couldn’t be loaded — please refresh, " +
          "or browse all 5,404 exercises in the app.";
      });
  });
})();
