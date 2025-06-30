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

digital_signature = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
verification_code = f"VER-{digital_signature[:8].upper()}-{certificate_id[-4:]}"

qr = qrcode.QRCode(box_size=7, border=3)
qr.add_data(digital_signature)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

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

width, height = 850, 520
certificate = Image.new("RGB", (width, height), "#fffefa")
draw = ImageDraw.Draw(certificate)

draw.rectangle([(15, 15), (width-15, height-15)], outline="#555555", width=3)
draw.line([(20, 80), (width-20, 80)], fill="#999999", width=2)

draw.text((40, 30), "OpenAI – Certificate of Membership", font=font_title, fill="#222222")

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

draw.text((40, y_text + 10), f"Verification Code: {verification_code}", font=font_header, fill="#444444")

draw.text((40, y_text + 50), "SHA-256 Digital Signature:", font=font_header, fill="#222222")

sig_1 = digital_signature[:len(digital_signature)//2]
sig_2 = digital_signature[len(digital_signature)//2:]
draw.text((40, y_text + 80), sig_1, font=font_small, fill="#555555")
draw.text((40, y_text + 100), sig_2, font=font_small, fill="#555555")

qr_size = 150
qr_position = (width - qr_size - 40, height - qr_size - 40)
qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
certificate.paste(qr_img, qr_position, qr_img)

# -- Seal with hidden texts --
seal_diameter = 160
seal = Image.new("RGBA", (seal_diameter, seal_diameter), (255,255,255,0))
seal_draw = ImageDraw.Draw(seal)
center = seal_diameter // 2

# Outer and inner rings
seal_draw.ellipse([(5,5), (seal_diameter-5, seal_diameter-5)], outline=(0,51,102,255), width=8)
seal_draw.ellipse([(20,20), (seal_diameter-20, seal_diameter-20)], outline=(0,102,204,255), width=3)

# Radial lines
num_rays = 24
for i in range(num_rays):
    angle = (360 / num_rays) * i
    sx = center + int((seal_diameter//2 - 20) * math.cos(math.radians(angle)))
    sy = center + int((seal_diameter//2 - 20) * math.sin(math.radians(angle)))
    ex = center + int((seal_diameter//2 - 5) * math.cos(math.radians(angle)))
    ey = center + int((seal_diameter//2 - 5) * math.sin(math.radians(angle)))
    seal_draw.line([(sx, sy), (ex, ey)], fill=(0,51,102,180), width=2)

# Hidden secret texts in very small font around circle (like watermark)
hidden_texts = [
    "CONFIDENTIAL", "AUTHORIZED", "OFFICIAL USE ONLY",
    "SERIAL#:" + certificate_id[-6:],
    "DIGITAL SIGNATURE VERIFIED",
    "OPENAI SECURE SEAL",
    "AUTHORIZED PERSONNEL ONLY",
    "SECURE TRANSACTION",
    "DO NOT COPY", "VALIDATED", "REGISTERED",
]

hidden_font = font_small
radius_hidden = seal_diameter//2 - 12
num_hidden = len(hidden_texts)
angle_start = 0

for i, txt in enumerate(hidden_texts):
    angle = angle_start + (360 / num_hidden) * i
    x = center + int(radius_hidden * math.cos(math.radians(angle)))
    y = center + int(radius_hidden * math.sin(math.radians(angle)))
    # بسیار ریز و کم‌رنگ
    seal_draw.text((x-15, y-7), txt, font=hidden_font, fill=(0,0,0,40))

# Center text
center_text = "Official Seal"
bbox = seal_draw.textbbox((0,0), center_text, font=font_small)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
seal_draw.text(((seal_diameter - w)//2, seal_diameter - h - 15), center_text, font=font_small, fill=(0,51,102,200))

# Paste seal on top right corner
certificate.paste(seal, (width - seal_diameter - 40, 40), seal)

# Save final image
certificate.save("openai_certificate_with_hidden_texts.png")
print("✅ Certificate image created with hidden seal texts: openai_certificate_with_hidden_texts.png")
