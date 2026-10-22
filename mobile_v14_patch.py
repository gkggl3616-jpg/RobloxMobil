from pathlib import Path

root = Path("unpacked/RobloxMobilKasa")
src = root / "app/src/main/java/com/pixelya/robloxvault"
main = src / "MainActivity.java"
s=main.read_text(encoding="utf-8")

def rep(a,b):
    global s
    n=s.count(a)
    assert n == 1, f"expected one match, found {n}: {a[:110]!r}"
    s=s.replace(a,b,1)

rep('import android.provider.Settings;',
'''import android.provider.Settings;
import android.util.Base64;
import android.os.Handler;
import android.os.Looper;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;''')

rep('    private String pendingFloatingAction;',
'''    private String pendingFloatingAction;
    private Uri pendingQuettaConfirmation;''')

rep('        pendingFloatingAction = getIntent().getStringExtra("floatingAction");',
'''        pendingFloatingAction = getIntent().getStringExtra("floatingAction");
        acceptQuettaConfirmationIntent(getIntent());''')

rep('                    runFloatingAction();\n                    if (retryOnUnlock != null) {',
'''                    processQuettaConfirmation();
                    runFloatingAction();
                    if (retryOnUnlock != null) {''')

rep('        pendingFloatingAction = intent.getStringExtra("floatingAction");\n        if (pendingFloatingAction != null) {',
'''        pendingFloatingAction = intent.getStringExtra("floatingAction");
        acceptQuettaConfirmationIntent(intent);
        if (pendingFloatingAction != null || pendingQuettaConfirmation != null) {''')

rep('        if (vault != null && pendingFloatingAction != null) runFloatingAction();',
'''        if (vault != null) {
            processQuettaConfirmation();
            if (pendingFloatingAction != null) runFloatingAction();
        }''')

rep('    private void showLocked()',
'''    private void acceptQuettaConfirmationIntent(Intent intent) {
        Uri u = intent == null ? null : intent.getData();
        if (u == null) return;
        if ("robloxkasa".equals(u.getScheme()) && "confirm".equals(u.getHost())) {
            pendingQuettaConfirmation = u;
        }
    }

    /** Receives an account-success signal from our Quetta extension, validated against
     *  a random one-time nonce that was encrypted in the device vault before navigation. */
    private void processQuettaConfirmation() {
        if (vault == null || pendingQuettaConfirmation == null) return;
        Uri u=pendingQuettaConfirmation;
        pendingQuettaConfirmation=null;
        String id=u.getQueryParameter("id");
        String user=u.getQueryParameter("username");
        String token=u.getQueryParameter("token");
        if (id == null || user == null || token == null) return;
        secure(() -> {
            JSONArray all=vault.accounts();
            for(int i=0;i<all.length();i++) {
                JSONObject r=all.optJSONObject(i);
                if (r == null || !"pending".equals(r.optString("status"))) continue;
                if (!id.equals(r.optString("id")) || !user.equals(r.optString("username"))) continue;
                String correct=r.optString("bridgeNonce","");
                if (correct.length()<24 || !java.security.MessageDigest.isEqual(
                        correct.getBytes(StandardCharsets.UTF_8),
                        token.getBytes(StandardCharsets.UTF_8))) continue;
                vault.setConfirmed(id);
                r.remove("bridgeNonce");
                vault.save();
                if (activeRecord != null && id.equals(activeRecord.optString("id"))) {
                    activeRecord.put("status","confirmed");
                }
                toast("Quetta kayıt doğrulaması kasaya aktarıldı: "+user);
                showVault();
                return;
            }
            error("Quetta eşleşmesi doğrulanamadı. Bekleyen hesabı kasadan kontrol et.");
        });
    }

    /** User-triggered temporary clipboard bridge. Never exposes browser cookies. */
    private void fillInQuetta() {
        if (vault == null) {unlock(this::fillInQuetta);return;}
        if (activeRecord == null) {
            activeRecord=latestPendingFromBridge();
            if (activeRecord == null) { error("Önce yeni kullanıcı adı/şifre üret.");return; }
        }
        final JSONObject record=activeRecord;
        new AlertDialog.Builder(this).setTitle("Quetta'ya form bilgilerini aktar")
          .setMessage("Kullanıcı adı, doğum tarihi ve şifre kısa süreliğine telefon panosuna kopyalanır. "
             + "Quetta kayıt sayfasında kendi eklentimizin Doldur düğmesine basarak formu doldurursun. "
             + "Pano içeriği diğer uygulamalardan gizli kabul edilmemelidir. Devam edilsin mi?")
          .setPositiveButton("Kopyala ve Quetta'yı aç",(d,w)->secure(()->{
              if (record.optString("bridgeNonce").length()<24) {
                  byte[] bytes=new byte[24];
                  new SecureRandom().nextBytes(bytes);
                  record.put("bridgeNonce",Base64.encodeToString(bytes,
                      Base64.NO_PADDING|Base64.NO_WRAP|Base64.URL_SAFE));
                  vault.save();
              }
              JSONObject data=new JSONObject();
              data.put("v",1);
              data.put("id",record.optString("id"));
              data.put("username",record.optString("username"));
              data.put("password",record.optString("password"));
              data.put("birth",record.optString("birth"));
              data.put("nonce",record.optString("bridgeNonce"));
              String payload="RKASA1."+Base64.encodeToString(
                 data.toString().getBytes(StandardCharsets.UTF_8),
                 Base64.NO_PADDING|Base64.NO_WRAP|Base64.URL_SAFE);
              android.content.ClipboardManager cm=(android.content.ClipboardManager)
                  getSystemService(CLIPBOARD_SERVICE);
              cm.setPrimaryClip(android.content.ClipData.newPlainText("RobloxKasa-Gecici",payload));
              // Clear only if still our exact payload; do not remove newer user clipboard items.
              new Handler(Looper.getMainLooper()).postDelayed(()->{
                  try {
                      android.content.ClipData now=cm.getPrimaryClip();
                      if(now != null && now.getItemCount()>0 &&
                          payload.contentEquals(now.getItemAt(0).coerceToText(this))) {
                          cm.setPrimaryClip(android.content.ClipData.newPlainText("",""));
                      }
                  }catch(Exception ignored){}
              },90000);
              rememberPending(record);
              FloatingBrowserBarService.start(this);
              ExtensionBrowserBridge.openRoblox(this);
          }))
          .setNegativeButton("İptal",null).show();
    }

    private void saveOnlyFromQuetta() {
        activeRecord=latestPendingFromBridge();
        if(activeRecord == null) {showVault();return;}
        if("confirmed".equals(activeRecord.optString("status"))) {
            showVault();return;
        }
        askConfirmActive();
    }

    private void repeatOnly() {
        if(vault == null) {unlock(this::repeatOnly);return;}
        activeRecord=latestPendingFromBridge();
        if(activeRecord != null && !"confirmed".equals(activeRecord.optString("status"))) {
            error("Bu hesap hâlâ BEKLEYEN. Önce Kaydet ile doğrula veya kasada durumu kontrol et.");
            return;
        }
        secure(()->{
            String birth=vault.birth();
            if (TextUtils.isEmpty(birth)) {error("Önce doğum tarihini seç.");return;}
            String name=AccountGenerator.username(vault.prefix(),vault.usedNames());
            String pass=AccountGenerator.password();
            activeRecord=vault.addPending(name,pass,birth,vault.email());
            rememberPending(activeRecord);
            // Preserve current records: vault.addPending already writes encrypted data.
            showDashboard();
            fillInQuetta();
        });
    }

    private void showQuettaDesktopInfo() {
        new AlertDialog.Builder(this).setTitle("Quetta masaüstü modu")
            .setMessage("Quetta başka bir uygulama olduğu için onun tarayıcı ayarını burada değiştiremiyoruz. "
               + "Quetta'da menü (⋮) → Masaüstü sitesi / Desktop site seçeneğini aç. "
               + "Bizim WebView PC modu ayrı olarak çalışmaya devam eder.")
            .setPositiveButton("Quetta'yı aç",(d,w)->ExtensionBrowserBridge.openRoblox(this))
            .setNegativeButton("Kapat",null).show();
    }

    private void showLocked()''')

