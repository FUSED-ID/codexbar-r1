/* r1-sdk.js
 * Tiny, dependency-free wrappers over the OFFICIAL Rabbit R1 Creations SDK
 * channels (see rabbit-hmi-oss/creations-sdk · plugin-demo/reference/creation-triggers.md).
 * Every call degrades gracefully when a channel is absent, so the same code
 * runs on-device, in the dev harness, and in a plain browser.
 *
 * Channels mirrored:
 *   window.creationStorage.{plain,secure}  (async, Base64-encoded values)
 *   window.creationSensors.accelerometer
 *   PluginMessageHandler + window.onPluginMessage   (LLM round-trip)
 *   closeWebView.postMessage("")
 *   window events: sideClick, longPressStart, longPressEnd, scrollUp, scrollDown
 */
(function (g) {
  "use strict";
  var has = function (n) { return typeof g[n] !== "undefined"; };
  var b64 = {
    enc: function (s) { return btoa(unescape(encodeURIComponent(s))); },
    dec: function (s) { return decodeURIComponent(escape(atob(s))); }
  };

  // Official storage is Base64-in/Base64-out; we encode/decode for you.
  var storage = {
    get: async function (key, secure) {
      try {
        var s = g.creationStorage && g.creationStorage[secure ? "secure" : "plain"];
        if (!s) return null;
        var v = await s.getItem(key);
        return v == null ? null : b64.dec(v);
      } catch (e) { return null; }
    },
    set: async function (key, val, secure) {
      try {
        var s = g.creationStorage && g.creationStorage[secure ? "secure" : "plain"];
        if (!s) return false;
        await s.setItem(key, b64.enc(String(val)));
        return true;
      } catch (e) { return false; }
    }
  };

  var on = function (evt, fn) { g.addEventListener(evt, fn); return fn; };
  var hardware = {
    onSideClick:      function (fn) { return on("sideClick", fn); },
    onLongPressStart: function (fn) { return on("longPressStart", fn); },
    onLongPressEnd:   function (fn) { return on("longPressEnd", fn); },
    onScrollUp:       function (fn) { return on("scrollUp", fn); },
    onScrollDown:     function (fn) { return on("scrollDown", fn); }
  };

  // LLM round-trip: send via PluginMessageHandler, receive via window.onPluginMessage.
  // opts may include { wantsR1Response, wantsJournalEntry }.
  function llm(message, opts) {
    return new Promise(function (resolve, reject) {
      if (!has("PluginMessageHandler")) return reject(new Error("PluginMessageHandler unavailable"));
      var prev = g.onPluginMessage;
      g.onPluginMessage = function (data) {
        g.onPluginMessage = prev;
        var parsed = null;
        try { parsed = data && data.data ? JSON.parse(data.data) : null; } catch (e) {}
        resolve({ raw: data, message: data && data.message, data: parsed });
      };
      var payload = Object.assign({ message: message, useLLM: true }, opts || {});
      g.PluginMessageHandler.postMessage(JSON.stringify(payload));
    });
  }

  var accelerometer = {
    isAvailable: function () {
      try { return g.creationSensors.accelerometer.isAvailable(); }
      catch (e) { return Promise.resolve(false); }
    },
    start: function (cb, opts) { try { return g.creationSensors.accelerometer.start(cb, opts || { frequency: 60 }); } catch (e) {} },
    stop:  function () { try { return g.creationSensors.accelerometer.stop(); } catch (e) {} }
  };

  var close = function () { try { g.closeWebView.postMessage(""); } catch (e) {} };

  g.R1 = {
    storage: storage,
    hardware: hardware,
    accelerometer: accelerometer,
    llm: llm,
    close: close,
    available: {
      storage: function () { return has("creationStorage"); },
      sensors: function () { return has("creationSensors"); },
      llm:     function () { return has("PluginMessageHandler"); }
    }
  };
})(window);
