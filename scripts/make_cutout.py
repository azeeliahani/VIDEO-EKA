"""Cut EKA out of its white background and split the waving arm into its own layer.

Outputs (assets/):
  eka_full.png  - whole robot, transparent background
  eka_body.png  - robot without the raised arm
  eka_arm.png   - the raised (waving) arm only, same canvas size, for rotating around the shoulder
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "assets/source/eka_original.png").convert("RGB")
a = np.asarray(src).astype(np.int16)
h, w, _ = a.shape

# Background = near-white, low-saturation pixels connected to the border.
mn = a.min(axis=2)
mx = a.max(axis=2)
bgish = (mn > 222) & ((mx - mn) < 22)
bg = np.zeros((h, w), bool)
q = deque()
for x in range(w):
    for y in (0, h - 1):
        if bgish[y, x]:
            bg[y, x] = True
            q.append((y, x))
for y in range(h):
    for x in (0, w - 1):
        if bgish[y, x] and not bg[y, x]:
            bg[y, x] = True
            q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx] and bgish[ny, nx]:
            bg[ny, nx] = True
            q.append((ny, nx))

# Soft alpha: hard mask, slightly feathered, plus whiteness-based fade on the rim.
alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
al = np.asarray(alpha).astype(np.float32)
# De-fringe: pull white halo pixels on the edge towards the interior colour.
rgb = a.astype(np.float32)
edge = (al > 0) & (al < 250)
white_amt = np.clip((mn.astype(np.float32) - 180) / 75, 0, 1)
al = np.where(edge, al * (1 - 0.6 * white_amt), al)
rgba = np.dstack([rgb, al]).clip(0, 255).astype(np.uint8)
full = Image.fromarray(rgba, "RGBA")

# Keep only the robot itself (the component containing the chest), dropping stray specks.
solid = al > 8
keep = np.zeros_like(solid)
q = deque([(700, 410)])
keep[700, 410] = True
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and solid[ny, nx] and not keep[ny, nx]:
            keep[ny, nx] = True
            q.append((ny, nx))
grown = np.asarray(Image.fromarray(keep.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
al = np.where(grown, al, 0)
rgba[..., 3] = al.clip(0, 255).astype(np.uint8)
full = Image.fromarray(rgba, "RGBA")

# Crop to content with padding.
ys, xs = np.where(al > 8)
pad = 24
box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, w), min(ys.max() + pad, h))
full = full.crop(box)
ox, oy = box[0], box[1]

# Raised arm polygon (original image coordinates), from the shoulder pad outwards.
arm_poly = [(555, 555), (565, 540), (605, 492), (615, 462), (650, 442), (703, 462), (680, 530),
            (675, 552), (655, 592), (620, 618), (590, 615), (560, 600), (552, 580)]
arm_poly = [(x - ox, y - oy) for x, y in arm_poly]
# Elbow pivot for the wave, in cropped-canvas pixels (used by the animation).
print("elbow pivot", 572 - ox, 578 - oy)
m = Image.new("L", full.size, 0)
ImageDraw.Draw(m).polygon(arm_poly, fill=255)
m = m.filter(ImageFilter.GaussianBlur(1.5))

fa = np.asarray(full).astype(np.float32)
mm = np.asarray(m).astype(np.float32) / 255
arm = fa.copy(); arm[..., 3] *= mm
body = fa.copy(); body[..., 3] *= (1 - mm)

out = ROOT / "assets"
full.save(out / "eka_full.png")
Image.fromarray(arm.astype(np.uint8), "RGBA").save(out / "eka_arm.png")
Image.fromarray(body.astype(np.uint8), "RGBA").save(out / "eka_body.png")
print("crop box", box, "size", full.size)
