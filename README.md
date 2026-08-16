# おと譜 — MP3から楽譜を作成

音声ファイルからメロディを解析し、読みやすい五線譜を作成するローカル動作のMVPです。音声は外部APIへ送信しません。

## MVPの範囲

- 入力：MP3 / WAV / M4A / FLAC
- BPM・キーの推定
- Basic PitchによるメロディMIDI生成
- 4分音符、8分音符、16分音符、三連符のクオンタイズ
- MIDI → MusicXML変換
- ブラウザ内の楽譜プレビュー
- MIDI / MusicXML / PDF出力

採譜結果は音源の品質、楽器数、残響、リズムの複雑さに左右されます。MVPは「完璧なフルスコア」ではなく、一般ユーザーが読めるメロディ譜を素早く作ることを目標にしています。

## 対応OSと必要ソフト

- macOS（Apple Siliconを含む）またはWindowsを目標
- Python 3.9〜3.11
- Node.js 20以上、npm
- FFmpeg（MP3/M4A/FLAC入力で推奨）
- MuseScore Studio 4（PDF出力時のみ必要）

Python 3.12以降は、音楽解析ライブラリの対応状況により未検証です。

## インストール

```bash
git clone <リポジトリURL>
cd music-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './backend[transcription,dev]'
npm install --prefix frontend
```

Windows PowerShellでは、仮想環境の有効化を次のように行います。

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[transcription,dev]"
npm install --prefix frontend
```

## 外部ソフトの設定

FFmpegは、公式配布物またはHomebrew等でインストールし、`ffmpeg -version` が通るようにPATHへ追加してください。

PDF出力にはMuseScore Studio 4を別途インストールしてください。アプリにMuseScore本体は同梱しません。インストール後、macOSでは `mscore`、Windowsでは `MuseScore4.exe` がPATHから見える設定を推奨します。PDF出力に失敗しても、MIDIとMusicXMLは保存できます。

## 起動方法

最も簡単な方法は、プロジェクト直下で次を実行することです。

```bash
make start
```

このコマンドはバックエンドとフロントエンドをバックグラウンドで起動し、ログを `.runtime/` に保存します。終了する場合は別のターミナルで次を実行します。

```bash
make stop
```

白画面になった場合は、`make stop` の後に `make start` を実行して再起動してください。

手動で起動する場合は、ターミナルを2つ開きます。

```bash
# ターミナル1
cd music-app/backend
../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
# ターミナル2
npm run dev --prefix frontend -- --host 127.0.0.1
```

ブラウザで http://127.0.0.1:5173/ を開いてください。

macOSでGoogle Chromeを開く場合は、別のターミナルで次を実行できます。

```bash
make open-chrome
```

## 使い方

1. MP3などをドラッグ＆ドロップする
2. 解析方法を選ぶ
3. リズムの整え方を選ぶ
4. 「楽譜を作成」を押す
5. プレビューを確認し、MIDI / MusicXML / PDFを保存する

## テストと品質確認

```bash
.venv/bin/ruff check backend/app backend/tests
.venv/bin/pytest backend/tests -q
npm run build --prefix frontend
```

## トラブルシューティング

### `ModuleNotFoundError` が出る

プロジェクト直下で `.venv/bin/python -m pip install -e './backend[transcription,dev]'` を実行し、正しい仮想環境から起動してください。

### FFmpegが見つからない

`ffmpeg -version` を実行し、PATHを確認してください。WAV入力を使うと、形式変換の問題を切り分けやすくなります。

### PDFだけ作成されない

MuseScore StudioのインストールとPATHを確認してください。MuseScoreがGUIセッションを必要とする環境では、MusicXMLをMuseScoreで開き、手動でPDFを書き出せます。

### 解析に時間がかかる

最初のBasic Pitch実行ではモデルの読み込みに時間がかかります。まずは30秒以内の単音またはボーカル音源で確認してください。MVPでは入力音源を900秒まで読み込みます。

## 使用OSS

Basic Pitch、librosa、pretty_midi、mido、music21、FastAPI、React、Vite、OpenSheetMusicDisplayを使用します。詳細は [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) を参照してください。

## 将来の拡張

音源分離、コード推定、移調、パート別採譜、数字譜・簡譜の出力を追加できるよう、解析・楽譜変換・表示を分離した構成にしています。
