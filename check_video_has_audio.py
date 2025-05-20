import os
import tempfile
import torchaudio

class CheckVideoHasAudio:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":{
            "video_path": ("STRING", {"default": "", "multiline": False}),
        }
        }
    
    CATEGORY = "Video/Utility"
    DESCRIPTION = "检查视频是否包含音频轨道（Heygem节点需要检查），如果有则返回视频路径和音频信息"

    RETURN_TYPES = ("VIDEO","AUDIO")
    RETURN_NAMES = ("video_path", "audio_info")

    OUTPUT_NODE = False

    FUNCTION = "check_video_has_audio"

    def check_video_has_audio(self, video_path):
        if not os.path.exists(video_path):
            raise ValueError(f"视频文件不存在: {video_path}") 
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav",dir=input_dir,delete=False) as aud:
                os.system(f"""ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 44100 -ac 1 {aud.name} -y""")
            waveform, sample_rate = torchaudio.load(aud.name)
            audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
        except:
            raise ValueError(f"视频 {video} 不包含音频轨道或音频提取失败。请确保输入的视频包含音频。")
        return (video_path,audio)

NODE_CLASS_MAPPINGS = {
    "CheckVideoHasAudio": CheckVideoHasAudio
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckVideoHasAudio": "检查视频静音"
}