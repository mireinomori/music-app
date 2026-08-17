from __future__ import annotations

from pathlib import Path

DEMO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1"><work><work-title>おと譜 デモ</work-title></work><part-list><score-part id="P1"><part-name>メロディ</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>4</divisions><key><fifths>0</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes><direction placement="above"><direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>120</per-minute></metronome></direction-type><sound tempo="120"/></direction><note><pitch><step>C</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note><note><pitch><step>D</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note><note><pitch><step>E</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note><note><pitch><step>G</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note></measure></part></score-partwise>"""


def midi_to_musicxml(midi_path: Path, xml_path: Path, title: str = "おと譜") -> None:
    from music21 import converter

    try:
        score = converter.parse(str(midi_path))
        score.metadata.title = title
        score.write("musicxml", fp=str(xml_path))
    except Exception as exc:  # noqa: BLE001 - expose conversion failures to the UI
        raise RuntimeError("MIDIからMusicXMLへの変換に失敗しました。音源を短くするか、別の音源をお試しください。") from exc


def write_demo_xml(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEMO_XML, encoding="utf-8")
