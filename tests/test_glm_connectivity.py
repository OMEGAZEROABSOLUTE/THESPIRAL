import sys
import types
from pathlib import Path
import pytest

# Stub modules required by init_crown_agent import
sys.modules.setdefault("yaml", types.ModuleType("yaml"))
sys.modules.setdefault("vector_memory", types.ModuleType("vector_memory"))
sys.modules.setdefault("INANNA_AI.corpus_memory", types.ModuleType("corpus_memory"))
sys.modules.setdefault("servant_model_manager", types.ModuleType("servant_model_manager"))

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import init_crown_agent
import INANNA_AI.glm_integration as gi


def test_check_glm_success(caplog):
    integration = types.SimpleNamespace(endpoint="http://x", complete=lambda p: "pong")
    with caplog.at_level("INFO"):
        init_crown_agent._check_glm(integration)
    assert any("GLM test response" in r.message for r in caplog.records)


def test_check_glm_no_url():
    integration = types.SimpleNamespace(endpoint="", complete=lambda p: "pong")
    with pytest.raises(RuntimeError):
        init_crown_agent._check_glm(integration)


def test_check_glm_network_error():
    def raise_err(p):
        raise ValueError("boom")
    integration = types.SimpleNamespace(endpoint="http://x", complete=raise_err)
    with pytest.raises(RuntimeError):
        init_crown_agent._check_glm(integration)


def test_check_glm_error_message():
    integration = types.SimpleNamespace(endpoint="http://x", complete=lambda p: gi.SAFE_ERROR_MESSAGE)
    with pytest.raises(RuntimeError):
        init_crown_agent._check_glm(integration)
