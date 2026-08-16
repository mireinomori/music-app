# アーキテクチャ

## 方針

音声を外部へ送信しない、PCローカル完結の構成です。フロントエンドは操作とプレビュー、バックエンドは音楽解析とファイル生成を担当します。

```text
React / Vite
    │ HTTP localhost
    ▼
FastAPI
    ├─ librosa          BPM・キー・音響特徴
    ├─ Basic Pitch      音声 → MIDI
    ├─ pretty_midi      ノート整理・クオンタイズ
    ├─ music21          MIDI → MusicXML
    └─ MuseScore        MusicXML → PDF（任意）
```

## ディレクトリ

```text
backend/app/
  main.py       API、アップロード、ダウンロード
  analyzer.py   音響解析、Basic Pitch、クオンタイズ、PDF
  musicxml.py   MIDIからMusicXMLへの変換
backend/tests/  入力検証と機能検出のテスト
frontend/src/
  App.tsx       日本語UIと解析フロー
  components/   楽譜プレビュー
  styles.css    レスポンシブUI
```

## API

- `GET /api/health`：ローカルAPIの稼働確認
- `GET /api/capabilities`：Basic Pitch、FFmpeg、MuseScoreの検出
- `POST /api/analyze`：音声を解析し、ジョブ情報を返す
- `GET /api/jobs/{job_id}/{kind}`：MIDI、MusicXML、PDFを取得
- `GET /api/demo-score`：入力前のプレビュー用MusicXML

## 拡張ポイント

`analyze_audio`の前段にDemucs等の音源分離を追加し、解析対象をモードごとに切り替えます。コード推定はchroma解析から独立したサービスにし、将来の数字譜はMusicXMLのノート列を入力とする別レンダラーとして追加します。
