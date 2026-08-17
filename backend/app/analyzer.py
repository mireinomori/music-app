from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {".mp3", ".wav", ".m4a", ".flac"}


@dataclass
class AnalysisResult:
    bpm: float = 120.0
    key: str = "C Major"
    midi_path: Path | None = None
    xml_path: Path | None = None
    pdf_path: Path | None = None
    warning: str | None = None


def validate_audio(path: Path, max_bytes: int = 250 * 1024 * 1024) -> None:
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError("MP3、WAV、M4A、FLACのいずれかを選択してください。")
    if not path.exists() or path.stat().st_size == 0:
        raise ValueError("音声ファイルが空、または読み込めません。別のファイルをお試しください。")
    if path.stat().st_size > max_bytes:
        raise ValueError("音声ファイルが大きすぎます。MVPでは250MB以下にしてください。")


def analyze_audio(path: Path, output_dir: Path, quantize: str = "auto") -> AnalysisResult:
    validate_audio(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = AnalysisResult()
    try:
        import librosa

        y, sr = librosa.load(path, sr=None, mono=True, duration=900)
        if len(y) == 0 or float(abs(y).max()) < 1e-5:
            raise ValueError("音声が無音のようです。音が入ったファイルをお試しください。")
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        result.bpm = round(float(tempo[0] if hasattr(tempo, "__len__") else tempo), 1)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        result.key = _estimate_key(chroma)
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 - optional audio backends vary by OS
        result.warning = f"音響解析を一部省略しました: {exc}"

    midi_path = output_dir / "melody.mid"
    xml_path = output_dir / "score.musicxml"
    try:
        runtime_tmp = output_dir / ".runtime-tmp"
        runtime_tmp.mkdir(exist_ok=True)
        os.environ["TMPDIR"] = str(runtime_tmp)
        from basic_pitch import ICASSP_2022_MODEL_PATH
        from basic_pitch.inference import predict_and_save

        predict_and_save([str(path)], str(output_dir), True, False, False, False, ICASSP_2022_MODEL_PATH)
        candidates = list(output_dir.glob("*.mid"))
        if candidates:
            candidates[0].replace(midi_path)
        else:
            raise RuntimeError("MIDIが生成されませんでした")
    except Exception as exc:  # noqa: BLE001 - transcription must never return a fake score
        raise RuntimeError(
            "音程解析に失敗しました。Basic Pitchが未インストールか、音源を解析できませんでした。"
        ) from exc

    from .musicxml import midi_to_musicxml

    _quantize_midi(midi_path, result.bpm, quantize)
    midi_to_musicxml(midi_path, xml_path)
    result.midi_path, result.xml_path = midi_path, xml_path
    muse = _find_musescore()
    if muse:
        pdf_path = output_dir / "score.pdf"
        try:
            # Converter mode avoids opening the editor window during local runs.
            subprocess.run(
                [muse, "-o", str(pdf_path), str(xml_path)],
                check=True,
                timeout=20,
                capture_output=True,
                text=True,
            )
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                result.pdf_path = pdf_path
            else:
                raise RuntimeError("MuseScoreがPDFファイルを生成しませんでした")
        except Exception:  # noqa: BLE001 - MuseScore is an optional external tool
            result.warning = "PDF変換に失敗しました。MusicXMLは保存できます。MuseScore Studioを直接開いて書き出すこともできます。"
    else:
        result.warning = "PDF出力にはMuseScore Studioのインストールが必要です。"
    return result


def _quantize_midi(path: Path, bpm: float, quantize: str) -> None:
    grids = {"quarter": 1.0, "eighth": 0.5, "sixteenth": 0.25, "triplet": 1 / 3, "auto": 0.25}
    try:
        import pretty_midi

        midi = pretty_midi.PrettyMIDI(str(path))
        grid_seconds = (60.0 / max(bpm, 1.0)) * grids.get(quantize, grids["auto"])
        for instrument in midi.instruments:
            for note in instrument.notes:
                note.start = round(note.start / grid_seconds) * grid_seconds
                note.end = max(note.start + 0.04, round(note.end / grid_seconds) * grid_seconds)
        midi.write(str(path))
    except Exception:  # noqa: BLE001 - quantization must not block valid MIDI output
        return


def _estimate_key(chroma) -> str:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[int(chroma.mean(axis=1).argmax())]} Major"


def _find_musescore() -> str | None:
    for command in ("mscore", "musescore", "MuseScore4.exe"):
        found = shutil.which(command)
        if found:
            return found
    return None


def _write_demo_midi(path: Path) -> None:
    try:
        import mido

        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120)))
        for note in (60, 62, 64, 67):
            track.append(mido.Message("note_on", note=note, velocity=80, time=0))
            track.append(mido.Message("note_off", note=note, velocity=0, time=480))
        mid.save(path)
    except Exception:  # noqa: BLE001 - fallback MIDI keeps the UI usable
        path.write_bytes(b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xe0MTrk\x00\x00\x00\x04\x00\xff\x2f\x00")
