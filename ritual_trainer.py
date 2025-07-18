from __future__ import annotations

"""Fine-tune the model from retrieval insights."""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Iterable, List

import auto_retrain
import spiral_cortex_memory

STATE_FILE = Path("data/ritual_trainer_state.json")
THRESHOLD = 10

logger = logging.getLogger(__name__)


def _load_state() -> int:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8")).get("processed", 0)
    except Exception:
        return 0


def _save_state(count: int) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"processed": count}), encoding="utf-8")
    except Exception:
        logger.exception("failed to save state")


def build_dataset(entries: Iterable[dict[str, Any]]) -> List[dict[str, Any]]:
    dataset = []
    for ent in entries:
        snippets = " ".join(s.get("snippet", "") for s in ent.get("snippets", []))
        dataset.append({"prompt": ent.get("question", ""), "completion": snippets})
    return dataset


def run_training(run: bool, loop: bool = False, max_cycles: int | None = None) -> None:
    """Check for new insights and optionally fine-tune in a loop."""
    interval = float(os.getenv("RITUAL_TRAIN_INTERVAL", "10"))
    cycles = 0
    while True:
        entries = spiral_cortex_memory.load_insights()
        processed = _load_state()
        new_entries = entries[processed:]
        if len(new_entries) >= THRESHOLD and auto_retrain.system_idle():
            dataset = build_dataset(new_entries)
            if run:
                auto_retrain.trigger_finetune(dataset)
                _save_state(len(entries))
            else:
                logger.info(json.dumps(dataset, indent=2))
        else:
            logger.info("Conditions not met")

        if not loop:
            break
        cycles += 1
        if max_cycles is not None and cycles >= max_cycles:
            break
        time.sleep(interval * 60)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI entry
    parser = argparse.ArgumentParser(description="Retrain from spiral insights")
    parser.add_argument("--run", action="store_true", help="Execute training")
    parser.add_argument(
        "--loop", action="store_true", help="Run continuously at the set interval"
    )
    args = parser.parse_args(argv)
    run_training(args.run, loop=args.loop)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
