# Gündem Panosu

Etkinlikleri, duyuruları ve haberleri tek yerde toplayan basit bir pano.

- **Gündem:** bugünün uyarı bandı, yaklaşan etkinlikler, güncel duyurular ve son haberler bir arada
- **Etkinlikler:** gün, başlangıç–bitiş saati, yer, açıklama, "önemli" işareti; geçmiş etkinlikler ayrı
- **Duyurular:** günü, saati, metni, "önemli" işareti; geçmiş duyurular ayrı
- **Haberler:** ayrı haber sayfası; her haberin kendi sayfası (kapak, yazı, fotoğraf galerisi, tam ekran görüntüleme) ve çoklu fotoğraf yüklenebilen "Haber yaz" sayfası
- **Instagram:** üstte hesabımızın Instagram adresi
- Arama, düzenleme, silme; telefonda yüzen "+" butonu

## Çalıştırma

`index.html` dosyasını tarayıcıda açman yeterli. Kayıtlar tarayıcının yerel deposunda (localStorage) tutulur.

Kaynak: `src/gorev-sicili.html` — `index.html` bu dosyanın tam sayfa sürümüdür.

## Herkese açık uygulama (docs/)

`docs/` klasörü telefona yüklenebilen (PWA) herkese açık sürümdür. Ziyaretçiler okur; ekleme ve düzenleme yalnızca yönetici girişiyle yapılır. Veriler Firebase Firestore'da tutulur.

Kurulum:
1. GitHub: Settings → Pages → "Deploy from a branch" → dal `gorev-sicili`, klasör `/docs`.
2. Firebase: proje oluştur → Firestore Database (production mode) → `docs/firestore.rules` içeriğini Rules sekmesine yapıştırıp yönetici e-postasını yaz → Authentication'da Email/Password'ü aç ve yönetici kullanıcısını ekle → Authorized domains'e GitHub Pages alan adını ekle.
3. Proje ayarlarındaki web uygulamasının `firebaseConfig` değerini `docs/config.js` içine yaz.
