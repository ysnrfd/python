from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import qrcode
import hashlib
import random
import math
import os
import base64
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

# ======== Enhanced Configurations ========
CERT_WIDTH, CERT_HEIGHT = 1200, 900
MARGIN = 40
BACKGROUND_COLOR = (248, 246, 240)
BORDER_COLOR = (30, 30, 30)
TITLE_COLOR = (15, 15, 15)
TEXT_COLOR = (35, 35, 35)
WATERMARK_COLOR = (40, 40, 40, 20)
NOISE_INTENSITY = 4500
PAPER_TEXTURE_OPACITY = 0.15
HOLOGRAM_OPACITY = 0.35

# ======== Certificate Information ========
cert_info = {
    "Name": "Yasin",
    "Last Name": "Aryanfard",
    "User ID": "YSNRFD",
    "Membership Date": "April 1, 2023",
    "Issued Date": datetime.datetime.now().strftime("%B %d, %Y"),
    "Certificate ID": f"OPENAI-YSN-APR2023-CERT{random.randint(10000, 99999)}",
    "Signed By": "ChatGPT-4o",
    "Model ID": "GPT4O-REP-TRUST-2025",
    "Issuer": "OpenAI, Inc."
}

# ======== RSA Key Generation ========
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Save public key for verification
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open('certificate_public_key.pem', 'wb') as f:
        f.write(pem)
        
    return private_key, public_key

private_key, public_key = generate_rsa_keys()

# ======== Enhanced Font Loading ========
def load_font(name, size):
    fallback_fonts = [
        "arialbd.ttf", "timesbd.ttf", "courbd.ttf", 
        "DejaVuSans-Bold.ttf", "Georgia Bold.ttf"
    ]
    for font_name in [name] + fallback_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            continue
    return ImageFont.load_default(size=size)

font_title = load_font("georgiaz.ttf", 42)
font_header = load_font("georgiab.ttf", 24)
font_text = load_font("georgia.ttf", 20)
font_small = load_font("cour.ttf", 16)
font_signature = load_font("BrushScriptStd.otf", 28)

# ======== Digital Signature Generation ========
data_string = "\n".join(f"{k}: {v}" for k, v in cert_info.items()).encode('utf-8')

signature = private_key.sign(
    data_string,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA512()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA512()
)

digital_signature = base64.b64encode(signature).decode('utf-8')
verification_code = f"VER-{hashlib.sha3_256(data_string).hexdigest()[:10].upper()}"

