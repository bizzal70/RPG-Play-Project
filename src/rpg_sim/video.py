from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class VideoAssemblyError(Exception):
    pass


@dataclass
class VideoAssemblyResult:
    video_path: str
    clip_count: int


def assemble_episode_video(
    run_dir: str | Path,
    output_filename: str = "episode.mp4",
    fps: int = 24,
    resolution: str = "1280x720",
) -> VideoAssemblyResult:
    if shutil.which("ffmpeg") is None:
        raise VideoAssemblyError("ffmpeg is not installed or not available in PATH")

    width, height = _parse_resolution(resolution)
    base = Path(run_dir)
    audio_dir = base / "audio"
    image_dir = base / "images"

    audio_files = sorted(audio_dir.glob("*.mp3"))
    image_files = sorted(image_dir.glob("*.png"))

    if not audio_files:
        raise VideoAssemblyError(f"No audio files found in {audio_dir}")
    if not image_files:
        raise VideoAssemblyError(f"No image files found in {image_dir}")
    if len(audio_files) != len(image_files):
        raise VideoAssemblyError(
            f"Mismatched scene assets: {len(audio_files)} audio files vs {len(image_files)} image files"
        )

    temp_dir = base / "video_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    clip_paths: list[Path] = []
    for index, (audio_path, image_path) in enumerate(zip(audio_files, image_files), start=1):
        clip_path = temp_dir / f"clip_{index:03d}.mp4"
        command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-r",
            str(fps),
            "-c:a",
            "aac",
            "-shortest",
            str(clip_path),
        ]
        _run_ffmpeg(command, context=f"scene {index}")
        clip_paths.append(clip_path)

    concat_file = temp_dir / "concat.txt"
    concat_file.write_text("\n".join(f"file '{path.name}'" for path in clip_paths) + "\n", encoding="utf-8")

    output_path = base / output_filename
    concat_command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output_path),
    ]
    _run_ffmpeg(concat_command, context="final concat", cwd=temp_dir)

    return VideoAssemblyResult(video_path=str(output_path), clip_count=len(clip_paths))


def _run_ffmpeg(command: list[str], context: str, cwd: Path | None = None) -> None:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        details = stderr or stdout or "unknown ffmpeg error"
        raise VideoAssemblyError(f"ffmpeg failed during {context}: {details}")


def _parse_resolution(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise VideoAssemblyError(f"Invalid resolution format: {value}. Expected WIDTHxHEIGHT")
    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as error:
        raise VideoAssemblyError(f"Invalid resolution format: {value}. Expected WIDTHxHEIGHT") from error
    if width <= 0 or height <= 0:
        raise VideoAssemblyError(f"Resolution values must be positive: {value}")
    return width, height