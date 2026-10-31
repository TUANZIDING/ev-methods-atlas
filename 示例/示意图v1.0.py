#!/usr/bin/env python3
"""Hand-coded SVG teaching diagrams for ev-methods-atlas (no external assets)."""
import os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
FF = "PingFang SC, 'Noto Sans SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif"
INK, TEAL, SUB = '#18484b', '#2f8f94', '#5c6b70'


def svg(w, h, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FF}">
<title>{title}</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7faf9"/><stop offset="1" stop-color="#eef4f3"/></linearGradient>
  <filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1b4b4e" flood-opacity="0.12"/></filter>
  <radialGradient id="ev" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#e9f6f5"/><stop offset="1" stop-color="#7cc0c2"/></radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
{body}
</svg>'''


def grid():
    w, h = 980, 670
    x0, y0, x1, y1 = 130, 110, 900, 560
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">回收率 × 特异性：没有两全的分离方法</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">Recovery vs specificity grid · 依据 MISEV2018（Théry 2018）· 位置为定性示意，随参数与样本变化</text>']
    b.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="14" fill="#ffffff" stroke="#c9d9d9" filter="url(#sh)"/>')
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    b.append(f'<line x1="{mx}" y1="{y0}" x2="{mx}" y2="{y1}" stroke="#dbe6e5" stroke-dasharray="6 6"/><line x1="{x0}" y1="{my}" x2="{x1}" y2="{my}" stroke="#dbe6e5" stroke-dasharray="6 6"/>')
    b.append(f'<text x="{x1-14}" y="{y0+30}" text-anchor="end" font-size="15" fill="#a0632a" font-weight="600">高回收 + 高特异：目前可能无法实现</text>')
    b.append(f'<text x="{(x0+x1)/2}" y="{y1+34}" text-anchor="middle" font-size="16" fill="{INK}" font-weight="600">回收率 Recovery →</text>')
    b.append(f'<text x="{x0-56}" y="{(y0+y1)/2}" text-anchor="middle" font-size="16" fill="{INK}" font-weight="600" transform="rotate(-90 {x0-56} {(y0+y1)/2})">特异性 Specificity →</text>')
    pts = [  # name, recovery(0-1), specificity(0-1), colour
        ('聚合物沉淀 / PEG 试剂盒', 0.86, 0.12, '#c58b5a'), ('超滤 / TFF（单用）', 0.78, 0.2, '#c58b5a'),
        ('差速超离 dUC', 0.5, 0.45, TEAL), ('尺寸排阻 SEC', 0.6, 0.55, TEAL),
        ('密度梯度 DGC', 0.3, 0.76, '#3f6fa3'), ('免疫亲和（亚群）', 0.06, 0.93, '#3f6fa3'),
        ('AF4', 0.16, 0.64, '#3f6fa3'), ('SEC + 密度梯度', 0.46, 0.9, '#6d4ea0'), ('UF/TFF → SEC', 0.76, 0.66, '#6d4ea0')]
    for n, rx, sy, c in pts:
        x = x0 + 40 + rx * (x1 - x0 - 80); y = y1 - 40 - sy * (y1 - y0 - 80)
        tw = sum(15.5 if ord(ch) > 0x2E80 else 8.6 for ch in n) + 26
        lx = x + 14 if x + 14 + tw < x1 - 8 else x - 14 - tw
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{c}" stroke="#fff" stroke-width="2.5"/>')
        b.append(f'<rect x="{lx:.0f}" y="{y-14:.0f}" width="{tw:.0f}" height="28" rx="14" fill="#fff" stroke="{c}" stroke-opacity="0.5"/>')
        b.append(f'<text x="{lx+13:.0f}" y="{y+5:.0f}" font-size="15" fill="#253338">{n}</text>')
    b.append(f'<text x="{x0}" y="{h-22}" font-size="13" fill="{SUB}">紫色 = 组合策略。MISEV2018 把方法分为：高回收低特异 / 中等 / 低回收高特异 / 高回收高特异（可能尚无法实现）。</text>')
    return svg(w, h, '\n'.join(b), '回收率与特异性网格')


def timeline():
    ev = [('1946', 'Chargaff &amp; West', '血浆高速离心沉淀有促凝活性', '⚠'), ('1967', 'Wolf', '“platelet dust” 血小板尘埃', '⚠'),
          ('1981', 'Trams 等', '首次提出 “exosomes” 一词', '✓'), ('1983', 'Harding / Pan &amp; Johnstone', '网织红细胞转铁蛋白受体经囊泡外排', '✓'),
          ('1987', 'Johnstone 等', '网织红细胞囊泡称 exosomes', '✓'), ('1996', 'Raposo 等', 'B 细胞外泌体呈递抗原', '✓'),
          ('2007', 'Valadi 等', 'mRNA/miRNA 经外泌体转移', '✓'), ('2011', 'ISEV 成立', '国际细胞外囊泡学会', '✓'),
          ('2013', '诺贝尔奖', '胞内囊泡运输机制（非 EV 本身）', '✓'), ('2014', 'MISEV2014', '第一份最低要求', '✓'),
          ('2018', 'MISEV2018', '推荐通用词 EV；五类蛋白', '✓'), ('2020', 'Kalluri &amp; LeBleu', 'Science 外泌体综述', '✓'),
          ('2024', 'MISEV2023', 'EP/NVEP；不鼓励按生物发生命名', '✓')]
    w, h = 1520, 520
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">细胞外囊泡研究史</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">✓ 已核对 PubMed/Crossref 与摘要或原文　⚠ 只核对了元数据，细节来自二手文献</text>']
    y = 270
    b.append(f'<line x1="50" y1="{y}" x2="{w-40}" y2="{y}" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>')
    step = (w - 220) / (len(ev) - 1)
    for i, (yr, who, what, ok) in enumerate(ev):
        x = 110 + i * step
        up = i % 2 == 0
        cy = y - 120 if up else y + 50
        col = '#a0632a' if ok == '⚠' else TEAL
        b.append(f'<line x1="{x:.0f}" y1="{y}" x2="{x:.0f}" y2="{cy + (70 if up else 0)}" stroke="{col}" stroke-opacity="0.5" stroke-width="1.5"/>')
        b.append(f'<circle cx="{x:.0f}" cy="{y}" r="8" fill="#fff" stroke="{col}" stroke-width="4"/>')
        b.append(f'<rect x="{x-90:.0f}" y="{cy}" width="180" height="70" rx="12" fill="#fff" stroke="#d3e2e1" filter="url(#sh)"/>')
        b.append(f'<text x="{x:.0f}" y="{cy+22}" text-anchor="middle" font-size="16" font-weight="700" fill="{col}">{yr} {ok}</text>')
        b.append(f'<text x="{x:.0f}" y="{cy+41}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#253338">{who}</text>')
        b.append(f'<text x="{x:.0f}" y="{cy+59}" text-anchor="middle" font-size="11.5" fill="{SUB}">{what}</text>')
    b.append(f'<text x="40" y="{h-24}" font-size="13" fill="{SUB}">MISEV2023 的版本号为 2023，正式出版于 J Extracell Vesicles 2024 年 2 月。完整来源见 文档/研究史时间线v1.0.md。</text>')
    return svg(w, h, '\n'.join(b), '细胞外囊泡研究史时间线')


def misev():
    w, h = 1180, 560
    cols = [('MISEV2014', 'Lötvall 等 · JEV 2014', ['“EV” 作为统称，“exosome” 被称为流行词', '≥3 个蛋白半定量；第1/2/3类各≥1', '单囊泡表征 ≥2 种技术', '提出功能研究的对照']),
            ('MISEV2018', 'Théry 等 · JEV 2018', ['ISEV 推荐通用词 “EV”', '操作性术语：大小、密度、标志物、来源', '五类蛋白框架；不再推荐通用阴性对照', '回收率×特异性网格；建议上传 EV-TRACK', '核查清单 checklist']),
            ('MISEV2023', 'Welsh 等 · JEV 2024', ['新增 EP（细胞外颗粒）与 NVEP', '不鼓励 exosome/ectosome，除非证明来源', 'sEV ≠ 外泌体；200 nm 分界无严格共识', '无通用 EV 标志物；正交方法', '按来源分章：血液、尿液、组织、细菌等', '新增：释放与摄取、体内研究、报告要点'])]
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">MISEV 指南三版演变</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">要点均核对自 Europe PMC 全文（PMC4275645 · PMC6322352 · PMC10850029）</text>']
    cw = (w - 120) / 3
    shades = ['#7fb7b9', '#3f9a9f', '#1f6f74']
    for i, (t, ref, pts) in enumerate(cols):
        x = 40 + i * (cw + 20)
        b.append(f'<rect x="{x:.0f}" y="110" width="{cw:.0f}" height="400" rx="16" fill="#fff" stroke="#d3e2e1" filter="url(#sh)"/>')
        b.append(f'<rect x="{x:.0f}" y="110" width="{cw:.0f}" height="70" rx="16" fill="{shades[i]}"/><rect x="{x:.0f}" y="160" width="{cw:.0f}" height="20" fill="{shades[i]}"/>')
        b.append(f'<text x="{x+22:.0f}" y="147" font-size="24" font-weight="700" fill="#fff">{t}</text>')
        b.append(f'<text x="{x+22:.0f}" y="170" font-size="13" fill="#eaf6f5">{ref}</text>')
        for j, p in enumerate(pts):
            yy = 218 + j * 46
            b.append(f'<circle cx="{x+28:.0f}" cy="{yy-5}" r="5" fill="{shades[i]}"/>')
            b.append(f'<text x="{x+42:.0f}" y="{yy}" font-size="14.5" fill="#253338">{p}</text>')
        if i < 2:
            ax = x + cw + 3
            b.append(f'<path d="M{ax:.0f} 300 l14 10 l-14 10 z" fill="{shades[i+1]}"/>')
    b.append(f'<text x="40" y="{h-22}" font-size="13" fill="{SUB}">MISEV2023 原文：此前建议“在很大程度上或完全仍然有效”，应结合前两版一起阅读。</text>')
    return svg(w, h, '\n'.join(b), 'MISEV 指南三版演变')


def muscle():
    w, h = 1180, 470
    steps = [('取材', '新鲜肌组织\n称重并记录 mg', '#7fb7b9'), ('轻柔解离', '剪碎 + 胶原酶/DNase\n避免匀浆', '#5aa7aa'),
             ('逐级离心', '300 g → 2,000 g\n→ 10,000 g（lEV）', '#3f9a9f'), ('EV 分离', '超离或 SEC\n+ 密度梯度', '#2f8a8f'),
             ('表征', 'NTA/nFCM + EM\n1/2/3 类 + 线粒体/核', '#1f6f74'), ('归一化', '颗粒/蛋白\n按每 mg 组织', '#18484b')]
    b = [f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">骨骼肌组织 EV：从取材到可比较的数据</text>',
         f'<text x="40" y="82" font-size="15" fill="{SUB}">参考 Crescitelli 2021（Nat Protoc）与 MISEV2023 组织章节；具体参数为经验起点，需预实验优化</text>']
    sw = (w - 80 - 5 * 26) / 6
    for i, (t, d, c) in enumerate(steps):
        x = 40 + i * (sw + 26)
        b.append(f'<rect x="{x:.0f}" y="120" width="{sw:.0f}" height="150" rx="16" fill="#fff" stroke="{c}" stroke-width="2" filter="url(#sh)"/>')
        b.append(f'<circle cx="{x+30:.0f}" cy="150" r="16" fill="{c}"/><text x="{x+30:.0f}" y="156" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">{i+1}</text>')
        b.append(f'<text x="{x+54:.0f}" y="157" font-size="18" font-weight="700" fill="{INK}">{t}</text>')
        for k, line in enumerate(d.split('\n')):
            b.append(f'<text x="{x+18:.0f}" y="{200+k*24}" font-size="14" fill="#253338">{line}</text>')
        if i < 5:
            b.append(f'<path d="M{x+sw+6:.0f} 188 l14 7 l-14 7 z" fill="{c}"/>')
    warn = [('细胞碎片 / 线粒体', '肌肉线粒体极丰富：查 VDAC、TOMM20'), ('照射组', '坏死与凋亡增多：EV“增多”可能是碎片'),
            ('新生 vs 成年', '组织量、酶解时间一致；按每 mg 归一化'), ('来源证明', 'SGCA 免疫捕获或肌纤维报告小鼠')]
    for i, (t, d) in enumerate(warn):
        x = 40 + i * ((w - 80) / 4)
        b.append(f'<rect x="{x:.0f}" y="300" width="{(w-80)/4-16:.0f}" height="96" rx="14" fill="#fbf4e8" stroke="#e3c79a"/>')
        b.append(f'<text x="{x+16:.0f}" y="332" font-size="15.5" font-weight="700" fill="#8a5a1f">⚠ {t}</text>')
        b.append(f'<text x="{x+16:.0f}" y="362" font-size="13" fill="#5b4a33">{d}</text>')
    b.append(f'<text x="40" y="{h-24}" font-size="13" fill="{SUB}">证据：肌纤维约占循环四跨膜阳性 EV 的 5%（Estrada 2022）；肌源 EV 在肌间质富集（Watanabe 2022）；SGCA+ EV 占血浆 EV 1–5%（Guescini 2015）。</text>')
    return svg(w, h, '\n'.join(b), '骨骼肌组织 EV 分离流程')


for name, fn in [('回收率特异性网格v1.0.svg', grid), ('研究史时间线v1.0.svg', timeline), ('MISEV演变v1.0.svg', misev), ('骨骼肌EV流程v1.0.svg', muscle)]:
    open(os.path.join(OUT, name), 'w').write(fn())
print('svgs ok')
