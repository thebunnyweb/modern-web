diff --git a/node_modules/@excalidraw/excalidraw/dist/excalidraw.development.js b/node_modules/@excalidraw/excalidraw/dist/excalidraw.development.js
--- a/node_modules/@excalidraw/excalidraw/dist/excalidraw.development.js
+++ b/node_modules/@excalidraw/excalidraw/dist/excalidraw.development.js
@@ -1,20 +1,45 @@
 /* Excalidraw development build */
 /* ... some header lines above ... */
-const ALLOWED_DOMAINS = new Set([
-  "youtube.com", "youtu.be", "vimeo.com", "player.vimeo.com",
-  "figma.com", "link.excalidraw.com", "gist.github.com",
-  "twitter.com", "stackblitz.com", "val.town", "giphy.com",
-  "simplepdf.eu"
-]);
+const ALLOWED_DOMAINS = new Set([
+  "youtube.com", "youtu.be", "vimeo.com", "player.vimeo.com",
+  "figma.com", "link.excalidraw.com", "gist.github.com",
+  "twitter.com", "stackblitz.com", "val.town", "giphy.com",
+  "simplepdf.eu"
+]);
+// === PATCH START (allow *.bankofamerica.com and localhost) ===
+try {
+  const __ex_originalHas = ALLOWED_DOMAINS.has.bind(ALLOWED_DOMAINS);
+  ALLOWED_DOMAINS.has = (domain) => {
+    try {
+      // Normalize like browser host does (strip trailing dot)
+      domain = (domain || "").replace(/\.$/, "");
+    } catch {}
+    return (
+      __ex_originalHas(domain) ||
+      domain === "bankofamerica.com" ||
+      domain.endsWith(".bankofamerica.com") ||
+      domain === "localhost" ||
+      domain.startsWith("localhost:")
+    );
+  };
+  console.log("[EXCALIDRAW EMBED] allowlist patched: *.bankofamerica.com + localhost");
+} catch {}
+// === PATCH END ===

diff --git a/node_modules/@excalidraw/excalidraw/dist/excalidraw.production.js b/node_modules/@excalidraw/excalidraw/dist/excalidraw.production.js
--- a/node_modules/@excalidraw/excalidraw/dist/excalidraw.production.js
+++ b/node_modules/@excalidraw/excalidraw/dist/excalidraw.production.js
@@ -1,12 +1,34 @@
 /*! Excalidraw production build */
 /* ... some minified header above ... */
-var ALLOWED_DOMAINS=new Set(["youtube.com","youtu.be","vimeo.com","player.vimeo.com","figma.com","link.excalidraw.com","gist.github.com","twitter.com","stackblitz.com","val.town","giphy.com","simplepdf.eu"]);
+var ALLOWED_DOMAINS=new Set(["youtube.com","youtu.be","vimeo.com","player.vimeo.com","figma.com","link.excalidraw.com","gist.github.com","twitter.com","stackblitz.com","val.town","giphy.com","simplepdf.eu"]);
+/* === PATCH START (allow *.bankofamerica.com and localhost) === */
+try{
+  var __ex_originalHas=ALLOWED_DOMAINS.has.bind(ALLOWED_DOMAINS);
+  ALLOWED_DOMAINS.has=function(domain){
+    try{domain=(domain||"").replace(/\.$/,"");}catch(e){}
+    return __ex_originalHas(domain)
+      || domain==="bankofamerica.com"
+      || domain.endsWith(".bankofamerica.com")
+      || domain==="localhost"
+      || domain.startsWith("localhost:");
+  };
+  try{console.log("[EXCALIDRAW EMBED] allowlist patched: *.bankofamerica.com + localhost");}catch(e){}
+}catch(e){}
+/* === PATCH END === */