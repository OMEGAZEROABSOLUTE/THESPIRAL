import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from SPIRAL_OS import seven_dimensional_music as sdm


def test_analyze_seven_planes_populated():
    sr = 22050
    t = np.linspace(0, 0.5, sr // 2, endpoint=False)
    wave = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    planes = sdm.analyze_seven_planes(wave, sr)
    expected = {
        "physical",
        "emotional",
        "mental",
        "astral",
        "etheric",
        "celestial",
        "divine",
    }
    assert set(planes) == expected
    for val in planes.values():
        assert isinstance(val, dict)
        assert val
