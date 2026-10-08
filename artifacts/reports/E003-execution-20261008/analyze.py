"""Báo cáo từ artifact E003 đã freeze; không training hoặc chọn lại model."""
import json
import math
import shutil
from collections import Counter
from pathlib import Path

import torch

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import write_json
from ai_exam_monitoring.training.config import load_config, verify_approval
from ai_exam_monitoring.training.data import verify_dataset
from ai_exam_monitoring.training.metrics import evaluate_scores

ROOT = Path(__file__).resolve().parents[3]
EXEC = Path(__file__).resolve().parent
OUT = ROOT / 'artifacts/reports/E003'
TARGETS = ['phone_use', 'looking_around']


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def verify_artifacts(folder):
    pins = read(f'{folder}/checksums.json')
    for name, checksum in pins.items():
        path = (ROOT / folder / name).resolve()
        assert path.is_relative_to((ROOT / folder).resolve())
        assert sha256_file(path) == checksum, path
    assert not any('test' in name.lower() for name in pins)
    return pins


def report(rows):
    if not rows:
        return {'records': 0, 'reason': 'empty_slice', 'metrics': None}
    scores = torch.tensor([r['scores'] for r in rows], dtype=torch.float64)
    values = torch.tensor([[v or 0 for v in r['targets']] for r in rows], dtype=torch.float64)
    mask = torch.tensor([r['mask'] for r in rows], dtype=torch.bool)
    result = evaluate_scores(scores, values, mask, 0.5)
    bce = {}
    for c, name in enumerate(TARGETS):
        losses = []
        for row in rows:
            if row['mask'][c]:
                p = row['scores'][c]
                probability = p if row['targets'][c] else 1 - p
                if probability == 0:
                    raise ValueError('BCE vô hạn: cần đối chiếu logits, không clip')
                losses.append(-math.log(probability))
        bce[name] = sum(losses) / len(losses) if losses else None
    result['probability_bce_float64'] = bce
    result['macro_probability_bce_float64'] = (
        sum(bce.values()) / 2 if all(v is not None for v in bce.values()) else None)
    return result


def outcome(row, c):
    if not row['mask'][c]:
        return 'unknown'
    return ('T' if (row['scores'][c] >= 0.5) == bool(row['targets'][c]) else 'F') + (
        'P' if row['scores'][c] >= 0.5 else 'N')


