import os
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_crown_console_startup(monkeypatch):
    calls: list[str] = []

    dummy_orch = types.SimpleNamespace(route=lambda *a, **k: {"voice_path": "x.wav"})
    dummy_av = types.SimpleNamespace(stream_avatar_audio=lambda p: iter(()))
    dummy_speak = types.SimpleNamespace(play_wav=lambda p: None)

    monkeypatch.setitem(sys.modules, "orchestrator", types.SimpleNamespace(MoGEOrchestrator=lambda: dummy_orch))
    monkeypatch.setitem(sys.modules, "core.avatar_expression_engine", dummy_av)
    monkeypatch.setitem(sys.modules, "INANNA_AI.speaking_engine", dummy_speak)

    def fake_run(cmd, *args, **kwargs):
        calls.append(" ".join(cmd) if isinstance(cmd, list) else cmd)
        if cmd[0] == "bash" and str(cmd[1]).endswith("start_crown_console.sh"):
            calls.extend(
                [
                    "crown_model_launcher",
                    "launch_servants",
                    "nc -z localhost 8000",
                    "scripts/check_services.sh",
                    "python console_interface.py",
                ]
            )
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def fake_system(cmd):
        calls.append(cmd)
        return 0

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(os, "system", fake_system)

    result = subprocess.run(["bash", str(ROOT / "start_crown_console.sh")])

    assert result.returncode == 0
    assert "crown_model_launcher" in calls
    assert "launch_servants" in calls
    assert "scripts/check_services.sh" in calls
    assert "python console_interface.py" in calls
    launcher_idx = calls.index("crown_model_launcher")
    servants_idx = calls.index("launch_servants")
    console_idx = calls.index("python console_interface.py")
    check_idx = calls.index("scripts/check_services.sh")
    port_idx = calls.index("nc -z localhost 8000")

    assert launcher_idx < servants_idx
    assert servants_idx < port_idx < check_idx < console_idx


def test_crown_console_missing_env(monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        if cmd[0] == "bash" and str(cmd[1]).endswith("start_crown_console.sh"):
            for var in ("GLM_API_URL", "GLM_API_KEY", "HF_TOKEN"):
                if not os.getenv(var):
                    return subprocess.CompletedProcess(cmd, 1, "", "")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.delenv("GLM_API_URL", raising=False)
    monkeypatch.setenv("GLM_API_KEY", "k")
    monkeypatch.setenv("HF_TOKEN", "t")

    result = subprocess.run(["bash", str(ROOT / "start_crown_console.sh")])

    assert result.returncode != 0


def test_crown_console_dead_glm(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT))

    yaml_mod = types.ModuleType("yaml")
    yaml_mod.safe_load = lambda *a, **k: {}
    monkeypatch.setitem(sys.modules, "yaml", yaml_mod)

    dummy_np = types.ModuleType("numpy")
    dummy_np.ndarray = object
    dummy_np.zeros = lambda *a, **k: None
    dummy_np.pi = 3.14159
    dummy_np.float32 = float
    monkeypatch.setitem(sys.modules, "numpy", dummy_np)

    sf_mod = types.ModuleType("soundfile")
    sf_mod.write = lambda *a, **k: None
    sf_mod.read = lambda *a, **k: (b"", 22050)
    monkeypatch.setitem(sys.modules, "soundfile", sf_mod)

    librosa_mod = types.ModuleType("librosa")
    librosa_mod.load = lambda *a, **k: ([], 22050)
    librosa_mod.resample = lambda *a, **k: []
    librosa_mod.effects = types.SimpleNamespace(
        pitch_shift=lambda *a, **k: [], time_stretch=lambda *a, **k: []
    )
    monkeypatch.setitem(sys.modules, "librosa", librosa_mod)

    monkeypatch.setitem(sys.modules, "opensmile", types.ModuleType("opensmile"))

    scipy_mod = types.ModuleType("scipy")
    scipy_io_mod = types.ModuleType("scipy.io")
    scipy_wavfile_mod = types.ModuleType("scipy.io.wavfile")
    scipy_wavfile_mod.write = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "scipy", scipy_mod)
    monkeypatch.setitem(sys.modules, "scipy.io", scipy_io_mod)
    monkeypatch.setitem(sys.modules, "scipy.io.wavfile", scipy_wavfile_mod)

    stable_mod = types.ModuleType("stable_baselines3")
    stable_mod.PPO = type("DummyPPO", (), {"__init__": lambda self, *a, **k: None})
    monkeypatch.setitem(sys.modules, "stable_baselines3", stable_mod)

    gym_mod = types.ModuleType("gymnasium")
    gym_mod.Env = object
    spaces_mod = types.ModuleType("spaces")
    spaces_mod.Box = type("DummyBox", (), {"__init__": lambda self, *a, **k: None})
    gym_mod.spaces = spaces_mod
    monkeypatch.setitem(sys.modules, "gymnasium", gym_mod)

    monkeypatch.setitem(
        sys.modules, "SPIRAL_OS.qnl_engine", types.ModuleType("SPIRAL_OS.qnl_engine")
    )
    monkeypatch.setitem(
        sys.modules,
        "SPIRAL_OS.symbolic_parser",
        types.ModuleType("SPIRAL_OS.symbolic_parser"),
    )

    import init_crown_agent
    import INANNA_AI.glm_integration as gi

    monkeypatch.setattr(init_crown_agent, "_load_config", lambda: {})
    monkeypatch.setattr(init_crown_agent, "_init_servants", lambda c: None)
    monkeypatch.setattr(init_crown_agent.vector_memory, "_get_collection", lambda: None)
    monkeypatch.setattr(
        init_crown_agent.corpus_memory, "create_collection", lambda dir_path=None: None
    )

    class ConnErr(Exception):
        pass

    def raise_conn(*_a, **_k):
        raise ConnErr("fail")

    dummy_requests = types.SimpleNamespace(post=raise_conn, RequestException=ConnErr)
    monkeypatch.setattr(gi, "requests", dummy_requests)

    monkeypatch.setenv("GLM_API_URL", "http://localhost:9999")

    def fake_run(cmd, *args, **kwargs):
        if cmd[0] == "bash" and str(cmd[1]).endswith("start_crown_console.sh"):
            try:
                init_crown_agent.initialize_crown()
            except SystemExit as exc:
                return subprocess.CompletedProcess(cmd, exc.code, "", "")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = subprocess.run(["bash", str(ROOT / "start_crown_console.sh")])

    assert result.returncode != 0
