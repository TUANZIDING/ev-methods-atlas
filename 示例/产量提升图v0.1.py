#!/usr/bin/env python3
"""Self-drawn SVG figures for the upstream-yield chapter of ev-methods-atlas.
(1) Ascorbic-acid pretreatment timeline of KR 10-2159915 example.
(2) Differential ultracentrifugation step diagram of the same example.
Schematic teaching figures; the only quantitative value shown (≈4x) is the patent's own stated result."""
import os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
FF = "PingFang SC, 'Noto Sans SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif"
INK, TEAL, ORANGE, SUB = '#18484b', '#2f8f94', '#d98b3a', '#5c6b70'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FF}">\n'
            f'<title>{title}</title>\n<defs>'
            '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7faf9"/><stop offset="1" stop-color="#eef4f3"/></linearGradient>'
            '<filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1b4b4e" flood-opacity="0.12"/></filter>'
            f'</defs>\n<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>\n{body}\n</svg>')


def timeline():
    w, h = 1180, 476
    steps = [('接种', '人脂肪间充质干细胞\nα-MEM + 10% FBS\n6000 细胞/cm²', TEAL, '0 h'),
             ('加抗坏血酸', '接种 24 h 后加入\n10 / 30 / 100 µg/mL\n（对照组不加）', ORANGE, '24 h'),
             ('换液', '≥80% 汇合时换\n无血清 SFM 或\n2% 去EV FBS（EDM）\n仍含抗坏血酸', TEAL, '汇合时'),
             ('收集', '换液后再培养 24 h\n收集条件培养基\n并计数细胞', TEAL, '+24 h'),
             ('分离与定量', '差速超离分离 EV\nNTA + CD63 磁珠流式', '#1f6f74', '终点')]
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">抗坏血酸预处理流程（KR 10-2159915 实施例）</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">示意流程图，依据专利实施例 1–3；参数为该专利所述，非通用最优值</text>']
    sw = (w - 80 - 4 * 24) / 5
    for i, (t, d, c, tag) in enumerate(steps):
        x = 40 + i * (sw + 24)
        b.append(f'<rect x="{x:.0f}" y="150" width="{sw:.0f}" height="190" rx="16" fill="#fff" stroke="{c}" stroke-width="2" filter="url(#sh)"/>')
        b.append(f'<rect x="{x:.0f}" y="118" width="{sw:.0f}" height="30" rx="15" fill="{c}"/>')
        b.append(f'<text x="{x+sw/2:.0f}" y="138" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">{tag}</text>')
        b.append(f'<circle cx="{x+26:.0f}" cy="180" r="15" fill="{c}"/><text x="{x+26:.0f}" y="186" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">{i+1}</text>')
        b.append(f'<text x="{x+50:.0f}" y="186" font-size="17" font-weight="700" fill="{INK}">{t}</text>')
        for k, line in enumerate(d.split('\n')):
            b.append(f'<text x="{x+18:.0f}" y="{220+k*26}" font-size="13.5" fill="#253338">{line}</text>')
        if i < 4:
            b.append(f'<path d="M{x+sw+4:.0f} 240 l15 8 l-15 8 z" fill="{c}"/>')
    b.append(f'<rect x="40" y="362" width="{w-80}" height="92" rx="14" fill="#fbf4e8" stroke="#e3c79a"/>')
    b.append(f'<text x="58" y="396" font-size="15.5" font-weight="700" fill="#8a5a1f">⚠ 读图提醒</text>')
    b.append(f'<text x="58" y="420" font-size="13.5" fill="#5b4a33">专利称处理组每 mL 颗粒数约为对照 4 倍以上、CD63 含量显著升高；但未报告重复数、统计、TEM/WB 与每细胞产量。</text>')
    b.append(f'<text x="58" y="442" font-size="13.5" fill="#5b4a33">抗坏血酸本身促进 MSC 增殖，部分增量可能来自细胞数增加（推测，待每细胞归一化验证）。</text>')
    return svg(w, h, '\n'.join(b), '抗坏血酸预处理流程')


def uc():
    w, h = 1180, 470
    steps = [('300 ×g\n10 min', '去细胞', '取上清', '#5d9fa2'),
             ('2,000 ×g\n20 min', '去细胞碎片', '取上清', '#4f9599'),
             ('16,500 ×g\n10 min', '去微囊泡', '取上清', '#4a9ca0'),
             ('120,000 ×g\n120 min', '沉 EV', '弃上清、取沉淀', '#2f8a8f'),
             ('120,000 ×g\n120 min', 'PBS 洗涤后再离心', '重悬于 PBS', '#1f6f74')]
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">差速超离步骤（KR 10-2159915 实施例 2）</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">4℃ 逐级离心；转速越高沉降越小的颗粒，最后一步重复洗涤一次</text>']
    sw = (w - 80 - 4 * 24) / 5
    for i, (g, role, act, c) in enumerate(steps):
        x = 40 + i * (sw + 24)
        b.append(f'<rect x="{x:.0f}" y="150" width="{sw:.0f}" height="150" rx="16" fill="#fff" stroke="{c}" stroke-width="2" filter="url(#sh)"/>')
        for k, line in enumerate(g.split('\n')):
            b.append(f'<text x="{x+sw/2:.0f}" y="{188+k*26:.0f}" text-anchor="middle" font-size="18" font-weight="700" fill="{c}">{line}</text>')
        b.append(f'<text x="{x+sw/2:.0f}" y="{250 if chr(10) in g else 236:.0f}" text-anchor="middle" font-size="15" fill="{INK}">{role}</text>')
        b.append(f'<text x="{x+sw/2:.0f}" y="282" text-anchor="middle" font-size="13" fill="{SUB}">{act}</text>')
        if i < 4:
            b.append(f'<path d="M{x+sw+4:.0f} 220 l15 9 l-15 9 z" fill="{c}"/>')
    b.append(f'<rect x="40" y="330" width="{w-80}" height="100" rx="14" fill="#eef4f3" stroke="#cfe0df"/>')
    b.append(f'<text x="58" y="360" font-size="15.5" font-weight="700" fill="{INK}">和本图谱「分离」章的对应</text>')
    b.append(f'<text x="58" y="388" font-size="13.5" fill="#253338">这是经典差速超离（dUC）：得率中等、纯度受脂蛋白/蛋白共沉淀影响。本专利把它当作读出 EV 产量的工具，而非分离创新；</text>')
    b.append(f'<text x="58" y="412" font-size="13.5" fill="#253338">若要更高纯度，可在 120,000 ×g 沉淀后接密度梯度或 SEC（见「分离方法对比」）。按 MISEV2023，单一 dUC 不足以证明是 EV，需补 EM 与多标志物。</text>')
    return svg(w, h, '\n'.join(b), '差速超离步骤')


open(os.path.join(OUT, '抗坏血酸处理时间线v0.1.svg'), 'w').write(timeline())
open(os.path.join(OUT, '超离分离步骤v0.1.svg'), 'w').write(uc())
print('yield svgs ok')
