from __future__ import annotations

import base64
import json
import os
import re
import urllib.request
import urllib.error
from pathlib import Path

from .exporters import EpisodePackage


class MediaRenderError(Exception):
    pass


def render_episode_media(
    package: EpisodePackage,
    output_dir: str | Path,
    tts_provider: str = "openai",
    image_provider: str = "openai",
    openai_api_key_env: str = "OPENAI_API_KEY",
    tts_model: str = "gpt-4o-mini-tts",
    tts_voice: str = "alloy",
    image_model: str = "gpt-image-1",
    image_size: str = "1024x1024",
    elevenlabs_api_key_env: str = "ELEVENLABS_API_KEY",
    elevenlabs_voice_id: str = "EXAVITQu4vr4xnSDxMaL",
    elevenlabs_model_id: str = "eleven_multilingual_v2",
) -> dict:
    openai_key = os.getenv(openai_api_key_env)
    elevenlabs_key = os.getenv(elevenlabs_api_key_env)

    root = Path(output_dir)
    audio_dir = root / "audio"
    images_dir = root / "images"
    audio_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    audio_files: list[str] = []
    image_files: list[str] = []

    for scene in package.scene_cards:
        safe_scene_name = _slugify(f"scene_{scene.turn_index}_{scene.title}")

        if tts_provider == "openai":
            if not openai_key:
                raise MediaRenderError(f"Missing API key in environment variable: {openai_api_key_env}")
            audio_bytes = _openai_tts(
                api_key=openai_key,
                model=tts_model,
                voice=tts_voice,
                text=scene.narration,
            )
        elif tts_provider == "elevenlabs":
            if not elevenlabs_key:
                raise MediaRenderError(
                    f"Missing API key in environment variable: {elevenlabs_api_key_env}"
                )
            audio_bytes = _elevenlabs_tts(
                api_key=elevenlabs_key,
                voice_id=elevenlabs_voice_id,
                model_id=elevenlabs_model_id,
                text=scene.narration,
            )
        else:
            raise MediaRenderError(f"Unsupported TTS provider: {tts_provider}")

        audio_path = audio_dir / f"{safe_scene_name}.mp3"
        audio_path.write_bytes(audio_bytes)
        audio_files.append(str(audio_path))

        if image_provider == "openai":
            if not openai_key:
                raise MediaRenderError(f"Missing API key in environment variable: {openai_api_key_env}")
            image_bytes = _openai_image(
                api_key=openai_key,
                model=image_model,
                prompt=scene.image_prompt,
                size=image_size,
            )
        elif image_provider == "none":
            image_bytes = b""
        else:
            raise MediaRenderError(f"Unsupported image provider: {image_provider}")

        if image_provider == "none":
            continue

        image_path = images_dir / f"{safe_scene_name}.png"
        image_path.write_bytes(image_bytes)
        image_files.append(str(image_path))

    return {
        "tts_provider": tts_provider,
        "image_provider": image_provider,
        "audio_files": audio_files,
        "image_files": image_files,
    }


def _openai_tts(api_key: str, model: str, voice: str, text: str) -> bytes:
    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "format": "mp3",
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except Exception as error:
        raise MediaRenderError(f"TTS generation failed: {error}") from error


def _elevenlabs_tts(api_key: str, voice_id: str, model_id: str, text: str) -> bytes:
    payload = {
        "text": text,
        "model_id": model_id,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise MediaRenderError(f"ElevenLabs TTS failed: {error.code} {details}") from error
    except Exception as error:
        raise MediaRenderError(f"ElevenLabs TTS failed: {error}") from error


def _openai_image(api_key: str, model: str, prompt: str, size: str) -> bytes:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "response_format": "b64_json",
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise MediaRenderError(f"Image generation failed: {error}") from error

    data = response_data.get("data", [])
    if not data:
        raise MediaRenderError("Image generation returned empty data")

    encoded = data[0].get("b64_json")
    if not encoded:
        raise MediaRenderError("Image generation did not return b64 image data")

    try:
        return base64.b64decode(encoded)
    except Exception as error:
        raise MediaRenderError(f"Invalid base64 image data: {error}") from error


def _slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return normalized or "scene"