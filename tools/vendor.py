"""Refresh pinned browser bundles; verify npm registry SHA-512 before extraction."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / 'vendor'
PACKAGES = [
    ('xlsx', '0.18.5', ['dist/xlsx.full.min.js']),
    ('html-docx-js', '0.3.1', ['dist/html-docx.js']),
    ('jszip', '3.10.1', ['dist/jszip.min.js']),
    ('@cantoo/pdf-lib', '2.11.1', ['dist/pdf-lib.min.js']),
    ('@pdf-lib/fontkit', '1.1.1', ['dist/fontkit.umd.min.js']),
    ('pdfjs-dist', '3.11.174', ['build/pdf.min.js', 'build/pdf.worker.min.js']),
    ('diff', '5.2.0', ['dist/diff.min.js']),
    ('docx-preview', '0.3.3', ['dist/docx-preview.min.js']),
]


def main():
    ROOT.mkdir(exist_ok=True)
    manifest = []
    for name, version, paths in PACKAGES:
        with urllib.request.urlopen(f'https://registry.npmjs.org/{name}/{version}') as r:
            meta = json.load(r)
        dist = meta['dist']
        integrity = dist['integrity']
        algorithm, expected = integrity.split('-', 1)
        if algorithm != 'sha512':
            raise ValueError(f'Unsupported integrity algorithm: {algorithm}')
        with urllib.request.urlopen(dist['tarball']) as r:
            data = r.read()
        if base64.b64encode(hashlib.sha512(data).digest()).decode() != expected:
            raise ValueError(f'Integrity mismatch: {name}@{version}')
        files = {}
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            for path in paths:
                content = archive.extractfile('package/' + path).read()
                target = ROOT / Path(path).name
                target.write_bytes(content)
                files[target.name] = hashlib.sha256(content).hexdigest()
            license_paths = [m for m in archive.getmembers()
                             if m.isfile() and m.name.count('/') == 1
                             and Path(m.name).name.lower().startswith(('license', 'licence'))]
            if not license_paths:
                # fontkit's published package declares MIT in package.json and
                # README rather than shipping a separate license file.
                for path in ['README.md', 'package.json']:
                    target = ROOT / (name.replace('/', '-').replace('@', '') + '-' + path)
                    target.write_bytes(archive.extractfile('package/' + path).read())
            for member in license_paths:
                target = ROOT / (name.replace('/', '-').replace('@', '') + '-' + Path(member.name).name)
                target.write_bytes(archive.extractfile(member).read())
        manifest.append(dict(package=name, version=version, source=dist['tarball'],
                             integrity=integrity, files=files))
        print(f'Verified {name}@{version}')
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
