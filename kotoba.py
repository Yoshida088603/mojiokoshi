import torch
from transformers import pipeline
import torchaudio
import numpy as np
import os
import time
import argparse

def check_gpu_info():
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB単位
        print(f"GPU: {gpu_name}")
        print(f"Total GPU Memory: {total_memory:.2f} GB")
        print(f"CUDA Version: {torch.version.cuda}")
        return True
    else:
        print("GPU is not available. Using CPU.")
        return False

def transcribe_audio(input_file):
    print("Current working directory:", os.getcwd())
    print(f"Processing file: {input_file}")

    # GPU環境の確認
    use_gpu = check_gpu_info()

    # コンフィグ設定
    model_id = "kotoba-tech/kotoba-whisper-v2.0"
    device = "cuda:0" if use_gpu else "cpu"
    torch_dtype = torch.float16 if use_gpu else torch.float32
    model_kwargs = {"attn_implementation": "flash_attention_2"} if use_gpu else {}
    generate_kwargs = {"language": "japanese", "return_timestamps": True}

    print(f"\nUsing device: {device}")
    print(f"Using dtype: {torch_dtype}")
    if use_gpu:
        print("Using Flash Attention 2 for faster processing")
    print("\nLoading model...")

    # モデル読み込み
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_id,
        torch_dtype=torch_dtype,
        device=device,
        model_kwargs=model_kwargs
    )

    print("Model loaded successfully!")
    print("Loading audio file...")

    # 音声ファイルの読み込み (torchaudioを使用)
    waveform, sample_rate = torchaudio.load(input_file)
    print(f"Original sample rate: {sample_rate}Hz")
    print(f"Audio duration: {waveform.shape[-1]/sample_rate:.2f} seconds")

    # サンプリングレートの変換
    if sample_rate != 16000:
        print("Converting sample rate to 16kHz...")
        resample_waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)
    else:
        resample_waveform = waveform

    # PyTorch テンソルを NumPy 配列に変換
    resample_waveform_np = resample_waveform.numpy()

    # GPU使用状況の表示（GPU使用時のみ）
    if use_gpu:
        print("\nInitial GPU Memory Usage:")
        print(f"Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")
        print(f"Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f} GB")

    # 変換実行
    print("\nStarting transcription...")
    start_time = time.time()
    result = pipe({"array": resample_waveform_np[0], "sampling_rate": 16000}, generate_kwargs=generate_kwargs)
    end_time = time.time()

    # GPU使用状況の表示（GPU使用時のみ）
    if use_gpu:
        print("\nFinal GPU Memory Usage:")
        print(f"Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")
        print(f"Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f} GB")
        # GPUキャッシュのクリア
        torch.cuda.empty_cache()

    # 結果を保存
    output_file = "transcription.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    processing_time = end_time - start_time
    print(f"\nTranscription saved to {output_file}")
    print(f"Processing time: {processing_time:.2f} seconds ({processing_time/60:.2f} minutes)")
    return result["text"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="音声ファイルのパス")
    args = parser.parse_args()

    try:
        transcribe_audio(args.input_file)
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

