"""Rebuild the site portraits from the two source photographs.

  portrait-formal.webp   studio portrait (680x1020, exactly 2:3)  -> hero column
  portrait-outdoor.webp  garden portrait (1360x908, landscape)    -> pinned
                                                                     reveal band
                                                                     + about crop

Two graded treatments are produced per crop, at identical dimensions, so the
page can cross-fade between them on scroll:

  *-duo   soft mist/deep-teal duotone. Its highlight point is the page canvas
          (#EDF1EC) exactly, so the portrait dissolves into the background
          instead of sitting in a hard-edged box.
  *-col   a restrained natural grade (gently desaturated, cool shadows).

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
    "formal":  Image.open(SRC / "portrait-formal.webp").convert("RGB"),
    "outdoor": Image.open(SRC / "portrait-outdoor.webp").convert("RGB"),
}

IVORY = np.array([0.929, 0.945, 0.925], np.float32)   # #EDF1EC  page canvas
ESPRS = np.array([0.078, 0.149, 0.165], np.float32)   # #14262A  ink


def arr(im):
    return np.asarray(im).astype(np.float32) / 255.0


def img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def duotone(a, lo=0.04, hi=0.97, gamma=0.94, contrast=1.18):
    l = lum(a)
    l = np.clip((l - lo) / (hi - lo), 0, 1)           # normalise range
    l = np.clip((l - 0.5) * contrast + 0.5, 0, 1)     # contrast
    l = np.power(l, gamma)                            # tonal roll
    l = l[..., None]
    mid = np.array([-0.030, 0.020, 0.018], np.float32) * (4 * l * (1 - l))  # teal midtones
    return ESPRS * (1 - l) + IVORY * l + mid


def color(a, sat=0.80):
    l = lum(a)[..., None]
    a = a * sat + l * (1 - sat)
    tint = (np.array([0.006, 0.012, 0.012], np.float32) * (1 - l)
            + np.array([0.002, 0.006, 0.004], np.float32) * l)
    a = np.clip(a + tint, 0, 1)
    return np.clip((a - 0.5) * 1.10 + 0.5 + 0.004, 0, 1)


CROPS = {   # name: (source, box in source pixels, output size)
    "hero":  ("formal",  (0, 0, 680, 1020),     (858, 1287)),   # 2:3 tall — hero column
    "wide":  ("outdoor", (300, 0, 1360, 908),   (1152, 987)),   # editorial band — pinned reveal
    "close": ("outdoor", (590, 60, 1190, 760),  (816, 952)),    # tighter upper body — about
}

if __name__ == "__main__":
    for name, (src, box, size) in CROPS.items():
        crop = SOURCES[src].crop(box).resize(size, Image.LANCZOS)
        crop = crop.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=3))
        a = arr(crop)
        for mode, fn in (("duo", duotone), ("col", color)):
            out = img(fn(a))
            path = OUT / f"portrait-{name}-{mode}.webp"
            out.save(path, "WEBP", quality=86, method=6)
            print(f"{path.name:26s} {out.size[0]}x{out.size[1]}")
