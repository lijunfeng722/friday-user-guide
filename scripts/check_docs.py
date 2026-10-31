#!/usr/bin/env python3
"""Check documentation links, publication inputs and optionally built HTML."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.venv','site','.cache','.artifacts','__pycache__'}
PRIVATE_SUFFIXES={'.sqlite','.sqlite3','.db','.pem','.key','.mp4','.mov','.wav','.ses','.zip','.patch'}
RULES={
 'local_home':re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/'),
 'local_capture':re.compile(r'codex-clipboard-|/var/folders/'),
 'private_key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'provider_key':re.compile(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}'),
 'github_key':re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
 'jwt':re.compile(r'\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}'),
}
LINK=re.compile(r'(!?)\[([^\]]*)\]\(([^\s)]+)(?:\s+"[^"]*")?\)')
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.ids=set();self.links=[];self.lang=None;self.images=0;self.missing_alt=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if tag=='html':self.lang=a.get('lang')
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag=='img':
   self.images+=1
   if not a.get('alt'):self.missing_alt+=1

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--built',type=Path);args=parser.parse_args()
 errors=[];pages=list((ROOT/'docs').rglob('*.md'));images=set()
 for p in ROOT.rglob('*'):
  relative=p.relative_to(ROOT)
  if not p.is_file() or any(x in EXCLUDED for x in relative.parts):continue
  if p.suffix.lower() in PRIVATE_SUFFIXES:errors.append(f'private file type: {relative}')
  if p.name.startswith('.env'):errors.append(f'environment file: {relative}')
  # Vendored, unchanged third-party bytes are checked separately by digest.
  if 'vendor' in relative.parts:continue
  try:source=p.read_text()
  except (UnicodeDecodeError,OSError):continue
  if p==Path(__file__).resolve():continue
  for name,rule in RULES.items():
   if rule.search(source):errors.append(f'publication input: {relative} ({name})')
 for p in [*pages,ROOT/'README.md',*([ROOT/'USER_MANUAL.md'] if (ROOT/'USER_MANUAL.md').exists() else [])]:
  source=p.read_text()
  if re.search(r'__[A-Z_]+__|Screenshot needed|\[Project Name\]|\[username\]',source):errors.append(f'template marker: {p.relative_to(ROOT)}')
  if len(re.findall(r'^```',source,re.M))%2:errors.append(f'unclosed fence: {p.relative_to(ROOT)}')
  for image,alt,href in LINK.findall(source):
   u=urlsplit(href)
   if u.scheme or href.startswith('#'):continue
   path=(p.parent/unquote(u.path)).resolve()
   if not path.is_relative_to(ROOT) or not path.is_file():errors.append(f'missing link: {p.relative_to(ROOT)} -> {href}')
   if image:
    images.add(path)
    if not alt.strip():errors.append(f'empty image label: {p.relative_to(ROOT)}')
    if path.exists() and not path.read_bytes().startswith((b'\xff\xd8',b'\x89PNG',b'<svg',b'<?xml')):errors.append(f'unsupported image bytes: {href}')
 vendor=ROOT/'docs/assets/vendor/mermaid.min.js'
 manifest=json.loads((ROOT/'vendor-versions.json').read_text())
 if hashlib.sha256(vendor.read_bytes()).hexdigest()!=manifest['mermaid']['sha256']:errors.append('vendored Mermaid digest changed')
 built_pages=0
 if args.built:
  build=args.built.resolve();parsed={}
  for p in build.rglob('*.html'):
   html=HTML();html.feed(p.read_text());parsed[p]=html
   if html.lang not in {'zh','zh-CN'}:errors.append(f'HTML language: {p.relative_to(build)}')
   if html.missing_alt:errors.append(f'HTML image label: {p.relative_to(build)}')
  for p,html in parsed.items():
   if p.name in {'404.html'}:continue
   for href in html.links:
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    target=(build/unquote(u.path).lstrip('/')) if u.path.startswith('/') else p.parent/unquote(u.path)
    if not u.path:target=p
    if target.is_dir():target=target/'index.html'
    target=target.resolve()
    if not target.is_relative_to(build) or not target.exists():errors.append(f'built link: {p.relative_to(build)} -> {href}');continue
    if u.fragment and target in parsed and unquote(u.fragment) not in parsed[target].ids:errors.append(f'anchor: {p.relative_to(build)} -> {href}')
  built_pages=len(parsed)
 report={'markdown_pages':len(pages),'screenshots':len(images),'built_html_pages':built_pages,'errors':errors,'publication_inputs':'PASS' if not errors else 'FAIL'}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 raise SystemExit(bool(errors))
if __name__=='__main__':main()
