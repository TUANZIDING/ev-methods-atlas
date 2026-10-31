#!/usr/bin/env python3
"""Rebuild 综述v1.0 (numbered refs), BibTeX, RIS, CSV tables and PDF from 文档/综述源稿v1.0.md: numbered refs, BibTeX, RIS, CSV tables, HTML, PDF."""
import json, re, csv, os, html, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(ROOT, '..', '文档')
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)
REFS = json.load(open(os.path.join(DOC, '参考文献', '文献元数据v1.0.json')))

# Manual entries (no DOI or non-article), verified via PubMed / nobelprize.org on 2026-10-31
REFS['chargaff1946'] = dict(doi='', pmid='20273687', title='The biological significance of the thromboplastic protein of blood',
    journal='J Biol Chem', year=1946, vol='166', issue='1', page='189-197', authors=[('Chargaff', 'E'), ('West', 'R')], nauth=2)
REFS['johnstone1987'] = dict(doi='', pmid='3597417', title='Vesicle formation during reticulocyte maturation. Association of plasma membrane activities with released vesicles (exosomes)',
    journal='J Biol Chem', year=1987, vol='262', issue='19', page='9412-9420',
    authors=[('Johnstone', 'RM'), ('Adam', 'M'), ('Hammond', 'JR'), ('Orr', 'L'), ('Turbide', 'C')], nauth=5)
REFS['nobel2013'] = dict(doi='', pmid='', title='Press release: The Nobel Prize in Physiology or Medicine 2013 (Rothman JE, Schekman RW, Südhof TC)',
    journal='nobelprize.org', year=2013, vol='', issue='', page='', authors=[('Nobel Assembly at Karolinska Institutet', '')], nauth=1,
    url='https://www.nobelprize.org/prizes/medicine/2013/press-release/', web=True)

JABBR = {'Journal of Extracellular Vesicles': 'J Extracell Vesicles', 'The Journal of cell biology': 'J Cell Biol',
    'The Journal of experimental medicine': 'J Exp Med', 'Proceedings of the National Academy of Sciences': 'Proc Natl Acad Sci U S A',
    'British Journal of Haematology': 'Br J Haematol', 'Biochimica et Biophysica Acta (BBA) - Biomembranes': 'Biochim Biophys Acta',
    'Nature Cell Biology': 'Nat Cell Biol', 'Nature Medicine': 'Nat Med', 'Nature Methods': 'Nat Methods', 'Nature Protocols': 'Nat Protoc',
    'Current Protocols in Cell Biology': 'Curr Protoc Cell Biol', 'Cellular and Molecular Life Sciences': 'Cell Mol Life Sci',
    'Nanomedicine: Nanotechnology, Biology and Medicine': 'Nanomedicine', 'Scientific Reports': 'Sci Rep', 'Circulation Research': 'Circ Res',
    'American Journal of Physiology-Cell Physiology': 'Am J Physiol Cell Physiol', 'Cell Stem Cell': 'Cell Stem Cell', 'Cell Metabolism': 'Cell Metab',
    'Frontiers in Physiology': 'Front Physiol', 'The FASEB Journal': 'FASEB J', 'PLOS ONE': 'PLoS One', 'PLoS ONE': 'PLoS One',
    'Journal of Thrombosis and Haemostasis': 'J Thromb Haemost', 'Analytical Chemistry': 'Anal Chem', 'Lab on a Chip': 'Lab Chip',
    'PNAS Nexus': 'PNAS Nexus', 'Cells': 'Cells', 'Cell': 'Cell', 'Science': 'Science', 'Methods': 'Methods'}

def jab(j):
    for k, v in JABBR.items():
        if j.lower().startswith(k.lower()):
            return v
    return j

