import importlib
import os
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# dummy libs
pyautogui = types.ModuleType("pyautogui")
pyautogui.click = lambda *a, **k: None
pyautogui.typewrite = lambda *a, **k: None
pyautogui.scroll = lambda *a, **k: None
sys.modules["pyautogui"] = pyautogui

class DummyDriver:
    def get(self, url):
        pass

webdriver = types.SimpleNamespace(Firefox=lambda: DummyDriver())
selenium = types.ModuleType("selenium")
selenium.webdriver = webdriver
sys.modules["selenium"] = selenium
sys.modules["selenium.webdriver"] = webdriver


def test_yaml_policy_limits(tmp_path, monkeypatch):
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        "{"
        "\"policy\": \"allow\"," \
        " \"allowed_commands\": [\"foo\"]," \
        " \"command_limits\": {\"foo\": {\"max\": 1}}," \
        " \"allowed_domains\": [\"example.com\"]," \
        " \"domain_limits\": {\"example.com\": {\"max\": 1}}" \
        "}"
    )
    monkeypatch.setenv("OG_POLICY_FILE", str(policy))

    safety = importlib.import_module("os_guardian.safety")
    importlib.reload(safety)
    action_engine = importlib.import_module("os_guardian.action_engine")
    importlib.reload(action_engine)

    calls = []

    def fake_run(a, capture_output=True, text=True, check=False):
        calls.append(list(a))
        class CP:
            def __init__(self):
                self.args = a
                self.stdout = "ok"
        return CP()

    monkeypatch.setattr(action_engine.subprocess, "run", fake_run)
    monkeypatch.setattr(action_engine.safety, "register_undo", lambda f: None)
    res1 = action_engine.run_command(["foo"])
    res2 = action_engine.run_command(["foo"])
    assert res1 is not None
    assert res2 is None
    assert calls == [["foo"]]

    drv1 = action_engine.open_url("http://example.com")
    drv2 = action_engine.open_url("http://example.com")
    assert drv1 is not None
    assert drv2 is None

