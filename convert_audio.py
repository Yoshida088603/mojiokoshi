from pydub import AudioSegment
import os

def convert_webm_to_wav():
    try:
        # カレントディレクトリを基準に相対パスで指定
        input_file = "record.webm"
        output_file = "record.wav"
        
        print(f"Converting {input_file} to {output_file}...")
        
        # webmファイルを読み込む
        audio = AudioSegment.from_file(input_file, format="webm")
        
        # サンプリングレートを16kHzに変更
        audio = audio.set_frame_rate(16000)
        
        # モノラルに変換
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # wavファイルとして保存
        audio.export(output_file, format="wav")
        
        print("Conversion completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Detailed error information:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_webm_to_wav() 