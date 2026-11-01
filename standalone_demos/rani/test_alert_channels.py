"""
test_alert_channels.py
Test script to verify real Telegram and Email alerts from your .env file.
Run:
    python test_alert_channels.py
"""

import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import httpx

def load_env():
    # Check current directory .env first, then parent/rani
    candidates = [Path(".env"), Path("standalone_demos/rani/.env"), Path("../.env")]
    for p in candidates:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            print(f"Loaded configuration from: {p.resolve()}")
            break

def test_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    print("\n--- 1. Testing Telegram Alert ---")
    if not token or not chat_id:
        print("❌ Telegram is NOT configured in .env:")
        print(f"   TELEGRAM_BOT_TOKEN={'Set' if token else 'EMPTY'}")
        print(f"   TELEGRAM_CHAT_ID={'Set' if chat_id else 'EMPTY'}")
        return False

    print(f"   Using Bot Token: {token[:10]}...{token[-5:]}")
    print(f"   Target Chat ID:  {chat_id}")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🚨 [TEST ALERT] Healthcare Cloud Framework\n\nEmergency dispatch channel test: Telegram notifications are ACTIVE and working! ✅",
    }
    try:
        r = httpx.post(url, json=payload, timeout=10)
        res = r.json()
        if r.status_code == 200 and res.get("ok"):
            msg_id = res.get("result", {}).get("message_id")
            print(f"✅ SUCCESS! Telegram alert delivered (Message ID: {msg_id}).")
            print("   Check your Telegram phone app now!")
            return True
        else:
            print(f"❌ Telegram API returned error HTTP {r.status_code}:")
            print(f"   {res.get('description', res)}")
            if "chat not found" in str(res).lower() or "bot was blocked" in str(res).lower():
                print("\n   👉 TIP: Open your bot in Telegram on your phone and click '/start' first!")
            return False
    except Exception as e:
        print(f"❌ Connection error while contacting Telegram: {e}")
        return False

def test_email():
    host = os.environ.get("SMTP_HOST", "").strip()
    port = int(os.environ.get("SMTP_PORT", 587))
    username = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    sender = os.environ.get("SMTP_FROM", username).strip()
    recipient = os.environ.get("ALERT_EMAIL_TO", "").strip()

    print("\n--- 2. Testing Email Alert (SMTP) ---")
    if not password:
        print("⚠️ Email is NOT fully configured yet (SMTP_PASSWORD is empty).")
        print("   To enable Gmail delivery:")
        print("   1. Go to https://myaccount.google.com/apppasswords")
        print("   2. Generate a 16-character 'App Password'")
        print("   3. Put it in .env under SMTP_PASSWORD=xxxx xxxx xxxx xxxx")
        return False

    if not (host and username and recipient):
        print("❌ Missing SMTP settings in .env.")
        return False

    print(f"   SMTP Server: {host}:{port}")
    print(f"   From:        {sender}")
    print(f"   To:          {recipient}")

    msg = MIMEText("🚨 [TEST ALERT] Healthcare Cloud Framework\n\nEmergency vital threshold alert: Email channel test successful! ✅")
    msg["Subject"] = "[CRITICAL] Healthcare Cloud Framework - Test Alert"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP(host, port, timeout=15) as srv:
            srv.starttls()
            srv.login(username, password)
            srv.sendmail(sender, [recipient], msg.as_string())
        print(f"✅ SUCCESS! Email sent to {recipient}.")
        print("   Check your Gmail inbox (and Spam/Updates tab if not in Primary)!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        print("   👉 TIP: For Gmail, you CANNOT use your regular password.")
        print("   You MUST generate a 16-character 'App Password' at https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print(" Healthcare Cloud Framework - Alert Channel Verification")
    print("=" * 60)
    load_env()
    test_telegram()
    test_email()
    print("\n" + "=" * 60)
