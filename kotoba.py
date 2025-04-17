import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
import time
import os
from pydub import AudioSegment
import argparse
import numpy as np
import warnings
from transformers import logging
from tqdm import tqdm

# Transformersの警告を抑制
logging.set_verbosity_error()
warnings.filterwarnings("ignore")

class Timer:
    def __init__(self):
        self.times = {}
        self.start_time = time.time()
    
    def log(self, step):
        self.times[step] = time.time()
    
    def get_duration(self, start_step, end_step):
        return self.times[end_step] - self.times[start_step]
    
    def print_durations(self):
        print("\n処理時間の詳細:")
        print(f"{'ステップ':<20} {'所要時間':<10}")
        print("-" * 40)
        
        steps = list(self.times.keys())
        for i in range(1, len(steps)):
            duration = self.get_duration(steps[i-1], steps[i])
            print(f"{steps[i]:<20} {duration:>8.2f}秒")
        
        total_time = self.times[steps[-1]] - self.start_time
        print("-" * 40)
        print(f"{'合計時間':<20} {total_time:>8.2f}秒")

def convert_webm_to_wav(input_file, timer):
    """WebMファイルをWAVファイルに変換する"""
    print(f"Converting {input_file} to WAV format...")
    temp_wav = os.path.join(os.path.dirname(input_file), "temp_record.wav")
    
    try:
        timer.log("音声ファイル読み込み開始")
        print("Loading audio file...")
        audio = AudioSegment.from_file(input_file, format="webm")
        print(f"Original audio: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
        
        timer.log("モノラル変換開始")
        if audio.channels > 1:
            print("Converting to mono...")
            audio = audio.set_channels(1)
        
        timer.log("サンプリングレート変換開始")
        print("Converting sample rate to 16kHz...")
        audio = audio.set_frame_rate(16000)
        
        print(f"Processed audio: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
        
        timer.log("WAVファイル出力開始")
        with tqdm(total=100, desc="WAVファイル出力") as pbar:
            audio.export(temp_wav, format="wav")
            pbar.update(100)
        
        timer.log("音声変換完了")
        print("Conversion completed successfully!")
        return temp_wav
    except Exception as e:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
        raise Exception(f"音声変換エラー: {str(e)}")

def transcribe_audio(input_file):
    """音声ファイルをテキストに変換する"""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")

    timer = Timer()
    timer.log("処理開始")

    if torch.cuda.is_available():
        print(f"CUDA Memory before loading model: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    temp_wav = None
    try:
        # WebM形式の場合はWAVに変換
        if input_file.lower().endswith('.webm'):
            temp_wav = convert_webm_to_wav(input_file, timer)
            wav_file = temp_wav
        else:
            timer.log("WAVファイル処理開始")
            print("Loading WAV file...")
            audio = AudioSegment.from_file(input_file)
            print(f"Original audio: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
            
            needs_conversion = False
            if audio.channels > 1:
                print("Converting to mono...")
                audio = audio.set_channels(1)
                needs_conversion = True
            
            if audio.frame_rate != 16000:
                print("Converting sample rate to 16kHz...")
                audio = audio.set_frame_rate(16000)
                needs_conversion = True
            
            if needs_conversion:
                temp_wav = os.path.join(os.path.dirname(input_file), "temp_record.wav")
                print(f"Processed audio: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
                with tqdm(total=100, desc="WAVファイル出力") as pbar:
                    audio.export(temp_wav, format="wav")
                    pbar.update(100)
                wav_file = temp_wav
            else:
                wav_file = input_file
            timer.log("WAVファイル処理完了")
        
        # 出力ファイルパスの設定
        output_file = os.path.join(os.path.dirname(input_file), "transcription.txt")
        
        # モデルの準備
        print("\nLoading model...")
        timer.log("モデル読み込み開始")
        with tqdm(total=2, desc="モデル読み込み") as pbar:
            model_id = "kotoba-tech/kotoba-whisper-v2.0"
            processor = WhisperProcessor.from_pretrained(model_id)
            pbar.update(1)
            model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)
            pbar.update(1)
        
        timer.log("モデル読み込み完了")
        if torch.cuda.is_available():
            print(f"CUDA Memory after loading model: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
        print("Model loaded successfully!")
        
        # 文字起こしの実行
        print("\nStarting transcription...")
        timer.log("音声データ読み込み開始")
        
        print("Reading audio file...")
        audio_input, sample_rate = sf.read(wav_file)
        print(f"Audio shape: {audio_input.shape}, Sample rate: {sample_rate}Hz")
        timer.log("音声データ読み込み完了")
        
        # データ型をfloat32に変換し、値の範囲を-1から1に正規化
        audio_input = audio_input.astype(np.float32)
        if audio_input.max() > 1.0 or audio_input.min() < -1.0:
            print("Normalizing audio...")
            audio_input = audio_input / max(abs(audio_input.max()), abs(audio_input.min()))
        
        print("Processing audio features...")
        timer.log("特徴抽出開始")
        with tqdm(total=100, desc="特徴抽出") as pbar:
            input_features = processor(audio_input, sampling_rate=16000, return_tensors="pt").input_features.to(device)
            pbar.update(100)
        timer.log("特徴抽出完了")
        
        print(f"Input features shape: {input_features.shape}")
        
        print("Generating transcription...")
        timer.log("文字起こし開始")
        with tqdm(total=100, desc="文字起こし") as pbar:
            generated_ids = model.generate(input_features)
            transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            pbar.update(100)
        timer.log("文字起こし完了")
        
        # 結果の保存
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        timer.log("処理完了")
        print(f"\nTranscription saved to {output_file}")
        
        if torch.cuda.is_available():
            print(f"Final CUDA Memory: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
        
        # 処理時間の詳細を表示
        timer.print_durations()
        
        return output_file
    
    except Exception as e:
        raise Exception(f"文字起こしエラー: {str(e)}")
    
    finally:
        # 一時ファイルの削除
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
                print("Temporary WAV file removed")
            except Exception as e:
                print(f"Warning: Could not remove temporary file: {str(e)}")
        
        # GPUメモリの解放
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def main():
    parser = argparse.ArgumentParser(description='音声ファイルの文字起こしを行います')
    parser.add_argument('input_file', help='入力音声ファイルのパス（.webmまたは.wav形式）')
    args = parser.parse_args()

    try:
        transcribe_audio(args.input_file)
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()