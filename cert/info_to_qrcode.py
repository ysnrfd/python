import qrcode
from PIL import Image

# ===== اطلاعات گواهی یاسین =====
cert_info = {
    "Name": "Yasin",
    "Last Name": "Aryanfard",
    "User ID": "YSNRFD",
    "Membership Date": "April 1, 2023",
    "Issued Date": "June 28, 2025",
    "Certificate ID": "OPENAI-YSN-APR2023-CERT1001",
    "Signed By": "ChatGPT-4o",
    "Model ID": "GPT4O-REP-TRUST-2025",
    "Issuer": "OpenAI, Inc."
}

# تبدیل به یک رشته‌ی قابل خواندن برای QR
qr_text = "\n".join(f"{k}: {v}" for k, v in cert_info.items())

# ساخت QR Code
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=4
)
qr.add_data(qr_text)
qr.make(fit=True)

# ساخت تصویر QR
img = qr.make_image(fill_color="black", back_color="white")

# ذخیره در فایل
img.save("yasin_certificate_qrcode.png")
print("✅ QR Code ساخته شد و در فایل 'yasin_certificate_qrcode.png' ذخیره شد.")
