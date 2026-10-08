"""Kiểm hậu kiểm độc lập: artifact, lựa chọn epoch, bảo toàn và hồ sơ local."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import write_json
from ai_exam_monitoring.training.config import load_config, verify_approval
from ai_exam_monitoring.training.data import verify_dataset

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent


def read(path):
    return json.loads((root / path).read_text(encoding='utf-8'))


config = load_config(root / 'configs/experiments/E003.yaml')
verify_approval(config, root)
current = verify_dataset(root / config.dataset, config)
parent = load_config(root / 'configs/experiments/E002.yaml')
old = verify_dataset(root / parent.dataset, parent)
indexed = {r.sample_id: r for r in current}
for row in old:
    new = indexed[row.sample_id]
    for field in ['source', 'crop', 'group', 'target_values', 'target_mask', 'usage', 'split']:
        assert getattr(row, field) == getattr(new, field), (row.sample_id, field)
history = read('outputs/E003/history.json')
run = read('outputs/E003/run.json')
best = min(history, key=lambda row: row['val_loss'])
assert best['epoch'] == run['best_epoch'] == 45
reference, stale = float('inf'), 0
for i, row in enumerate(history, 1):
    assert row['epoch'] == i and stale < config.patience
    if row['val_loss'] < reference - config.min_delta:
        reference, stale = row['val_loss'], 0
    else:
        stale += 1
assert stale == config.patience and len(history) == run['completed_epochs'] == 64
for name in ['E003', 'E003-smoke', 'E003-val-evaluation']:
    for path, expected in read(f'outputs/{name}/checksums.json').items():
        assert sha256_file(root / 'outputs' / name / path) == expected
protocol = (root / 'docs/experiments/E003-protocol.md').read_text(encoding='utf-8')
reversed_space = re.sub(r'known (.) 0.5', r'known \g<1>0.5', protocol)
assert hashlib.sha256(reversed_space.encode()).hexdigest() == (
    '52acca0ff64329203afe26c6901825a6a746d2eeecf4b4c0e4b1b55a7d977421')
approval = read('docs/experiments/E003-approval.json')
assert sha256_file(root / approval['protocol']['path']) == approval['protocol']['sha256']
pins = read('artifacts/reports/E003-preparation-20261008/proposal-checksums.json')['sha256']
for path, expected in pins.items():
    if path not in ['docs/experiments/E003-protocol.md', 'docs/experiments/E003-approval.json']:
        assert sha256_file(root / path) == expected
commands = []
for command in [
    [str(root / '.venv/Scripts/python.exe'), '-m', 'ruff', 'check', str(out)],
    [str(root / '.venv/Scripts/python.exe'), 'scripts/check_repo.py', '--require-git'],
    ['git', 'diff', '--check'],
]:
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    commands.append({'command': command, 'exit_code': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, commands[-1]
write_json(out / 'final-verification.json', {
    'status': 'PASS', 'preserved_parent_records': len(old), 'test_inference': False,
    'raw_minimum_best_epoch': 45, 'early_stop_epoch': 64, 'stale': stale,
    'protocol_whitespace_only_drift_verified': True, 'preparation_snapshot_preserved': True,
    'dataset_and_output_checksums': 'PASS', 'commands': commands,
})
links = 0
for path in [root / 'docs/experiments/E003-results.md',
             root / 'docs/experiments/E003-runbook.md', out / 'README.md']:
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if '://' not in link:
            # File checksum hồ sơ được ghi ngay sau kiểm liên kết.
            target = (path.parent / link.split('#')[0]).resolve()
            assert target.exists() or target == out / 'handoff-checksums.json', target
            links += 1
files = sorted(p for folder in [out, root / 'artifacts/reports/E003']
               for p in folder.iterdir() if p.is_file() and p.name != 'handoff-checksums.json')
files += [root / f'outputs/{name}.dvc' for name in ['E003', 'E003-smoke', 'E003-val-evaluation']]
files += [root / f'docs/experiments/E003-{name}' for name in ['results.md', 'runbook.md',
                                                          'approval.json', 'protocol.md']]
write_json(out / 'handoff-checksums.json', {
    'status': 'FINISHED', 'markdown_links_checked': links,
    'files': {p.relative_to(root).as_posix(): sha256_file(p) for p in files},
})
print(f'FINAL PASS; {links} links; {len(files)} pinned files')