def clean_title(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', html.unescape(t)).strip()
    return t.rstrip('.')

def authors_vanc(r):
    au = r['authors']
    if r['key'] == 'vandeun2017evtrack':
        au = [('EV-TRACK Consortium', '')] + au
    names = []
    for fam, giv in au[:3]:
        ini = ''.join(w[0] for w in re.split(r'[\s\-\.]+', giv) if w) if giv else ''
        names.append((fam + ' ' + ini).strip())
    s = ', '.join(names)
    if len(au) > 3 or r.get('nauth', 0) > 3:
        s += ', et al'
    return s

src = open(os.path.join(DOC, '综述源稿v1.0.md')).read()
order = []
for m in re.finditer(r'\[(@[^\]]+)\]', src):
    for k in re.findall(r'@([\w]+)', m.group(1)):
        if k not in order:
            order.append(k)
missing = [k for k in order if k not in REFS]
assert not missing, missing
num = {k: i + 1 for i, k in enumerate(order)}

def repl(m):
    ks = re.findall(r'@([\w]+)', m.group(1))
    ns = sorted(num[k] for k in ks)
    # compress ranges
    out, i = [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(f'{ns[i]}–{ns[j]}' if j - i >= 2 else ','.join(map(str, ns[i:j + 1])))
        i = j + 1
    return '[' + ','.join(out) + ']'

body = re.sub(r'\[(@[^\]]+)\]', repl, src)

reflines = []
for k in order:
    r = REFS[k]; r['key'] = k
    t = clean_title(r['title'])
    if r.get('web'):
        line = f"{authors_vanc(r)}. {t}. {r['journal']}; {r['year']}. {r['url']}"
    else:
        vol = r.get('vol', ''); iss = r.get('issue', ''); pg = r.get('page', '')
        line = f"{authors_vanc(r)}. {t}. {jab(r['journal'])}. {r['year']};{vol}{'(' + iss + ')' if iss else ''}{':' + pg if pg else ''}."
        if r.get('doi'):
            line += f" doi:{r['doi']}."
        if r.get('pmid'):
            line += f" PMID: {r['pmid']}."
    reflines.append(f"{num[k]}. {line}")
body = body.replace('<!-- REFS -->', '\n'.join(reflines))
open(os.path.join(OUT, '综述v1.0.md'), 'w').write(body)

# BibTeX + RIS
bib, ris = [], []
for k in order:
    r = REFS[k]
    t = clean_title(r['title'])
    au = r['authors']
    if k == 'vandeun2017evtrack':
        au = [('EV-TRACK Consortium', '')] + au
    aus = ' and '.join(('{' + f + '}') if not g else f"{f}, {g}" for f, g in au)
    if r.get('web'):
        bib.append(f"@misc{{{k},\n  author = {{{{{au[0][0]}}}}},\n  title = {{{t}}},\n  year = {{{r['year']}}},\n  howpublished = {{\\url{{{r['url']}}}}},\n  note = {{Accessed 2026-10-31}}\n}}")
        ris.append(f"TY  - ELEC\nAU  - {au[0][0]}\nTI  - {t}\nPY  - {r['year']}\nUR  - {r['url']}\nID  - {k}\nER  - ")
        continue
    fields = [f"  author = {{{aus}}}", f"  title = {{{{{t}}}}}", f"  journal = {{{r['journal']}}}", f"  year = {{{r['year']}}}"]
    if r.get('vol'): fields.append(f"  volume = {{{r['vol']}}}")
    if r.get('issue'): fields.append(f"  number = {{{r['issue']}}}")
    if r.get('page'): fields.append(f"  pages = {{{r['page'].replace('-', '--')}}}")
    if r.get('doi'): fields.append(f"  doi = {{{r['doi']}}}")
    if r.get('pmid'): fields.append(f"  pmid = {{{r['pmid']}}}")
    bib.append(f"@article{{{k},\n" + ',\n'.join(fields) + "\n}")
    rl = ['TY  - JOUR'] + [f"AU  - {f}, {g}" if g else f"AU  - {f}" for f, g in au] + [f"TI  - {t}", f"JO  - {r['journal']}", f"J2  - {jab(r['journal'])}", f"PY  - {r['year']}"]
    if r.get('vol'): rl.append(f"VL  - {r['vol']}")
    if r.get('issue'): rl.append(f"IS  - {r['issue']}")
    if r.get('page'):
        p = r['page'].split('-')
        rl.append(f"SP  - {p[0]}")
        if len(p) > 1: rl.append(f"EP  - {p[1]}")
    if r.get('doi'): rl.append(f"DO  - {r['doi']}")
    if r.get('pmid'): rl.append(f"AN  - PMID:{r['pmid']}")
    rl += [f"ID  - {k}", 'ER  - ']
    ris.append('\n'.join(rl))
open(os.path.join(OUT, '参考文献v1.0.bib'), 'w').write('% EV methods atlas v1.0 - verified against Crossref/PubMed 2026-10-31\n\n' + '\n\n'.join(bib) + '\n')
open(os.path.join(OUT, '参考文献v1.0.ris'), 'w').write('\n'.join(ris) + '\n')

# CSV tables extracted from markdown tables by heading
def md_tables(text):
    tabs, cur = [], []
    for line in text.splitlines():
        if line.startswith('|'):
            cur.append(line)
        elif cur:
            tabs.append(cur); cur = []
    if cur: tabs.append(cur)
    res = []
    for tb in tabs:
        rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in tb if not re.match(r'^\|\s*-', l)]
        res.append(rows)
    return res
tabs = md_tables(body)
def save(rows, name):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows(rows)
for rows in tabs:
    h = rows[0]
    if h[0] == '方法' and '得率' in h: save(rows, '分离方法对比v1.0.csv')
    if h[0] == '年份': save(rows, '研究史时间线v1.0.csv')
    if h[0] == '技术': save(rows, '粒径计数方法v1.0.csv')
print('refs', len(order), 'tables', len(tabs))

# HTML + PDF
css = os.path.join(ROOT, '综述样式v1.0.css')
subprocess.run(['pandoc', os.path.join(OUT, '综述v1.0.md'), '-s', '--toc', '--toc-depth=2', '-f', 'markdown-yaml_metadata_block+yaml_metadata_block',
                '--metadata', 'lang=zh-CN', '--css', css, '--embed-resources', '-o', os.path.join(OUT, '综述v1.0.html')], check=True)
try:
    import weasyprint
except ImportError:
    print('weasyprint not installed: skipped PDF'); raise SystemExit
weasyprint.HTML(os.path.join(OUT, '综述v1.0.html')).write_pdf(os.path.join(OUT, '综述v1.0.pdf'))
print('done')
