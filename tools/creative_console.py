from __future__ import annotations

"""Command line tools for creative music experiments."""

import argparse
from pathlib import Path
import json

from music_generation import generate_from_text
from play_ritual_music import compose_ritual_music
from qnl_engine import hex_to_song
from scipy.io.wavfile import write



def _cmd_music(args: argparse.Namespace) -> None:
    path = generate_from_text(args.prompt, args.model)
    print(path)


def _cmd_ritual(args: argparse.Namespace) -> None:
    out = compose_ritual_music(args.emotion, args.symbol, hide=args.stego)
    print(out)


def _cmd_qnl_song(args: argparse.Namespace) -> None:
    phrases, waveform = hex_to_song(args.hex)
    print(json.dumps(phrases, indent=2, ensure_ascii=False))
    if waveform.size:
        out_file = Path("qnl_song.wav")
        write(out_file, 44100, waveform)
        print(out_file)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Creative music utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    music_p = sub.add_parser("music", help="Generate music from text")
    music_p.add_argument("prompt", help="Description of the desired music")
    music_p.add_argument(
        "--model",
        choices=["musicgen", "riffusion", "musenet"],
        default="musicgen",
        help="Model to use",
    )
    music_p.set_defaults(func=_cmd_music)

    ritual_p = sub.add_parser("ritual", help="Compose ritual music")
    ritual_p.add_argument("--emotion", required=True, help="Emotion driving the tone")
    ritual_p.add_argument("--symbol", required=True, help="Ritual symbol")
    ritual_p.add_argument("--stego", action="store_true", help="Hide ritual phrase")
    ritual_p.set_defaults(func=_cmd_ritual)

    qnl_p = sub.add_parser("qnl-song", help="Generate a QNL song from hex")
    qnl_p.add_argument("--hex", required=True, help="Hexadecimal string")
    qnl_p.set_defaults(func=_cmd_qnl_song)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
