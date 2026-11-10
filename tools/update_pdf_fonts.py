"""Embed complete pinned upstream Tinos fonts, including directional arrows."""
import base64
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '4106aab86ddefe26d58a69745e04ae9479d22993'
FONTS = {
    'r': ('Regular', '60a0e8ef0c04dd5dd69ffe91025fa2ae5836cbd35600a82ba031977557e2cb61'),
    'b': ('Bold', '393269dbab8899f938db19783eca5eac92eb431f7ae0ab45b8349ca895f1a06b'),
}


def main():
    fonts = {}
    manifest = {}
    for key, (weight, expected) in FONTS.items():
        source = f'https://raw.githubusercontent.com/googlefonts/tinos/{COMMIT}/fonts/ttf/Tinos-{weight}.ttf'
        with urllib.request.urlopen(source, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Unexpected font checksum: {weight}')
        fonts[key] = base64.b64encode(data).decode('ascii')
        manifest[key] = dict(source=source, sha256=expected, bytes=len(data))
    target = ROOT / 'index.html'
    html = target.read_text()
    pattern = r'(<script type="application/json" id="pdfFonts">).*?(</script>)'
    html, count = re.subn(pattern, lambda m:m[1]+json.dumps(fonts)+m[2], html, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one embedded font block')
    target.write_text(html)
    (ROOT / 'vendor/pdf-fonts.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
