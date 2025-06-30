import exiftool
import os
import json

def extract_all_metadata(image_path):
    if not os.path.exists(image_path):
        print("❌ فایل وجود ندارد.")
        return

    print(f"\n📂 فایل: {os.path.basename(image_path)}")
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(image_path)
        
        if not metadata:
            print("⛔️ هیچ متادیتایی پیدا نشد.")
            return

        print("\n📑 تمام metadata موجود:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
        
        # ذخیره در فایل JSON (اختیاری)
        json_output = image_path + ".metadata.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        print(f"\n✅ متادیتا در فایل ذخیره شد: {json_output}")

# مسیر عکس را وارد کن (فرمت PNG, JPG, WebP و ...)
image_file = "0002.png"
extract_all_metadata(image_file)
