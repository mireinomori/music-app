from pathlib import Path

import pytest
from app.analyzer import validate_audio
from app.main import capabilities


def test_validate_supported_audio(tmp_path: Path):
    path = tmp_path / "voice.wav"
    path.write_bytes(b"audio")
    validate_audio(path)


def test_validate_rejects_unsupported(tmp_path: Path):
    path = tmp_path / "voice.txt"
    path.write_bytes(b"audio")
    with pytest.raises(ValueError, match="MP3"):
        validate_audio(path)


def test_validate_rejects_empty(tmp_path: Path):
    path = tmp_path / "voice.mp3"
    path.write_bytes(b"")
    with pytest.raises(ValueError, match="空"):
        validate_audio(path)


def test_capabilities_are_local():
    result = capabilities()
    assert result["local_only"] is True
    assert result["musicxml"] is True
    assert set(result) >= {"basic_pitch", "musicxml", "musescore", "ffmpeg"}
