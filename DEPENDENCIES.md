# 依存関係

## Backend

| パッケージ | 用途 | 必須性 |
|---|---|---|
| FastAPI / Uvicorn | ローカルAPI | 必須 |
| librosa | BPM、キー、音響特徴 | 必須 |
| pretty_midi / mido | MIDI編集・フォールバックMIDI | 必須 |
| music21 | MusicXML生成 | 必須 |
| basic-pitch | 音声からの音高推定 | 採譜時に推奨 |
| python-multipart | FastAPIファイルアップロード | 必須 |

## Frontend

| パッケージ | 用途 |
|---|---|
| React / React DOM | UI |
| Vite | 開発サーバー・ビルド |
| OpenSheetMusicDisplay | MusicXMLの五線譜表示 |
| TypeScript | 型安全なフロントエンド |

## 外部ソフト

- FFmpeg：圧縮音声の読み込み補助。必須ではありませんが、MP3/M4A/FLACで推奨です。
- MuseScore Studio 4：MusicXMLからPDFを作る場合のみ必要です。アプリには同梱しません。

## 互換性方針

Pythonは3.9〜3.11をMVPの検証対象にします。Basic PitchはApple SiliconではCoreMLを使用できる場合がありますが、CPU実行へフォールバックできる設計にします。モデルファイルは初回インストール時に取得されるため、完全オフラインで初回から使う場合は事前に依存関係を準備してください。

## ライセンス確認

各ライブラリのライセンスは [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) に整理しています。依存更新時は、直接依存だけでなく間接依存も再確認します。
