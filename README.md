# Kotoba-Whisper による日本語音声文字起こし

## 概要
このシステムは、音声ファイル（webm、wav、mp3形式）を日本語テキストに変換するためのツールです。
kotoba-whisper-v2.0モデルを使用して高精度な日本語文字起こしを実現します。
より高度な機能が必要な場合は、[kotoba-whisper-v2.2](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.2)への移行も検討できます。
下記の記事を参考にしながら作業を行いました。
https://qiita.com/ryosuke_ohori/items/9634c1fd8a9cc9ff7c36

![Kotoba Whisper概要](images/kotoba_pngwhisper.png)

## 特徴
- 日本語に特化した高精度な文字起こし
- webm、wav、mp3形式の音声ファイルに対応
- GPUがある場合は自動的にFlash Attention 2を使用（なくてもCPU動作可能）
- GPUメモリ使用状況のリアルタイム表示
- ローカル環境で処理可能
- 詳細な処理時間の表示
- コマンドライン引数による柔軟なファイル指定

## システム要件

### 実行環境
- OS: Windows 11
- PowerShell 7以上
- Visual Studio Code + Cursor拡張（推奨開発環境）
- Git（バージョン管理用）

### ハードウェア要件
- CPU: マルチコアプロセッサー推奨
- メモリ: 8GB以上（16GB以上推奨）
- ストレージ: 10GB以上の空き容量（モデルのダウンロード用）
- GPU: NVIDIA GPU（オプション、CUDA対応必須）
  - GPU使用時はFlash Attention 2による高速化が有効

### ソフトウェア要件
- Python 3.10以上
- pip（最新版）
- FFmpeg
- 仮想環境（venv）

### 主要な依存パッケージ
- transformers
- torch（CUDA対応版）
- torchaudio
- numpy

### ネットワーク要件
- インターネット接続（初回実行時にモデルをダウンロード）
- モデルのダウンロードに約4GB程度の通信容量が必要

## インストール手順

### 1. FFmpegのセットアップ
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
   
   ![FFmpegダウンロード手順](images/FFmpeg_Download.png)

2. `C:\Program Files\ffmpeg\bin` にインストール
3. PATHに `C:\Program Files\ffmpeg\bin` を追加

動作確認：
```powershell
ffmpeg -version  # バージョン情報が表示されれば成功
```

### 2. Python環境のセットアップ
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 音声データの準備
音声・画面の録画には[VREW](https://vrew.ai/ja/)を使用しています。以下の特徴があります：
- Windows標準の録画機能では記録が難しいスニッピングツールなどの挙動も録画可能
- 高品質な音声録音
- 録画と同時に文字起こしも可能（本システムは別途高精度な文字起こしを提供）

## 使用方法

### 音声文字起こし
```powershell
# 仮想環境を有効化
.\venv\Scripts\activate

# 文字起こしを実行
python kotoba.py 音声ファイルのパス
```

例：
```powershell
# webmファイルの場合
python kotoba.py input.webm

# wavファイルの場合
python kotoba.py input.wav

# mp3ファイルの場合
python kotoba.py input.mp3
```

### 出力情報
- テキストファイル：入力ファイルと同じディレクトリに `transcription.txt` として出力
- GPU情報の表示（GPU使用時）：
  ```
  GPU: NVIDIA GeForce RTX XXXX
  Total GPU Memory: XX.XX GB
  CUDA Version: XX.X
  
  Initial GPU Memory Usage:
  Allocated: X.XX GB
  Reserved: X.XX GB
  
  Final GPU Memory Usage:
  Allocated: X.XX GB
  Reserved: X.XX GB
  ```
- 音声情報の表示：
  ```
  Original sample rate: XXXXXHz
  Audio duration: XX.XX seconds
  ```
- 処理時間の表示：
  ```
  Processing time: XX.XX seconds (X.XX minutes)
  ```

## 注意事項
- 必ず仮想環境を有効化してから実行してください
- 初回実行時はモデルのダウンロードが必要です（約4GB）
- 大きな音声ファイルは処理に時間がかかる可能性があります
- GPU使用時はメモリ使用量に注意してください
- 文字起こしの精度は音声品質に依存します

## 技術情報

### 使用モデル：kotoba-whisper-v2.0
- OpenAI Whisperをベースに日本語特化
- Flash Attention 2による高速化（GPU使用時）
- 日本語音声認識に最適化
- 開発：Kotoba Technologies社

### モデルバージョンについて
より高機能な[kotoba-whisper-v2.2](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.2)も利用可能ですが、本システムではv2.0を採用しています：

選定理由：
- シンプルな環境構築（追加認証不要）
- 最小限のパッケージ依存
- オフライン実行が可能
- 軽量な実行環境

v2.2で追加される機能：
- 話者分離機能（複数話者の識別）
- 句読点の自動追加
- より正確なタイムスタンプ
ただし、これらの機能を利用するには追加のセットアップ（Hugging Face認証、追加パッケージのインストール）が必要です。

用途に応じて、v2.2への移行を検討することも可能です。特に以下のような場合はv2.2が適しています：
- 複数話者の会話やインタビューの文字起こし
- より読みやすい形式（句読点付き）での出力が必要
- 詳細なタイムスタンプが必要

## 参考リンク
- [WindowsにFFmpegをインストールする方法](https://qiita.com/Tadataka_Takahashi/items/9dcb0cf308db6f5dc31b)
- [日本語特化の文字起こしAI『kotoba-whisper-v2.0』](https://qiita.com/ryosuke_ohori/items/9634c1fd8a9cc9ff7c36)
- [Kotoba Whisper Google Colab実装例](https://colab.research.google.com/drive/1BLNS7AG0NFaDKMbk2eag8aRZggMwjmBu?usp=sharing) - クラウド環境での実行例

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。