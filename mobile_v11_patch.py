from pathlib import Path

project = Path('unpacked/RobloxMobilKasa')
f = project / 'app/src/main/java/com/pixelya/robloxvault/MainActivity.java'
s = f.read_text(encoding='utf-8')

def replace(a,b):
    global s
    assert a in s, 'Patch target missing: ' + a[:90]
    s=s.replace(a,b,1)

replace('    private static final String REGISTRATION_URL = "https://www.roblox.com/tr/CreateAccount";',
'''    private static final String REGISTRATION_URL = "https://www.roblox.com/tr/CreateAccount";
    private boolean desktopMode = true;
    private static final String PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
''')
replace('        super.onCreate(state);\n        showLocked();',
'''        super.onCreate(state);
        desktopMode = getSharedPreferences("web_display", MODE_PRIVATE).getBoolean("pc_mode", true);
        showLocked();''')
replace('        button(main, "Yeni bilgiler üret + bekleyenlere kaydet", true, this::generate);',
'''        button(main, "Yeni bilgiler üret + bekleyenlere kaydet", true, this::generate);
        note("Yeni kayıtlarda 'Kaydet + Tekrarla' ile sıradaki kullanıcı adı ve şifreyi üret. Her kayıt onayı ve CAPTCHA sende.");
        note("Uygulama içi Roblox tarayıcısı varsayılan PC görünümündedir.");''')
replace('        addMiniButton(actions,"Doldur",()->fillWebForm(user,pass,birth));',
'''        addMiniButton(actions,"Doldur",()->fillWebForm(user,pass,birth));''')
replace('        web = new WebView(this);',
'''        LinearLayout modeBar = new LinearLayout(this);
        modeBar.setPadding(dp(9),0,dp(9),dp(5));root.addView(modeBar);
        addMiniButton(modeBar,desktopMode ? "PC modu: AÇIK" : "PC modu: KAPALI", () -> {
            desktopMode = !desktopMode;
            getSharedPreferences("web_display",MODE_PRIVATE).edit().putBoolean("pc_mode",desktopMode).apply();
            destroyWeb();showRegistration();
        });
        addMiniButton(modeBar,"Sayfayı yenile",()->{if(web!=null)web.reload();});
        web = new WebView(this);''')
replace('        s.setDomStorageEnabled(true);',
'''        s.setDomStorageEnabled(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setSupportZoom(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        if (desktopMode) s.setUserAgentString(PC_UA);''')
replace('        addMiniButton(bottom,"✓ Kayıt tamamlandı",this::askConfirmActive);',
'''        addMiniButton(bottom,"✓ Kaydet",this::askConfirmActive);
        addMiniButton(bottom,"✓ Kaydet + Tekrarla",this::confirmAndRepeat);''')
replace('    private void addMiniButton(LinearLayout parent, String caption, Runnable action) {',
'''    private void confirmAndRepeat() {
        if(activeRecord == null || vault == null) return;
        if("confirmed".equals(activeRecord.optString("status"))) {
            createNextRegistration();return;
        }
        final String id = activeRecord.optString("id");
        new AlertDialog.Builder(this)
            .setTitle("Başarılı kaydet + tekrarla")
            .setMessage(activeRecord.optString("username") + " hesabının Roblox'ta gerçekten açıldığını onaylıyor musun? Sonraki kullanıcı adı ve şifre üretilir. Kayıt ve CAPTCHA otomatik tamamlanmaz.")
            .setPositiveButton("Evet, sonraki kayıt",(dialog,which)->secure(()->{
                vault.setConfirmed(id);
                if(activeRecord != null) activeRecord.put("status","confirmed");
                createNextRegistration();
            }))
            .setNegativeButton("Vazgeç",null).show();
    }

    private void createNextRegistration() {
        secure(()->{
            String birth = vault.birth();
            if(TextUtils.isEmpty(birth)) {error("Doğum tarihini seç.");return;}
            String name=AccountGenerator.username(vault.prefix(),vault.usedNames());
            String pass=AccountGenerator.password();
            // Save the new pending record before any website navigation.
            JSONObject newRecord=vault.addPending(name,pass,birth,vault.email());
            destroyWeb();
            activeRecord=newRecord;
            showRegistration();
        });
    }

    private void addMiniButton(LinearLayout parent, String caption, Runnable action) {''')
replace("Roblox WebView'i reddederse Chrome seçeneğini kullan.",
        "Sayfa açılmazsa Chrome'u açıp üç nokta menüsünden 'Masaüstü sitesi' seç. Formu Chrome'da elle doldur.")
f.write_text(s,encoding='utf-8')
g = project/'app/build.gradle'
t = g.read_text(encoding='utf-8').replace('versionCode 1','versionCode 2').replace("versionName '1.0.0'","versionName '1.1.0'")
g.write_text(t,encoding='utf-8')
print('Mobile v1.1 patch completed')
