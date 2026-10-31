#!/usr/bin/env python3
"""Marker-protein gallery (same Å scale): static PNG + rotating GIF. Real PDB coordinates only."""
import importlib.util, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mr', os.path.join(HERE, '分子渲染v1.0.py'))
mr = importlib.util.module_from_spec(spec); spec.loader.exec_module(mr)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
FONT = os.path.expanduser('~/.fonts/NotoSansSC.ttf')


def font(sz, w='Regular'):
    f = ImageFont.truetype(FONT, sz)
    f.set_variation_by_name(w)
    return f

TEAL, ORANGE, GREY = (0.36, 0.72, 0.74), (0.96, 0.66, 0.38), (0.78, 0.62, 0.66)
# (pdb, chain, Chinese name, English, MISEV2023 category label, colour, highlight residue range)
ITEMS = [
    ('5TCX', 'A', 'CD81', '四跨膜蛋白 Tetraspanin', '第1类 · EV膜蛋白', TEAL, (113, 201)),
    ('6K4J', 'A', 'CD9', '四跨膜蛋白 Tetraspanin', '第1类 · EV膜蛋白', TEAL, (112, 195)),
    ('1KPP', 'A', 'TSG101', 'UEV结构域 (ESCRT-I)', '第2类 · 胞质蛋白', ORANGE, None),
    ('2OEV', 'A', 'ALIX', 'Bro1-V结构域', '第2类 · 胞质蛋白', ORANGE, None),
    ('1N99', 'A', 'Syntenin-1', 'PDZ串联结构域', '第2类 · 胞质蛋白', ORANGE, None),
    ('1AV1', 'A', 'ApoA1', '载脂蛋白A-I (Δ1-43)', '第3类 · 脂蛋白污染', GREY, None),
    ('1AO6', 'A', '白蛋白', '人血清白蛋白 HSA', '第3类 · 蛋白污染', GREY, None),
]
SCALE = 1.9  # px per Å, identical for every tile -> sizes comparable
TILE = (330, 330)


def prep(pdb, ch, hl, base):
    xyz, el, res = mr.load(pdb, chains=ch)
    c = xyz - xyz.mean(0)
    w, v = np.linalg.eigh(np.cov(c.T))
    R = mr.align_axis(v[:, -1])  # longest axis vertical
    c = c @ R.T
    if hl:  # tetraspanins: put the large extracellular loop (LEL) on top
        top = c[(res >= hl[0]) & (res <= hl[1])].mean(0)[1]
        if top < 0:
            c = c @ np.diag([1, -1, -1.0]).T
    r = np.array([mr.VDW.get(e, 1.7) for e in el])
    col = mr.palette(base, len(c), el)
    grp = np.zeros(len(c), int)
    if hl:
        m = (res >= hl[0]) & (res <= hl[1])
        col[m] = np.clip(col[m] * 0.75 + 0.25, 0, 1)
        grp[m] = 1
    return c, r, col, grp


PREP = [prep(p, ch, hl, b) for p, ch, _, _, _, b, hl in ITEMS]


def tile(i, ang):
    c, r, col, grp = PREP[i]
    img = mr.render(c @ mr.rot(0.12, ang).T, r, col, size=TILE, scale=SCALE, center=np.zeros(3), groups=grp)
    return Image.fromarray(img)


def compose(ang, scale_bar=True):
    cols, gap, top, lab = 4, 10, 96, 78
    W = cols * TILE[0] + (cols + 1) * gap
    H = top + 2 * (TILE[1] + lab) + 70
    canvas = Image.new('RGBA', (W, H), (250, 251, 249, 255))
    d = ImageDraw.Draw(canvas)
    d.text((gap + 6, 18), 'EV表征常用蛋白的真实三维结构', font=font(30, 'Bold'), fill=(24, 72, 75))
    d.text((gap + 8, 60), 'Marker & contaminant proteins at the same scale · PDB 实验结构 · MISEV2023 表3 分类', font=font(17), fill=(90, 100, 105))
    for i, it in enumerate(ITEMS):
        rr, cc = divmod(i, cols)
        x = gap + cc * (TILE[0] + gap); y = top + rr * (TILE[1] + lab)
        d.rounded_rectangle([x, y, x + TILE[0], y + TILE[1] + lab - 8], 14, fill=(255, 255, 255, 255), outline=(222, 230, 230))
        canvas.alpha_composite(tile(i, ang), (x, y))
        colr = tuple(int(255 * v * 0.7) for v in it[5])
        d.text((x + 14, y + TILE[1] - 6), it[2], font=font(22, 'Bold'), fill=colr)
        d.text((x + 14 + d.textlength(it[2], font=font(22, 'Bold')) + 8, y + TILE[1] + 1), it[3], font=font(13), fill=(80, 88, 92))
        d.text((x + 14, y + TILE[1] + 28), f'{it[4]} · PDB {it[0]}', font=font(14, 'Medium'), fill=(110, 118, 120))
    # legend tile
    x = gap + 3 * (TILE[0] + gap); y = top + (TILE[1] + lab)
    d.rounded_rectangle([x, y, x + TILE[0], y + TILE[1] + lab - 8], 14, fill=(244, 248, 247, 255), outline=(222, 230, 230))
    ly = y + 22
    for name, c in [('第1类 跨膜/GPI锚定：证明有脂双层', TEAL), ('第2类 胞质蛋白：证明有腔内内容', ORANGE), ('第3类 共分离物：评估纯度', GREY)]:
        d.ellipse([x + 18, ly + 3, x + 36, ly + 21], fill=tuple(int(255 * v) for v in c), outline=(40, 40, 40))
        d.text((x + 46, ly), name, font=font(14), fill=(40, 52, 56)); ly += 36
    d.text((x + 18, ly + 4), 'CD81/CD9 的浅色部分为大胞外环 LEL', font=font(13), fill=(90, 100, 105)); ly += 30
    if scale_bar:
        bar = int(50 * SCALE)
        d.line([x + 18, ly + 20, x + 18 + bar, ly + 20], fill=(30, 30, 30), width=4)
        d.text((x + 26 + bar, ly + 8), '5 nm（同一比例尺）', font=font(14), fill=(30, 30, 30)); ly += 48
    d.text((x + 18, ly), '原子坐标来自 RCSB PDB（CC0）；\n颜色与光照仅为示意。\nCD63 无实验全长结构，未画。', font=font(12), fill=(110, 118, 120), spacing=5)
    d.text((gap + 6, H - 40), '注：TSG101/ALIX/Syntenin 仅为结构域片段；ApoA1 为截短晶体结构；真实 EV 中的拷贝数和取向未在此表示。', font=font(13), fill=(110, 118, 120))
    return canvas


if __name__ == '__main__':
    static = compose(0.5)
    static.convert('RGB').save(os.path.join(OUT, '标志蛋白图集v1.0.png'), optimize=True)
    frames = []
    n = 36
    for k in range(n):
        f = compose(2 * np.pi * k / n).convert('RGB').resize((870, int(870 * static.size[1] / static.size[0])), Image.LANCZOS)
        frames.append(f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
        print('frame', k, flush=True)
    frames[0].save(os.path.join(OUT, '标志蛋白旋转v1.0.gif'), save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=True)
