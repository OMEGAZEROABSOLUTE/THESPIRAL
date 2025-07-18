from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_vast_start_launch(monkeypatch):
    calls: list[str] = []

    def fake_run(cmd, *args, **kwargs):
        joined = " ".join(str(c) for c in cmd) if isinstance(cmd, list) else str(cmd)
        calls.append(joined)
        if cmd[0] == "bash" and str(cmd[1]).endswith("vast_start.sh"):
            if "--setup" in cmd:
                calls.append(f"bash {ROOT / 'scripts/setup_vast_ai.sh'} --download")
                calls.append(f"bash {ROOT / 'scripts/setup_glm.sh'}")
            calls.extend(
                [
                    "docker-compose up -d INANNA_AI",
                    "nc -z localhost 8000",
                    f"python -m webbrowser {ROOT / 'web_console/index.html'}",
                    "docker-compose logs -f INANNA_AI",
                ]
            )
            return subprocess.CompletedProcess(cmd, 0, "crown> ", "")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("GLM_API_URL", "http://localhost:8001")
    monkeypatch.setenv("DEEPSEEK_URL", "http://localhost:8002")
    monkeypatch.setenv("MISTRAL_URL", "http://localhost:8003")
    monkeypatch.setenv("KIMI_K2_URL", "http://localhost:8004")

    result = subprocess.run(["bash", str(ROOT / "scripts/vast_start.sh")])

    assert result.returncode == 0
    assert "docker-compose up -d INANNA_AI" in calls
    assert "docker-compose logs -f INANNA_AI" in calls
    assert "crown>" in result.stdout
