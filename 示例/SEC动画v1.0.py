#!/usr/bin/env python3
"""Teaching animation: size-exclusion chromatography (SEC) separates EVs from soluble protein,
but not from similarly sized lipoproteins. Schematic only - not experimental data.
Logic follows Böing 2014 (doi:10.3402/jev.v3.23430) and Karimi 2018 (doi:10.1007/s00018-018-2773-4)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
FONT = os.path.expanduser('~/.fonts/NotoSansSC.ttf')
rng = np.random.default_rng(3)


def font(sz, w='Regular'):
    f = ImageFont.truetype(FONT, sz); f.set_variation_by_name(w); return f

W, H = 760, 640
CX0, CX1, CY0, CY1 = 80, 300, 120, 520  # column
KINDS = {  # name, colour, radius px, speed, count
    'EV': ((63, 160, 166), 7.5, 9.0, 34),
    'LDL/VLDL': ((226, 178, 64), 6.0, 8.3, 26),
    'HDL': ((236, 214, 120), 3.6, 4.0, 36),
    '可溶蛋白': ((150, 150, 158), 2.3, 3.0, 90),
}
P = []
for k, (c, r, v, n) in KINDS.items():
    for _ in range(n):
        P.append([k, rng.uniform(CX0 + 12, CX1 - 12), rng.uniform(CY0 - 90, CY0 - 10), v * rng.uniform(0.85, 1.15)])
beads = [(rng.uniform(CX0 + 10, CX1 - 10), rng.uniform(CY0 + 10, CY1 - 10)) for _ in range(70)]
NF = 26  # fractions
hist = {k: np.zeros(NF) for k in KINDS}
FR_T = 7  # frames per fraction
frames = []
T = NF * FR_T
for t in range(T):
    im = Image.new('RGB', (W, H), (248, 250, 248))
    d = ImageDraw.Draw(im)
    d.text((24, 18), '尺寸排阻色谱 SEC：大颗粒先出峰', font=font(28, 'Bold'), fill=(24, 72, 75))
    d.text((26, 58), 'Size-exclusion chromatography · 示意动画，不是实验数据', font=font(15), fill=(100, 110, 114))
    d.rounded_rectangle([CX0, CY0, CX1, CY1], 16, fill=(236, 241, 240), outline=(150, 175, 176), width=3)
    for bx, by in beads:
        d.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(214, 224, 222), outline=(186, 200, 199))
        for a in range(5):
            ox, oy = 6 * np.cos(a * 1.3 + bx), 6 * np.sin(a * 1.7 + by)
            d.ellipse([bx + ox - 1.6, by + oy - 1.6, bx + ox + 1.6, by + oy + 1.6], fill=(196, 208, 206))
    d.text((CX0 + 6, CY1 + 8), '多孔填料：小分子钻进孔里，走得慢', font=font(14), fill=(90, 100, 105))
    for p in P:
        k, x, y, v = p
        if y > CY1 + 30:
            continue
        p[2] += v * (0.7 + 0.6 * rng.random())
        p[1] = np.clip(x + rng.normal(scale=1.2), CX0 + 8, CX1 - 8)
        if p[2] > CY1 and y <= CY1:
            hist[k][min(t // FR_T, NF - 1)] += 1
        c, r, _, _ = KINDS[k]
        if CY0 - 100 < p[2] < CY1:
            if k == 'EV':
                d.ellipse([p[1] - r, p[2] - r, p[1] + r, p[2] + r], fill=(220, 240, 240), outline=c, width=3)
            else:
                d.ellipse([p[1] - r, p[2] - r, p[1] + r, p[2] + r], fill=c)
    # elution chart
    gx0, gx1, gy0, gy1 = 360, 730, 150, 470
    d.line([gx0, gy1, gx1, gy1], fill=(60, 60, 60), width=2); d.line([gx0, gy0, gx0, gy1], fill=(60, 60, 60), width=2)
    d.text((gx0, gy1 + 8), '早  ←  洗脱组分  →  晚', font=font(14), fill=(80, 88, 92))
    d.text((gx0, gy0 - 30), '各组分中颗粒数', font=font(15, 'Medium'), fill=(40, 52, 56))
    bw = (gx1 - gx0) / NF
    mx = max(10, max(h.max() for h in hist.values()))
    for j in range(NF):
        base = gy1
        for k, (c, _, _, _) in KINDS.items():
            hgt = hist[k][j] / mx * (gy1 - gy0) * 0.55
            if hgt > 0:
                d.rectangle([gx0 + j * bw + 1, base - hgt, gx0 + (j + 1) * bw - 1, base], fill=c)
            base -= hgt
    ly = 500
    for k, (c, r, _, _) in KINDS.items():
        d.ellipse([370, ly + 4, 384, ly + 18], fill=c if k != 'EV' else (220, 240, 240), outline=c, width=3 if k == 'EV' else 1)
        d.text((392, ly), k, font=font(16), fill=(40, 52, 56)); ly += 28
    d.text((470, 500), '要点：EV 与可溶蛋白分得开；\n与大小相近的 LDL/VLDL\n分不开 → 血浆需再加密度梯度', font=font(16), fill=(150, 70, 50), spacing=6)
    frames.append(im.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
frames += [frames[-1]] * 18
os.makedirs(OUT, exist_ok=True)
frames[0].save(os.path.join(OUT, 'SEC原理动画v1.0.gif'), save_all=True, append_images=frames[1:], duration=55, loop=0, optimize=True)
print('ok', len(frames))