rep('        } else if ("repeat".equals(action) || "register".equals(action)) {',
'''        } else if ("fill".equals(action)) {
            fillInQuetta();
        } else if ("save".equals(action)) {
            saveOnlyFromQuetta();
        } else if ("repeat".equals(action)) {
            repeatOnly();
        } else if ("pc".equals(action)) {
            showQuettaDesktopInfo();
        } else if ("register".equals(action)) {''')

rep('        button(main, "Quetta ve yüzen kontrolleri aç", false, this::launchQuetta);',
'''        button(main, "Quetta'ya Doldur (panodan aktar)", true, this::fillInQuetta);
        button(main, "Quetta ve yüzen kontrolleri aç", false, this::launchQuetta);
        button(main, "Kaydet (yalnızca doğrulanmış hesap)", false, this::saveOnlyFromQuetta);
        button(main, "Tekrarla (yeni bilgiler üret)", false, this::repeatOnly);
        button(main, "Quetta PC modu rehberi", false, this::showQuettaDesktopInfo);''')

rep('        addMiniButton(actions,"🧩 Quetta", this::launchQuetta);',
'''        addMiniButton(actions,"🧩 Quetta'da Doldur", this::fillInQuetta);''')

rep('        addMiniButton(bottom,"✓ Kaydet + Tekrarla",this::confirmAndRepeat);',
'''        addMiniButton(bottom,"↻ Tekrarla",this::repeatOnly);''')

main.write_text(s,encoding="utf-8")

overlay=src/"FloatingBrowserBarService.java"
o=overlay.read_text(encoding="utf-8")
a='''        button(b,"Kasa", () -> openMain("vault"));
        button(b,"✓ Kaydet +\\nTekrarla", () -> openMain("repeat"));
        button(b,"Uygulama", () -> openMain("register"));
        button(b,"Gizle", this::stopSelf);'''
b='''        button(b,"Doldur", () -> openMain("fill"));
        button(b,"Kaydet", () -> openMain("save"));
        button(b,"Tekrarla", () -> openMain("repeat"));
        button(b,"PC modu", () -> openMain("pc"));
        button(b,"Kasa", () -> openMain("vault"));'''
assert a in o, "overlay buttons not found"
o=o.replace(a,b,1)
overlay.write_text(o,encoding="utf-8")

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text(encoding="utf-8")
a='''            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>'''
b='''            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="robloxkasa" android:host="confirm" />
            </intent-filter>'''
assert a in m, "intent filter not found"
m=m.replace(a,b,1)
manifest.write_text(m,encoding="utf-8")

gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
assert "versionCode 4" in g and "versionName '1.3.0'" in g
g=g.replace("versionCode 4","versionCode 5").replace("versionName '1.3.0'","versionName '1.4.0'")
gradle.write_text(g,encoding="utf-8")
print("v1.4 Quetta form bridge, auto encrypted pending, split buttons, PC help ready")
