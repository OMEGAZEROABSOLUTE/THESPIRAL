import sys
from pathlib import Path
import types

# Provide dummy numpy so fallback_tts can import
np_stub = types.ModuleType("numpy")
np_stub.linspace = lambda start, stop, num, endpoint=False: [0.0] * num
np_stub.sin = lambda arr: [0.0 for _ in arr]
np_stub.pi = 3.14159
np_stub.float32 = float
sys.modules.setdefault("numpy", np_stub)
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from INANNA_AI import fallback_tts


def test_sine_wave_used_when_pyttsx3_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(fallback_tts, "pyttsx3", None)
    called = {}

    def fake_sine(text: str, path: Path, pitch: float) -> None:
        called["args"] = (text, path, pitch)
        Path(path).write_bytes(b"x")

    monkeypatch.setattr(fallback_tts, "_sine_wave", fake_sine)
    monkeypatch.setattr(fallback_tts.tempfile, "gettempdir", lambda: str(tmp_path))

    out = fallback_tts.speak("hello", pitch=0.5)
    assert Path(out).exists()
    assert called["args"] == ("hello", Path(out), 0.5)


def test_pyttsx3_failure_falls_back(tmp_path, monkeypatch):
    class DummyEngine:
        def save_to_file(self, text, path):
            pass
        def runAndWait(self):
            raise RuntimeError("fail")
        def getProperty(self, name):
            return 100
        def setProperty(self, name, value):
            pass

    dummy_mod = types.SimpleNamespace(init=lambda: DummyEngine())
    called = {}

    def fake_sine(text: str, path: Path, pitch: float) -> None:
        called["args"] = (text, path, pitch)
        Path(path).write_bytes(b"x")

    monkeypatch.setattr(fallback_tts, "pyttsx3", dummy_mod)
    monkeypatch.setattr(fallback_tts, "_sine_wave", fake_sine)
    monkeypatch.setattr(fallback_tts.tempfile, "gettempdir", lambda: str(tmp_path))

    out = fallback_tts.speak("hi", pitch=-0.2)
    assert Path(out).exists()
    assert called["args"] == ("hi", Path(out), -0.2)
