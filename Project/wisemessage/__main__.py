"""WiseMessage prediction, API, and training command-line entry points."""

import argparse
import json
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wisemessage", description="Chinese SMS spam/scam classification with MindSpore")
    commands = parser.add_subparsers(dest="command", required=True)
    predict = commands.add_parser("predict", help="Classify supplied message text without fetching links")
    predict.add_argument("--model-dir", required=True)
    predict.add_argument("--device-target", choices=("CPU", "GPU"), default="CPU")
    predict.add_argument("--batch-size", type=int, default=32)
    source = predict.add_mutually_exclusive_group(required=True)
    source.add_argument("--message", action="append", help="Message text; may be repeated")
    source.add_argument("--input-json", help="UTF-8 JSON array of messages, or '-' for stdin")
    serve = commands.add_parser("serve", help="Serve a local message-classification API")
    serve.add_argument("--model-dir", required=True)
    serve.add_argument("--device-target", choices=("CPU", "GPU"), default="CPU")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8011)
    commands.add_parser("train", add_help=False, help="Run the standalone training workflow")
    args, remaining = parser.parse_known_args(argv)
    if args.command == "train":
        from .train import main as train_main
        return train_main(remaining)
    if remaining:
        parser.error("unrecognized arguments: " + " ".join(remaining))
    # Linux's dynamic loader reads LD_LIBRARY_PATH at process startup. Re-exec
    # once, before importing MindSpore, so WSL GPU libraries are discoverable.
    if args.device_target == "GPU" and os.environ.get("WISEMESSAGE_GPU_BOOTSTRAPPED") != "1":
        from .runtime import configure_environment
        configure_environment()
        environment = os.environ.copy()
        environment["WISEMESSAGE_GPU_BOOTSTRAPPED"] = "1"
        original_arguments = list(sys.argv[1:] if argv is None else argv)
        os.execvpe(sys.executable, [sys.executable, "-m", "wisemessage", *original_arguments], environment)
    if args.command == "predict":
        from .predictor import MessagePredictor
        if args.message is not None:
            messages = args.message
        else:
            raw = sys.stdin.read() if args.input_json == "-" else Path(args.input_json).read_text(encoding="utf-8")
            messages = json.loads(raw)
            if not isinstance(messages, list) or not messages:
                parser.error("--input-json must contain a nonempty JSON array of strings")
        predictor = MessagePredictor(args.model_dir, device_target=args.device_target, batch_size=args.batch_size)
        print(json.dumps({"results": predictor.predict(messages)}, ensure_ascii=False, indent=2))
        return 0
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    from .service import create_app
    import uvicorn
    uvicorn.run(create_app(args.model_dir, device_target=args.device_target), host=args.host,
                port=args.port, access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
