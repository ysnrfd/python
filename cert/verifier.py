from PIL import Image
import qrcode
import base64
import hashlib
from pyzbar.pyzbar import decode
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# فایل تصویر گواهی
CERT_IMAGE_PATH = "openai_certificate_yasin_realistic.png"

# کلید عمومی PEM
PUBLIC_KEY_PATH = "public_key.pem"

# داده‌های گواهی (باید دقیقا مثل داده‌های اولیه باشه)
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

def extract_qr_signature(image_path):
    img = Image.open(image_path)
    decoded_objs = decode(img)
    for obj in decoded_objs:
        data = obj.data.decode('utf-8')
        if data.startswith("-----"):  # اگر کلید عمومی یا امضای بزرگ باشه
            continue
        return data  # اولین داده QR کد که امضا هست
    return None

def extract_stego_message(img):
    pixels = img.load()
    width, height = img.size
    bits = []
    for y in range(height):
        for x in range(width):
            r, g, b, *rest = pixels[x, y]
            bits.append(str(r & 1))
    # تبدیل بیت‌ها به کاراکترها
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        byte_str = ''.join(byte)
        char = chr(int(byte_str, 2))
        if char == '\x00':  # پایان پیام فرضی
            break
        chars.append(char)
    return ''.join(chars)

def verify_signature(public_key, signature, data):
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def main():
    # بارگذاری تصویر
    img = Image.open(CERT_IMAGE_PATH).convert("RGBA")

    # استخراج امضا از QR
    digital_signature_base64 = extract_qr_signature(CERT_IMAGE_PATH)
    if not digital_signature_base64:
        print("❌ امضا دیجیتال در QR کد یافت نشد!")
        return

    print("📥 امضا دیجیتال استخراج شده از QR کد.")

    # استخراج پیام استگانوگرافی (CertificateID و VerificationCode)
    stego_msg = extract_stego_message(img)
    print(f"📥 پیام مخفی استگانوگرافی: {stego_msg}")

    # بازسازی رشته داده برای امضا (باید دقیقاً مثل زمان ساخت گواهی)
    data_string = "\n".join(f"{k}: {v}" for k, v in cert_info.items()).encode('utf-8')

    # بارگذاری کلید عمومی
    with open(PUBLIC_KEY_PATH, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # تبدیل امضا به بایت
    signature_bytes = base64.b64decode(digital_signature_base64)

    # بررسی امضا
    if verify_signature(public_key, signature_bytes, data_string):
        print("✅ امضا دیجیتال معتبر است.")
    else:
        print("❌ امضا دیجیتال نامعتبر است یا داده‌ها تغییر کرده‌اند!")

    # بررسی کد تأیید در پیام استگانوگرافی
    expected_verification_code = f"VER-{hashlib.sha256(data_string).hexdigest()[:8].upper()}-{cert_info['Certificate ID'][-4:]}"
    if expected_verification_code in stego_msg:
        print("✅ کد تأیید در پیام مخفی استگانوگرافی معتبر است.")
    else:
        print("❌ کد تأیید در پیام مخفی یافت نشد یا اشتباه است!")

if __name__ == "__main__":
    main()
