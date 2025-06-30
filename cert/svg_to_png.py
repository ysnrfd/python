import cairosvg
from PIL import Image

# تبدیل svg به png موقت
cairosvg.svg2png(url="openai_seal.svg", write_to="openai_seal.png")

# بارگذاری png تبدیل شده
logo = Image.open("openai_seal.png").convert("RGBA")

# حالا مثل قبل از لوگو استفاده کن
