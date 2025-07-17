import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _make_stub_bin(tmp_path: Path, record: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python").write_text(
        f"#!/bin/sh\n" f"echo \"python $@\" >> '{record}'\n"
    )
    (bin_dir / "python").chmod(0o755)
    (bin_dir / "nc").write_text(
        f"#!/bin/sh\n" f"echo \"nc $@\" >> '{record}'\n" f"exit 0\n"
    )
    (bin_dir / "nc").chmod(0o755)
    return bin_dir

def _write_stub(file: Path, msg: str, record: Path) -> None:
    file.write_text(f"#!/bin/sh\necho {msg} >> '{record}'\n")
    file.chmod(0o755)

def test_crown_console_startup(tmp_path):
    record = tmp_path / "calls.txt"
    bin_dir = _make_stub_bin(tmp_path, record)
    _write_stub(tmp_path / "crown_model_launcher.sh", "crown_model_launcher", record)
    _write_stub(tmp_path / "launch_servants.sh", "launch_servants", record)

    start_script = tmp_path / "start_crown_console.sh"
    start_script.write_text((ROOT / "start_crown_console.sh").read_text())
    start_script.chmod(0o755)

    (tmp_path / "secrets.env").write_text(
        "GLM_API_URL=http://localhost:8000\nGLM_API_KEY=key\nHF_TOKEN=tok\n"
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = subprocess.run([
        "bash",
        str(start_script),
    ], cwd=tmp_path, env=env, capture_output=True, text=True)

    assert result.returncode == 0
    lines = record.read_text().splitlines()
    assert "crown_model_launcher" in lines
    assert "launch_servants" in lines
    assert lines[-1] == "python console_interface.py"
    assert lines.index("crown_model_launcher") < lines.index("launch_servants") < lines.index("python console_interface.py")
