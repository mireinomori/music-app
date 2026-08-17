from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from pathlib import Path


def transcribe_and_attach(audio_path: Path, musicxml_path: Path) -> dict[str, object]:
    """Transcribe local audio with faster-whisper and attach words to melody notes."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "自動歌詞認識にはfaster-whisperが必要です。READMEの追加インストールを実行してください。"
        ) from exc

    model_name = os.getenv("OTOFUDE_WHISPER_MODEL", "small")
    device = os.getenv("OTOFUDE_WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("OTOFUDE_WHISPER_COMPUTE", "int8")
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(audio_path), language="ja", beam_size=5, word_timestamps=True, vad_filter=True
    )
    words: list[str] = []
    for segment in segments:
        if segment.words:
            words.extend(word.word.strip() for word in segment.words if word.word.strip())
        elif segment.text.strip():
            words.extend(segment.text.strip().split())
    words = [word for word in words if word]
    _attach_lyrics(musicxml_path, words)
    return {"text": "".join(words), "language": info.language, "word_count": len(words)}


def _attach_lyrics(path: Path, words: list[str]) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    notes = [note for note in root.iter() if note.tag.rsplit("}", 1)[-1] == "note"]
    pitched_notes = [
        note for note in notes if any(child.tag.rsplit("}", 1)[-1] == "pitch" for child in note)
    ]
    for note, word in zip(pitched_notes, words):
        for child in list(note):
            if child.tag.rsplit("}", 1)[-1] == "lyric":
                note.remove(child)
        lyric = ET.Element("lyric", {"number": "1"})
        ET.SubElement(lyric, "syllabic").text = "single"
        ET.SubElement(lyric, "text").text = word
        note.append(lyric)
    tree.write(path, encoding="utf-8", xml_declaration=True)
