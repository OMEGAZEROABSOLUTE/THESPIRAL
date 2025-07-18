from __future__ import annotations

"""Simple seven dimensional music utility used in tests."""

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa

from MUSIC_FOUNDATION.qnl_utils import quantum_embed
def embedding_to_params(_emb):
    """Return pitch, tempo and volume from embedding."""
    return 0.0, 1.0, 1.0


def analyze_seven_planes(waveform: np.ndarray, sample_rate: int) -> dict:
    """Return spectral metrics mapped to seven planes.

    Metrics:
        physical.rms: Root mean square amplitude.
        emotional.centroid: Spectral centroid (Hz).
        mental.flux: Mean spectral flux.
        astral.bandwidth: Spectral bandwidth (Hz).
        etheric.rolloff: Spectral rolloff (Hz).
        celestial.flatness: Spectral flatness.
        divine.zcr: Zero crossing rate.
    """

    wave = waveform.mean(axis=1) if waveform.ndim == 2 else waveform
    rms = float(librosa.feature.rms(y=wave).mean())
    centroid = float(
        librosa.feature.spectral_centroid(y=wave, sr=sample_rate).mean()
    )
    onset_env = librosa.onset.onset_strength(y=wave, sr=sample_rate)
    flux = float(np.mean(np.abs(np.diff(onset_env)))) if len(onset_env) > 1 else 0.0
    bandwidth = float(
        librosa.feature.spectral_bandwidth(y=wave, sr=sample_rate).mean()
    )
    rolloff = float(
        librosa.feature.spectral_rolloff(y=wave, sr=sample_rate).mean()
    )
    flatness = float(librosa.feature.spectral_flatness(y=wave).mean())
    zcr = float(librosa.feature.zero_crossing_rate(y=wave).mean())

    return {
        "physical": {"rms": rms},
        "emotional": {"centroid": centroid},
        "mental": {"flux": flux},
        "astral": {"bandwidth": bandwidth},
        "etheric": {"rolloff": rolloff},
        "celestial": {"flatness": flatness},
        "divine": {"zcr": zcr},
    }


def generate_quantum_music(context: str, emotion: str, *, output_dir: Path = Path(".")) -> Path:
    embed = quantum_embed(context)
    _pitch, _tempo, _vol = embedding_to_params(embed)
    sr = 44100
    duration = 0.25 + 0.05 * len(context)
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * 220 * t)
    out = Path(output_dir) / "quantum.wav"
    sf.write(out, wave, sr, subtype="PCM_16")
    planes = analyze_seven_planes(wave, sr)
    planes.setdefault("physical", {})["element"] = "bass"
    (out.with_suffix(".json")).write_text(json.dumps({"planes": planes}), encoding="utf-8")
    return out


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    parser.add_argument("--secret")
    opts = parser.parse_args(args)

    data, sr = sf.read(opts.input, always_2d=False)
    sf.write(opts.output, data, sr, subtype="PCM_16")

    if opts.secret:
        from MUSIC_FOUNDATION.synthetic_stego import embed_data
        embed_data(Path("human_layer.wav"), opts.secret)

    planes = analyze_seven_planes(data, sr)
    planes.setdefault("physical", {})["element"] = "bass"
    Path(opts.output).with_suffix(".json").write_text(json.dumps({"planes": planes}), encoding="utf-8")


if __name__ == "__main__":
    main()
