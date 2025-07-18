import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import types

dummy_np = types.ModuleType("numpy")
dummy_np.array = lambda x, dtype=None: x
dummy_np.asarray = lambda x: x
dummy_np.linalg = types.SimpleNamespace(norm=lambda v: 1.0)
dummy_np.ndarray = list
dummy_np.float32 = float
sys.modules.setdefault("numpy", dummy_np)
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))

import ritual_trainer
import spiral_cortex_memory as scm
import auto_retrain


def test_training_loop_triggers(tmp_path, monkeypatch):
    mem_file = tmp_path / "mem.jsonl"
    state_file = tmp_path / "state.json"
    entry = {"question": "q", "snippets": [{"snippet": "s"}], "sentiment": 0.0}
    mem_file.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    monkeypatch.setattr(scm, "INSIGHT_FILE", mem_file)
    monkeypatch.setattr(ritual_trainer, "STATE_FILE", state_file)
    monkeypatch.setattr(ritual_trainer, "THRESHOLD", 1)

    calls = []
    monkeypatch.setattr(auto_retrain, "system_idle", lambda: True)
    monkeypatch.setattr(auto_retrain, "trigger_finetune", lambda ds: calls.append(ds))

    monkeypatch.setenv("RITUAL_TRAIN_INTERVAL", "0")
    monkeypatch.setattr(ritual_trainer.time, "sleep", lambda s: None)

    ritual_trainer.run_training(True, loop=True, max_cycles=1)

    assert calls
