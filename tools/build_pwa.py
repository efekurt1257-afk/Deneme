import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src', 'gorev-sicili.html')).read()
s = src
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"MISMATCH ({n}) for: {old[:80]!r}")
    s = s.replace(old, new)

# --- yönetici görünürlüğü
rep('class="btn primary add-top" id="add-btn"', 'class="btn primary add-top admin-only" id="add-btn"')
rep('<button class="fab" id="fab"', '<button class="fab admin-only" id="fab"')
rep('<button class="btn danger" type="button" id="v-del">Sil</button>', '<button class="btn danger admin-only" type="button" id="v-del">Sil</button>')
rep('<button class="btn" type="button" id="v-edit">Düzenle</button>', '<button class="btn admin-only" type="button" id="v-edit">Düzenle</button>')
rep('b.className = "btn small"; $("ig-bar")', 'b.className = "btn small admin-only"; $("ig-bar")')
rep('<button class="btn primary" type="button" data-nav="haber-yaz">', '<button class="btn primary admin-only" type="button" data-nav="haber-yaz">')
rep('<div class="backbar">${back}<div class="acts">', '<div class="backbar">${back}<div class="acts admin-only">')
rep('</style>', '''body:not(.is-admin) .admin-only { display: none !important; }
.site-foot { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between; border-top: 1px solid var(--line); padding-block: 18px 110px; margin-top: 8px; }
.site-foot .notice { margin: 0; }
.setup { border: 1px dashed var(--line-strong); border-radius: var(--r); padding: 14px 16px; font-size: .9rem; color: var(--muted); background: var(--surface); margin-top: 18px; }
.setup b { color: var(--ink); }
.install { display: flex; gap: 10px; align-items: center; padding: 12px 14px; border: 1px solid var(--line); border-radius: var(--r); background: var(--surface); margin-top: 18px; flex-wrap: wrap; }
.install span { flex: 1 1 200px; font-size: .9rem; }
</style>''')
rep('<p class="notice" id="notice" style="padding-bottom:96px;margin-top:-80px"></p>',
    '''<footer class="site-foot">
    <p class="notice" id="notice"></p>
    <span style="display:flex;gap:8px;align-items:center">
      <span class="notice" id="who"></span>
      <button class="btn small ghost" type="button" id="login-btn">Yönetici girişi</button>
      <button class="btn small ghost" type="button" id="logout-btn" hidden>Çıkış yap</button>
    </span>
  </footer>''')
rep('<section class="overview" aria-label="Özet" id="overview">',
    '''<div class="setup" id="setup" hidden><b>Kurulum bekleniyor.</b> Veritabanı henüz bağlanmadı; şu an gördüğün kayıtlar örnek ve yalnızca bu cihazda duruyor.</div>
  <div class="install" id="install" hidden><span id="install-text">Bu siteyi telefonuna uygulama olarak yükleyebilirsin.</span><button class="btn small primary" type="button" id="install-btn">Uygulamayı yükle</button><button class="btn small ghost" type="button" id="install-x" aria-label="Kapat">✕</button></div>
  <section class="overview" aria-label="Özet" id="overview">''')
# giriş diyaloğu
rep('<!-- Tam ekran fotoğraf -->', '''<dialog id="ldlg">
  <form class="form" id="lform" novalidate>
    <header><h2>Yönetici girişi</h2><button class="btn small ghost" type="button" data-close aria-label="Kapat">✕</button></header>
    <div class="body">
      <p class="muted" style="margin:0">Etkinlik, duyuru ve haber eklemek için giriş yap. Ziyaretçilerin giriş yapmasına gerek yok.</p>
      <label class="f">E-posta<input id="l-email" type="email" autocomplete="username"></label>
      <label class="f">Şifre<input id="l-pass" type="password" autocomplete="current-password"></label>
      <p class="err" id="l-err" hidden></p>
    </div>
    <footer><span style="flex:1"></span><button class="btn primary" type="submit" id="l-go">Giriş yap</button></footer>
  </form>
</dialog>

<!-- Tam ekran fotoğraf -->''')

