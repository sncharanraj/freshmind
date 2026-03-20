# notifier.py
# Person A owns this file
# Checks expiry dates daily and sends desktop notifications

import os
import sys
import platform
import schedule
import time
import subprocess
from datetime import date
from database import get_expiring_items

# ─────────────────────────────────────────
# DETECT ENVIRONMENT
# ─────────────────────────────────────────

def is_wsl():
    """
    Detects if the code is running inside WSL
    (Windows Subsystem for Linux).

    Returns:
        True if running in WSL, False otherwise
    """
    # Check if 'microsoft' appears in kernel version info
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def is_windows():
    """
    Detects if running on native Windows.

    Returns:
        True if Windows, False otherwise
    """
    return platform.system() == "Windows"


# ─────────────────────────────────────────
# SEND NOTIFICATION
# ─────────────────────────────────────────

def send_notification(title, message):
    """
    Sends a desktop notification.
    Automatically handles WSL, Windows, and Linux.

    Parameters:
        title   (str): Notification title
        message (str): Notification body text
    """

    if is_wsl():
        # WSL: Use PowerShell to send Windows notification
        try:
            powershell_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = "{title}"
            $notification.BalloonTipText = "{message}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            Start-Sleep -Seconds 6
            $notification.Dispose()
            """
            subprocess.run(
                ["powershell.exe", "-Command", powershell_script],
                capture_output=True
            )
            print(f"🔔 Notification sent (WSL→Windows): {title}")
        except Exception as e:
            # Fallback: just print to terminal
            print(f"🔔 NOTIFICATION: {title}")
            print(f"   {message}")

    elif is_windows():
        # Native Windows: use plyer
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="FreshMind 🥗",
                timeout=10   # notification stays for 10 seconds
            )
            print(f"🔔 Notification sent (Windows): {title}")
        except Exception as e:
            print(f"🔔 NOTIFICATION: {title}")
            print(f"   {message}")

    else:
        # Linux: use plyer
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="FreshMind 🥗",
                timeout=10
            )
            print(f"🔔 Notification sent (Linux): {title}")
        except Exception as e:
            print(f"🔔 NOTIFICATION: {title}")
            print(f"   {message}")


# ─────────────────────────────────────────
# CHECK EXPIRY & NOTIFY
# ─────────────────────────────────────────

def check_and_notify():
    """
    Main function that:
    1. Fetches items expiring within 7 days
    2. Sends a desktop notification for each one
    3. Prints a summary in the terminal

    This runs once daily via the scheduler.
    """
    print(f"\n🔍 Checking expiry dates... ({date.today()})")

    # Get items expiring within 7 days from database
    expiring_items = get_expiring_items(days=7)

    if not expiring_items:
        print("✅ No items expiring soon. Pantry looks good!")
        return

    print(f"⚠️  Found {len(expiring_items)} item(s) expiring soon!\n")

    # Send a notification for each expiring item
    for item in expiring_items:
        # Calculate how many days until expiry
        expiry_date = date.fromisoformat(item["expiry_date"])
        days_left = (expiry_date - date.today()).days

        # Build notification message
        title = f"⚠️ FreshMind: {item['name']} Expiring Soon!"

        if days_left == 0:
            urgency = "expires TODAY!"
        elif days_left == 1:
            urgency = "expires TOMORROW!"
        else:
            urgency = f"expires in {days_left} days"

        message = (
            f"{item['name']} ({item['category']}) {urgency}\n"
            f"Quantity: {item['quantity']}\n"
            f"Use it before: {item['expiry_date']}"
        )

        # Send the notification
        send_notification(title, message)

        # Also print to terminal for visibility
        print(f"  ⚠️  {item['name']} — {urgency}")

    # Send one summary notification too
    summary_title = "🥗 FreshMind Pantry Alert"
    summary_message = (
        f"{len(expiring_items)} item(s) expiring within 7 days!\n"
        f"Open FreshMind to check your pantry."
    )
    send_notification(summary_title, summary_message)
    print(f"\n📊 Summary notification sent!")


# ─────────────────────────────────────────
# SCHEDULER — RUNS DAILY
# ─────────────────────────────────────────

def start_scheduler():
    """
    Starts the background scheduler that runs
    check_and_notify() every day at 9:00 AM.

    This keeps running until you stop it (Ctrl+C).
    Person B will call this when the app starts.
    """
    print("⏰ FreshMind Notifier Started!")
    print("📅 Will check expiry dates daily at 9:00 AM")
    print("Press Ctrl+C to stop\n")

    # Run once immediately when started
    check_and_notify()

    # Then schedule to run every day at 6:00 AM
    schedule.every().day.at("06:00").do(check_and_notify)

    # Keep the scheduler running forever
    while True:
        # Check if any scheduled job needs to run
        schedule.run_pending()
        # Wait 60 seconds before checking again
        time.sleep(60)


# ─────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("🧪 Testing FreshMind Notifier...\n")

    # Test 1: Check environment detection
    print(f"Running on WSL: {is_wsl()}")
    print(f"Running on Windows: {is_windows()}")
    print()

    # Test 2: Send a test notification
    print("Sending test notification...")
    send_notification(
        title="🥗 FreshMind Test",
        message="Notifier is working correctly!"
    )

    # Test 3: Run expiry check manually
    print("\nRunning expiry check...")
    check_and_notify()
