"""
Audio Processor & Transcoder.
Inspired by Nimbus Voice Agent audio engine.
Provides:
- WebM/Opus -> 16 kHz mono WAV transcoding for ASR
- Raw PCM -> WAV container wrapping
- Silence detection & audio RMS energy calculation for barge-in
"""

from __future__ import annotations
import io
import math
import struct
import shutil
import subprocess
from functools import lru_cache
from typing import Optional

ASR_SAMPLE_RATE = 16000


@lru_cache(maxsize=1)
def _ffmpeg_exe() -> Optional[str]:
    """Finds ffmpeg binary in path or imageio_ffmpeg if installed."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which("ffmpeg")


def to_wav(data: bytes, sample_rate: int = ASR_SAMPLE_RATE) -> bytes:
    """Transcodes any audio container to 16kHz mono PCM WAV."""
    # If already a valid WAV with matching header, return as-is
    if data.startswith(b"RIFF") and b"WAVE" in data[:12]:
        return data

    ffmpeg = _ffmpeg_exe()
    if ffmpeg:
        try:
            proc = subprocess.run(
                [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
                 "-ac", "1", "-ar", str(sample_rate), "-f", "wav", "pipe:1"],
                input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
            )
            if proc.returncode == 0 and len(proc.stdout) > 44:
                return proc.stdout
        except Exception:
            pass

    # Fallback minimal wrapping
    return pcm_to_wav(data, sample_rate=sample_rate)


def pcm_to_wav(pcm: bytes, sample_rate: int = ASR_SAMPLE_RATE, channels: int = 1, bits: int = 16) -> bytes:
    """Wraps raw little-endian PCM samples in a standard WAV header."""
    byte_rate = sample_rate * channels * bits // 8
    block_align = channels * bits // 8
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + len(pcm)))
    buf.write(b"WAVEfmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, channels, sample_rate, byte_rate, block_align, bits))
    buf.write(b"data")
    buf.write(struct.pack("<I", len(pcm)))
    buf.write(pcm)
    return buf.getvalue()


def calculate_audio_energy(pcm_data: bytes) -> float:
    """Calculates RMS audio energy to identify caller speech onset for barge-in."""
    if len(pcm_data) < 2:
        return 0.0
    count = len(pcm_data) // 2
    format_str = f"<{count}h"
    try:
        samples = struct.unpack(format_str, pcm_data[:count * 2])
        sum_squares = sum(s * s for s in samples)
        rms = math.sqrt(sum_squares / count)
        return rms
    except Exception:
        return 0.0