# --- fotoğraflar: küçük önizleme kayıtta, tam boy ayrı belgede
rep('const srcOf = (p) => p.asset ? "/_blob/" + p.asset : (p.data || p.tmp || "");',
'''const srcOf = (p) => p.thumb || p.data || p.tmp || "";
  const photoCache = {}, photoPending = new Set();
  let paintQueued = false;
  function repaint() {
    if (paintQueued) return; paintQueued = true;
    requestAnimationFrame(() => { paintQueued = false; if (route.page === "edit") { if (ed && $("n-thumbs")) renderThumbs(); } else render(); if ($("lb").open) showLb(); });
  }
  function fullSrc(p) {
    if (!p.pid || mode !== "fb") return srcOf(p);
    if (photoCache[p.pid]) return photoCache[p.pid];
    if (!photoPending.has(p.pid)) {
      photoPending.add(p.pid);
      fs.collection("photos").doc(p.pid).get().then((d) => { photoCache[p.pid] = (d.exists && d.data().data) || p.thumb || ""; repaint(); }).catch(() => {}).finally(() => photoPending.delete(p.pid));
    }
    return p.thumb || "";
  }''')
rep('<img class="hero-img" src="${esc(srcOf(ph[0]))}"', '<img class="hero-img" src="${esc(fullSrc(ph[0]))}"')
rep('<img class="cover" src="${esc(srcOf(ph[0]))}"', '<img class="cover" src="${esc(fullSrc(ph[0]))}"')
rep('$("lb-img").src = srcOf(lbList[lbIdx]);', '$("lb-img").src = fullSrc(lbList[lbIdx]);')

# --- kayıt katmanı: Firebase
rep('''    if (mode === "db") { const body = JSON.parse(JSON.stringify(a)); delete body.id; await db.collection("announcements").doc(a.id).set(body); }''',
    '''    if (mode === "fb") { const body = JSON.parse(JSON.stringify(a)); delete body.id; await fs.collection("items").doc(a.id).set(body); }''')
rep('''    if (mode === "db") await db.collection("announcements").doc(id).delete();''',
    '''    if (mode === "fb") await fs.collection("items").doc(id).delete();''')
rep('if (mode === "db") await db.doc("settings/site").set({ instagram: h });', 'if (mode === "fb") await fs.collection("settings").doc("site").set({ instagram: h });')

rep('''          if (assets) {
            const c = await shrink(f, 1800, 0.85);
            const blob = await new Promise((r) => c.toBlob(r, "image/jpeg", 0.85));
            const up = await assets.upload(blob, { type: "image/jpeg" });
            entry.asset = up.id;
          } else {
            const c = await shrink(f, 720, 0.7);
            let q = 0.7, out = c.toDataURL("image/jpeg", q);
            while (out.length > 70000 && q > 0.35) { q -= 0.1; out = c.toDataURL("image/jpeg", q); }
            entry.data = out;
          }''',
'''          const big = await shrink(f, 1400);
          let q = 0.82, out = big.toDataURL("image/jpeg", q);
          while (out.length > 650000 && q > 0.3) { q -= 0.08; out = big.toDataURL("image/jpeg", q); }
          const small = await shrink(f, 480);
          let tq = 0.7, th = small.toDataURL("image/jpeg", tq);
          while (th.length > 45000 && tq > 0.3) { tq -= 0.1; th = small.toDataURL("image/jpeg", tq); }
          entry.data = out; entry.thumb = th;''')
