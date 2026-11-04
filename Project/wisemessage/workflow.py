"""Standalone WiseMessage training supervisor and live progress reporting."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

from .training import save_json, now, file_hash


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}


def run(run_dir, budget_minutes=45, data_dir=None, init_model_dir=None, epochs=6, learning_rate=5e-5):
    from .runtime import configure_environment
    configure_environment()
    run_dir = Path(run_dir).resolve()
    data_dir = Path(data_dir or ROOT / 'data/prepared').resolve()
    init_model_dir = Path(init_model_dir).resolve() if init_model_dir else None
    run_dir.mkdir(parents=True, exist_ok=True)
    identity_path = run_dir / 'supervisor.pid.json'
    status = read_json(run_dir / 'status.json')
    status.update(status='running', project='WiseMessage', framework='MindSpore',
                  pretrained_model='hfl/minirbt-h256', pid=os.getpid(),
                  started_at=status.get('started_at', now()), results={})
    def update(**values):
        status.update(values)
        status['updated_at'] = now()
        save_json(run_dir / 'status.json', status)
    process = None
    started = time.perf_counter()
    try:
        update(phase='preparing_inputs', stage_description='Waiting for verified MiniRBT and prepared labelled Chinese messages')
        deadline = time.time() + 900
        while not (ROOT / 'artifacts/pretrained/manifest.json').is_file() or not (data_dir / 'manifest.json').is_file():
            if time.time() > deadline:
                raise TimeoutError('Prepared model and datasets are not ready after15minutes')
            update(phase='preparing_inputs', elapsed_seconds=time.perf_counter() - started)
            time.sleep(3)
        source_manifest = read_json(data_dir / 'manifest.json')
        for name, entry in source_manifest['files'].items():
            path = data_dir / entry['filename']
            if file_hash(path) != entry['sha256']:
                raise ValueError(f'Dataset identity mismatch: {name}')
        save_json(run_dir / 'workflow_config.json', {'project': 'WiseMessage', 'framework': 'MindSpore',
            'model': 'hfl/minirbt-h256', 'budget_minutes': budget_minutes,
            'max_epochs': epochs, 'learning_rate': learning_rate, 'max_length': 256,
            'data_dir': str(data_dir), 'init_model_dir': str(init_model_dir) if init_model_dir else None,
            'labels': ['normal', 'spam', 'scam'], 'all_encoder_layers_trainable': True,
            'data_manifest_sha256': file_hash(data_dir / 'manifest.json'),
            'provisional_quality_requirements': {'macro_f1': .8, 'scam_recall': .8, 'max_normal_false_positive_rate': .1},
            'test_selection_policy': 'No held-out rows train the model. Initial external baseline failure motivated domain repair; the original external test is now a seen diagnostic, and new domain tests are reserved before training.',
            'all_files_retained': True})
        def stage(name, status_file):
            nonlocal process
            arguments = [sys.executable, '-B', '-u', '-m', 'wisemessage.workflow', '--worker', name,
                         '--run-dir', str(run_dir), '--budget-minutes', str(budget_minutes),
                         '--data-dir', str(data_dir), '--epochs', str(epochs), '--learning-rate', str(learning_rate)]
            if init_model_dir:
                arguments += ['--init-model-dir', str(init_model_dir)]
            log_path = run_dir / f'{name}.log'
            with log_path.open('a', encoding='utf-8') as log:
                process = subprocess.Popen(arguments, cwd=ROOT, env=os.environ.copy(),
                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            update(phase=name, child_pid=process.pid, stage_description=f'WiseMessage {name}',
                   training_started=True)
            end = time.time() + budget_minutes * 60 + 300
            while process.poll() is None:
                progress = read_json(status_file)
                update(phase=progress.get('phase', name), progress=progress,
                       elapsed_seconds=time.perf_counter() - started)
                if time.time() > end:
                    process.terminate()
                    raise TimeoutError(f'{name} exceeded its time budget; see retained logs and checkpoints')
                time.sleep(2)
            if process.returncode:
                raise RuntimeError(f'{name} exited {process.returncode}; inspect {log_path.name}')
            process = None
            update(child_pid=None, progress=read_json(status_file))
        stage('training', run_dir / 'training_status.json')
        training = read_json(run_dir / 'training_result.json')
        status['results']['training'] = training
        update(selected_model_dir=training['model_dir'])
        stage('evaluation', run_dir / 'evaluation_status.json')
        evaluation = read_json(run_dir / 'evaluation/performance.json')
        status['results']['evaluation'] = evaluation
        qualified = bool(evaluation['main_test_requirements_passed'] and evaluation['converted_traditional_requirements_passed']
                         and evaluation.get('external_binary_requirements_passed', False)
                         and evaluation.get('supplementary_requirements_passed', True)
                         and training.get('validation_requirements_passed', False))
        summary = {'status': 'completed', 'framework': 'MindSpore', 'model_dir': training['model_dir'],
            'training': training, 'performance': evaluation,
            'heldout_requirements_passed': qualified,
            'internal_requirements_passed': bool(evaluation['main_test_requirements_passed'] and evaluation['converted_traditional_requirements_passed']),
            'production_ready': False,
            'native_traditional_external_validation_complete': False,
            'external_binary_test_semantics': 'normal versus unwanted; does not establish independent scam-class recall',
            'elapsed_seconds': time.perf_counter() - started, 'completed_at': now(),
            'all_files_retained': True, 'linkwise_modified': False}
        save_json(run_dir / 'result.json', summary)
        update(status='completed', phase='completed', stage_description='WiseMessage model trained; performance reports ready',
               heldout_requirements_passed=qualified, production_ready=False,
               metrics=evaluation['datasets']['test']['metrics'],
               traditional_metrics=evaluation['datasets']['test_traditional_converted']['metrics'],
               results=status['results'], selected_model_dir=training['model_dir'],
               elapsed_seconds=time.perf_counter() - started, eta_seconds=0)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
        return summary
    except BaseException as exc:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed', phase='failed',
               child_pid=None, error=f'{type(exc).__name__}: {exc}', traceback=traceback.format_exc())
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', help='New run directory; defaults to a fresh timestamped directory')
    parser.add_argument('--budget-minutes', type=int, default=45)
    parser.add_argument('--background', action='store_true')
    parser.add_argument('--worker', choices=['training', 'evaluation'])
    parser.add_argument('--data-dir', default=str(ROOT / 'data/prepared'))
    parser.add_argument('--init-model-dir')
    parser.add_argument('--epochs', type=int, default=6)
    parser.add_argument('--learning-rate', type=float, default=5e-5)
    args = parser.parse_args(argv)
    if not 10 <= args.budget_minutes <= 90:
        parser.error('budget-minutes must be10..90')
    if not 1 <= args.epochs <= 12 or not 0 < args.learning_rate <= .001:
        parser.error('epochs must be1..12 and learning-rate must be >0 and <=.001')
    from .runtime import configure_environment
    configure_environment()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYTHONPATH'] = str(ROOT)
    run_dir = Path(args.run_dir) if args.run_dir else ROOT / 'artifacts/runs' / ('wisemessage_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    if args.worker:
        if args.worker == 'training':
            from .training import train
            train(ROOT / 'artifacts/pretrained', args.data_dir, run_dir, epochs=args.epochs,
                  learning_rate=args.learning_rate, init_model_dir=args.init_model_dir,
                  budget_minutes=max(5, args.budget_minutes - 10))
        else:
            from .evaluation import evaluate
            evaluate(run_dir / 'model', args.data_dir, run_dir / 'evaluation')
        return 0
    if (run_dir / 'training_result.json').exists() or (run_dir / 'training_status.json').exists():
        parser.error('Use a fresh run directory; existing training records are preserved')
    if args.background:
        run_dir.mkdir(parents=True, exist_ok=True)
        arguments = [sys.executable, '-B', '-u', '-m', 'wisemessage.workflow', '--run-dir', str(run_dir),
                     '--budget-minutes', str(args.budget_minutes), '--data-dir', args.data_dir,
                     '--epochs', str(args.epochs), '--learning-rate', str(args.learning_rate)]
        if args.init_model_dir:
            arguments += ['--init-model-dir', args.init_model_dir]
        with (run_dir / 'supervisor.log').open('a', encoding='utf-8') as log:
            process = subprocess.Popen(arguments, cwd=ROOT, env=os.environ.copy(),
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        save_json(run_dir / 'supervisor.pid.json', {'pid': process.pid, 'command': arguments, 'started_at': now()})
        print(json.dumps({'pid': process.pid, 'run_dir': str(run_dir), 'status': 'started'}), flush=True)
        return 0
    run(run_dir, args.budget_minutes, args.data_dir, args.init_model_dir, args.epochs, args.learning_rate)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
