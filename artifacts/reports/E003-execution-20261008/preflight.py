"""Kiểm trước chạy; chạy từ clean checkout với workspace riêng, không inference."""
import json
import platform
import shutil
import subprocess
from importlib.metadata import version
from pathlib import Path

import psutil

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import code_identity, write_json
from ai_exam_monitoring.training.config import load_config, verify_approval
from ai_exam_monitoring.training.data import verify_dataset

workspace = Path(__file__).resolve().parents[3]
checkout = Path.cwd()
out = Path(__file__).resolve().parent
assert subprocess.check_output(['git', 'status', '--porcelain'], text=True) == ''
for name in ['E003', 'E003-smoke']:
    config = load_config(checkout / f'configs/experiments/{name}.yaml')
    verify_approval(config, workspace)
    assert (checkout / f'configs/experiments/{name}.yaml').read_bytes() == (
        workspace / f'configs/experiments/{name}.yaml').read_bytes()
approval = json.loads((workspace / config.approval_ref).read_text(encoding='utf-8'))
assert sha256_file(checkout / approval['protocol']['path']) == approval['protocol']['sha256']
assert sha256_file(workspace / config.weights) == config.weights_sha256
records = verify_dataset(workspace / config.dataset, config)
lock = (checkout / 'requirements/classifier-cpu-lock.txt').read_text().splitlines()
packages = {line.split('==')[0]: version(line.split('==')[0]) for line in lock
            if '==' in line and not line.startswith('#')}
assert all(packages[line.split('==')[0]] == line.split('==')[1] for line in lock
           if '==' in line and not line.startswith('#'))
for name in ['E003', 'E003-smoke', 'E003-val-evaluation']:
    assert not (workspace / 'outputs' / name).exists()
checks = []
for command in [
    [str(workspace / 'outputs/E001-env/Scripts/python.exe'), '-m', 'pip', 'check'],
    [str(workspace / '.venv/Scripts/python.exe'), '-m', 'ruff', 'check', 'src', 'tests', 'scripts'],
    [str(workspace / '.venv/Scripts/python.exe'), '-m', 'compileall', '-q',
     'src', 'tests', 'scripts'],
    [str(workspace / '.venv/Scripts/python.exe'), 'scripts/check_repo.py', '--require-git'],
]:
    result = subprocess.run(command, capture_output=True, text=True)
    checks.append({'command': command, 'exit_code': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, checks[-1]
write_json(out / 'preflight.json', {
    'status': 'PASS', 'git_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], text=True).strip(), 'git_dirty': False,
    'code': code_identity(), 'python': platform.python_version(), 'packages': packages,
    'records': len(records), 'disk_free_bytes': shutil.disk_usage(workspace).free,
    'ram_available_bytes': psutil.virtual_memory().available, 'checks': checks,
    'protocol_sha256': approval['protocol']['sha256'], 'configs': approval['configs'],
})
print('PREFLIGHT PASS')