def main():
    OUT.mkdir(exist_ok=False)
    config = load_config(ROOT / 'configs/experiments/E003.yaml')
    verify_approval(config, ROOT)
    records = verify_dataset(ROOT / config.dataset, config)
    metadata = {r.sample_id: r for r in records}
    pins = {folder: verify_artifacts(f'outputs/{folder}')
            for folder in ['E003', 'E003-smoke', 'E003-val-evaluation']}
    run = read('outputs/E003/run.json')
    smoke = read('outputs/E003-smoke/run.json')
    assert run['status'] == smoke['status'] == 'FINISHED'
    assert smoke['completed_epochs'] == 3 and len(smoke['resumed_at']) == 1
    assert not run['environment']['git_dirty'] and not smoke['environment']['git_dirty']
    predictions = {s: read(f'outputs/E003/predictions-{s}.json') for s in ['train', 'val']}
    metrics = read('outputs/E003/metrics.json')
    assert predictions['val'] == read('outputs/E003-val-evaluation/predictions.json')
    assert metrics['val'] == read('outputs/E003-val-evaluation/metrics.json')
    for split, rows in predictions.items():
        assert sorted(r['sample_id'] for r in rows) == sorted(
            r.sample_id for r in records if r.usage == split)
        for row in rows:
            m = metadata[row['sample_id']]
            assert row['targets'] == list(m.target_values) and row['mask'] == list(m.target_mask)
        computed = report(rows)
        assert computed['targets'] == metrics[split]['targets']
        assert abs(computed['macro_probability_bce_float64'] -
                   metrics[split]['macro_masked_bce']) < 1e-6
    preparation = read('artifacts/reports/E003-preparation-20261008/verification.json')
    previous_pin = preparation['historical_predictions']
    assert sha256_file(ROOT / previous_pin['path']) == previous_pin['sha256']
    previous = read(previous_pin['path'])
    old_ids = set(preparation['historical_val_ids'])
    historical = [r for r in predictions['val'] if r['sample_id'] in old_ids]
    added = [r for r in predictions['val'] if r['sample_id'] not in old_ids]
    assert len(historical) == len(previous) == 13 and len(added) == 37
    constant = []
    prevalence = []
    for c in range(2):
        known = [r['targets'][c] for r in predictions['train'] if r['mask'][c]]
        prevalence.append(sum(known) / len(known))
    for row in predictions['val']:
        constant.append({**row, 'scores': prevalence})
    constant_metrics = report(constant)
    constant_bce = constant_metrics['macro_probability_bce_float64']
    assert abs(constant_bce - preparation['constant_val_bce']['macro']) < 1e-12
    slices = {}
    errors = {}
    for split, rows in predictions.items():
        slices[split] = {'all': report(rows), 'by_source': {}, 'by_group': {}, 'by_normal': {}}
        for field, key in [('source_id', 'by_source'), ('group_id', 'by_group')]:
            for value in sorted({r[field] for r in rows}):
                slices[split][key][value] = report([r for r in rows if r[field] == value])
        for value in sorted({metadata[r['sample_id']].normal_review for r in rows}):
            slices[split]['by_normal'][value] = report([
                r for r in rows if metadata[r['sample_id']].normal_review == value])
        errors[split] = [{**row, 'target': target, 'outcome': outcome(row, c),
                          'score': row['scores'][c]}
                         for row in rows for c, target in enumerate(TARGETS)
                         if outcome(row, c) in ['FP', 'FN']]
    slices['historical_val'] = report(historical)
    slices['added_val'] = report(added)
    old = {r['sample_id']: r for r in previous}
    transitions = []
    for row in historical:
        before = old[row['sample_id']]
        assert row['targets'] == before['targets'] and row['mask'] == before['mask']
        for c, target in enumerate(TARGETS):
            if row['mask'][c]:
                transitions.append({'sample_id': row['sample_id'], 'target': target,
                                    'before': outcome(before, c), 'after': outcome(row, c),
                                    'score_before': before['scores'][c],
                                    'score_after': row['scores'][c],
                                    'delta_score': row['scores'][c] - before['scores'][c]})
    previous_metrics = report(previous)
    comparison = {'E002_historical13': previous_metrics,
                  'E003_historical13': slices['historical_val'],
                  'delta_probability_bce_float64': slices['historical_val'][
                      'macro_probability_bce_float64'] - previous_metrics[
                          'macro_probability_bce_float64'],
                  'transitions': transitions,
                  'transition_counts': dict(Counter(
                      f"{r['before']}->{r['after']}" for r in transitions))}
    primary = metrics['val']['macro_masked_bce']
    summary = {'status': 'FINISHED', 'owner': config.owner, 'parent': 'E002',
               'primary_bce': primary, 'constant_bce': constant_bce,
               'delta_bce': primary - constant_bce, 'h1_supported': primary < constant_bce,
               'best_epoch': run['best_epoch'], 'epochs': run['completed_epochs'],
               'train_val_bce_gap': primary - metrics['train']['macro_masked_bce'],
               'error_counts': {s: dict(Counter(r['outcome'] for r in rows))
                                for s, rows in errors.items()},
               'run': run, 'best_sha256': pins['E003']['best.pt'],
               'test_evaluated': False, 'promotion': False,
               'decision': 'Tiếp tục nghiên cứu, không promotion; không tuning lại E003.'}
    for name, value in [('summary', summary), ('slices', slices), ('comparison', comparison),
                        ('error-analysis', errors), ('constant-baseline', constant_metrics)]:
        write_json(OUT / f'{name}.json', value)
    for name in ['run.json', 'metrics.json', 'history.json', 'learning-curve.svg',
                 'resolved-config.json', 'code-provenance.json']:
        shutil.copyfile(ROOT / 'outputs/E003' / name, OUT / name)
    for folder, checksums in pins.items():
        write_json(OUT / f'{folder}-artifact-checksums.json', checksums)
    write_json(EXEC / 'validation-reproducibility.json', {
        'status': 'PASS', 'exact_scores': True, 'exact_metrics': True,
        'validation_records': 50, 'test_inference': False,
        'dataset_reverified': True, 'smoke_resume_verified': True,
        'artifact_checksums_verified': True})
    print(json.dumps({'primary': primary, 'constant': constant_bce, 'delta': primary-constant_bce,
                      'historical_delta': comparison['delta_probability_bce_float64'],
                      'best': run['best_epoch'], 'epochs': run['completed_epochs']}))


if __name__ == '__main__':
    main()
