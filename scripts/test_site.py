#!/usr/bin/env python3
"""Offline, read-only checks for generated public HTML and coupon data."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://tototete909090-collab.github.io/couponova/'
PREFIX = '/couponova/'
GENERATED = ['index.html', 'en/index.html', 'en/shein/index.html', 'shein/index.html', 'shein/how-to-use/index.html', 'shein/new-user-code/index.html', 'editorial-policy/index.html']

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.in_script = False
        self.script = ''
        self.schemas = []
        self.links = []
        self.canonical = []
        self.alternates = {}
        self.description = None
        self.lang = None
        self.h1s = 0
        self.copies = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'head': self.in_head = True
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1s += 1
        if tag == 'script' and a.get('type') == 'application/ld+json':
            assert self.in_head, 'JSON-LD outside head'
            self.in_script = True
            self.script = ''
        if tag == 'meta' and a.get('name') == 'description':
            assert self.in_head, 'Description outside head'
            self.description = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical':
            assert self.in_head, 'Canonical outside head'
            self.canonical.append(a['href'])
        if tag == 'link' and a.get('hreflang'):
            assert self.in_head
            self.alternates[a['hreflang']] = a['href']
        if a.get('data-copy'): self.copies.append(a['data-copy'])
        if tag in ['a', 'link'] and a.get('href'): self.links.append(a['href'])
        if tag in ['script', 'img'] and a.get('src'): self.links.append(a['src'])
    def handle_endtag(self, tag):
        if tag == 'head': self.in_head = False
        if tag == 'script' and self.in_script:
            self.schemas.append(json.loads(self.script))
            self.in_script = False
    def handle_data(self, value):
        if self.in_script: self.script += value
        elif not self.in_head: self.text.append(value)


def file_for_url(url):
    path = urlparse(url).path
    assert path.startswith(PREFIX), f'Wrong project path: {url}'
    relative = unquote(path[len(PREFIX):])
    target = ROOT / relative
    if not relative or path.endswith('/'): target = target / 'index.html'
    return target

pages = {}
for name in GENERATED:
    source = (ROOT / name).read_text(encoding='utf-8')
    assert source.lstrip().lower().startswith('<!doctype html>'), name
    assert '```' not in source, name
    assert 'H3RAW' not in source, name
    assert 'couponova.cfd' not in source, name
    assert 'مجرّبة عالميًا' not in source, name
    assert 'verified_working' not in source, name
    p = Page(); p.feed(source)
    assert p.h1s == 1, name
    assert p.description and len(p.canonical) == 1, name
    expected = BASE + (name[:-10] if name.endswith('index.html') else name)
    assert p.canonical[0] == expected, (name, p.canonical, expected)
    assert p.copies == (['S4T32'] if name != 'editorial-policy/index.html' else []), (name, p.copies)
    for url in p.links:
        u = urlparse(url)
        if u.scheme in ['data', 'mailto', 'tel']: continue
        if u.netloc and u.netloc != urlparse(BASE).netloc: continue
        if url.startswith('#'): continue
        assert file_for_url(url).exists(), (name, url)
    visible = ' '.join(' '.join(p.text).split())
    for schema in p.schemas:
        for value in schema.get('@graph', [schema]):
            assert value.get('@type') not in ['Product', 'Offer', 'AggregateRating']
            if value.get('@type') == 'FAQPage':
                for q in value['mainEntity']:
                    assert q['name'] in visible, (name, q['name'])
                    assert q['acceptedAnswer']['text'] in visible, (name, q['name'])
    pages[p.canonical[0]] = p
    print('PASS', name)

for url, p in pages.items():
    if p.lang in ['ar', 'en'] and ('en' if p.lang == 'ar' else 'ar') in p.alternates:
        other = p.alternates['en' if p.lang == 'ar' else 'ar']
        assert pages[other].alternates[p.lang] == url, (url, other)
        assert pages[other].alternates['x-default'] == p.alternates['x-default']

urls = [loc.text for loc in ET.parse(ROOT / 'sitemap.xml').getroot().findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls) == 9 and len(set(urls)) == 9
assert all(file_for_url(url).exists() for url in urls)
assert set(pages).issubset(urls)
assert 'https://tototete909090-collab.github.io/couponova/shein/new-user-code/' in urls

data = json.loads((ROOT / 'data/coupons.json').read_text())
assert data['primaryCode'] == 'S4T32'
assert [c['code'] for c in data['coupons'] if c['published']] == ['S4T32']
c = data['coupons'][0]
assert c['type'] == 'app_search_campaign' and c['displayedDiscount'] is None
assert c['testedAt'] is None and c['country'] is None
assert not c['checkoutDiscountVerified'] and not c['worldwideAvailabilityVerified']
assert [(v['discountPercent'], v['minimumSpend'], v['maximumDiscount']) for v in c['observedCoupons']] == [(50,79,40),(40,179,80)]
assert all(v['minimumSpendOperator'] == '>' and v['expiresAt'] is None and not v['currentlyAvailableVerified'] for v in c['observedCoupons'])
assert (ROOT / 'googlebfdc6b4f70c32d24.html').exists()
print('PASS data, reciprocal hreflang, nine sitemap URLs and verification file retained')
