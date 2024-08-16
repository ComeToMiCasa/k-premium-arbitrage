from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import numpy as np


def create_moire_pattern(size, frequency=20, angle=15):
    x = np.arange(0, size[0])
    y = np.arange(0, size[1])
    X, Y = np.meshgrid(x, y)

    angle_rad = np.radians(angle)
    X_rot = X * np.cos(angle_rad) - Y * np.sin(angle_rad)

    pattern = np.sin(2 * np.pi * X_rot / frequency)
    return ((pattern + 1) * 127.5).astype(np.uint8)


def screen_photo_effect(image_path, output_path):
    # Open the image
    img = Image.open(image_path).convert("RGB")

    # 1. Increase contrast and saturation
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.1)

    # 2. Add screen texture
    texture = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(texture)
    for x in range(0, img.width, 3):
        for y in range(0, img.height, 3):
            draw.point((x, y), fill=(0, 0, 0, 10))
    img = Image.alpha_composite(img.convert("RGBA"), texture).convert("RGB")

    # 3. Add moiré pattern
    moire = create_moire_pattern(img.size, frequency=5)
    moire_img = Image.fromarray(moire, mode="L").convert("RGB")
    img = Image.blend(img, moire_img, 0.05)

    # 4. Add noise (simulating screen and camera noise)
    noise = np.random.normal(0, 2, (img.height, img.width, 3)).astype(np.uint8)
    noise_img = Image.fromarray(noise, mode="RGB")
    img = Image.blend(img, noise_img, 0.05)

    # 5. Add slight fuzziness
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Save the result
    img.save(output_path)


# Usage
screen_photo_effect("input_image.png", "output_image.png")