rep('''    const photos = ed.photos.map((p) => p.asset ? { asset: p.asset } : { data: p.data }).filter((p) => p.asset || p.data);
    const a = { id: ed.id || newId(), type: ed.kind || "haber", title, date, text: $("n-text").value.trim(), photos, updatedAt: new Date().toISOString() };
    if (mode === "db" && JSON.stringify(a).length > 240000) { fail("Fotoğraflar bu kayıt için çok büyük; birkaçını çıkarıp tekrar dene."); return; }
    const btn = $("n-save"); btn.disabled = true; btn.textContent = "Kaydediliyor…";
    try {
      await saveItem(a);
      if (assets && ed.orig) {
        const keep = new Set(photos.map((p) => p.asset).filter(Boolean));
        photosOf(ed.orig).forEach((p) => { if (p.asset && !keep.has(p.asset)) assets.delete(p.asset).catch(() => {}); });
      }''',
'''    const btn = $("n-save"); btn.disabled = true; btn.textContent = "Kaydediliyor…";
    try {
      const photos = [];
      for (const p of ed.photos) {
        if (p.pid) { photos.push({ pid: p.pid, thumb: p.thumb || "" }); continue; }
        if (!p.data) continue;
        if (mode === "fb") {
          const ref = await fs.collection("photos").add({ data: p.data, createdAt: new Date().toISOString() });
          photoCache[ref.id] = p.data; p.pid = ref.id;
          photos.push({ pid: ref.id, thumb: p.thumb || "" });
        } else photos.push({ data: p.thumb || p.data, thumb: p.thumb || p.data });
      }
      const now = new Date().toISOString();
      const a = { id: ed.id || newId(), type: ed.kind || "haber", title, date, text: $("n-text").value.trim(), photos, videos: await saveVideos(), createdAt: (ed.orig && ed.orig.createdAt) || now, updatedAt: now };
      if (JSON.stringify(a).length > 900000) { throw { message: "too-big" }; }
      await saveItem(a);
      if (mode === "fb" && ed.orig) {
        const keep = new Set(photos.map((p) => p.pid).filter(Boolean));
        photosOf(ed.orig).forEach((p) => { if (p.pid && !keep.has(p.pid)) fs.collection("photos").doc(p.pid).delete().catch(() => {}); });
      }''')
rep('''      fail(err && err.code === "invalid_argument" ? "Bu sayfaya haber ekleme iznin yok." : err && err.code === "quota_exceeded" ? "Kayıt alanı doldu; eski kayıtları silip tekrar dene." : "Kaydedilemedi, tekrar dene.");''',
    '''      fail(err && err.message === "video" ? "Video yüklenemedi. Yönetici girişi yaptığından emin ol ya da daha küçük bir video dene." : err && err.message === "too-big" ? "Bu haberde çok fazla fotoğraf var; birkaçını çıkarıp tekrar dene." : err && err.code === "permission-denied" ? "Kaydetme iznin yok; yönetici olarak giriş yaptığından emin ol." : "Kaydedilemedi, internet bağlantını kontrol edip tekrar dene.");''')
rep('''        if (assets) photosOf(a).forEach((p) => { if (p.asset) assets.delete(p.asset).catch(() => {}); });''',
    '''        if (mode === "fb") photosOf(a).forEach((p) => { if (p.pid) fs.collection("photos").doc(p.pid).delete().catch(() => {}); });''')
rep('''err && err.code === "invalid_argument" ? "Bu sayfaya kayıt ekleme iznin yok." : err && err.code === "quota_exceeded" ? "Kayıt alanı doldu; eski kayıtları silip tekrar dene." : "Kaydedilemedi, tekrar dene.";''',
    '''err && err.code === "permission-denied" ? "Kaydetme iznin yok; yönetici olarak giriş yaptığından emin ol." : "Kaydedilemedi, internet bağlantını kontrol edip tekrar dene.";''')

