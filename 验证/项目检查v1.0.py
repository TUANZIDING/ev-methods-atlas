#!/usr/bin/env python3
"""Repository checks for ev-methods-atlas (standard library only)."""
import csv, json, os, re, sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPT = {'README.md', 'LICENSE', '.gitignore'}
errors = []
files = []
for d, _, fs in os.walk(ROOT):
    if '/.git' in d or d.endswith('.git') or '/pdb' in d:
        continue
    for f in fs:
        files.append(os.path.relpath(os.path.join(d, f), ROOT))

for f in files:
    name = os.path.basename(f)
    if name in EXEMPT:
        continue
    if '_' in name:
        errors.append(f'文件名含下划线: {f}')
    if not re.search(r'v\d+\.\d+', name):
        errors.append(f'文件名缺版本号: {f}')

# only our own PDF is allowed (no paywalled full texts)
for f in files:
    if f.lower().endswith('.pdf') and f != os.path.join('文档', '综述v1.0.pdf'):
        errors.append(f'不允许的 PDF: {f}')

# SVG well-formed
for f in files:
    if f.endswith('.svg'):
        try:
            ET.parse(os.path.join(ROOT, f))
        except ET.ParseError as e:
            errors.append(f'SVG 无法解析: {f}: {e}')

# references: every cited key exists, every entry has DOI or PMID
meta = json.load(open(os.path.join(ROOT, '文档', '参考文献', '文献元数据v1.0.json'), encoding='utf-8'))
src = open(os.path.join(ROOT, '文档', '综述源稿v1.0.md'), encoding='utf-8').read()
keys = set(re.findall(r'@(\w+)', ' '.join(re.findall(r'\[(@[^\]]+)\]', src))))
manual = {'chargaff1946', 'johnstone1987', 'nobel2013'}
for k in sorted(keys - set(meta) - manual):
    errors.append(f'源稿引用了未核对的文献: {k}')
bib = open(os.path.join(ROOT, '文档', '参考文献', '参考文献v1.0.bib'), encoding='utf-8').read()
for k in keys:
    if '{' + k + ',' not in bib:
        errors.append(f'BibTeX 缺少条目: {k}')
for k, v in meta.items():
    if not (v.get('doi') or v.get('pmid')):
        errors.append(f'文献无 DOI/PMID: {k}')

# local links in markdown resolve
for f in files:
    if not f.endswith('.md'):
        continue
    text = open(os.path.join(ROOT, f), encoding='utf-8').read()
    for link in re.findall(r'(?:\]\(|src=")([^)"#\s]+)', text):
        if link.startswith(('http://', 'https://', 'mailto:')):
            continue
        p = os.path.normpath(os.path.join(ROOT, os.path.dirname(f), link))
        if not os.path.exists(p):
            errors.append(f'{f} 中的链接不存在: {link}')

# CSV readable
for f in files:
    if f.endswith('.csv'):
        rows = list(csv.reader(open(os.path.join(ROOT, f), encoding='utf-8-sig')))
        if len(rows) < 2:
            errors.append(f'CSV 为空: {f}')

if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'项目检查通过：{len(files)} 个文件，{len(keys)} 条引用。')
