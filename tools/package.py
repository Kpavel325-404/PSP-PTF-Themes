#!/usr/bin/env python3
"""Package this complete repository as one deterministic ZIP snapshot.
SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from check_package import check

ROOT = Path(__file__).resolve().parents[1]


def files():
    ignored = {'.git', '__pycache__', '.venv', 'node_modules'}
    return sorted(path for path in ROOT.rglob('*') if path.is_file()
                  and not ignored.intersection(path.relative_to(ROOT).parts)
                  and path.suffix != '.pyc' and path.name != 'ci-result.json')


def checksums():
    (ROOT / 'FILES_SHA256.txt').write_text(''.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}\n'
        for path in files() if path.name != 'FILES_SHA256.txt'))


def package(output):
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError('Put the ZIP output outside the repository directory')
    themes = json.loads((ROOT / 'verification/latest.json').read_text())
    rebuild = json.loads((ROOT / 'verification/rebuild.json').read_text())
    if themes['status'] != 'PASS' or themes['theme_count'] != 9 or themes['graphic_resources'] != 661 or rebuild['status'] != 'PASS' or rebuild['theme_count'] != 9:
        raise ValueError('Complete verification and source rebuilding before packaging')
    checksums()
    check()
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = files()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            member = zipfile.ZipInfo('PSP-PTF-Themes/' + path.relative_to(ROOT).as_posix(), date_time=(2026, 10, 9, 11, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.create_system = 3
            member.external_attr = 0o100644 << 16
            archive.writestr(member, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() or len(archive.namelist()) != len(paths):
            raise ValueError('ZIP CRC or entry count failed')
        for path in paths:
            if archive.read('PSP-PTF-Themes/' + path.relative_to(ROOT).as_posix()) != path.read_bytes():
                raise ValueError('ZIP member byte comparison failed: ' + path.name)
    report = dict(file=output.name, bytes=output.stat().st_size, sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  entries=len(paths), crc_test='PASS', every_member_byte_comparison='PASS')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    package(args.output)