# --- başlatma
rep(s[s.index('  async function startDb() {'):s.index('  /* ---------- olaylar ---------- */')],
'''  let fs = null, auth = null, isAdmin = false;
  function setAdmin(user) {
    isAdmin = !!user || mode === "local";
    document.body.classList.toggle("is-admin", isAdmin);
    $("login-btn").hidden = !!user || mode === "local";
    $("logout-btn").hidden = !user;
    $("who").textContent = user ? "Yönetici: " + (user.email || "") : "";
    if (!isAdmin && route.page === "edit") nav("haberler");
  }
  function startFirebase(cfg) {
    try {
      firebase.initializeApp(cfg);
      fs = firebase.firestore(); auth = firebase.auth();
    } catch (e) { startLocal("Veritabanına bağlanılamadı; örnek kayıtlar gösteriliyor."); $("setup").hidden = false; setAdmin(null); return; }
    mode = "fb"; items = []; setAdmin(null); render();
    $("notice").textContent = "Kayıtlar yükleniyor…";
    auth.onAuthStateChanged((u) => { setAdmin(u); render(); });
    fs.collection("settings").doc("site").onSnapshot((d) => { siteIg = (d.exists && d.data().instagram) || ""; renderIg(); }, () => {});
    fs.collection("items").onSnapshot((snap) => {
      items = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
      loaded = true; $("notice").textContent = "Gündem Panosu";
      render();
    }, () => { $("notice").textContent = "Kayıtlar okunamadı; internet bağlantını kontrol et."; });
  }

  /* giriş */
  $("login-btn").onclick = () => { $("l-err").hidden = true; $("ldlg").showModal(); $("l-email").focus(); };
  $("logout-btn").onclick = () => auth && auth.signOut();
  $("lform").addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = $("l-go"); btn.disabled = true;
    try { await auth.signInWithEmailAndPassword($("l-email").value.trim(), $("l-pass").value); $("ldlg").close(); $("l-pass").value = ""; }
    catch (err) { $("l-err").textContent = "E-posta ya da şifre hatalı."; $("l-err").hidden = false; }
    finally { btn.disabled = false; }
  });

  /* telefona yükleme */
  let installEvt = null;
  const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
  let installHidden = false; try { installHidden = localStorage.getItem("gp-install-x") === "1"; } catch (e) {}
  window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); installEvt = e; if (!installHidden) $("install").hidden = false; });
  if (!standalone && !installHidden && /iphone|ipad|ipod/i.test(navigator.userAgent)) {
    $("install-text").textContent = "Uygulama olarak yüklemek için Safari'de Paylaş düğmesine dokun, sonra “Ana Ekrana Ekle”yi seç.";
    $("install-btn").hidden = true; $("install").hidden = false;
  }
  $("install-btn").onclick = async () => { if (!installEvt) return; installEvt.prompt(); await installEvt.userChoice.catch(() => {}); installEvt = null; $("install").hidden = true; };
  $("install-x").onclick = () => { $("install").hidden = true; try { localStorage.setItem("gp-install-x", "1"); } catch (e) {} };
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});

''')
rep('  if (window.claude && window.claude.use) startDb(); else startLocal();',
    '''  const CFG = window.FIREBASE_CONFIG;
  /* GitHub ile yönetim */
  const GH = { owner: "zaferpartisihaber", repo: "zaferpartisihaber.github.io", branch: "main" };
  let ghToken = ""; try { ghToken = localStorage.getItem("gp-gh-token") || ""; } catch (e) {}
  window.__localImg = {};
  function toast(msg) { let t = $("toast"); if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; t.setAttribute("role", "status"); document.body.appendChild(t); } t.textContent = msg; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, 4500); }
  function utf8ToB64(str) { const b = new TextEncoder().encode(str); let bin = ""; for (let i = 0; i < b.length; i += 0x8000) bin += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000)); return btoa(bin); }
  function b64ToUtf8(b64) { const bin = atob(String(b64).replace(/\\n/g, "")); return new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0))); }
  async function gh(path, opts = {}) {
    const r = await fetch("https://api.github.com/repos/" + GH.owner + "/" + GH.repo + (path ? "/" + path : ""), { ...opts, headers: { Authorization: "Bearer " + ghToken, Accept: "application/vnd.github+json", ...(opts.headers || {}) } });
    if (!r.ok) { const e = new Error("gh " + r.status); e.status = r.status; throw e; }
    return r.status === 204 ? null : r.json();
  }
  async function ghGetFile(path) { try { return await gh("contents/" + path + "?ref=" + GH.branch); } catch (e) { if (e.status === 404) return null; throw e; } }
  async function ghPut(path, b64, message) { const cur = await ghGetFile(path); return gh("contents/" + path, { method: "PUT", body: JSON.stringify({ message, content: b64, branch: GH.branch, ...(cur ? { sha: cur.sha } : {}) }) }); }
  async function ghDel(path, message) { const cur = await ghGetFile(path); if (!cur) return; return gh("contents/" + path, { method: "DELETE", body: JSON.stringify({ message, sha: cur.sha, branch: GH.branch }) }); }
  async function ghSaveData(message) { await ghPut("data.json", utf8ToB64(JSON.stringify({ instagram: siteIg, items }, null, 2) + "\\n"), message); }
  async function enterGh() {
    const repo = await gh("");
    if (!repo.permissions || !repo.permissions.push) throw new Error("no-push");
    const f = await ghGetFile("data.json");
    if (f) { const d = JSON.parse(b64ToUtf8(f.content)); items = Array.isArray(d.items) ? d.items : []; siteIg = d.instagram || ""; }
    mode = "gh"; setAdmin({ email: "" }); $("who").textContent = "Yönetici modu açık"; renderIg(); render();
  }
  function openTok() { $("t-err").hidden = true; $("tdlg").showModal(); $("t-key").focus(); }
  $("tform").addEventListener("submit", async (e) => {
    e.preventDefault();
    const k = $("t-key").value.trim(); if (!k) return;
    const btn = $("t-go"); btn.disabled = true; ghToken = k;
    try { await enterGh(); try { localStorage.setItem("gp-gh-token", k); } catch (er) {} $("tdlg").close(); $("t-key").value = ""; toast("Yönetici modu açıldı. Artık ekleyip düzenleyebilirsin."); }
    catch (er) { ghToken = ""; $("t-err").textContent = er.message === "no-push" ? "Bu anahtarın siteye yazma izni yok." : "Anahtar geçersiz ya da süresi dolmuş."; $("t-err").hidden = false; }
    finally { btn.disabled = false; }
  });

  async function startStatic() {
    mode = "static"; setAdmin(null);
    $("login-btn").hidden = false; $("login-btn").onclick = openTok;
    $("logout-btn").onclick = () => { try { localStorage.removeItem("gp-gh-token"); } catch (e) {} ghToken = ""; mode = "static"; setAdmin(null); $("login-btn").hidden = false; $("who").textContent = ""; render(); toast("Çıkış yapıldı."); };
    $("notice").textContent = "Yükleniyor…";
    try {
      const r = await fetch("data.json?v=" + Date.now(), { cache: "no-store" });
      const d = await r.json();
      items = Array.isArray(d.items) ? d.items : []; siteIg = d.instagram || "";
      $("notice").textContent = "Zafer Partisi Pendik · Gündem";
    } catch (e) { items = []; $("notice").textContent = "Kayıtlar yüklenemedi; internet bağlantını kontrol et."; }
    loaded = true; renderIg(); render();
    if (ghToken) { try { await enterGh(); } catch (e) { if (e.status === 401) { try { localStorage.removeItem("gp-gh-token"); } catch (er) {} ghToken = ""; } } }
  }
  // Ziyaretçide site kendini güncel tutar: her dakika ve uygulamaya geri dönülünce yeni kayıtlar gelir
  async function refreshStatic() {
    if (mode !== "static" || document.hidden || route.page === "edit" || document.querySelector("dialog[open]")) return;
    try {
      const r = await fetch("data.json?v=" + Date.now(), { cache: "no-store" });
      const d = await r.json(); const next = Array.isArray(d.items) ? d.items : [];
      if (JSON.stringify(next) !== JSON.stringify(items) || (d.instagram || "") !== siteIg) { items = next; siteIg = d.instagram || ""; renderIg(); render(); }
    } catch (e) {}
  }
  setInterval(refreshStatic, 60000);
  document.addEventListener("visibilitychange", refreshStatic);
  window.addEventListener("focus", refreshStatic);
  if (CFG && CFG.apiKey && window.firebase) startFirebase(CFG);
  else startStatic();''')
