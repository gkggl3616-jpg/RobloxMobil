# Roblox Mobil Kasa v1.4 — Quetta entegrasyonu

Bu repo, yerel Android Keystore ile şifrelenmiş kayıt kasasını ve Quetta'nın üstünde görünen Android kontrol çubuklarını içerir.

## Özellikler

- **Doldur:** Kullanıcı onayıyla geçici panoya kullanıcı adı, güçlü şifre ve gerçek doğum tarihi aktarılır; Quetta eklentisindeki Doldur düğmesi Roblox kayıt formuna yazar.
- **Kaydet:** Başarılı hesabı yerel şifreli kasaya aktarır. Doğrulanmış kullanıcı adı ve tek kullanımlık eşleşme anahtarını taşıyan robloxkasa://confirm bağlantısı desteklenir; bu bağlantı tarayıcı politikaları nedeniyle otomatik açılmayabilir.
- **Tekrarla:** Kaydet işleminden ayrı düğmedir. Yeni kullanıcı adı/şifre oluşturur, bilgileri kayıt sayfası açılmadan önce **Bekleyen** olarak kasaya kaydeder.
- **PC modu:** Uygulama içi WebView için PC modu ayarı vardır. Quetta'nın masaüstü görünümü **Quetta menüsü → Desktop site** üzerinden ayrıca açılır.
- **Üst / alt yüzen kontroller:** Android'in 'Diğer uygulamaların üzerinde göster' izni gerekir.

## Kurulum

1. Repo **Actions** → son başarılı **Android APK olustur** derlemesi → Artifacts → **RobloxMobilKasa-v1-4-Quetta-APK** dosyasını indir.
2. ZIP'ten app-debug.apk'yi çıkar ve Android'de yükle.
3. Önceki kasanda kayıt varsa yedeğini almadan eski sürümü kaldırma. GitHub Actions debug anahtarı derlemeler arasında değişebilir.
4. Quetta'yı Google Play'den yükle. Ayrı Quetta form doldurucu ZIP'i uzantılar menüsünden içe aktar (desteklenen Quetta sürümlerinde).
5. Uygulamada cihaz ekran kilidiyle kasayı aç, doğum tarihini ayarla ve yeni bilgiler üret.
6. **Quetta'ya Doldur** → onay ver → Quetta kayıt sayfasında **Doldur**.
7. Gerekirse Quetta üç nokta menüsünden **Masaüstü sitesi** aç.
8. CAPTCHA'yı çöz ve Roblox kaydını kendin tamamla. Başarı algılanamazsa **Kaydet** ile manuel doğrula.
9. Sonraki hesap bilgilerini hazırlamak için **Tekrarla**.

## Sınırlar ve güvenlik

Quetta başka bir uygulamadır, APK'nın içine gömülmez. Android ekran üstü butonları Quetta'nın sayfa içeriklerini otomatik kontrol edemez. Doldurma işlevi için ayrı, kullanıcı tarafından kurulan Quetta Manifest V3 eklentisi gerekir. Quetta'nın eklenti ZIP desteği ve Android Clipboard API davranışı cihaz/sürüme göre değişebilir.

Şifreli kasa Android Keystore kullanır; parola içeren pano verisi geçicidir (yaklaşık 90 saniye sonra temizleme denenir). Herhangi bir CAPTCHA çözme, kayıt onayı gönderme, oturum cookie/token çıkarma yapılmaz. **Roblox'un gerçek kayıt ekranında uçtan uca test edilmedi.**
