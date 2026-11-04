"""Execute the app's real Java tokenizer against exact training-tokenizer outputs."""
import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, required=True)
    args = parser.parse_args()
    assets = ROOT / 'android/app/src/main/assets/wisemessage'
    cases = json.loads((assets / 'parity_cases.json').read_text(encoding='utf-8'))
    # Additional adversarial Unicode and token-boundary inputs are checked against
    # the actual Python tokenizer, not an independent imitation of its rules.
    extra = ['[CLS]message[SEP]', 'a[MASK]b[UNK]c[PAD]', '\u0085abc\u00a0def',
             '\ue000secret\u200btext', 'İSTANBUL Σ ΟΣ', 'a\u0301\u0327中文',
             'line\r\nline\tend', '中𠀀\U00030000文', '😀👩\u200d💻验证码',
             '  ', '合法简讯' * 256, 'ΟΣΟΣ ΤΕΛΟΣ Σ', 'a\u0378b']
    extra += [f'a{chr(code)}b' for code in range(32)]
    extra += [f'a{chr(code)}b' for code in (0x85, 0xa0, 0x1680, 0x2000, 0x2028, 0x2029, 0x2b820, 0x2b910, 0x2b920)]
    from wisemessage.tokenizer import MessageTokenizer
    reference = MessageTokenizer(assets / 'vocab.txt', 256)
    expected = reference.encode_batch(extra)
    cases += [{'id': f'edge-{index:02}', 'text': text,
               **{name: array[index].tolist() for name, array in expected.items()}}
              for index, text in enumerate(extra)]
    output = ROOT / 'artifacts/android/java_tokenizer'
    output.mkdir(parents=True, exist_ok=True)
    classes = output / 'classes'
    classes.mkdir(exist_ok=True)
    source = ROOT / 'android/app/src/main/java/hk/wisemessage/app/ml/WordPieceTokenizer.java'
    subprocess.run([str(args.jdk / 'bin/javac'), '-encoding', 'UTF-8', '-d', str(classes),
                    str(source), str(Path(__file__).with_name('TokenizerProbe.java'))], check=True)
    inputs = output / 'cases.base64.txt'
    inputs.write_text('\n'.join(base64.b64encode(case['text'].encode('utf-8')).decode('ascii') for case in cases) + '\n')
    result = subprocess.run([str(args.jdk / 'bin/java'), '-cp', str(classes), 'TokenizerProbe',
                             str(assets / 'vocab.txt'), str(inputs)], check=True, capture_output=True, text=True)
    actual = [json.loads(line) for line in result.stdout.splitlines()]
    failures = []
    if len(actual) != len(cases):
        raise ValueError('Java tokenizer did not return all cases')
    for case, value in zip(cases, actual):
        for name in ('input_ids', 'attention_mask', 'token_type_ids'):
            if case[name] != value[name]:
                failures.append({'id': case['id'], 'field': name,
                                 'first_differences': [i for i, (a, b) in enumerate(zip(case[name], value[name])) if a != b][:8]})
    report = {'passed': not failures, 'samples': len(cases), 'failures': failures,
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Exact Android Java tokenizer source on desktop JVM versus training tokenizer; not Android hardware execution'}
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
