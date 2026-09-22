import os
import subprocess
import sys
from pathlib import Path

output = Path('exports/run_20260919')
for script, day, label in [
    ('lt_screener.py', '2026-09-19', 'screener'),
    ('lt_allocator.py', '2026-09-19', 'allocator_20260919'),
    ('lt_allocator.py', '2026-09-21', 'allocator_preview_20260921'),
]:
    env = dict(os.environ, PYTHONIOENCODING='utf-8', NGAY_CHAY=day)
    result = subprocess.run([sys.executable, script], env=env, text=True,
                            encoding='utf-8', capture_output=True)
    (output / f'{label}.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    print(f'{label}: exit={result.returncode}')
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)
