import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
import time
import os

def transcribe_audio():
    print("Loading model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        # カレントディレクトリを基準に相対パスで指定
        input_file = "record.wav"
        output_file = "transcription.txt"
        
        # モデルとプロセッサのロード
        model_id = "kotoba-tech/kotoba-whisper-v2.0"
        processor = WhisperProcessor.from_pretrained(model_id)
        model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)
        
        print("Model loaded successfully!")
        
        print("Starting transcription...")
        start_time = time.time()
        
        # 音声ファイルの読み込み
        print("Loading audio file...")
        audio_input, sample_rate = sf.read(input_file)
        
        # 音声データの前処理
        input_features = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt").input_features.to(device)
        
        # 推論の実行
        generated_ids = model.generate(input_features)
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nTranscription completed in {processing_time:.2f} seconds")
        
        # 結果を保存
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        print(f"\nTranscription saved to {output_file}")
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Detailed error information:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    transcribe_audio()