rep('''let db = null, mode = "local"''', '''let mode = "local"''')
rep('''    if (!isAdmin && route.page === "edit") nav("haberler");''', '''    if (!isAdmin && route.page === "edit") nav("haberler");''')
# local mode: no "Kayıtlar bu cihazda" confusion
rep('<title>Gündem Panosu</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n', '')


# --- marka: Zafer Partisi
rep('<div class="logo-mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg></div>',
    '<img class="logo-img" src="logo.png" alt="Zafer Partisi logosu" onerror="this.hidden=true;this.nextElementSibling.hidden=false"><div class="logo-mark" aria-hidden="true" hidden>ZP</div>')
rep('<div class="logo-name">Gündem Panosu<small>', '<div class="logo-name">Zafer Partisi Pendik<small>')
rep('$("notice").textContent = "Gündem Panosu";', '$("notice").textContent = "Zafer Partisi Pendik · Gündem";')
rep('.logo-mark svg { width: 17px; height: 17px; }', '.logo-mark svg { width: 17px; height: 17px; }\n.logo-mark { font-weight: 700; font-size: .8rem; letter-spacing: -.02em; }\n.logo-img { width: 40px; height: 40px; object-fit: contain; border-radius: 10px; flex: none; background: #fff; border: 1px solid var(--line); }')


