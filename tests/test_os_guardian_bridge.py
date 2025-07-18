import sys
from pathlib import Path
import types

sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
dummy_np = types.ModuleType("numpy")
dummy_np.clip = lambda val, lo, hi: val
dummy_np.mean = lambda arr: 0
sys.modules.setdefault("numpy", dummy_np)
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crown_prompt_orchestrator import crown_prompt_orchestrator
import os_guardian
import corpus_memory_logging as cml


class DummyGLM:
    def complete(self, prompt: str, quantum_context: str | None = None) -> str:
        return prompt


def test_osg_directive(monkeypatch):
    recorded = {}
    monkeypatch.setattr(os_guardian.planning, "plan", lambda text: recorded.setdefault("plan", text) or ["type_text('hi')"])
    calls = []
    monkeypatch.setattr(os_guardian.action_engine, "type_text", lambda txt: calls.append(txt))
    log_calls = []
    monkeypatch.setattr(cml, "log_interaction", lambda i, intent, res, o, **k: log_calls.append(intent))

    glm = DummyGLM()
    result = crown_prompt_orchestrator("/osg greet", glm)

    assert recorded["plan"] == "greet"
    assert calls == ["hi"]
    assert log_calls and log_calls[0] == {"action": "os_guardian"}
    assert result["action"] == "os_guardian"
