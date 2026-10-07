(function (window, document) {
  "use strict";

  // Do not change this check. Tracking must stay limited to templates.aiven.io.
  if (window.location.hostname !== "templates.aiven.io") {
    return;
  }

  var COLLECTOR_URL = "https://dc.aiven.io";
  var SNOWPLOW_APP_ID = "templates-aiven-io";
  var ONETRUST_DOMAIN_SCRIPT = "01a11528-d2ee-7a99-9a30-01ce237f392b-test";
  const ONETRUST_UX_COOKIE_GROUP_ID = "115";
  const ONETRUST_PERFORMANCE_COOKIE_GROUP_ID = "2";

  function trackWebInteraction(object, action, value) {
    if (typeof window.snowplow !== "function") return;

    window.snowplow("trackSelfDescribingEvent", {
      event: {
        schema: "iglu:io.aiven/web_interaction/jsonschema/1-0-0",
        data: {
          object: object,
          action: action,
          value: value,
        },
      },
    });
  }

  function trackSearchTerm(term) {
    if (typeof window.snowplow !== "function") return;

    window.snowplow("trackSelfDescribingEvent", {
      event: {
        schema: "iglu:io.aiven/search/jsonschema/1-0-0",
        data: {
          terms: term,
        },
      },
    });
  }

  function trackFilters(filters) {
    if (typeof window.snowplow !== "function") return;

    window.snowplow("trackSelfDescribingEvent", {
      event: {
        schema: "iglu:io.aiven/search/jsonschema/1-0-0",
        data: {
          filters: filters,
        },
      },
    });
  }

  window.aivenTracking = {
    trackInteraction: trackWebInteraction,
    trackSearchTerm: trackSearchTerm,
    trackFilters: trackFilters,
  };

  function addConsentButtonTracking() {
    var consentButtonGroups = [
      {
        selector:
          "#onetrust-accept-btn-handler, #accept-recommended-btn-handler",
        value: "Allow all",
      },
      {
        selector: "#onetrust-pc-btn-handler",
        value: "Customize settings",
      },
      {
        selector: ".save-preference-btn-handler",
        value: "Save settings",
      },
    ];

    consentButtonGroups.forEach(function (group) {
      document.querySelectorAll(group.selector).forEach(function (button) {
        if (button.hasTrackingClickListener) return;

        button.addEventListener("click", function () {
          trackWebInteraction("consent button", "click", group.value);
        });
        button.hasTrackingClickListener = true;
      });
    });
  }

  window.OptanonWrapper = function () {
    if (typeof window.OnetrustActiveGroups === "undefined") return;

    // UX (115) or performance (2) consent allows persistent Snowplow identifiers.
    if (
      window.OnetrustActiveGroups.includes(
        "," + ONETRUST_UX_COOKIE_GROUP_ID + ",",
      ) ||
      window.OnetrustActiveGroups.includes(
        "," + ONETRUST_PERFORMANCE_COOKIE_GROUP_ID + ",",
      )
    ) {
      window.snowplow("setCollectorUrl", COLLECTOR_URL);
      window.snowplow("disableAnonymousTracking", {
        stateStorageStrategy: "cookieAndLocalStorage",
      });
    } else {
      // Without consent, remove stored identifiers but preserve the current session.
      window.snowplow("clearUserData", { preserveSession: true });
    }

    trackWebInteraction(
      "consent",
      "given",
      window.OnetrustActiveGroups,
    );
    addConsentButtonTracking();
  };

  // Standard Snowplow loader: stores tracking commands until the library finishes loading.
  (function (p, l, o, w, i, n, g) {
    if (!p[i]) {
      p.GlobalSnowplowNamespace = p.GlobalSnowplowNamespace || [];
      p.GlobalSnowplowNamespace.push(i);
      p[i] = function () {
        (p[i].q = p[i].q || []).push(arguments);
      };
      p[i].q = p[i].q || [];
      n = l.createElement(o);
      g = l.getElementsByTagName(o)[0];
      n.async = true;
      n.src = w;
      g.parentNode.insertBefore(n, g);
    }
  })(
    window,
    document,
    "script",
    "https://storage.googleapis.com/aiven-dw-prod-snowplow-tracker/3.4.0/gh7rnaha.js",
    "snowplow",
  );

  function hasStoredConsent() {
    try {
      var cookie = document.cookie.match(/(?:^|; )OptanonConsent=([^;]*)/);
      var groups =
        cookie &&
        decodeURIComponent(decodeURIComponent(cookie[1])).match(
          /groups=([^&]*)/,
        );
      var activeGroups = groups ? "," + groups[1] + "," : "";

      return (
        activeGroups.indexOf(
          "," + ONETRUST_UX_COOKIE_GROUP_ID + ":1,",
        ) !== -1 ||
        activeGroups.indexOf(
          "," + ONETRUST_PERFORMANCE_COOKIE_GROUP_ID + ":1,",
        ) !== -1
      );
    } catch (_error) {
      return false;
    }
  }

  var storedConsent = hasStoredConsent();

  window.snowplow("newTracker", "at", COLLECTOR_URL, {
    appId: SNOWPLOW_APP_ID,
    platform: "web",
    forceSecureTracker: true,
    discoverRootDomain: true,
    cookieSameSite: "Lax",
    anonymousTracking: storedConsent
      ? false
      : {
          withSessionTracking: false,
          withServerAnonymisation: true,
        },
    stateStorageStrategy: storedConsent ? "cookieAndLocalStorage" : "none",
    eventMethod: "post",
    postPath: "/aiven/dc2",
    contexts: {
      webPage: true,
      gaCookies: true,
    },
  });

  window.snowplow("enableActivityTracking", {
    minimumVisitLength: 10,
    heartbeatDelay: 10,
  });
  window.snowplow("trackPageView");

  var oneTrust = document.createElement("script");
  oneTrust.src = "https://cdn.cookielaw.org/scripttemplates/otSDKStub.js";
  oneTrust.setAttribute("data-language", "en");
  oneTrust.setAttribute("charset", "UTF-8");
  oneTrust.setAttribute("data-domain-script", ONETRUST_DOMAIN_SCRIPT);
  document.head.appendChild(oneTrust);
})(window, document);
