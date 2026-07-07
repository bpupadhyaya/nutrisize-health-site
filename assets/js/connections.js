/* Nutrisize — Connections Explorer (/connections).
 * Surfaces the app's cross-domain knowledge graph in every direction:
 *   • By parameter → the nutrition and exercise that move it (cited), the foods
 *     and exercises in our database that affect it, and connected parameters.
 *   • By exercise  → the physiological parameters it changes (direction,
 *     magnitude, timeframe) and how to fuel it (pre/during/post foods).
 *   • By food      → the parameters it touches and its best timing around
 *     exercise.
 * All data is the app's own (assets/data/free/*.json). Inline [n] citation
 * chips and a per-parameter reference list open in a popup; external links open
 * in a new tab. Runs entirely in memory — nothing is stored in the browser.
 * No dependencies. */
(function () {
  "use strict";

  var params = null, paramById = {}, foods = null, foodById = {}, exIndex = null;
  var exCatCache = {}; // category -> {id: exercise}
  var els = {}, activeLens = "parameter";

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function titleCase(s) {
    return String(s || "").replace(/[-_]/g, " ")
      .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  // --------------------------------------------------------------- citations

  var citeOverlay;
  function ensureCiteOverlay() {
    if (citeOverlay) return;
    citeOverlay = document.createElement("div");
    citeOverlay.className = "nutri-modal";
    citeOverlay.setAttribute("hidden", "");
    citeOverlay.innerHTML = '<div class="nm-card" role="dialog" aria-modal="true">' +
      '<button class="nm-close" type="button" aria-label="Close">&times;</button>' +
      '<div class="nm-head"><span class="nm-eyebrow">Sources &amp; references</span>' +
      '<h3 id="cx-cite-title"></h3></div><div class="cx-refs" id="cx-cite-body"></div>' +
      '<p class="nm-note">Evidence grades: A — meta-analyses / large RCTs; ' +
      'B — cohort studies &amp; guidelines; C — expert consensus. Links open in a new tab.</p>' +
      '</div>';
    document.body.appendChild(citeOverlay);
    citeOverlay.addEventListener("click", function (e) { if (e.target === citeOverlay) closeCite(); });
    citeOverlay.querySelector(".nm-close").addEventListener("click", closeCite);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !citeOverlay.hasAttribute("hidden")) closeCite();
    });
  }
  function openCite(title, citations) {
    ensureCiteOverlay();
    citeOverlay.querySelector("#cx-cite-title").textContent = title;
    citeOverlay.querySelector("#cx-cite-body").innerHTML = refListHTML(citations);
    citeOverlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    citeOverlay.querySelector(".nm-card").scrollTop = 0;
    citeOverlay.querySelector(".nm-close").focus();
  }
  function closeCite() {
    if (!citeOverlay) return;
    citeOverlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
  }

  function refListHTML(citations, only) {
    if (!citations || !citations.length) return '<p class="cx-empty">No citations listed.</p>';
    return citations.filter(function (c) { return !only || only.indexOf(c.id) !== -1; })
      .map(function (c) {
        var g = (c.evidenceGrade || "").toLowerCase();
        var badge = '<span class="cx-grade ' + (g || "na") + '">' + (g ? g.toUpperCase() : "–") + "</span>";
        var link = c.url
          ? '<a href="' + esc(c.url) + '" target="_blank" rel="noopener">' + esc(c.text) + "</a>"
          : esc(c.text);
        var src = c.source ? ' <span class="cx-src">— ' + esc(c.source) + "</span>" : "";
        return '<div class="cx-ref">' + badge + "<span>" + link + src + "</span></div>";
      }).join("");
  }

  // A citation chip references one citation id within the subject's list.
  function citeChip(id) {
    if (id == null) return "";
    return '<button class="cx-cite" data-cite="' + id + '" title="View source">[' + id + "]</button>";
  }

  // --------------------------------------------------------------- shared bits

  function subjectHeader(title, sys, blurb, range) {
    return '<div class="cx-subject">' +
      (sys ? '<span class="cx-sys">' + esc(titleCase(sys)) + "</span>" : "") +
      "<h2>" + esc(title) + "</h2>" +
      (blurb ? "<p>" + esc(blurb) + "</p>" : "") +
      (range ? '<p class="cx-range">Typical healthy range: <b>' + esc(range) + "</b></p>" : "") +
      "</div>";
  }

  function foodChip(name) {
    var f = foodById[String(name).toLowerCase()];
    if (f) return '<a class="cx-badge food" href="../foods/?q=' + encodeURIComponent(f.name) + '">' + esc(f.name) + "</a>";
    return '<span class="cx-badge food">' + esc(name) + "</span>";
  }

  // --------------------------------------------------------------- by parameter

  function renderParameter(p) {
    var html = subjectHeader(p.name, p.system, p.simplyPut, p.normalRange);

    // Nutrition that moves it (forward, cited)
    html += '<div class="cx-block"><h3>Nutrition that moves it <span class="cx-dir">nutrition → parameter</span></h3>';
    if (p.nutritionLinks.length) {
      html += p.nutritionLinks.map(function (n) {
        var foods = (n.foods || []).map(foodChip).join(" ");
        return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
          esc(n.nutrient) + "</span>" + citeChip(n.citation) + "</div>" +
          '<p class="cx-rel-eff">' + esc(n.effect) + "</p>" +
          (n.mechanism ? '<p class="cx-mech">' + esc(n.mechanism) + "</p>" : "") +
          (foods ? '<div class="cx-foodlist">' + foods + "</div>" : "") + "</div>";
      }).join("");
    } else { html += '<p class="cx-empty">No nutrition links listed.</p>'; }
    html += "</div>";

    // Exercise that moves it (forward, cited)
    html += '<div class="cx-block"><h3>Exercise that moves it <span class="cx-dir">exercise → parameter</span></h3>';
    if (p.exerciseLinks.length) {
      html += p.exerciseLinks.map(function (x) {
        return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
          esc(x.type) + "</span>" + citeChip(x.citation) + "</div>" +
          '<p class="cx-rel-eff">' + esc(x.effect) + "</p>" +
          (x.mechanism ? '<p class="cx-mech">' + esc(x.mechanism) + "</p>" : "") +
          (x.recommendation ? '<div class="cx-rel-meta"><span class="cx-badge time">' +
            esc(x.recommendation) + "</span></div>" : "") + "</div>";
      }).join("");
    } else { html += '<p class="cx-empty">No exercise links listed.</p>'; }
    html += "</div>";

    // Reverse: specific exercises in our database that affect it
    if (p.affectingExercises && p.affectingExercises.length) {
      html += '<div class="cx-block"><h3>Exercises in our database that affect it ' +
        '<span class="cx-dir">' + p.affectingExercises.length + ' exercises</span></h3>';
      html += p.affectingExercises.slice(0, 12).map(function (e) {
        return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
          esc(e.name) + '</span></div><p class="cx-rel-eff">' + esc(e.effect || "") + "</p>" +
          relMeta(e) + "</div>";
      }).join("");
      if (p.affectingExercises.length > 12) {
        html += '<p class="cx-hint" style="margin-top:10px">…and ' +
          (p.affectingExercises.length - 12) + " more in the app.</p>";
      }
      html += "</div>";
    }

    // Reverse: foods that affect it
    if (p.affectingFoods && p.affectingFoods.length) {
      html += '<div class="cx-block"><h3>Foods that affect it <span class="cx-dir">' +
        p.affectingFoods.length + ' foods</span></h3><div class="cx-foodlist">' +
        p.affectingFoods.slice(0, 30).map(function (f) {
          return '<a class="cx-badge food" href="../foods/?q=' + encodeURIComponent(f.name) + '">' +
            esc(f.name) + "</a>";
        }).join("") + "</div>" +
        (p.affectingFoods.length > 30 ? '<p class="cx-hint" style="margin-top:8px">…and ' +
          (p.affectingFoods.length - 30) + " more.</p>" : "") + "</div>";
    }

    // Connected parameters
    if (p.interconnections && p.interconnections.length) {
      html += '<div class="cx-block"><h3>Connected parameters <span class="cx-dir">parameter ↔ parameter</span></h3>';
      html += p.interconnections.map(function (ic) {
        var other = paramById[ic.parameterId];
        var name = other ? other.name : titleCase(ic.parameterId);
        var head = other
          ? '<button class="cx-rel-name cx-jump" data-param="' + esc(ic.parameterId) +
            '" style="background:none;border:none;cursor:pointer;padding:0">' + esc(name) + "</button>"
          : '<span class="cx-rel-name">' + esc(name) + "</span>";
        return '<div class="cx-rel"><div class="cx-rel-head">' + head + "</div>" +
          '<p class="cx-rel-eff">' + esc(ic.relationship) + "</p></div>";
      }).join("");
      html += "</div>";
    }

    // References
    html += '<div class="cx-block"><h3>References for ' + esc(p.name) + "</h3>" +
      '<div class="cx-refs">' + refListHTML(p.citations) + "</div></div>";

    els.result.innerHTML = html;
    els.result.__citations = p.citations;
    els.result.__citeTitle = p.name;
  }

  function relMeta(e) {
    var parts = [];
    if (e.direction) parts.push('<span class="cx-badge ' + (e.direction === "increase" ? "up" : "down") +
      '">' + (e.direction === "increase" ? "▲ " : "▼ ") + esc(titleCase(e.direction)) + "</span>");
    if (e.magnitude) parts.push('<span class="cx-badge mag">' + esc(e.magnitude) + "</span>");
    if (e.duration) parts.push('<span class="cx-badge time">' + esc(e.duration) + "</span>");
    return parts.length ? '<div class="cx-rel-meta">' + parts.join("") + "</div>" : "";
  }

  // --------------------------------------------------------------- by exercise

  function loadExercise(id, category, cb) {
    var cat = category;
    if (exCatCache[cat]) return cb(exCatCache[cat][id]);
    fetch("../assets/data/free/exercises/" + cat + ".json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var map = {};
        data.exercises.forEach(function (e) { map[e.id] = e; });
        exCatCache[cat] = map;
        cb(map[id]);
      })
      .catch(function () { cb(null); });
  }

  function renderExercise(e) {
    if (!e) { els.result.innerHTML = '<p class="cx-empty">Couldn’t load this exercise.</p>'; return; }
    var html = subjectHeader(e.name, e.category + (e.musclePrimary ? " · " + e.musclePrimary : ""),
      e.simplyPut, null);

    // Parameters it moves
    html += '<div class="cx-block"><h3>Physiological parameters it changes <span class="cx-dir">exercise → parameters</span></h3>';
    var pl = e.physiologyLinks || [];
    if (pl.length) {
      html += pl.map(function (l) {
        var other = paramById[l.param];
        var name = other ? other.name : titleCase(l.param);
        var head = other
          ? '<button class="cx-rel-name cx-jump" data-param="' + esc(l.param) +
            '" style="background:none;border:none;cursor:pointer;padding:0">' + esc(name) + "</button>"
          : '<span class="cx-rel-name">' + esc(name) + "</span>";
        return '<div class="cx-rel"><div class="cx-rel-head">' + head + "</div>" +
          '<p class="cx-rel-eff">' + esc(l.effect || "") + "</p>" + relMeta(l) + "</div>";
      }).join("");
    } else { html += '<p class="cx-empty">No parameter links listed.</p>'; }
    html += "</div>";

    // Fueling around this exercise
    var nt = e.nutritionTiming;
    if (nt && (nt.pre_workout || nt.during_workout || nt.post_workout)) {
      html += '<div class="cx-block"><h3>How to fuel it <span class="cx-dir">food ↔ exercise timing</span></h3><div class="cx-fuel">';
      html += fuelCol("Before", nt.pre_workout);
      html += fuelCol("During", nt.during_workout);
      html += fuelCol("After", nt.post_workout);
      html += "</div></div>";
    }

    // Beneficial foods with mechanism/timing/dose
    if (Array.isArray(e.foodsPositive) && e.foodsPositive.length) {
      html += '<div class="cx-block"><h3>Foods that help this exercise <span class="cx-dir">food → performance</span></h3>';
      html += e.foodsPositive.map(function (f) {
        var meta = [];
        if (f.timing) meta.push('<span class="cx-badge time">' + esc(f.timing) + "</span>");
        if (f.dose) meta.push('<span class="cx-badge mag">' + esc(f.dose) + "</span>");
        return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-rel-name">' +
          foodChip(f.food).replace(/^<a /, "<a ").replace(/^<span /, "<span ") +
          "</span></div>" +
          '<p class="cx-rel-eff">' + esc(f.benefit || "") + "</p>" +
          (f.mechanism ? '<p class="cx-mech">' + esc(f.mechanism) + "</p>" : "") +
          (meta.length ? '<div class="cx-rel-meta">' + meta.join("") + "</div>" : "") + "</div>";
      }).join("");
      html += "</div>";
    }

    // Foods to avoid around it
    if (Array.isArray(e.foodsNegative) && e.foodsNegative.length) {
      html += '<div class="cx-block"><h3>Foods to avoid around it <span class="cx-dir">food → impairment</span></h3>';
      html += e.foodsNegative.map(function (f) {
        return '<div class="cx-rel"><div class="cx-rel-head"><span class="cx-badge avoid">' +
          esc(f.food) + "</span></div>" +
          '<p class="cx-rel-eff">' + esc(f.impairment || "") + "</p>" +
          (f.mechanism ? '<p class="cx-mech">' + esc(f.mechanism) + "</p>" : "") + "</div>";
      }).join("");
      html += "</div>";
    }

    els.result.innerHTML = html;
    els.result.__citations = null;
  }

  function fuelCol(label, block) {
    if (!block) return "";
    var foods = (block.foods || []).map(foodChip).join(" ");
    var avoid = (block.foods_to_avoid || []).map(function (n) {
      return '<span class="cx-badge avoid">' + esc(n) + "</span>";
    }).join(" ");
    return '<div class="cx-fuel-col"><h4>' + label + "</h4>" +
      (block.timing ? '<p class="cx-when">' + esc(block.timing) + "</p>" : "") +
      (foods ? '<div class="cx-foodlist">' + foods + "</div>" : "") +
      (avoid ? '<div class="cx-foodlist" style="margin-top:8px">' + avoid + "</div>" : "") +
      (block.why_avoid ? '<p class="cx-why">' + esc(block.why_avoid) + "</p>" : "") +
      (block.recovery_note ? '<p class="cx-why">' + esc(block.recovery_note) + "</p>" : "") +
      "</div>";
  }

  // --------------------------------------------------------------- by food

  function renderFood(f) {
    var html = subjectHeader(f.name, f.category, f.description, null);

    html += '<div class="cx-block"><h3>Physiological parameters it touches <span class="cx-dir">food → parameters</span></h3>';
    var pl = f.physiologyLinks || [];
    if (pl.length) {
      html += pl.map(function (l) {
        var other = paramById[l.param];
        var name = other ? other.name : titleCase(l.param);
        var head = other
          ? '<button class="cx-rel-name cx-jump" data-param="' + esc(l.param) +
            '" style="background:none;border:none;cursor:pointer;padding:0">' + esc(name) + "</button>"
          : '<span class="cx-rel-name">' + esc(name) + "</span>";
        return '<div class="cx-rel"><div class="cx-rel-head">' + head + "</div>" +
          '<p class="cx-rel-eff">' + esc(l.effect || "") + "</p></div>";
      }).join("");
    } else {
      html += '<p class="cx-empty">No direct parameter links for this food — try one in the app’s full library.</p>';
    }
    html += "</div>";

    // Best timing around exercise (may be a string or list)
    if (f.exerciseTimingBest) {
      var t = f.exerciseTimingBest;
      var text = Array.isArray(t) ? t.map(esc).join("; ") : esc(t);
      html += '<div class="cx-block"><h3>Best timing around exercise <span class="cx-dir">food ↔ exercise timing</span></h3>' +
        '<div class="cx-rel"><p class="cx-rel-eff">' + text + "</p></div></div>";
    }

    els.result.innerHTML = html;
    els.result.__citations = null;
  }

  // --------------------------------------------------------------- pickers

  function fillParamPicker(filter) {
    var q = (filter || "").toLowerCase();
    var opts = params.filter(function (p) {
      return !q || p.name.toLowerCase().indexOf(q) !== -1 ||
        String(p.system).toLowerCase().indexOf(q) !== -1;
    });
    els.select.innerHTML = '<option value="">Choose a parameter…</option>' +
      opts.map(function (p) {
        return '<option value="' + esc(p.id) + '">' + esc(p.name) + " · " +
          esc(titleCase(p.system)) + "</option>";
      }).join("");
  }

  function fillFoodPicker(filter) {
    var q = (filter || "").toLowerCase();
    var opts = foods.filter(function (f) { return !q || f.name.toLowerCase().indexOf(q) !== -1; })
      .slice(0, 300);
    els.select.innerHTML = '<option value="">Choose a food…</option>' +
      opts.map(function (f) { return '<option value="' + esc(f.id) + '">' + esc(f.name) + "</option>"; }).join("");
  }

  function fillExercisePicker(filter) {
    var q = (filter || "").toLowerCase();
    var opts = exIndex.filter(function (e) { return !q || e.name.toLowerCase().indexOf(q) !== -1; })
      .slice(0, 300);
    els.select.innerHTML = '<option value="">Choose an exercise…</option>' +
      opts.map(function (e) {
        return '<option value="' + esc(e.id) + '" data-cat="' + esc(e.category) + '">' +
          esc(e.name) + " · " + esc(titleCase(e.category)) + "</option>";
      }).join("");
  }

  function setLens(lens) {
    activeLens = lens;
    Array.prototype.forEach.call(els.tabs.children, function (btn) {
      btn.setAttribute("aria-selected", btn.dataset.lens === lens ? "true" : "false");
    });
    els.search.value = "";
    els.result.innerHTML = "";
    if (lens === "parameter") {
      els.search.placeholder = "Filter parameters…";
      els.hint.textContent = "Pick a physiological parameter to see the nutrition and exercise that move it — with sources.";
      fillParamPicker("");
    } else if (lens === "exercise") {
      els.search.placeholder = "Filter exercises…";
      els.hint.textContent = "Pick an exercise to see which parameters it changes and how to fuel it.";
      fillExercisePicker("");
    } else {
      els.search.placeholder = "Filter foods…";
      els.hint.textContent = "Pick a food to see the parameters it touches and its best timing around exercise.";
      fillFoodPicker("");
    }
    syncURL();
  }

  function onSelect() {
    var v = els.select.value;
    if (!v) { els.result.innerHTML = ""; syncURL(); return; }
    if (activeLens === "parameter") {
      renderParameter(paramById[v]);
    } else if (activeLens === "food") {
      renderFood(foodById[v] || foodByIdRaw[v]);
    } else {
      var opt = els.select.selectedOptions[0];
      var cat = opt ? opt.dataset.cat : null;
      els.result.innerHTML = '<p class="cx-empty">Loading…</p>';
      loadExercise(v, cat, function (e) {
        if (e && !e.category) e.category = cat;
        renderExercise(e);
      });
    }
    syncURL();
  }

  var foodByIdRaw = {};

  function syncURL() {
    var p = new URLSearchParams();
    p.set("lens", activeLens);
    if (els.select.value) p.set("id", els.select.value);
    history.replaceState(null, "", "?" + p.toString());
  }

  function applyURL() {
    var p = new URLSearchParams(location.search);
    var lens = p.get("lens");
    if (["parameter", "exercise", "food"].indexOf(lens) !== -1) setLens(lens);
    else setLens("parameter");
    var id = p.get("id");
    if (id) {
      // exercise options carry a data-cat; ensure the option exists then select
      var opt = els.select.querySelector('option[value="' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"]');
      if (opt) { els.select.value = id; onSelect(); }
    }
  }

  // --------------------------------------------------------------- wiring

  function wire() {
    els.tabs.addEventListener("click", function (e) {
      var b = e.target.closest(".cx-tab");
      if (b) setLens(b.dataset.lens);
    });
    els.search.addEventListener("input", function () {
      var q = this.value.trim();
      if (activeLens === "parameter") fillParamPicker(q);
      else if (activeLens === "exercise") fillExercisePicker(q);
      else fillFoodPicker(q);
    });
    els.select.addEventListener("change", onSelect);

    // Delegated: citation chips, jump-to-parameter buttons.
    els.result.addEventListener("click", function (e) {
      var chip = e.target.closest(".cx-cite");
      if (chip) {
        var cites = els.result.__citations;
        var id = +chip.dataset.cite;
        openCite(els.result.__citeTitle || "Source",
          (cites || []).filter(function (c) { return c.id === id; }));
        return;
      }
      var jump = e.target.closest(".cx-jump");
      if (jump && paramById[jump.dataset.param]) {
        e.preventDefault();
        setLens("parameter");
        els.select.value = jump.dataset.param;
        onSelect();
        els.result.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  function boot() {
    ["tabs", "search", "select", "hint", "result"].forEach(function (k) {
      els[k] = document.getElementById("cx-" + k);
    });
    if (!els.result) return;

    Promise.all([
      fetch("../assets/data/free/parameters.json").then(function (r) { return r.json(); }),
      fetch("../assets/data/free/foods.json").then(function (r) { return r.json(); }),
      fetch("../assets/data/free/exercises-index.json").then(function (r) { return r.json(); }),
    ]).then(function (res) {
      params = res[0].parameters;
      params.forEach(function (p) { paramById[p.id] = p; });
      foods = res[1].foods;
      foods.forEach(function (f) {
        foodById[f.id] = f; foodByIdRaw[f.id] = f;
        foodById[f.name.toLowerCase()] = f;
      });
      exIndex = res[2].exercises;
      wire();
      applyURL();
    }).catch(function () {
      els.result.innerHTML = '<p class="cx-empty">The connections data couldn’t be loaded — ' +
        "please refresh, or explore the full graph in the app.</p>";
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