# ======== QR Code Generation ========
def create_qr_code(data, size=220):
    qr = qrcode.QRCode(
        version=7,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(
        fill_color="#002855", 
        back_color="#F8F6F0"
    ).convert("RGBA")
    
    # Add holographic effect
    hologram = Image.new("RGBA", qr_img.size)
    holo_draw = ImageDraw.Draw(hologram)
    for i in range(0, qr_img.width, 5):
        alpha = int(255 * (0.3 + 0.7 * abs(math.sin(i/50))))
        holo_draw.line([(i, 0), (i, qr_img.height)], 
                      fill=(100, 200, 255, alpha), width=3)
    
    return Image.alpha_composite(qr_img, hologram)

qr_img = create_qr_code(f"{digital_signature}|{verification_code}")

# ======== Background Design ========
def create_certificate_base():
    # Base with gradient
    base = Image.new("RGB", (CERT_WIDTH, CERT_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(base)
    
    # Draw subtle grid
    for i in range(0, CERT_WIDTH, 40):
        alpha = 15 if i % 120 == 0 else 8
        draw.line([(i, 0), (i, CERT_HEIGHT)], fill=(200, 200, 200, alpha), width=1)
    for i in range(0, CERT_HEIGHT, 40):
        alpha = 15 if i % 120 == 0 else 8
        draw.line([(0, i), (CERT_WIDTH, i)], fill=(200, 200, 200, alpha), width=1)
    
    # Add paper texture
    texture = Image.new("RGBA", (CERT_WIDTH, CERT_HEIGHT), (0, 0, 0, 0))
    tex_draw = ImageDraw.Draw(texture)
    for _ in range(15000):
        x, y = random.randint(0, CERT_WIDTH), random.randint(0, CERT_HEIGHT)
        alpha = random.randint(10, 25)
        size = random.randint(1, 3)
        tex_draw.ellipse([(x, y), (x+size, y+size)], 
                        fill=(150, 150, 150, alpha))
    
    return Image.alpha_composite(base.convert("RGBA"), texture).convert("RGB")

# ======== Official Seal with OpenAI Logo ========
def create_official_seal(diameter=200):
    seal = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(seal)
    center = diameter // 2
    
    # Complex seal pattern
    for i in range(1, 15):
        alpha = int(255 * (1 - i/15))
        radius = center - i*3
        color = (0, 48, 92, alpha)
        draw.ellipse(
            [(center - radius, center - radius), 
             (center + radius, center + radius)],
            outline=color,
            width=2
        )
    
    # Ornate details
    num_points = 24
    for i in range(num_points):
        angle = math.radians(i * 360/num_points)
        x1 = center + int((diameter*0.42) * math.cos(angle))
        y1 = center + int((diameter*0.42) * math.sin(angle))
        x2 = center + int((diameter*0.47) * math.cos(angle))
        y2 = center + int((diameter*0.47) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=(0, 48, 92, 220), width=3)
    
    # Add holographic effect
    for i in range(0, diameter, 4):
        alpha = int(180 * (0.4 + 0.6 * abs(math.sin(i/20))))
        draw.arc(
            [(i//4, i//4), (diameter-i//4, diameter-i//4)],
            start=0,
            end=360,
            fill=(100, 200, 255, alpha),
            width=2
        )
    
    # Seal text
    text = "OFFICIAL SEAL • VERIFIED • DIGITAL"
    font_seal = load_font("timesbd.ttf", 14)
    for i, char in enumerate(text):
        angle = math.radians(i * 360/len(text) - 90)
        x = center + int(center*0.65 * math.cos(angle)) - 5
        y = center + int(center*0.65 * math.sin(angle)) - 5
        draw.text((x, y), char, font=font_seal, fill=(0, 48, 92, 255))
    
    # Add OpenAI logo to center of seal
    try:
        logo = Image.open("openai_seal.png").convert("RGBA")
        logo_size = diameter // 2  # Size relative to seal diameter
        logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
        logo_pos = (center - logo.width // 2, center - logo.height // 2)
        
        # Create glow effect around logo
        glow = Image.new("RGBA", (logo.width+10, logo.height+10), (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse([(0,0), (logo.width+10, logo.height+10)], 
                         fill=(100, 200, 255, 60))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Paste glow then logo
        seal.paste(glow, (logo_pos[0]-5, logo_pos[1]-5), glow)
        seal.paste(logo, logo_pos, logo)
    except Exception as e:
        print(f"⚠️ Could not load openai_seal.png: {e}")
        # Draw simple OpenAI-inspired logo as fallback
        draw.regular_polygon((center, center, diameter//4), 
                            n_sides=6, 
                            fill=(0, 48, 92, 180))
    
    return seal

# ======== Main Certificate Creation ========
certificate = create_certificate_base().convert("RGBA")
draw = ImageDraw.Draw(certificate)

# Border design
for i, thickness in enumerate([8, 5, 3, 1]):
    offset = MARGIN - i*3
    draw.rectangle(
        [offset, offset, CERT_WIDTH - offset, CERT_HEIGHT - offset],
        outline=(30, 30, 30),
        width=thickness
    )

# Title section
title = "CERTIFICATE OF AUTHENTICITY"
bbox = draw.textbbox((0, 0), title, font=font_title)
draw.text(
    ((CERT_WIDTH - bbox[2])/2, MARGIN + 30), 
    title, 
    fill=TITLE_COLOR, 
    font=font_title
)

subtitle = "Issued by OpenAI for Distinguished Contribution"
font_subtitle = load_font("georgiai.ttf", 22)
bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
draw.text(
    ((CERT_WIDTH - bbox[2])/2, MARGIN + 90), 
    subtitle, 
    fill=(70, 70, 70), 
    font=font_subtitle
)

# Decorative elements
draw.line(
    [(MARGIN+50, MARGIN+150), (CERT_WIDTH-MARGIN-50, MARGIN+150)], 
    fill=(150, 150, 150), 
    width=2
)

# Certificate information
info_y = MARGIN + 180
for key, value in cert_info.items():
    draw.text(
        (MARGIN+80, info_y), 
        f"{key}:", 
        font=font_header, 
        fill=(80, 80, 80))
    draw.text(
        (MARGIN+300, info_y), 
        value, 
        font=font_text, 
        fill=TEXT_COLOR)
    info_y += 50

# Security section
info_y += 30
draw.text(
    (MARGIN+80, info_y), 
    "Digital Verification:", 
    font=font_header, 
    fill=(80, 80, 80))
draw.text(
    (MARGIN+300, info_y), 
    verification_code, 
    font=font_text, 
    fill=(0, 70, 120))
info_y += 40

# Digital signature block
sig_text = "Cryptographic Signature:"
draw.text((MARGIN+80, info_y), sig_text, font=font_small, fill=(100, 100, 100))
info_y += 25
signature_lines = [digital_signature[i:i+64] for i in range(0, len(digital_signature), 64)]
for line in signature_lines[:4]:
    draw.text((MARGIN+100, info_y), line, font=font_small, fill=(70, 70, 70))
    info_y += 22

# Official elements with OpenAI logo
seal = create_official_seal()
certificate.paste(
    seal, 
    (CERT_WIDTH - MARGIN - seal.width - 50, MARGIN + 180), 
    seal
)

qr_position = (CERT_WIDTH - MARGIN - qr_img.width, CERT_HEIGHT - MARGIN - qr_img.height - 50)
certificate.paste(qr_img, qr_position, qr_img)

# Signature area
signature_y = CERT_HEIGHT - MARGIN - 150
draw.line(
    [(MARGIN+100, signature_y), (MARGIN+400, signature_y)], 
    fill=(30, 30, 30), 
    width=2
)
draw.text(
    (MARGIN+100, signature_y + 10), 
    "Dr. Sam Altman, Chief Executive Officer", 
    font=font_small, 
    fill=(60, 60, 60))
draw.text(
    (MARGIN+100, signature_y - 40), 
    "Authorized Signature", 
    font=font_signature, 
    fill=(30, 30, 30))

# Security watermarks
watermarks = [
    "SECURE DOCUMENT", "OFFICIAL RECORD", "DO NOT DUPLICATE", 
    "VERIFIED", cert_info['Certificate ID'], verification_code,
    "PROTECTED CONTENT", "DIGITALLY SIGNED", "OPENAI AUTHENTICATED"
]

for _ in range(150):
    wm_text = random.choice(watermarks)
    txt_img = Image.new("RGBA", (400, 40), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    
    alpha = random.randint(15, 30)
    txt_draw.text(
        (10, 10), 
        wm_text, 
        font=font_small, 
        fill=(40, 40, 40, alpha))
    
    angle = random.uniform(-45, 45)
    txt_img = txt_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    
    x = random.randint(0, CERT_WIDTH - txt_img.width)
    y = random.randint(0, CERT_HEIGHT - txt_img.height)
    certificate.paste(txt_img, (x, y), txt_img)

# Final touches
certificate = certificate.filter(ImageFilter.SMOOTH)
certificate = certificate.filter(ImageFilter.SHARPEN)

# Save certificate
output_filename = f"OpenAI_Certificate_{cert_info['Certificate ID']}.png"
certificate.save(output_filename, dpi=(300, 300), quality=100)
print(f"✅ Professional certificate created: {output_filename}")
print(f"🔑 Public key saved to: certificate_public_key.pem")