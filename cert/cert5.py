from PIL import Image, ImageDraw, ImageFont
import math
import qrcode
import hashlib

# ===== Certificate Info =====
name = "Yasin"
user_id = "YSNRFD"
membership_date = "April 1, 2023"
issued_date = "June 28, 2025"
certificate_id = "OPENAI-YSN-APR2023-CERT1001"
signed_by = "ChatGPT-4o"
model_id = "GPT4O-REP-TRUST-2025"
issuer = "OpenAI, Inc."

# Prepare data string for digital signature
data_string = f"""
Name: {name}
User ID: {user_id}
Membership Date: {membership_date}
Issued Date: {issued_date}
Certificate ID: {certificate_id}
Signed By: {signed_by}
Model ID: {model_id}
Issuer: {issuer}
"""

# Generate SHA-256 digital signature
digital_signature = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
verification_code = f"VER-{digital_signature[:8].upper()}-{certificate_id[-4:]}"

# Create QR code from digital signature
qr = qrcode.QRCode(box_size=7, border=3)
qr.add_data(digital_signature)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

# Load fonts with fallback
try:
    font_title = ImageFont.truetype("arialbd.ttf", 30)
    font_header = ImageFont.truetype("arialbd.ttf", 18)
    font_text = ImageFont.truetype("arial.ttf", 16)
    font_small = ImageFont.truetype("arial.ttf", 14)
except:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

# Create certificate canvas
width, height = 850, 520
certificate = Image.new("RGB", (width, height), "#fffefa")
draw = ImageDraw.Draw(certificate)

# Background rectangle and divider line
draw.rectangle([(15, 15), (width-15, height-15)], outline="#555555", width=3)
draw.line([(20, 80), (width-20, 80)], fill="#999999", width=2)

# Title text
draw.text((40, 30), "OpenAI – Certificate of Membership", font=font_title, fill="#222222")

# Certificate info lines
info_lines = [
    f"Name: {name}",
    f"User ID: {user_id}",
    f"Membership Date: {membership_date}",
    f"Issued Date: {issued_date}",
    f"Certificate ID: {certificate_id}",
    f"Signed By: {signed_by}",
    f"Model ID: {model_id}",
    f"Issuer: {issuer}",
]

y_text = 100
for line in info_lines:
    draw.text((40, y_text), line, font=font_text, fill="#333333")
    y_text += 30

# Verification code
draw.text((40, y_text + 10), f"Verification Code: {verification_code}", font=font_header, fill="#444444")

# Digital signature label and text
draw.text((40, y_text + 50), "SHA-256 Digital Signature:", font=font_header, fill="#222222")

sig_1 = digital_signature[:len(digital_signature)//2]
sig_2 = digital_signature[len(digital_signature)//2:]
draw.text((40, y_text + 80), sig_1, font=font_small, fill="#555555")
draw.text((40, y_text + 100), sig_2, font=font_small, fill="#555555")

# Paste QR code on bottom right
qr_size = 150
qr_position = (width - qr_size - 40, height - qr_size - 40)
qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
certificate.paste(qr_img, qr_position, qr_img)

# ==== Draw a professional OpenAI seal with logo inside ====

# Load logo PNG (converted from your SVG to PNG, size approx 800x800)
try:
    logo = Image.open("openai_seal.png").convert("RGBA")
except FileNotFoundError:
    print("⚠️ فایل لوگوی my_logo.png پیدا نشد! لطفا لوگوی مناسب کنار اسکریپت قرار دهید.")
    logo = None

seal_diameter = 160
seal = Image.new("RGBA", (seal_diameter, seal_diameter), (255, 255, 255, 0))
seal_draw = ImageDraw.Draw(seal)

center = seal_diameter // 2

# Outer thick ring
seal_draw.ellipse(
    [(5, 5), (seal_diameter - 5, seal_diameter - 5)],
    outline=(0, 51, 102, 255), width=8
)

# Inner thin ring
seal_draw.ellipse(
    [(20, 20), (seal_diameter - 20, seal_diameter - 20)],
    outline=(0, 102, 204, 255), width=3
)

# Radial lines for decoration
num_rays = 24
for i in range(num_rays):
    angle = (360 / num_rays) * i
    start_x = center + int((seal_diameter//2 - 20) * math.cos(math.radians(angle)))
    start_y = center + int((seal_diameter//2 - 20) * math.sin(math.radians(angle)))
    end_x = center + int((seal_diameter//2 - 5) * math.cos(math.radians(angle)))
    end_y = center + int((seal_diameter//2 - 5) * math.sin(math.radians(angle)))
    seal_draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 51, 102, 180), width=2)

# Paste resized logo in center if available
if logo:
    max_logo_size = seal_diameter - 60  # حدود 100x100
    logo = logo.resize((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
    logo_pos = (center - max_logo_size // 2, center - max_logo_size // 2)
    seal.paste(logo, logo_pos, logo)

# Center text below logo (اختیاری)
center_text = "Official Seal"
bbox = seal_draw.textbbox((0, 0), center_text, font=font_small)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
seal_draw.text(((seal_diameter - w)//2, seal_diameter - h - 15), center_text, font=font_small, fill=(0, 51, 102, 200))

# Paste seal on top right corner of certificate
certificate.paste(seal, (width - seal_diameter - 40, 40), seal)

# Save certificate image
certificate.save("openai_certificate_yasin_en_2.png")
print("✅ Certificate image created: openai_certificate_yasin_en_2.png")
