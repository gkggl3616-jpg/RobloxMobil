package com.pixelya.robloxvault;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;

/**
 * Opens a separate Android browser with Chrome Web Store support.
 * Chromium Android WebView cannot host desktop Chrome extensions.
 * Never shares vault passwords, account cookies or tokens.
 */
public final class ExtensionBrowserBridge {
    private static final String QUETTA = "net.quetta.browser";
    private static final String ROBLOX = "https://www.roblox.com/tr/CreateAccount";
    private static final String STORE = "https://chromewebstore.google.com/category/extensions";
    private static final String PLAY = "https://play.google.com/store/apps/details?id=net.quetta.browser";
    private static final String HELP = "https://www.quetta.net/blog/how-to-use-browser-extensions-on-android-phone";

    private ExtensionBrowserBridge() {}

    public static void show(Activity activity) {
        new AlertDialog.Builder(activity)
            .setTitle("Chrome Extensions / Eklenti Tarayıcısı")
            .setMessage("Gerçek Chrome Web Store eklentileri Android WebView içinde çalışmaz. "
                    + "Quetta ayrı bir tarayıcıdır; eklentiler yalnızca Quetta'da çalışır. "
                    + "Kasadaki kullanıcı adı, şifre, cookie ve token verileri başka uygulamaya gönderilmez.")
            .setItems(new String[] {
                "1 · Quetta'yı Google Play'den kur",
                "2 · Chrome Web Store'u Quetta'da aç",
                "3 · Roblox kayıt sayfasını Quetta'da aç",
                "4 · Quetta'nın eklenti kurulum rehberini aç"
            }, (dialog, which) -> {
                switch (which) {
                    case 0: openGeneral(activity, PLAY); break;
                    case 1: openInQuetta(activity, STORE); break;
                    case 2: openRoblox(activity); break;
                    case 3: openGeneral(activity, HELP); break;
                }
            })
            .setNeutralButton("Kapat", null)
            .show();
    }

    public static void openRoblox(Activity activity) {
        openInQuetta(activity, ROBLOX);
    }

    public static void openInQuetta(Activity activity, String url) {
        Uri uri = Uri.parse(url);
        if (!"https".equalsIgnoreCase(uri.getScheme())) {
            Toast.makeText(activity, "Yalnızca HTTPS bağlantıları açılır.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, uri);
            intent.addCategory(Intent.CATEGORY_BROWSABLE);
            intent.setPackage(QUETTA);
            activity.startActivity(intent);
            if (ROBLOX.equals(url)) {
                Toast.makeText(activity,
                    "Quetta ayrı bir tarayıcıdır. Dışarıdaki kayıt uygulamada otomatik doğrulanmaz; "
                    + "Bekleyenler bölümünde kendin onayla.", Toast.LENGTH_LONG).show();
            }
        } catch (ActivityNotFoundException e) {
            new AlertDialog.Builder(activity)
                .setTitle("Quetta bulunamadı")
                .setMessage("Chrome Web Store eklentileri için Quetta'yı Google Play'den yükle. "
                        + "Yükledikten sonra uygulamaya dönüp tekrar dene.")
                .setPositiveButton("Google Play", (d,w) -> openGeneral(activity, PLAY))
                .setNegativeButton("Vazgeç", null)
                .show();
        } catch (Exception e) {
            Toast.makeText(activity, "Eklenti tarayıcısı açılamadı: " + e.getMessage(),
                Toast.LENGTH_LONG).show();
        }
    }

    private static void openGeneral(Activity activity, String url) {
        try {
            activity.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))
                .addCategory(Intent.CATEGORY_BROWSABLE));
        } catch (Exception e) {
            Toast.makeText(activity, "Bağlantı açılamadı.", Toast.LENGTH_LONG).show();
        }
    }
}
