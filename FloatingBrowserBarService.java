package com.pixelya.robloxvault;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.IBinder;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

/**
 * User-enabled floating shortcuts over an external browser.
 * This service NEVER reads the browser DOM, cookies, password fields, or accessibility data.
 * Chrome extensions continue to run only in the separate Quetta application.
 */
public final class FloatingBrowserBarService extends Service {
    public static final String ACTION_STOP = "com.pixelya.robloxvault.STOP_FLOATING_BARS";
    private static final String CHANNEL = "floating_browser_tools";
    private static final int NOTIFICATION_ID = 1042;
    private WindowManager manager;
    private View top;
    private View bottom;

    public static void start(Activity activity) {
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(activity)) {
            Toast.makeText(activity, "Önce 'Diğer uygulamaların üzerinde göster' iznini aç.",
                Toast.LENGTH_LONG).show();
            Intent settings = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                android.net.Uri.parse("package:" + activity.getPackageName()));
            activity.startActivity(settings);
            return;
        }
        try {
            activity.startForegroundService(new Intent(activity, FloatingBrowserBarService.class));
        } catch (Exception e) {
            Toast.makeText(activity, "Yüzen araç çubukları açılamadı: " + e.getMessage(),
                Toast.LENGTH_LONG).show();
        }
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopSelf();
            return START_NOT_STICKY;
        }
        ensureNotification();
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(this)) {
            stopSelf();
            return START_NOT_STICKY;
        }
        if (top == null || bottom == null) showFloatingBars();
        return START_NOT_STICKY;
    }

    private void ensureNotification() {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Yüzen tarayıcı araçları",
                NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Quetta açıkken kasaya geri dönme ve kayıt yönetimi");
            nm.createNotificationChannel(ch);
        }
        Intent open = new Intent(this, MainActivity.class);
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP |
            Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent click = PendingIntent.getActivity(this, 1, open,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_menu_view)
            .setContentTitle("Roblox Mobil Kasa")
            .setContentText("Quetta için yüzen kontroller açık · Durdurmak için uygulamaya dön.")
            .setOngoing(true)
            .setContentIntent(click).build();
        startForeground(NOTIFICATION_ID, n);
    }

    private int dp(int n) { return (int) (getResources().getDisplayMetrics().density * n + .5f); }
    private GradientDrawable bg(int color) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color); d.setCornerRadius(dp(13)); return d;
    }
    private LinearLayout bar() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(dp(6), dp(4), dp(6), dp(4));
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackground(bg(0xF0192546));
        return row;
    }
    private void button(LinearLayout parent, String title, Runnable runnable) {
        TextView b = new TextView(this);
        b.setText(title);
        b.setTextColor(Color.WHITE);
        b.setTextSize(11);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(5), dp(9), dp(5), dp(9));
        b.setBackground(bg(0xFF3656A0));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(44), 1);
        p.setMargins(dp(2), 0, dp(2), 0);
        parent.addView(b,p);
        b.setOnClickListener(v -> runnable.run());
    }
    private void showFloatingBars() {
        manager = (WindowManager) getSystemService(WINDOW_SERVICE);
        LinearLayout t = bar();
        button(t,"◆ Roblox Kasa", () -> openMain("vault"));
        button(t,"Dön", () -> openMain("register"));
        button(t,"✕ Gizle", this::stopSelf);
        top = t;
        LinearLayout b = bar();
        button(b,"Kasa", () -> openMain("vault"));
        button(b,"✓ Kaydet +\nTekrarla", () -> openMain("repeat"));
        button(b,"Uygulama", () -> openMain("register"));
        button(b,"Gizle", this::stopSelf);
        bottom = b;
        try {
            WindowManager.LayoutParams pTop = params(Gravity.TOP | Gravity.CENTER_HORIZONTAL, dp(57));
            WindowManager.LayoutParams pBottom = params(Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL, dp(72));
            manager.addView(top,pTop);
            manager.addView(bottom,pBottom);
        } catch (Exception e) {
            Toast.makeText(this,"Yüzen çubuklar gösterilemedi: "+e.getMessage(),
                Toast.LENGTH_LONG).show();
            stopSelf();
        }
    }
    private WindowManager.LayoutParams params(int gravity, int y) {
        WindowManager.LayoutParams p = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
              WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            android.graphics.PixelFormat.TRANSLUCENT);
        p.gravity=gravity;
        p.y=y;
        return p;
    }
    private void openMain(String target) {
        Intent i = new Intent(this, MainActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP |
            Intent.FLAG_ACTIVITY_SINGLE_TOP);
        i.putExtra("floatingAction",target);
        try { startActivity(i); }
        catch (Exception e) {
            Toast.makeText(this,"Uygulama açılamadı: "+e.getMessage(),Toast.LENGTH_LONG).show();
        }
        stopSelf();
    }
    @Override public void onDestroy() {
        if (manager != null) {
            if (top != null) { try {manager.removeView(top);} catch (Exception ignored) {} }
            if (bottom != null) { try {manager.removeView(bottom);} catch (Exception ignored) {} }
        }
        top=null; bottom=null; manager=null;
        super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent) { return null; }
}
