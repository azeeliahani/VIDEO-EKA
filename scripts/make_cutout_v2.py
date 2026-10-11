"""Prepares the pointing EKA (already transparent) for animation.

Outputs (assets/):
  eka2_full.png - whole robot, cropped
  eka2_body.png - robot without the pointing forearm
  eka2_arm.png  - pointing forearm + hand only (same canvas), rotated around the elbow
Prints the elbow pivot, eye and mouth boxes in cropped-canvas pixels for src/hub_v2.html.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
im = np.asarray(Image.open(ROOT / "assets/source/eka_pointing_original.webp").convert("RGBA")).astype(np.float32)
# The source alpha sits around 252; make the body fully opaque but keep the soft edge.
a = im[..., 3]
im[..., 3] = np.clip((a - 8) * 255 / 236, 0, 255)

ys, xs = np.where(im[..., 3] > 8)
pad = 20
box = (xs.min() - pad, ys.min() - pad, xs.max() + pad, ys.max() + pad)
full = Image.fromarray(im.clip(0, 255).astype(np.uint8), "RGBA").crop(box)
ox, oy = box[0], box[1]

arm_poly = [(705, 690), (740, 652), (753, 645), (756, 598), (800, 590), (830, 660), (850, 675), (885, 750), (895, 830),
            (880, 885), (840, 915), (770, 925), (725, 900), (712, 830), (705, 760)]
m = Image.new("L", full.size, 0)
ImageDraw.Draw(m).polygon([(x - ox, y - oy) for x, y in arm_poly], fill=255)
mm = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
fa = np.asarray(full).astype(np.float32)
arm = fa.copy(); arm[..., 3] *= mm
body = fa.copy(); body[..., 3] *= 1 - mm

out = ROOT / "assets"
full.save(out / "eka2_full.png")
Image.fromarray(arm.astype(np.uint8), "RGBA").save(out / "eka2_arm.png")
Image.fromarray(body.astype(np.uint8), "RGBA").save(out / "eka2_body.png")
print("size", full.size)
print("elbow pivot", 740 - ox, 880 - oy)
for name, (x0, y0, x1, y1) in {"eyeL": (200, 360, 372, 550), "eyeR": (495, 305, 690, 520), "mouth": (378, 550, 502, 585)}.items():
    print(name, x0 - ox, y0 - oy, x1 - x0, y1 - y0)
