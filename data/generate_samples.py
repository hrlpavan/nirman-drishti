"""
Generate sample benchmark images with EXIF GPS metadata for testing Nirman-Drishti.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_sample_images():
    os.makedirs("data/sample_images", exist_ok=True)

    # 1. Unpaved Road (Fraud claim: claim says 100% finished asphalt, image shows gravel)
    img1 = Image.new("RGB", (800, 600), color=(140, 130, 115))
    draw1 = ImageDraw.Draw(img1)
    # Draw gravel texture & stones
    draw1.rectangle([50, 100, 750, 500], fill=(160, 150, 135), outline=(100, 90, 80), width=4)
    for y in range(120, 480, 40):
        draw1.line([(60, y), (740, y + 10)], fill=(120, 110, 100), width=2)
    draw1.text((70, 130), "[SITE PHOTO] PMGSY Road - Chainage 0/0 to 1/8", fill=(20, 20, 20))
    draw1.text((70, 160), "Stage: Compacted Water Bound Macadam (WBM Gravel Base)", fill=(40, 40, 40))
    draw1.text((70, 190), "Status: Surface Dress / Bitumen Wear Layer Missing", fill=(180, 20, 20))
    img1.save("data/sample_images/road_wbm_unpaved.jpg", "JPEG")

    # 2. Solar Pump Verified (Genuine claim: 100% complete)
    img2 = Image.new("RGB", (800, 600), color=(100, 160, 210))
    draw2 = ImageDraw.Draw(img2)
    # Draw ground
    draw2.rectangle([0, 400, 800, 600], fill=(110, 140, 90))
    # Draw solar panels
    draw2.polygon([(200, 200), (380, 140), (460, 240), (280, 310)], fill=(20, 40, 90), outline=(200, 200, 200))
    # Draw pump tank
    draw2.rectangle([520, 220, 660, 420], fill=(180, 180, 190), outline=(60, 60, 60), width=3)
    draw2.text((70, 50), "[SITE PHOTO] Jal Jeevan Mission - PHC Shirwal", fill=(10, 10, 10))
    draw2.text((70, 80), "Equipment: 5HP Solar Submersible Pump & Elevated HDPE Tank", fill=(10, 10, 10))
    draw2.text((70, 110), "Status: Commissioned & Fully Operational", fill=(10, 120, 20))
    img2.save("data/sample_images/solar_pump_verified.jpg", "JPEG")

    # 3. Community Center Frame (Vigilance hold: Plinth/Frame complete, rate issue)
    img3 = Image.new("RGB", (800, 600), color=(180, 200, 220))
    draw3 = ImageDraw.Draw(img3)
    draw3.rectangle([0, 450, 800, 600], fill=(130, 110, 90))
    # Draw concrete frame columns & beams
    for x in (150, 350, 550):
        draw3.rectangle([x, 200, x + 30, 460], fill=(150, 150, 150), outline=(80, 80, 80), width=2)
    draw3.rectangle([140, 200, 590, 230], fill=(160, 160, 160), outline=(80, 80, 80), width=2)
    draw3.text((70, 50), "[SITE PHOTO] MPLADS Community Center Najafgarh", fill=(10, 10, 10))
    draw3.text((70, 80), "Stage: RCC Frame & Column Casting (Milestone 1)", fill=(10, 10, 10))
    img3.save("data/sample_images/building_frame_stage.jpg", "JPEG")

    print("Sample benchmark test images generated in data/sample_images/")


if __name__ == "__main__":
    create_sample_images()
