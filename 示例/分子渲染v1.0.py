#!/usr/bin/env python3
"""Goodsell-style sphere renderer for PDB structures (numpy + scipy + Pillow only).

Every atom position comes from an experimental PDB entry (RCSB, CC0). Nothing is invented:
colours, lighting and outlines are styling only. Used by the figure scripts of ev-methods-atlas.
"""
import os, urllib.request
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'pdb')
VDW = {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8, 'P': 1.8}


def fetch(pdb_id):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, pdb_id.upper() + '.pdb')
    if not os.path.exists(p):
        urllib.request.urlretrieve(f'https://files.rcsb.org/download/{pdb_id.upper()}.pdb', p)
    return p


def load(pdb_id, chains=None, model=1, ca_only=False):
    """Return (xyz[N,3], element[N], resseq[N]) heavy atoms of protein chains, first model."""
    xyz, el, res = [], [], []
    m = 1
    for line in open(fetch(pdb_id)):
        if line.startswith('ENDMDL'):
            m += 1
            if m > model:
                break
        if not line.startswith('ATOM'):
            continue
        ch = line[21]
        if chains and ch not in chains:
            continue
        name = line[12:16].strip()
        e = (line[76:78].strip() or name[0]).upper()
        if e == 'H' or (ca_only and name != 'CA'):
            continue
        if line[16] not in (' ', 'A'):
            continue
        xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        el.append(e)
        res.append(int(line[22:26]))
    return np.array(xyz), np.array(el), np.array(res)


def rot(ax, ay, az=0.0):
    cx, sx, cy, sy, cz, sz = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay), np.cos(az), np.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def align_axis(v, target=np.array([0, 1.0, 0])):
    """Rotation matrix taking unit vector v onto target."""
    v = v / np.linalg.norm(v); t = target / np.linalg.norm(target)
    c = np.dot(v, t); k = np.cross(v, t); s = np.linalg.norm(k)
    if s < 1e-8:
        return np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    k /= s
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(np.arccos(c)) * K + (1 - c) * K @ K


def render(xyz, radii, colors, size=(600, 600), scale=None, center=None, light=(-0.45, 0.55, 0.7),
           outline=True, groups=None, bg=(255, 255, 255, 0), ao=True, fog=0.25, ss=2, edge_dark=0.3, edge_depth=7.0):
    """Orthographic z-buffer sphere render. xyz in Å (already rotated). +z towards viewer.
    colors: [N,3] floats 0-1. groups: int per atom; boundaries between groups get thin lines."""
    if ss > 1:
        from PIL import Image
        big = render(xyz, radii, colors, size=(size[0] * ss, size[1] * ss), scale=None if scale is None else scale * ss,
                     center=center, light=light, outline=outline, groups=groups, bg=bg, ao=ao, fog=fog, ss=1, edge_dark=edge_dark, edge_depth=edge_depth)
        return np.array(Image.fromarray(big).resize(size, Image.LANCZOS))
    W, H = size
    if center is None:
        center = (xyz.max(0) + xyz.min(0)) / 2
    p = xyz - center
    if scale is None:
        ext = max(np.ptp(p[:, 0]), np.ptp(p[:, 1])) + 2 * radii.max()
        scale = 0.9 * min(W, H) / ext
    px = p[:, 0] * scale + W / 2
    py = -p[:, 1] * scale + H / 2
    pz = p[:, 2] * scale
    pr = radii * scale
    depth = np.full((H, W), -1e9)
    ident = np.full((H, W), -1, dtype=np.int64)
    nz = np.zeros((H, W))
    order = np.argsort(pz)
    for i in order:
        r = pr[i]
        x0, x1 = int(max(0, np.floor(px[i] - r))), int(min(W, np.ceil(px[i] + r) + 1))
        y0, y1 = int(max(0, np.floor(py[i] - r))), int(min(H, np.ceil(py[i] + r) + 1))
        if x0 >= x1 or y0 >= y1:
            continue
        xs = np.arange(x0, x1) + 0.5 - px[i]
        ys = np.arange(y0, y1) + 0.5 - py[i]
        d2 = ys[:, None] ** 2 + xs[None, :] ** 2
        inside = d2 < r * r
        h = np.sqrt(np.clip(r * r - d2, 0, None))
        z = pz[i] + h
        sub = depth[y0:y1, x0:x1]
        upd = inside & (z > sub)
        sub[upd] = z[upd]
        ident[y0:y1, x0:x1][upd] = i
        nz[y0:y1, x0:x1][upd] = (h / r)[upd]
    mask = ident >= 0
    col = np.zeros((H, W, 3))
    col[mask] = colors[ident[mask]]
    # lighting: approximate normal from sphere geometry
    L = np.array(light) / np.linalg.norm(light)
    ii = ident.clip(0)
    yy, xx = np.mgrid[0:H, 0:W] + 0.5
    nx = (xx - px[ii]) / np.maximum(pr[ii], 1e-6)
    ny = -(yy - py[ii]) / np.maximum(pr[ii], 1e-6)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    shade = 0.72 + 0.33 * lam
    if ao:
        dfill = np.where(mask, depth, depth[mask].min() if mask.any() else 0)
        blur = ndimage.gaussian_filter(dfill, sigma=max(2, 4 * scale))
        occl = np.clip((blur - dfill) / (6 * scale + 1e-6), 0, 1)
        shade *= (1 - 0.45 * occl)
    if fog and mask.any():
        dz = depth[mask]
        f = np.zeros((H, W))
        f[mask] = (dz.max() - dz) / (np.ptp(dz) + 1e-6)
        shade = shade * (1 - fog * f) + fog * f * 0.92
    img = col * shade[..., None]
    if outline:
        # Goodsell-style outlines at silhouette and depth/group discontinuities
        dpad = np.where(mask, depth, -1e9)
        gx = np.abs(np.diff(dpad, axis=1, append=dpad[:, -1:]))
        gy = np.abs(np.diff(dpad, axis=0, append=dpad[-1:, :]))
        edge = (gx > edge_depth * scale) | (gy > edge_depth * scale)
        if groups is not None:
            g = np.where(mask, groups[ii], -1)
            edge |= (np.diff(g, axis=1, append=g[:, -1:]) != 0) | (np.diff(g, axis=0, append=g[-1:, :]) != 0)
        edge = ndimage.binary_dilation(edge & ndimage.binary_dilation(mask), iterations=1) & (mask | ndimage.binary_dilation(mask))
        img[edge] = img[edge] * edge_dark
        mask = mask | edge
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[..., :3] = np.array(bg[:3])
    rgba[..., 3] = bg[3]
    rgba[mask, :3] = np.clip(img[mask] * 255, 0, 255).astype(np.uint8)
    rgba[mask, 3] = 255
    return rgba


def palette(base, n, el=None, spread=0.22):
    """Gentle N->C gradient around a base colour; heteroatoms slightly darker (Goodsell)."""
    base = np.array(base, float)
    t = np.linspace(-1, 1, n)[:, None]
    c = np.clip(base + spread * t * (np.array([1, 1, 1]) - base) * 0.5 - spread * 0.25 * t * base, 0, 1)
    if el is not None:
        c[el != 'C'] *= 0.86
    return c