# ziyaretçiye dönük boş durum metinleri
rep('`Önümüzdeki günler için ${label} yok. <b>Yeni ekle</b> ile ilkini yaz.`', '`Önümüzdeki günler için ${label} yok.`')
rep('"İlk haberi yazmak için <b>Haber yaz</b>\'a dokun. Fotoğraf yükleyip yazını ekleyebilirsin."', '"Henüz haber yok."')
rep('<span class="next-meta">Yeni ekle\'den bir etkinlik oluşturabilirsin.</span>', '<span class="next-meta">Yeni etkinlikler için takipte kalın.</span>')


# --- GitHub ile yönetim (Firebase'siz): yönetici anahtarıyla data.json ve photos/ güncellenir
rep('const srcOf = (p) => p.thumb || p.data || p.tmp || "";',
    'const srcOf = (p) => { const s = p.thumb || p.data || p.tmp || ""; return (window.__localImg && window.__localImg[s]) || s; };')
rep('    if (!p.pid || mode !== "fb") return srcOf(p);',
    '    if (!p.pid || mode !== "fb") { const f = p.data || ""; return (window.__localImg && window.__localImg[f]) || f || srcOf(p); }')
rep('  async function saveItem(a) {\n',
    '  async function saveItem(a) {\n    if (mode === "gh") { const prev = items.slice(); const i = items.findIndex((x) => x.id === a.id); if (i >= 0) items[i] = a; else items.push(a); try { await ghSaveData((i >= 0 ? "Güncellendi: " : "Eklendi: ") + a.title); } catch (e) { items = prev; throw e; } render(); toast("Kaydedildi. Herkese 1-2 dakika içinde görünür."); return; }\n')
rep('  async function removeItem(id) {\n',
    '  async function removeItem(id) {\n    if (mode === "gh") { const prev = items.slice(); const a = items.find((x) => x.id === id); items = items.filter((x) => x.id !== id); try { await ghSaveData("Silindi: " + (a ? a.title : id)); } catch (e) { items = prev; throw e; } if (a) for (const p of photosOf(a)) for (const f of [p.data, p.thumb]) if (f && f.startsWith("photos/")) await ghDel(f, "Fotoğraf silindi").catch(() => {}); if (a && Array.isArray(a.videos)) for (const v of a.videos) if (v.src && v.src.startsWith("videos/")) await ghDel(v.src, "Video silindi").catch(() => {}); render(); toast("Silindi. Herkese 1-2 dakika içinde yansır."); return; }\n')
