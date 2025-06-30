from PIL import Image, ImageDraw, ImageFont
import math

from PIL import Image, ImageDraw, ImageFont
import math
import qrcode
from PIL import Image, ImageDraw, ImageFont
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

# Draw a professional OpenAI seal
seal_diameter = 140
seal = Image.new("RGBA", (seal_diameter, seal_diameter), (255, 255, 255, 0))
seal_draw = ImageDraw.Draw(seal)

# Simple radial gradient circle for seal
for i in range(seal_diameter//2, 0, -1):
    color_val = 40 + int((seal_diameter//2 - i) * 1.5)
    color = (color_val, color_val, color_val, 255)
    seal_draw.ellipse(
        [seal_diameter//2 - i, seal_diameter//2 - i, seal_diameter//2 + i, seal_diameter//2 + i],
        fill=color
    )

# Seal text with shadow
# Seal text with shadow
text = "OpenAI"
bbox = seal_draw.textbbox((0, 0), text, font=font_header)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
text_pos = ((seal_diameter - w)//2, (seal_diameter - h)//2)

# سایه
seal_draw.text((text_pos[0]+2, text_pos[1]+2), text, font=font_header, fill=(20, 20, 20, 255))
# متن اصلی
seal_draw.text(text_pos, text, font=font_header, fill=(240, 240, 240, 255))


# Paste seal on top right
certificate.paste(seal, (width - seal_diameter - 40, 40), seal)

# Save certificate image
certificate.save("openai_certificate_yasin_en_2.png")
print("✅ Certificate image created: openai_certificate_yasin_en.png")


# Draw a professional OpenAI seal (more realistic)
seal_diameter = 160
seal = Image.new("RGBA", (seal_diameter, seal_diameter), (255, 255, 255, 0))
seal_draw = ImageDraw.Draw(seal)

center = seal_diameter // 2

# Outer ring (thick)
seal_draw.ellipse(
    [(5, 5), (seal_diameter - 5, seal_diameter - 5)],
    outline=(0, 51, 102, 255), width=8
)

# Inner ring (thin)
seal_draw.ellipse(
    [(20, 20), (seal_diameter - 20, seal_diameter - 20)],
    outline=(0, 102, 204, 255), width=3
)

# Radial lines (like sun rays)
num_rays = 24
for i in range(num_rays):
    angle = (360 / num_rays) * i
    # Calculate start and end points of each ray
    start_x = center + int( (seal_diameter//2 - 20) * math.cos(math.radians(angle)) )
    start_y = center + int( (seal_diameter//2 - 20) * math.sin(math.radians(angle)) )
    end_x = center + int( (seal_diameter//2 - 5) * math.cos(math.radians(angle)) )
    end_y = center + int( (seal_diameter//2 - 5) * math.sin(math.radians(angle)) )
    seal_draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 51, 102, 180), width=2)

# Text around the circle
import math

seal_text = "OFFICIAL SEAL OF OPENAI"
font_seal = font_header  # از فونت اصلی استفاده کن یا فونت مناسب دیگه
radius_text = seal_diameter // 2 - 30

for i, char in enumerate(seal_text):
    angle = 180 + (i * (360 / len(seal_text)))  # چرخش متن دور دایره
    x = center + int(radius_text * math.cos(math.radians(angle)))
    y = center + int(radius_text * math.sin(math.radians(angle)))
    seal_draw.text((x-7, y-7), char, font=font_seal, fill=(0, 51, 102, 255))

# Center text (Organization Name)
center_text = "OpenAI"
bbox = seal_draw.textbbox((0, 0), center_text, font=font_title)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
seal_draw.text(((seal_diameter - w)//2, (seal_diameter - h)//2), center_text, font=font_title, fill=(0, 51, 102, 255))

# Simulated signature below center text
signature_text = "Digitally Signed"
sig_font = font_small
sig_bbox = seal_draw.textbbox((0,0), signature_text, font=sig_font)
sw = sig_bbox[2] - sig_bbox[0]
sh = sig_bbox[3] - sig_bbox[1]
seal_draw.text(((seal_diameter - sw)//2, (seal_diameter + h)//2 + 5), signature_text, font=sig_font, fill=(0, 51, 102, 180))

# Paste seal on top right
certificate.paste(seal, (width - seal_diameter - 40, 40), seal)


# Load OpenAI logo (transparent PNG)
try:
    logo = Image.open("openai_seal.png").convert("RGBA")
except FileNotFoundError:
    print("⚠️ فایل لوگوی openai_logo.png پیدا نشد! لطفا لوگوی مناسب کنار اسکریپت قرار دهید.")
    logo = None

# Draw a professional OpenAI seal with logo inside
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

# Add logo at center if loaded
if logo:
    # Resize logo to fit inside inner circle
    max_logo_size = seal_diameter - 60
    logo = logo.resize((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
    logo_pos = (center - max_logo_size // 2, center - max_logo_size // 2)
    seal.paste(logo, logo_pos, logo)  # Use logo as mask for transparency

# Optionally add text around seal (like قبلی) یا حذفش کن

# Paste seal on top right
certificate.paste(seal, (width - seal_diameter - 40, 40), seal)
