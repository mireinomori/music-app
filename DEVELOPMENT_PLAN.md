# 開発計画

## Phase 0 — 調査・設計（完了）

- Basic Pitch / librosa / music21 / OSMD / MuseScoreの公式情報とライセンスを確認
- React + Vite と FastAPIの責務を分離
- 日本語UIの主要導線を設計

## Phase 1 — MVP（実装中）

1. 音声アップロードと入力検証
2. BPM・キー推定
3. Basic Pitchがインストール済みならメロディMIDI抽出
4. ノートの無音・短音除去とクオンタイズ
5. music21でMusicXML生成
6. OSMDでブラウザプレビュー
7. MIDI / MusicXML / PDFダウンロード
8. 基本テストとCI

### 現在の状態

- PCローカルのReact + FastAPI構成：実装済み
- Basic Pitchによる短い音源のMIDI生成：確認済み
- BPM・キー推定、クオンタイズ：実装済み
- MusicXML生成とブラウザプレビュー：確認済み
- MuseScore PDF出力：MuseScoreのmacOS GUIセッションで最終確認待ち
- README、依存関係、起動用Makefile：整備済み

### 次に行う作業

1. MuseScore Studioを使ったPDF出力の実機確認
2. 単音・ボーカル・ピアノ・複数楽器のサンプル評価
3. Basic Pitch失敗時、無音、長尺、メモリ不足のUI確認
4. コード推定を追加するためのデータ構造を確定

## Phase 2

- Demucsをオプションのボーカル分離として追加
- コード推定、移調、パート選択
- 長尺音源の分割処理とキャンセル

## Phase 3以降

- ピアノ左右手・ドラム譜・歌詞
- 数字譜 / 簡譜のレンダリングアダプタ
- デスクトップ配布（TauriまたはPyInstaller）

## 受け入れ条件

短い音源を選択し、解析開始からMIDI・MusicXMLの生成、ブラウザ譜面表示、MuseScore導入環境でPDF出力まで確認できること。
