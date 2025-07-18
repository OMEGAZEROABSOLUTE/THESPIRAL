import sys
import types
from pathlib import Path

ptk_mod = types.ModuleType("prompt_toolkit")
ptk_mod.PromptSession = lambda *a, **k: None
sys.modules.setdefault("prompt_toolkit", ptk_mod)
ptk_hist = types.ModuleType("prompt_toolkit.history")
ptk_hist.FileHistory = lambda *a, **k: None
sys.modules.setdefault("prompt_toolkit.history", ptk_hist)
ptk_patch = types.ModuleType("prompt_toolkit.patch_stdout")
ptk_patch.patch_stdout = lambda: None
sys.modules.setdefault("prompt_toolkit.patch_stdout", ptk_patch)

init_mod = types.ModuleType("init_crown_agent")
init_mod.initialize_crown = lambda: object()
sys.modules.setdefault("init_crown_agent", init_mod)

orch_mod = types.ModuleType("orchestrator")
orch_mod.MoGEOrchestrator = lambda: types.SimpleNamespace(route=lambda *a, **k: {})
sys.modules.setdefault("orchestrator", orch_mod)

aee_mod = types.ModuleType("core.avatar_expression_engine")
aee_mod.stream_avatar_audio = lambda p: iter(())
sys.modules.setdefault("core.avatar_expression_engine", aee_mod)

inanna_mod = types.ModuleType("INANNA_AI")
speaking_stub = types.ModuleType("INANNA_AI.speaking_engine")
speaking_stub.play_wav = lambda p: None
inanna_mod.speaking_engine = speaking_stub
sys.modules.setdefault("INANNA_AI", inanna_mod)
sys.modules.setdefault("INANNA_AI.speaking_engine", speaking_stub)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import console_interface
from core import context_tracker
import emotional_state


class DummySession:
    def __init__(self, prompts):
        self._prompts = prompts

    def prompt(self, prompt_str):
        if not self._prompts:
            raise EOFError
        return self._prompts.pop(0)


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_emotion_command(monkeypatch):
    monkeypatch.setattr(console_interface, "initialize_crown", lambda: object())
    monkeypatch.setattr(console_interface, "PromptSession", lambda history=None: DummySession(["/emotion joy", "/exit"]))
    monkeypatch.setattr(console_interface, "patch_stdout", lambda: DummyContext())

    captured = {}
    monkeypatch.setattr(emotional_state, "set_last_emotion", lambda e: captured.setdefault("emotion", e))

    console_interface.run_repl([])

    assert captured["emotion"] == "joy"


def test_avatar_command(monkeypatch):
    monkeypatch.setattr(console_interface, "initialize_crown", lambda: object())
    monkeypatch.setattr(console_interface, "PromptSession", lambda history=None: DummySession(["/avatar A", "/exit"]))
    monkeypatch.setattr(console_interface, "patch_stdout", lambda: DummyContext())

    called = {}
    monkeypatch.setattr(console_interface.avatar_expression_engine, "stream_avatar_audio", lambda p: called.setdefault("path", p) or iter(()))

    context_tracker.state.avatar_style = None
    console_interface.run_repl([])

    assert context_tracker.state.avatar_style == "A"
    assert isinstance(called.get("path"), Path)
