from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import qrcode
import hashlib
import random
import math
import os

# ======== تنظیمات قابل تغییر ========
CERT_WIDTH, CERT_HEIGHT = 900, 550
MARGIN = 30
BACKGROUND_COLOR = (255, 255, 250)
BORDER_COLOR = (60, 60, 60)
TITLE_COLOR = (20, 20, 20)
TEXT_COLOR = (40, 40, 40)
WATERMARK_COLOR = (60, 60, 60, 25)  # با آلفای کم
NOISE_INTENSITY = 1200  # تعداد پیکسل نویز

# ======== اطلاعات گواهی ========
cert_info = {
    "Name": "Yasin",
    "User ID": "YSNRFD",
    "Membership Date": "April 1, 2023",
    "Issued Date": "June 28, 2025",
    "Certificate ID": "OPENAI-YSN-APR2023-CERT1001",
    "Signed By": "ChatGPT-4o",
    "Model ID": "GPT4O-REP-TRUST-2025",
    "Issuer": "OpenAI, Inc."
}

# ======== تابع بارگذاری فونت پویا با fallback ========
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
    # فونت پیش‌فرض PIL
    return ImageFont.load_default()

# فونت‌ها
font_title = load_font("arialbd.ttf", 36)
font_header = load_font("arialbd.ttf", 20)
font_text = load_font("arial.ttf", 18)
font_small = load_font("arial.ttf", 14)

# ======== تولید رشته داده برای امضا دیجیتال ========
data_string = "\n".join(f"{k}: {v}" for k, v in cert_info.items())
digital_signature = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
verification_code = f"VER-{digital_signature[:8].upper()}-{cert_info['Certificate ID'][-4:]}"

# ======== ایجاد QR code به صورت با کیفیت و رنگ سفارشی ========
def create_qr_code(data, size=180):
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#003366", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    return qr_img

qr_img = create_qr_code(digital_signature, size=180)

# ======== طراحی پس‌زمینه با گرادیانت ملایم ========
def draw_gradient(draw, width, height, start_color, end_color):
    for i in range(height):
        r = int(start_color[0] + (float(i) / height) * (end_color[0] - start_color[0]))
        g = int(start_color[1] + (float(i) / height) * (end_color[1] - start_color[1]))
        b = int(start_color[2] + (float(i) / height) * (end_color[2] - start_color[2]))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

