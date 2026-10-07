(function (window, document) {
  "use strict";

  var SEARCH_DEBOUNCE_MS = 500;

  function trackInteraction(object, action, value) {
    if (!window.aivenTracking) return;
    window.aivenTracking.trackInteraction(object, action, value);
  }

  // Resolve nested event targets to their tracked parent,
  // e.g. an <svg> clicked inside an <a data-track-click>.
  function closestTrackedElement(event, attribute) {
    if (!event.target || typeof event.target.closest !== "function") return null;
    return event.target.closest("[" + attribute + "]");
  }

  function trackActiveFilters() {
    if (!window.aivenTracking) return;

    var filters = Array.prototype.slice
      .call(document.querySelectorAll("[data-track-filter]:checked"))
      .map(function (element) {
        return element.dataset.trackValue || element.value;
      });

    window.aivenTracking.trackFilters(filters);
  }

  // Track clicks on elements marked with data-track-click.
  document.addEventListener("click", function (event) {
    if (closestTrackedElement(event, "data-track-filter-update")) {
      trackActiveFilters();
    }

    var element = closestTrackedElement(event, "data-track-click");
    if (!element) return;

    trackInteraction(
      element.dataset.trackClick,
      element.dataset.trackAction || "click",
      element.dataset.trackValue || element.textContent.trim(),
    );
  });

  // Track selections and deselections on marked filters and controls.
  document.addEventListener("change", function (event) {
    if (closestTrackedElement(event, "data-track-filter")) {
      trackActiveFilters();
      return;
    }

    var element = closestTrackedElement(event, "data-track-change");
    if (!element) return;

    var action =
      element.type === "checkbox"
        ? element.checked
          ? "select"
          : "deselect"
        : "select";

    trackInteraction(
      element.dataset.trackChange,
      action,
      element.dataset.trackValue || element.value,
    );
  });

  // Track search terms after the visitor pauses typing.
  var searchInput = document.querySelector("[data-track-search]");
  if (searchInput) {
    var searchTimer;
    var lastTrackedQuery = "";

    // List.js applies search terms on keyup, so measure results after the same event.
    searchInput.addEventListener("keyup", function () {
      window.clearTimeout(searchTimer);

      var query = searchInput.value.trim();
      if (!query) {
        lastTrackedQuery = "";
        return;
      }
      if (query === lastTrackedQuery) return;

      searchTimer = window.setTimeout(function () {
        if (window.aivenTracking) {
          window.aivenTracking.trackSearchTerm(query);
        }
        lastTrackedQuery = query;
      }, SEARCH_DEBOUNCE_MS);
    });
  }

  // Track transitions into the no-results state without sending duplicate events.
  var emptyState = document.getElementById("empty-state");
  if (emptyState) {
    var wasEmpty = !emptyState.hidden;
    var emptyStateObserver = new MutationObserver(function () {
      var isEmpty = !emptyState.hidden;
      if (isEmpty && !wasEmpty) {
        trackInteraction("catalog results", "empty", "0");
      }
      wasEmpty = isEmpty;
    });

    emptyStateObserver.observe(emptyState, {
      attributes: true,
      attributeFilter: ["hidden"],
    });
  }
})(window, document);
