from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import hashlib
import random
import math
import os
import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# تنظیمات
CERT_WIDTH, CERT_HEIGHT = 900, 650
MARGIN = 30
BACKGROUND_COLOR = (255, 255, 250)
TITLE_COLOR = (20, 20, 20)
TEXT_COLOR = (40, 40, 40)
WATERMARK_COLOR = (60, 60, 60, 25)
NOISE_INTENSITY = 10000

# اطلاعات گواهی
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

# ساخت کلیدهای RSA
def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

# ذخیره کلیدها
def save_rsa_keys(private_key, public_key):
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# بارگذاری فونت ساده (می‌توان پیشرفته‌تر کرد)
def load_font(name, size):
    paths = [
        name,
        os.path.join("/usr/share/fonts/truetype/dejavu/", name),
        os.path.join("/Library/Fonts/", name),
        os.path.join("C:/Windows/Fonts/", name)
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

font_title = load_font("timesbd.ttf", 36)
font_text = load_font("times.ttf", 18)
font_small = load_font("times.ttf", 14)

# ساخت گرادیانت پس‌زمینه
def draw_gradient(draw, width, height, start_color, end_color):
    for i in range(height):
        r = int(start_color[0] + (float(i) / height) * (end_color[0] - start_color[0]))
        g = int(start_color[1] + (float(i) / height) * (end_color[1] - start_color[1]))
        b = int(start_color[2] + (float(i) / height) * (end_color[2] - start_color[2]))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

# ساخت QR code
def create_qr_code(data, size=180):
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#003366", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    return qr_img

def encode_message_in_pixels(img, message):
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    pixels = img.load()
    width, height = img.size
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx >= len(binary_message):
                return
            r, g, b, a = pixels[x, y]
            r = (r & ~1) | int(binary_message[idx])
            pixels[x, y] = (r, g, b, a)
            idx += 1

def main():
    private_key, public_key = generate_rsa_keys()
    save_rsa_keys(private_key, public_key)

    # داده‌های برای امضا
    data_string = "\n".join(f"{k}: {v}" for k, v in cert_info.items()).encode('utf-8')

    digital_signature_bytes = private_key.sign(
        data_string,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    digital_signature = base64.b64encode(digital_signature_bytes).decode('utf-8')
    verification_code = f"VER-{hashlib.sha256(data_string).hexdigest()[:8].upper()}-{cert_info['Certificate ID'][-4:]}"

    qr_img = create_qr_code(digital_signature, size=180)

    certificate = Image.new("RGBA", (CERT_WIDTH, CERT_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(certificate)
    draw_gradient(draw, CERT_WIDTH, CERT_HEIGHT, (255, 255, 250), (220, 230, 255))

    title_text = "OpenAI – Certificate of Membership"
    w, h = draw.textsize(title_text, font=font_title)
    draw.text(((CERT_WIDTH - w) / 2, MARGIN + 10), title_text, fill=TITLE_COLOR, font=font_title)

    info_x, info_y = MARGIN + 30, MARGIN + 70
    line_spacing = 36
    for key, val in cert_info.items():
        text_line = f"{key}: {val}"
        draw.text((info_x, info_y), text_line, font=font_text, fill=TEXT_COLOR)
        info_y += line_spacing

    verification_label = "Verification Code:"
    draw.text((info_x, info_y + 20), verification_label, font=font_text, fill=TEXT_COLOR)
    draw.text((info_x + 190, info_y + 20), verification_code, font=font_text, fill=(0, 70, 120))

    sig_lines = [digital_signature[i:i+60] for i in range(0, len(digital_signature), 60)]
    sig_y = info_y + 60
    for line in sig_lines:
        draw.text((info_x, sig_y), line, font=font_small, fill=(100, 100, 120))
        sig_y += 20

    qr_pos = (CERT_WIDTH - qr_img.width - MARGIN - 20, CERT_HEIGHT - qr_img.height - MARGIN - 20)
    certificate.paste(qr_img, qr_pos, qr_img)

    # درج پیام مخفی استگانوگرافی (CertificateID و VerificationCode)
    hidden_message = f"CertificateID:{cert_info['Certificate ID']};VerificationCode:{verification_code}"
    encode_message_in_pixels(certificate, hidden_message)

    output_file = "openai_certificate_yasin_realistic2.png"
    certificate.convert("RGB").save(output_file, quality=95)
    print(f"✅ Certificate created and saved as: {output_file}")

if __name__ == "__main__":
    main()
