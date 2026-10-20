"""Rebuild the site portraits from the two source photographs.

  portrait-office.webp   consulting-room photo (1360x908)        -> hero column
  portrait-outdoor.webp  garden portrait (1360x908, landscape)    -> pinned reveal band
  portrait-formal.webp   studio portrait (680x1020, 2:3)          -> About crop

Each source is used exactly once, so no photograph repeats on the page.

Each crop is saved in natural colour (a very light grade only: a touch of
contrast, colours left true). There is deliberately no black-and-white or
duotone treatment.

The sources are modest in size, so everything is LANCZOS-upscaled and lightly
unsharp-masked; the duotone is what makes that softness read as film rather
than as a low-resolution image.

Run:  python tools/process-portraits.py        (requires Pillow + numpy)
"""

import pathlib

import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/img/_source"
OUT = ROOT / "assets/img"

SOURCES = {
    "office":  Image.open(SRC / "portrait-office.webp").convert("RGB"),
    "formal":  Image.open(SRC / "portrait-formal.webp").convert("RGB"),
    "outdoor": Image.open(SRC / "portrait-outdoor.webp").convert("RGB"),
}



def arr(im):
    return np.asarray(im).astype(np.float32) / 255.0


def img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def color(a, sat=0.97):
    """Natural colour: a hair of contrast, colours kept true."""
    l = lum(a)[..., None]
    a = a * sat + l * (1 - sat)
    return np.clip((a - 0.5) * 1.04 + 0.5, 0, 1)


CROPS = {   # name: (source, box in source pixels, output size)
    "hero":  ("office",  (320, 60, 860, 870),    (858, 1287)),   # 2:3 tall — hero column
    "wide":  ("outdoor", (300, 0, 1360, 908),   (1152, 987)),   # editorial band — pinned reveal
    "close": ("formal",  (0, 10, 680, 803),     (816, 952)),    # head and shoulders — about
}

if __name__ == "__main__":
    for name, (src, box, size) in CROPS.items():
        crop = SOURCES[src].crop(box).resize(size, Image.LANCZOS)
        crop = crop.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=3))
        a = arr(crop)
        out = img(color(a))
        path = OUT / f"portrait-{name}-col.webp"
        out.save(path, "WEBP", quality=88, method=6)
        print(f"{path.name:26s} {out.size[0]}x{out.size[1]}")
