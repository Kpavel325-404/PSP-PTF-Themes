#!/usr/bin/env python3
"""Rebuild all nine themes in a temporary directory and compare original hashes.

SPDX-License-Identifier: GPL-3.0-only
Canonical PSP/THEME files and prepared source assets are never overwritten.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from PIL import __version__ as pillow_version
import numpy

ROOT = Path(__file__).resolve().parents[1]


def rebuild():
    themes = json.loads((ROOT / 'themes.json').read_text())
    log, results = [], []
    commands = {
        'vista': [[sys.executable, 'build_theme.py']],
        'glass': [[sys.executable, 'source/build_themes.py']],
        'classic-five': [[sys.executable, 'source/build_assets.py'], ['node', 'source/gim_codec.js'],
                         [sys.executable, 'source/build_ptf.py']],
    }
    with tempfile.TemporaryDirectory(prefix='psp-theme-rebuild-') as temporary:
        for family, steps in commands.items():
            destination = Path(temporary) / family
            shutil.copytree(ROOT / 'sources' / family, destination,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'dist', 'build', 'deliverables'))
            for command in steps:
                label = ' '.join([Path(command[0]).name] + command[1:])
                print(f'Building {family}: {label}', flush=True)
                process = subprocess.run(command, cwd=destination, capture_output=True, text=True)
                log.append(f'{family}: {label}\n{process.stdout}{process.stderr}')
                if process.returncode:
                    raise RuntimeError(f'{family} failed:\n{process.stdout}\n{process.stderr}')
            for theme in [t for t in themes if t['source_family'] == family]:
                path = destination / ('deliverables' if family == 'classic-five' else 'dist') / theme['file']
                rebuilt = path.read_bytes()
                expected = (ROOT / 'PSP/THEME' / theme['file']).read_bytes()
                actual_hash = hashlib.sha256(rebuilt).hexdigest()
                if rebuilt != expected or actual_hash != theme['sha256']:
                    raise ValueError('Source rebuild differs from the archived original: ' + theme['file'])
                results.append(dict(file=theme['file'], status='PASS', sha256=actual_hash,
                                    bytes=len(rebuilt), byte_identical=True,
                                    graphics_stage='redrawn icons and re-encoded GIM' if family == 'classic-five' else 'prepared indexed PNG artwork'))
                print(f'PASS rebuild {theme["file"]}', flush=True)
    report = dict(status='PASS', rebuilt_at=datetime.now(timezone.utc).isoformat(),
                  theme_count=len(results), byte_identical_rebuild=True,
                  environment=dict(python=platform.python_version(), pillow=pillow_version,
                                   numpy=numpy.__version__, node=subprocess.check_output(['node', '--version'], text=True).strip()),
                  hardware_test='NOT_RUN', themes=results)
    folder = ROOT / 'verification'
    folder.mkdir(exist_ok=True)
    (folder / 'rebuild.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (folder / 'rebuild.log').write_text('\n'.join(log))
    print(f'PASS: {len(results)} source builds match the original PTF bytes.')
    return report


if __name__ == '__main__':
    rebuild()
