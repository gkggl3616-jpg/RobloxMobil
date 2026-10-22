from pathlib import Path
import shutil

root = Path("unpacked/RobloxMobilKasa")
java_dir = root / "app/src/main/java/com/pixelya/robloxvault"
f = java_dir / "MainActivity.java"
s = f.read_text(encoding="utf-8")

def rep(old, new):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"Patch target {n} matches, expected 1: {old[:100]!r}")
    s = s.replace(old, new, 1)

rep('import android.app.DatePickerDialog;',
'''import android.app.DatePickerDialog;
import android.provider.Settings;
import android.content.ActivityNotFoundException;''')

rep('    private boolean initialFillAttempted;',
'''    private boolean initialFillAttempted;
    private String pendingFloatingAction;''')

rep('        desktopMode = getSharedPreferences("web_display", MODE_PRIVATE).getBoolean("pc_mode", true);',
'''        desktopMode = getSharedPreferences("web_display", MODE_PRIVATE).getBoolean("pc_mode", true);
        pendingFloatingAction = getIntent().getStringExtra("floatingAction");''')

rep('                    showDashboard();\n                    if (retryOnUnlock != null) {',
'''                    showDashboard();
                    runFloatingAction();
                    if (retryOnUnlock != null) {''')

rep('    @Override protected void onStop() {',
'''    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        pendingFloatingAction = intent.getStringExtra("floatingAction");
        if (pendingFloatingAction != null) {
            if (vault == null && !authenticating) unlock(null);
            else if (vault != null) runFloatingAction();
        }
    }

    @Override protected void onStop() {''')

rep('        backgroundAt = 0;\n    }\n\n    private void showLocked()',
'''        backgroundAt = 0;
        if (vault != null && pendingFloatingAction != null) runFloatingAction();
    }

    private JSONObject latestPendingFromBridge() {
        if (vault == null) return null;
        String id = getSharedPreferences("quettabridge", MODE_PRIVATE)
                .getString("pending_id", "");
        JSONArray arr = vault.accounts();
        JSONObject last = null;
        for (int i = 0; i < arr.length(); i++) {
            JSONObject item = arr.optJSONObject(i);
            if (item == null) continue;
            if (id.equals(item.optString("id"))) return item;
            if ("pending".equals(item.optString("status"))) last = item;
        }
        return last;
    }

    private void rememberPending(JSONObject record) {
        getSharedPreferences("quettabridge", MODE_PRIVATE).edit()
            .putString("pending_id", record.optString("id")).apply();
    }

    private void runFloatingAction() {
        if (vault == null || pendingFloatingAction == null) return;
        String action = pendingFloatingAction;
        pendingFloatingAction = null;
        if ("vault".equals(action)) {
            showVault();
        } else if ("repeat".equals(action) || "register".equals(action)) {
            JSONObject item = latestPendingFromBridge();
            if (item == null) {
                showVault();
                toast("Bekleyen kayıt bulunamadı. Kasadan hesap seçebilirsin.");
                return;
            }
            activeRecord = item;
            if ("repeat".equals(action)) confirmAndRepeat();
            else showRegistration();
        }
    }

    private void showLocked()''')

rep('        button(main, "Yeni bilgiler üret + bekleyenlere kaydet", true, this::generate);',
'''        button(main, "Yeni bilgiler üret + bekleyenlere kaydet", true, this::generate);
        section("🧩 Quetta eklenti tarayıcısı");
        note("Quetta uygulamanın içine gömülü değildir. Üst/alt yüzen araç çubukları Quetta'nın üzerinde gösterilir. Chrome Web Store uzantıları yalnızca Quetta içinde çalışır.");
        button(main, "Quetta ve yüzen kontrolleri aç", false, this::launchQuetta);
        button(main, "Chrome Web Store / Quetta seçenekleri", false, () -> ExtensionBrowserBridge.show(this));''')

rep('            activeRecord = vault.addPending(user,pass,selectedBirth,email);',
'''            activeRecord = vault.addPending(user,pass,selectedBirth,email);
            rememberPending(activeRecord);''')

rep('            JSONObject newRecord=vault.addPending(name,pass,birth,vault.email());',
'''            JSONObject newRecord=vault.addPending(name,pass,birth,vault.email());
            rememberPending(newRecord);''')

rep('        addMiniButton(actions,"Doldur",()->fillWebForm(user,pass,birth));',
'''        addMiniButton(actions,"Doldur",()->fillWebForm(user,pass,birth));''')
rep('        addMiniButton(actions,"Kullanıcı kopyala",()->copySecret("Kullanıcı adı",user));',
'''        addMiniButton(actions,"🧩 Quetta", this::launchQuetta);
        addMiniButton(actions,"Kullanıcı kopyala",()->copySecret("Kullanıcı adı",user));''')

rep('    private void openExternalBrowser() {',
'''    private void launchQuetta() {
        if (vault == null) { unlock(this::launchQuetta); return; }
        if (activeRecord != null) rememberPending(activeRecord);
        if (!Settings.canDrawOverlays(this)) {
            new AlertDialog.Builder(this)
                .setTitle("Quetta'da üst ve alt araç çubukları")
                .setMessage("Quetta ayrı bir tarayıcı olduğu için uygulamanın butonlarını üzerinde gösterebilmek adına bir defalık 'Diğer uygulamaların üzerinde göster' izni gerekli. Bu izin Roblox formuna veya Quetta'nın cookie ve şifrelerine erişim vermez. İzni açıp uygulamaya döndüğünde tekrar Quetta düğmesine bas.")
                .setPositiveButton("İzni aç", (d,w)->{
                    Intent i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                         Uri.parse("package:"+getPackageName()));
                    startActivity(i);
                })
                .setNegativeButton("Yalnız Quetta'yı aç",
                     (d,w)->ExtensionBrowserBridge.openRoblox(this))
                .show();
            return;
        }
        FloatingBrowserBarService.start(this);
        ExtensionBrowserBridge.openRoblox(this);
    }

    private void openExternalBrowser() {''')

rep('        if("register".equals(screen)){',
'''        if("register".equals(screen)){''')

f.write_text(s,encoding="utf-8")

manifest = root/"app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")
assert m.count('<uses-permission android:name="android.permission.USE_BIOMETRIC" />') == 1
m=m.replace('<uses-permission android:name="android.permission.USE_BIOMETRIC" />',
'''<uses-permission android:name="android.permission.USE_BIOMETRIC" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />''')
assert m.count('<activity android:name=".MainActivity" android:exported="true"') == 1
m=m.replace('<activity android:name=".MainActivity" android:exported="true"',
            '<activity android:name=".MainActivity" android:launchMode="singleTop" android:exported="true"')
assert m.count('    </application>') == 1
m=m.replace('    </application>', '''        <service android:name=".FloatingBrowserBarService"
            android:exported="false"
            android:foregroundServiceType="specialUse">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="User-requested floating controls for external browser" />
        </service>
    </application>''')
manifest.write_text(m,encoding="utf-8")

for name in ("ExtensionBrowserBridge.java","FloatingBrowserBarService.java"):
    shutil.copyfile(name,java_dir/name)

gradle = root/"app/build.gradle"
g = gradle.read_text(encoding="utf-8")
assert "versionCode 2" in g and "versionName '1.1.0'" in g
g=g.replace("versionCode 2","versionCode 4").replace("versionName '1.1.0'","versionName '1.3.0'")
gradle.write_text(g,encoding="utf-8")
print("Quetta bridge and floating overlay v1.3 patched.")