# ======== رسم مهر رسمی با افکت سه‌بعدی ========
def create_official_seal(diameter=160):
    seal = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(seal)
    center = diameter // 2

    # حلقه بیرونی با گرادیانت شعاعی
    for i in range(8):
        alpha = int(255 * (1 - i/8))
        radius = center - i*6
        draw.ellipse(
            [(center - radius, center - radius), (center + radius, center + radius)],
            outline=(0, 51, 102, alpha),
            width=3
        )

    # خطوط شعاعی تزئینی
    num_rays = 28
    outer_r = center - 15
    inner_r = center - 45
    for i in range(num_rays):
        angle = 360 / num_rays * i
        x1 = center + int(inner_r * math.cos(math.radians(angle)))
        y1 = center + int(inner_r * math.sin(math.radians(angle)))
        x2 = center + int(outer_r * math.cos(math.radians(angle)))
        y2 = center + int(outer_r * math.sin(math.radians(angle)))
        draw.line([(x1, y1), (x2, y2)], fill=(0, 51, 102, 180), width=2)

    # قرار دادن لوگوی openai_seal.png در وسط مهر
    try:
        logo = Image.open("openai_seal.png").convert("RGBA")
        max_logo_size = diameter - 90  # حدود 70x70 یا کمی بزرگ‌تر
        logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
        logo_pos = (center - logo.width // 2, center - logo.height // 2)
        seal.paste(logo, logo_pos, logo)
    except FileNotFoundError:
        print("⚠️ فایل openai_seal.png پیدا نشد! مهر بدون لوگو ساخته شد.")

    # متن مهر دایره‌ای
    seal_text = "OFFICIAL OPENAI SEAL"
    font_circle = load_font("arialbd.ttf", 16)
    radius_text = center - 12

    for i, char in enumerate(seal_text):
        angle_deg = (360 / len(seal_text)) * i - 90
        angle_rad = math.radians(angle_deg)
        x = center + int(radius_text * math.cos(angle_rad))
        y = center + int(radius_text * math.sin(angle_rad))
        draw.text((x-8, y-8), char, font=font_circle, fill=(0, 51, 102, 220))

    # سایه ملایم برای زیبایی
    seal = seal.filter(ImageFilter.GaussianBlur(radius=0.5))

    return seal

official_seal = create_official_seal()

# ======== ایجاد تصویر گواهی ========
certificate = Image.new("RGBA", (CERT_WIDTH, CERT_HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(certificate)

# گرادیانت پس زمینه ملایم
draw_gradient(draw, CERT_WIDTH, CERT_HEIGHT, (255, 255, 250), (230, 240, 255))

# قاب حاشیه‌ای چند لایه
for i, thickness in enumerate([6, 4, 2]):
    color_val = 80 - i * 20
    draw.rectangle(
        [MARGIN - i*2, MARGIN - i*2, CERT_WIDTH - MARGIN + i*2, CERT_HEIGHT - MARGIN + i*2],
        outline=(color_val, color_val, color_val)
    )

# عنوان اصلی
title_text = "OpenAI – Certificate of Membership"
bbox = draw.textbbox((0, 0), title_text, font=font_title)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
draw.text(((CERT_WIDTH - w) / 2, MARGIN + 10), title_text, fill=TITLE_COLOR, font=font_title)

# خط جداکننده زیبا
line_y = MARGIN + h + 30
draw.line([(MARGIN + 10, line_y), (CERT_WIDTH - MARGIN - 10, line_y)], fill=(100, 100, 120), width=3)

# نوشتن اطلاعات گواهی
info_x = MARGIN + 30
info_y = line_y + 20
line_spacing = 36

for key, val in cert_info.items():
    text_line = f"{key}: {val}"
    draw.text((info_x, info_y), text_line, font=font_text, fill=TEXT_COLOR)
    info_y += line_spacing

# کد تایید اعتبار
verification_label = "Verification Code:"
verification_text = verification_code
info_y += 20
draw.text((info_x, info_y), verification_label, font=font_header, fill=TEXT_COLOR)
draw.text((info_x + 190, info_y), verification_text, font=font_header, fill=(0, 70, 120))

# متن امضای دیجیتال (شکسته به دو خط)
sig_half = len(digital_signature) // 2
sig_1 = digital_signature[:sig_half]
sig_2 = digital_signature[sig_half:]
draw.text((info_x, info_y + 40), sig_1, font=font_small, fill=(100, 100, 120))
draw.text((info_x, info_y + 60), sig_2, font=font_small, fill=(100, 100, 120))

# قرار دادن QR Code در پایین سمت راست
qr_pos = (CERT_WIDTH - qr_img.width - MARGIN - 20, CERT_HEIGHT - qr_img.height - MARGIN - 20)

# قرار دادن مهر رسمی بالای QR Code
seal_pos = (qr_pos[0], qr_pos[1] - official_seal.height - 15)  # 15 پیکسل فاصله بالاتر

certificate.paste(official_seal, seal_pos, official_seal)
certificate.paste(qr_img, qr_pos, qr_img)

# ======== متن‌های واترمارک عجیب‌تر و معتبرتر ========
watermarks = [
    "AUTHORIZED", "CONFIDENTIAL", "OFFICIAL_USE_ONLY", "SECURE",
    "AUTHENTICATED", "NON-TRANSFERABLE", "GOVERNMENT APPROVED", "VERIFIED BY BLOCKCHAIN",
    "HIGHLY CONFIDENTIAL", "DIGITAL SIGNED", "SECURE DOCUMENT", "UNIQUE IDENTIFIER",
    "ENCRYPTED SEAL",
    cert_info["Certificate ID"], digital_signature[:16], verification_code,
    "VALIDATED", "NO_COPY", "OPENAI"
]

# ======== اضافه کردن واترمارک نامرئی با فونت کوچک و زاویه تصادفی ========
for _ in range(80):  # تعداد را کمی بیشتر کردم
    wm_text = random.choice(watermarks)
    txt_img = Image.new("RGBA", (220, 20), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((0, 0), wm_text, font=font_small, fill=WATERMARK_COLOR)
    angle = random.uniform(-25, 25)
    txt_img = txt_img.rotate(angle, expand=1)

    # موقعیت تصادفی اما دور از لبه‌ها
    x = random.randint(MARGIN + 10, CERT_WIDTH - 230)
    y = random.randint(MARGIN + 10, CERT_HEIGHT - 30)
    certificate.paste(txt_img, (x, y), txt_img)

# ======== اضافه کردن نویز پیکسلی برای ضد جعل ========
pixels = certificate.load()
for _ in range(NOISE_INTENSITY):
    px = random.randint(0, CERT_WIDTH - 1)
    py = random.randint(0, CERT_HEIGHT - 1)
    r, g, b, a = pixels[px, py]
    noise = random.randint(-5, 5)
    r = max(0, min(255, r + noise))
    g = max(0, min(255, g + noise))
    b = max(0, min(255, b + noise))
    pixels[px, py] = (r, g, b, a)

# ======== ذخیره فایل نهایی ========
output_file = "openai_certificate_yasin_professional.png"
certificate.convert("RGB").save(output_file, quality=95)
print(f"✅ Professional certificate created: {output_file}")
