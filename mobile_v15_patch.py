from pathlib import Path
root=Path("unpacked/RobloxMobilKasa")
java=root/"app/src/main/java/com/pixelya/robloxvault"
f=java/"MainActivity.java"
s=f.read_text(encoding="utf-8")
def rep(a,b):
    global s
    n=s.count(a)
    assert n==1,f"Expected exactly once: {a[:120]!r}, got {n}"
    s=s.replace(a,b,1)
def span(start,end,replacement):
    global s
    i=s.find(start);j=s.find(end,i+len(start))
    assert i>=0 and j>i,(start,end)
    s=s[:i]+replacement+"\n\n"+s[j:]

span(
    "    /** User-triggered temporary clipboard bridge. Never exposes browser cookies. */",
    "    private void saveOnlyFromQuetta() {",
'''    /** Open a Quetta extension command without sharing account details over the
     *  clipboard, URI, Intent extras or other application boundaries.
     *  The Quetta extension reads its own locally stored registration profiles. */
    private void fillInQuetta() {
        ExtensionBrowserBridge.openInQuetta(this,
            "https://www.roblox.com/tr/CreateAccount#rkasa-fill");
    }''')

span(
    "    private void saveOnlyFromQuetta() {",
    "    private void showQuettaDesktopInfo() {",
'''    private void saveOnlyFromQuetta() {
        ExtensionBrowserBridge.openInQuetta(this,
            "https://www.roblox.com/tr/CreateAccount#rkasa-save");
    }

    /** Repeat is separate from Save: the Quetta extension advances its own list
     *  and fills the next profile without ever sending secrets via a clipboard. */
    private void repeatOnly() {
        ExtensionBrowserBridge.openInQuetta(this,
            "https://www.roblox.com/tr/CreateAccount#rkasa-next");
    }''')

rep('        button(main, "Quetta\'ya Doldur (panodan aktar)", true, this::fillInQuetta);',
'''        button(main, "Quetta eklentisinde Doldur (panosuz)", true, this::fillInQuetta);''')

rep('        button(main, "Kaydet (yalnızca doğrulanmış hesap)", false, this::saveOnlyFromQuetta);',
'''        button(main, "Quetta eklentisinde Kaydet", false, this::saveOnlyFromQuetta);''')

rep('        button(main, "Tekrarla (yeni bilgiler üret)", false, this::repeatOnly);',
'''        button(main, "Quetta eklentisinde Tekrarla", false, this::repeatOnly);''')

rep('        note("Quetta uygulamanın içine gömülü değildir. Üst/alt yüzen araç çubukları Quetta\'nın üzerinde gösterilir. Chrome Web Store uzantıları yalnızca Quetta içinde çalışır.");',
'''        note("Quetta uygulamanın içine gömülü değildir. 50 hazır profil ve TXT yükleme Quetta eklentisindedir. APK kasası ve eklenti kasası ayrı depolardır. Eklenti Doldur, Kaydet ve Tekrarla düğmeleri kopyala-yapıştır kullanmaz.");''')

f.write_text(s,encoding="utf-8")

overlay=java/"FloatingBrowserBarService.java"
o=overlay.read_text(encoding="utf-8")
for act in ("fill","save","repeat"):
    old=f'button(b,"{"Doldur" if act=="fill" else "Kaydet" if act=="save" else "Tekrarla"}", () -> openMain("{act}"));'
    new=f'button(b,"{"Doldur" if act=="fill" else "Kaydet" if act=="save" else "Tekrarla"}", () -> sendToQuetta("{act}"));'
    assert old in o,old
    o=o.replace(old,new,1)
anchor='    private void openMain(String target) {'
assert anchor in o
o=o.replace(anchor,'''    private void sendToQuetta(String command) {
        String fragment="fill".equals(command) ? "rkasa-fill" :
             "save".equals(command) ? "rkasa-save" : "rkasa-next";
        try {
            Intent intent=new Intent(Intent.ACTION_VIEW,
                android.net.Uri.parse("https://www.roblox.com/tr/CreateAccount#"+fragment));
            intent.addCategory(Intent.CATEGORY_BROWSABLE);
            intent.setPackage("net.quetta.browser");
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch(Exception e) {
            Toast.makeText(this,"Quetta açılamadı; uygulamayı kurup tekrar dene.",
                Toast.LENGTH_LONG).show();
        }
    }

'''+anchor,1)
overlay.write_text(o,encoding="utf-8")

g=root/"app/build.gradle"
content=g.read_text(encoding="utf-8")
assert "versionCode 5" in content and "versionName '1.4.0'" in content
content=content.replace("versionCode 5","versionCode 6")
content=content.replace("versionName '1.4.0'","versionName '1.5.0'")
g.write_text(content,encoding="utf-8")
print("Roblox Mobil Kasa v1.5: Quetta command-only integration; clipboard removed from extension flow.")
