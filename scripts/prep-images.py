"""Build site/img/ from the illustrations in public/photos/.

Scenes are resized and saved as WebP. The two standing portraits are saved as
transparent cutouts: Nabil's already has an alpha channel, Risha's has a
checkerboard baked into the pixels, which is removed here.

Run from anywhere:  python scripts/prep-images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public" / "photos"
OUT = ROOT / "site" / "img"

SCENE_MAX_WIDTH = 1600
PORTRAIT_MAX_HEIGHT = 1280

# output name -> glob that matches exactly one source file
SCENES = {
    "nsu-walk": "Nabil*Determined Campus Walk.png",
    "nsu-glance": "A Fleeting Courtyard Glance*.png",
    "beach-sunset": "Nabil and Risha at Sunset.png",
    "beach-night": "Moonlit Beach Hand-in-Hand.png",
    "beach-moon": "Moonlit Beach Walk Together.png",
    "cafe": "Cozy Tabaq Coffee Conversation.png",
    "london": "Warm London Night Video Call.png",
    "journeys": "England to Dhaka_ Five Journeys.png",
}

# Scenes that are shown letterboxed on tall phones and need a backdrop.
FILLS = {"beach-sunset", "beach-night", "beach-moon"}

# The baked checkerboard is two neutral greys (about 238 and 254).
BACKDROP_MIN = 226
BACKDROP_CHROMA = 9
# Enclosed pockets of checkerboard (not touching the border) at least this big
# are cleared too.
POCKET_MIN_PIXELS = 500


def source(pattern: str) -> Path:
    matches = sorted(SRC.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"Expected one file for {pattern!r}, found {matches}")
    return matches[0]


def save(image: Image.Image, name: str, quality: int) -> None:
    path = OUT / f"{name}.webp"
    image.save(path, "WEBP", quality=quality, method=6)
    print(f"{path.name:18} {image.size[0]}x{image.size[1]}  {path.stat().st_size // 1024} KB")


def scene(name: str, pattern: str) -> None:
    image = Image.open(source(pattern)).convert("RGB")
    if image.width > SCENE_MAX_WIDTH:
        height = round(image.height * SCENE_MAX_WIDTH / image.width)
        image = image.resize((SCENE_MAX_WIDTH, height), Image.LANCZOS)
    save(image, name, 80)
    if name in FILLS:
        # A tiny blurred copy. Stretched behind the scene on tall phones, it
        # carries the sky and the shore past the picture's edges.
        fill = image.resize((12, 16), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
        save(fill, f"{name}-fill", 70)


def backdrop_mask(image: Image.Image) -> Image.Image:
    """255 where a pixel looks like the checkerboard, 0 elsewhere."""
    mask = Image.new("L", image.size, 0)
    out = mask.load()
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue = pixels[x, y]
            low = min(red, green, blue)
            if low >= BACKDROP_MIN and max(red, green, blue) - low <= BACKDROP_CHROMA:
                out[x, y] = 255
    return mask


def clear_pockets(mask: Image.Image) -> None:
    """Mark enclosed checkerboard pockets (value 255) as background (128)."""
    pixels = mask.load()
    for y in range(0, mask.height, 4):
        for x in range(0, mask.width, 4):
            if pixels[x, y] != 255:
                continue
            ImageDraw.floodfill(mask, (x, y), 200, thresh=0)
            region = mask.point(lambda value: 255 if value == 200 else 0)
            count = region.histogram()[255]
            # A pocket of real checkerboard holds both greys; a white highlight
            # inside the drawing does not, and stays.
            keep = count < POCKET_MIN_PIXELS
            fill = 60 if keep else 128
            ImageDraw.floodfill(mask, (x, y), fill, thresh=0)


def cut_checkerboard(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    mask = backdrop_mask(image)
    # A 1px frame of backdrop joins every border region into one flood fill.
    framed = ImageOps.expand(mask, border=1, fill=255)
    ImageDraw.floodfill(framed, (0, 0), 128, thresh=0)
    mask = framed.crop((1, 1, framed.width - 1, framed.height - 1))
    clear_pockets(mask)
    alpha = mask.point(lambda value: 0 if value == 128 else 255)
    # Pull the edge in by a pixel to drop the pale halo, then feather it.
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.9))
    result = image.convert("RGBA")
    result.putalpha(alpha)
    return result


def clear_fringe(image: Image.Image) -> Image.Image:
    """Drop near-invisible stray pixels so the bounding box is the figure."""
    image = image.convert("RGBA")
    alpha = image.getchannel("A").point(lambda value: 0 if value < 24 else value)
    image.putalpha(alpha)
    return image


def portrait(name: str, image: Image.Image) -> None:
    box = image.getchannel("A").getbbox()
    if box is None:
        raise SystemExit(f"{name}: the cutout has no visible pixels")
    image = image.crop(box)
    if image.height > PORTRAIT_MAX_HEIGHT:
        width = round(image.width * PORTRAIT_MAX_HEIGHT / image.height)
        image = image.resize((width, PORTRAIT_MAX_HEIGHT), Image.LANCZOS)
    save(image, name, 86)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, pattern in SCENES.items():
        scene(name, pattern)
    portrait("risha", cut_checkerboard(Image.open(source("Risha.png"))))
    portrait("nabil", clear_fringe(Image.open(source("Relaxed Cartoon Man in Green Shirt.png"))))


if __name__ == "__main__":
    main()
