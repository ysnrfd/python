import qrcode
import base64
import json
from crypto.Cipher import AES
from crypto.Random import get_random_bytes
from crypto.Protocol.KDF import PBKDF2
from crypto.Util.Padding import pad

# ========== مرحله ۱: اطلاعات یاسین ==========
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
data_json = json.dumps(cert_info).encode("utf-8")

# ========== مرحله ۲: رمزنگاری AES ==========
password = "ysn2025secure"  # رمز عبور دلخواه شما
salt = get_random_bytes(16)
key = PBKDF2(password, salt, dkLen=32, count=100000)  # کلید مشتق‌شده

cipher = AES.new(key, AES.MODE_CBC)
ciphertext = cipher.encrypt(pad(data_json, AES.block_size))

# ترکیب IV، salt و ciphertext برای رمزگشایی بعدی
payload = {
    "salt": base64.b64encode(salt).decode(),
    "iv": base64.b64encode(cipher.iv).decode(),
    "data": base64.b64encode(ciphertext).decode()
}
payload_json = json.dumps(payload)

# ========== مرحله ۳: ساخت QR Code ==========
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q)
qr.add_data(payload_json)
qr.make(fit=True)
img = qr.make_image(fill_color="#001133", back_color="white")
img.save("encrypted_yasin_qrcode.png")

print("✅ QR رمزنگاری‌شده ساخته شد و در فایل 'encrypted_yasin_qrcode.png' ذخیره شد.")