rep('if (mode === "fb") await fs.collection("settings").doc("site").set({ instagram: h });',
    'if (mode === "fb") await fs.collection("settings").doc("site").set({ instagram: h });\n      else if (mode === "gh") { const old = siteIg; siteIg = h; try { await ghSaveData("Instagram güncellendi"); } catch (e) { siteIg = old; throw e; } }')
rep('        if (p.pid) { photos.push({ pid: p.pid, thumb: p.thumb || "" }); continue; }',
    '        if (p.pid) { photos.push({ pid: p.pid, thumb: p.thumb || "" }); continue; }\n        if (typeof p.data === "string" && p.data.startsWith("photos/")) { photos.push({ data: p.data, thumb: p.thumb || p.data }); continue; }')
rep('        } else photos.push({ data: p.thumb || p.data, thumb: p.thumb || p.data });',
    """        } else if (mode === "gh") {
          const base = "photos/" + (ed.id || "haber") + "-" + Date.now().toString(36) + "-" + photos.length;
          await ghPut(base + ".jpg", p.data.split(",")[1], "Fotoğraf yüklendi");
          await ghPut(base + "-k.jpg", (p.thumb || p.data).split(",")[1], "Küçük fotoğraf yüklendi");
          window.__localImg[base + ".jpg"] = p.data; window.__localImg[base + "-k.jpg"] = p.thumb || p.data;
          p.data = base + ".jpg"; p.thumb = base + "-k.jpg";
          photos.push({ data: p.data, thumb: p.thumb });
        } else photos.push({ data: p.thumb || p.data, thumb: p.thumb || p.data });""")
rep('      if (mode === "fb" && ed.orig) {',
    '      if (mode === "gh" && ed.orig) { const keep = new Set(photos.flatMap((p) => [p.data, p.thumb])); for (const p of photosOf(ed.orig)) for (const f of [p.data, p.thumb]) if (f && f.startsWith("photos/") && !keep.has(f)) await ghDel(f, "Fotoğraf silindi").catch(() => {}); }\n      if (mode === "gh" && ed.orig && Array.isArray(ed.orig.videos)) { const kv = new Set((a.videos || []).map((v) => v.src)); for (const v of ed.orig.videos) if (v.src && v.src.startsWith("videos/") && !kv.has(v.src)) await ghDel(v.src, "Video silindi").catch(() => {}); }\n      if (mode === "fb" && ed.orig) {')
rep('</style>', """.toast { position: fixed; left: 50%; translate: -50% 0; bottom: calc(env(safe-area-inset-bottom, 0px) + 96px); z-index: 40; background: var(--inv); color: var(--inv-ink); padding: 10px 16px; border-radius: 12px; font-size: .9rem; box-shadow: var(--shadow); max-width: calc(100vw - 32px); text-align: center; }
</style>""")
rep('<!-- Tam ekran fotoğraf -->', """<dialog id="tdlg">
  <form class="form" id="tform" novalidate>
    <header><h2>Yönetici girişi</h2><button class="btn small ghost" type="button" data-close aria-label="Kapat">✕</button></header>
    <div class="body">
      <p class="muted" style="margin:0">GitHub'dan aldığın yönetici anahtarını yapıştır. Anahtar sadece bu cihazda saklanır; kimseyle paylaşma.</p>
      <label class="f">Yönetici anahtarı<input id="t-key" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="ghp_…"></label>
      <p class="err" id="t-err" hidden></p>
    </div>
    <footer><span style="flex:1"></span><button class="btn primary" type="submit" id="t-go">Giriş yap</button></footer>
  </form>
</dialog>

<!-- Tam ekran fotoğraf -->""")

head = '''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Zafer Partisi Pendik</title>
<meta name="description" content="Zafer Partisi Pendik duyuruları, gündemi ve haberleri">
<meta name="theme-color" content="#fafafa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#09090b" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="ZP Pendik">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="config.js"></script>
</head>
<body>
'''
open(os.path.join(ROOT, 'index.html'), 'w').write(head + s + '\n</body>\n</html>\n')
print("ok")
