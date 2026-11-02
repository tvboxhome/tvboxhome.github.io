"""Submit canonical sitemap URLs only after their exact content is public."""
import argparse
import json
from pathlib import Path
import time
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = 'tvboxhome.github.io'
BASE = 'https://' + HOST


def payload(root=ROOT):
    urls = [n.text for n in ET.parse(root / 'sitemap.xml').getroot().findall('{*}url/{*}loc')]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError('Empty or duplicate sitemap')
    for url in urls:
        p = urlsplit(url)
        if p.scheme != 'https' or p.netloc != HOST or p.query or p.fragment or '..' in p.path.split('/') or not p.path.endswith('/'):
            raise ValueError('Unexpected sitemap URL')
        content = (root / p.path.lstrip('/') / 'index.html').read_text()
        if 'noindex' in content or ('href="' + url + '"') not in content:
            raise ValueError('Non-canonical or excluded page')
    return {'host': HOST, 'key': (root / 'indexnow-key.txt').read_text().strip(),
            'keyLocation': BASE + '/indexnow-key.txt', 'urlList': urls}


def ready(data):
    targets = [(BASE + '/indexnow-key.txt', ROOT / 'indexnow-key.txt')]
    targets += [(url, ROOT / urlsplit(url).path.lstrip('/') / 'index.html') for url in data['urlList']]
    for url, local in targets:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'Cache-Control': 'no-cache'}), timeout=15) as r:
                if r.status != 200 or r.read() != local.read_bytes():
                    return False
        except (OSError, TimeoutError):
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Validate locally, without network requests')
    args = parser.parse_args()
    data = payload()
    if args.check:
        print('Validated', len(data['urlList']), 'canonical URLs; no requests sent')
        return
    for attempt in range(12):
        if ready(data):
            break
        if attempt == 11:
            raise RuntimeError('Current Pages content not published; nothing submitted')
        print('Waiting for current Pages content', attempt + 1, flush=True)
        time.sleep(20)
    request = urllib.request.Request('https://api.indexnow.org/indexnow', data=json.dumps(data).encode(),
                                     headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 202):
            raise RuntimeError('IndexNow rejected submission')
        print('IndexNow HTTP', response.status, 'URLs:', len(data['urlList']), '(received, not proof of indexing)')


if __name__ == '__main__':
    main()
