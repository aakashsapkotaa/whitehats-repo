"""
OTP Email Verification Utility
Sends OTP codes via Gmail SMTP using App Password.
"""
import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# In-memory OTP store (key=email, value={otp, expires_at, user_data})
otp_store: dict = {}

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

OTP_EXPIRY_MINUTES = 5


def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email via Gmail SMTP."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[OTP] Gmail credentials not configured. OTP:", otp)
        return True  # Allow bypass for dev

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎓 EduHub - Your Verification Code: {otp}"
    msg["From"] = f"EduHub <{GMAIL_ADDRESS}>"
    msg["To"] = to_email

    html = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif; max-width:480px; margin:0 auto; background:#1a1a2e; border-radius:16px; overflow:hidden;">
        <div style="background:linear-gradient(135deg,#0F5257,#55D6BE); padding:32px; text-align:center;">
            <h1 style="color:white; margin:0; font-size:28px;">🎓 EduHub</h1>
            <p style="color:rgba(255,255,255,0.85); margin-top:8px; font-size:14px;">Email Verification</p>
        </div>
        <div style="padding:32px; color:#e0e0e0;">
            <p style="margin-bottom:24px; font-size:15px;">Hi there! Use this code to verify your email:</p>
            <div style="background:rgba(85,214,190,0.1); border:2px solid #55D6BE; border-radius:12px; padding:24px; text-align:center; margin-bottom:24px;">
                <span style="font-size:36px; font-weight:700; letter-spacing:8px; color:#55D6BE;">{otp}</span>
            </div>
            <p style="color:#999; font-size:13px;">This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>
            <p style="color:#999; font-size:13px;">If you didn't request this, please ignore this email.</p>
        </div>
        <div style="background:rgba(255,255,255,0.05); padding:16px; text-align:center;">
            <p style="color:#666; font-size:11px; margin:0;">© EduHub — Community-Driven Learning</p>
        </div>
    </div>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        print(f"[OTP] Attempting to send email from {GMAIL_ADDRESS} to {to_email}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        print(f"[OTP] Email successfully sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[OTP] Authentication failed: {e}")
        print(f"[OTP] Check if GMAIL_ADDRESS='{GMAIL_ADDRESS}' and GMAIL_APP_PASSWORD are correct")
        return False
    except Exception as e:
        print(f"[OTP] Email send failed: {type(e).__name__}: {e}")
        return False


def store_otp(email: str, otp: str, user_data: dict):
    """Store OTP with expiry and associated registration data."""
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "user_data": user_data,
        "attempts": 0,
    }


def verify_otp(email: str, otp: str) -> dict | None:
    """Verify OTP. Returns user_data if valid, None otherwise."""
    entry = otp_store.get(email)
    if not entry:
        return None

    # Check expiry
    if datetime.utcnow() > entry["expires_at"]:
        del otp_store[email]
        return None

    # Rate limit: max 5 attempts
    entry["attempts"] += 1
    if entry["attempts"] > 5:
        del otp_store[email]
        return None

    if entry["otp"] != otp:
        return None

    # Valid — extract user data and clean up
    user_data = entry["user_data"]
    del otp_store[email]
    return user_data
