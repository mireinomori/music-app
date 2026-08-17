from __future__ import annotations

import os
import unicodedata
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
    segments_text: list[str] = []
    for segment in segments:
        if segment.text.strip():
            segments_text.append(segment.text.strip())
    if str(info.language).lower().startswith("ja"):
        # Japanese transcription has no spaces.  Treat readable kana/kanji
        # units as lyric syllables instead of reporting Whisper segments as
        # a misleading word count (e.g. 23 long segments).
        words = [char for text in segments_text for char in text if _is_lyric_char(char)]
    else:
        words = [word for text in segments_text for word in text.split() if word]
    _attach_lyrics(musicxml_path, words)
    return {"text": "".join(words), "language": info.language, "word_count": len(words)}


def _is_lyric_char(char: str) -> bool:
    category = unicodedata.category(char)
    return category[0] in {"L", "N"} or char in "ーっゃゅょぁぃぅぇぉ"


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
