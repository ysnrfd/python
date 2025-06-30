from PIL import Image, ExifTags
from collections import Counter
import os

def extract_image_info(image_path):
    if not os.path.exists(image_path):
        print("فایل وجود ندارد!")
        return

    with Image.open(image_path) as img:
        print("======== اطلاعات کلی ========")
        print(f"فرمت: {img.format}")
        print(f"ابعاد: {img.size} (عرض × ارتفاع)")
        print(f"مود رنگی: {img.mode}")
        print(f"اطلاعات DPI: {img.info.get('dpi', 'نامشخص')}")
        print(f"دارای Alpha channel: {'A' in img.mode}")
        print(f"اطلاعات دیگر: {img.info}")

        print("\n======== رنگ غالب و میانگین ========")
        img_rgb = img.convert('RGB')
        pixels = list(img_rgb.getdata())
        most_common = Counter(pixels).most_common(1)[0][0]
        average_color = tuple(sum(x) // len(x) for x in zip(*pixels))
        print(f"رنگ غالب: {most_common}")
        print(f"میانگین رنگ: {average_color}")

        print("\n======== هیستوگرام رنگی ========")
        hist = img.histogram()
        print(f"تعداد مقادیر هیستوگرام: {len(hist)}")

        print("\n======== اطلاعات EXIF ========")
        try:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    print(f"{tag_name}: {value}")
            else:
                print("هیچ اطلاعات EXIF وجود ندارد.")
        except Exception as e:
            print(f"خطا در خواندن EXIF: {e}")

# ======= اجرا =======
path = "0002.png"  # مسیر تصویر خود را اینجا وارد کنید
extract_image_info(path)
