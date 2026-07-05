/* Nutrisize — sources & references window.
 * Any element with [data-ref-open] opens a wide in-page window (85% of the
 * viewport height, page dimmed but visible behind) holding the page's
 * reference library (#ref-library, hidden inline for SEO). Closes on the ×
 * button, a click outside, or Esc — the page never navigates away. External
 * citation links open in a new tab. No dependencies. */
(function () {
  "use strict";

  var overlay, lastFocus;

  function build() {
    var lib = document.getElementById("ref-library");
    overlay = document.createElement("div");
    overlay.className = "ref-modal";
    overlay.setAttribute("hidden", "");
    overlay.innerHTML =
      '<div class="rm-card" role="dialog" aria-modal="true" aria-labelledby="rm-title">' +
      '<div class="rm-head"><h3 id="rm-title">Sources &amp; references</h3>' +
      '<button class="rm-close" type="button" aria-label="Close">&times;</button></div>' +
      '<div class="rm-body">' + (lib ? lib.innerHTML : "") + "</div>" +
      "</div>";
    document.body.appendChild(overlay);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close(); // click outside → back to the page
    });
    overlay.querySelector(".rm-close").addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.hasAttribute("hidden")) close();
    });
  }

  function open() {
    if (!overlay) build();
    lastFocus = document.activeElement;
    overlay.removeAttribute("hidden");
    document.body.classList.add("nm-open");
    overlay.querySelector(".rm-body").scrollTop = 0;
    overlay.querySelector(".rm-close").focus();
  }

  function close() {
    overlay.setAttribute("hidden", "");
    document.body.classList.remove("nm-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-ref-open]");
    if (t) { e.preventDefault(); open(); }
  });
})();
