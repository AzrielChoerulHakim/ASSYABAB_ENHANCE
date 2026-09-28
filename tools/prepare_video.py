#!/usr/bin/env python3
"""Prepare the user-supplied film for predictable, inexpensive scroll seeking.

Requires FFmpeg with libx264. Python itself only needs the standard library.
The input is always read-only; only the named output files are replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


START = 0.25
DURATION = 9.5
FPS = 24
GOP = 6
# Preserve the original room and lighting, while easing the heavy amber cast.
GRADE = (
    "colorbalance=rh=-0.022:bh=0.012:rm=-0.008:bm=0.006,"
    "eq=contrast=0.99:brightness=0.006:saturation=0.91:gamma=1.025"
)


def run(ffmpeg: str, arguments: list[str]) -> None:
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "warning", "-nostdin", *arguments],
        check=True,
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original 18622.mp4")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(__file__).resolve().parents[1] / "assets",
    )
    parser.add_argument(
        "--contact-sheet", type=Path,
        help="Optional QA image; not needed by the website",
    )
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error("FFmpeg is required. Add it to PATH or pass --ffmpeg PATH.")
    source = args.source.resolve(strict=True)
    source_hash = digest(source)
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, width, quality in (
        ("cahaya-scroll.mp4", 1280, 19),
        ("cahaya-scroll-mobile.mp4", 960, 21),
    ):
        output = destination / name
        if output == source:
            parser.error("The source cannot be an output path.")
        filters = f"{GRADE},scale={width}:-2:flags=lanczos,fps={FPS},setsar=1"
        run(args.ffmpeg, [
            "-y", "-ss", str(START), "-i", str(source), "-t", str(DURATION),
            "-map", "0:v:0", "-an", "-sn", "-dn", "-map_metadata", "-1",
            "-vf", filters, "-c:v", "libx264", "-preset", "slow",
            "-crf", str(quality), "-profile:v", "high", "-level:v", "3.1",
            "-pix_fmt", "yuv420p", "-g", str(GOP), "-keyint_min", str(GOP),
            "-sc_threshold", "0", "-bf", "0",
            "-x264-params", "open-gop=0", "-movflags", "+faststart",
            str(output),
        ])
        # Decode every frame; a successful encoder alone does not verify the file.
        run(args.ffmpeg, ["-v", "error", "-i", str(output), "-f", "null", "-"])
        outputs.append(output)

    poster = destination / "cahaya-poster.jpg"
    run(args.ffmpeg, [
        "-y", "-i", str(outputs[0]), "-frames:v", "1", "-q:v", "2",
        "-update", "1", str(poster),
    ])
    outputs.append(poster)
    if args.contact_sheet:
        args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
        run(args.ffmpeg, [
            "-y", "-i", str(outputs[0]),
            "-vf", "fps=1,scale=400:-2,tile=5x2:padding=4:margin=4:color=0x132c27",
            "-frames:v", "1", "-q:v", "2", "-update", "1",
            str(args.contact_sheet),
        ])

    if digest(source) != source_hash:
        raise RuntimeError("Source checksum changed unexpectedly")
    print(json.dumps({
        "source_sha256": source_hash,
        "duration_seconds": DURATION,
        "fps": FPS,
        "keyframe_interval_frames": GOP,
        "audio": False,
        "outputs": [
            {"file": p.name, "bytes": p.stat().st_size, "sha256": digest(p)}
            for p in outputs
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
