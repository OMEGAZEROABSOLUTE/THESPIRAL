#!/usr/bin/env python3
"""System resource monitoring utilities."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any, Dict, List

import psutil
from fastapi import FastAPI
import uvicorn


def _get_gpu_stats() -> List[Dict[str, int]]:
    """Return GPU utilisation and memory usage via ``nvidia-smi``."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []

    gpus: List[Dict[str, int]] = []
    for line in result.stdout.strip().splitlines():
        util, total, used = [int(x.strip()) for x in line.split(",")]
        gpus.append(
            {
                "utilization": util,
                "memory_total": total,
                "memory_used": used,
            }
        )
    return gpus


def collect_stats() -> Dict[str, Any]:
    """Gather basic CPU, memory, network and GPU usage statistics."""
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": mem.percent,
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "gpus": _get_gpu_stats(),
    }


def _print_stats_loop(interval: float) -> None:
    """Continuously print system stats until interrupted."""
    try:
        while True:
            print(json.dumps(collect_stats()))
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


app = FastAPI()


@app.get("/stats")
def stats_endpoint() -> Dict[str, Any]:
    """Return current system statistics."""
    return collect_stats()


def _serve(host: str, port: int) -> None:
    """Launch FastAPI service exposing ``/stats``."""
    uvicorn.run(app, host=host, port=port)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="System monitor")
    parser.add_argument("--watch", action="store_true", help="continuously display stats")
    parser.add_argument(
        "--interval", type=float, default=1.0, help="refresh interval when watching"
    )
    parser.add_argument("--serve", action="store_true", help="run FastAPI service")
    parser.add_argument("--host", default="0.0.0.0", help="bind host when serving")
    parser.add_argument("--port", type=int, default=8000, help="bind port when serving")
    args = parser.parse_args(argv)

    if args.serve:
        _serve(args.host, args.port)
    elif args.watch:
        _print_stats_loop(args.interval)
    else:
        print(json.dumps(collect_stats()))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
