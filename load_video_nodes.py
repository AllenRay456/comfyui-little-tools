import os
import subprocess
import json
import tempfile
from datetime import datetime
import folder_paths
import sys
import site

def find_ytdl():
    """查找yt-dlp或youtube-dl的路径"""
    # 首先检查系统PATH
    try:
        import shutil
        ytdl_path = shutil.which('yt-dlp') or shutil.which('youtube-dl')
        if ytdl_path:
            return ytdl_path
    except:
        pass
    
    # 检查Python包安装路径
    for path in site.getsitepackages():
        ytdl_path = os.path.join(path, 'bin', 'yt-dlp')
        if os.path.exists(ytdl_path):
            return ytdl_path
        ytdl_path = os.path.join(path, 'bin', 'youtube-dl')
        if os.path.exists(ytdl_path):
            return ytdl_path
    
    # 检查当前Python环境的bin目录
    bin_dir = os.path.join(sys.prefix, 'bin')
    ytdl_path = os.path.join(bin_dir, 'yt-dlp')
    if os.path.exists(ytdl_path):
        return ytdl_path
    ytdl_path = os.path.join(bin_dir, 'youtube-dl')
    if os.path.exists(ytdl_path):
        return ytdl_path
    
    return None

# 尝试查找 yt-dlp 或 youtube-dl
ytdl_path = find_ytdl()

class URLVideoDownloader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_url": ("STRING", {"default": "https://example.com/video.mp4", "multiline": False}),
                "output_dir": ("STRING", {"default": folder_paths.get_temp_directory()}),
                "filename": ("STRING", {"default": "video_{timestamp}.mp4"}),
            },
            "optional": {
                "format": (["best", "bestvideo+bestaudio", "mp4", "webm", "avi", "mkv", "mov"], {"default": "best"}),
                "quality": (["最高", "高", "中", "低"], {"default": "最高"}),
                "extract_audio": (["否", "是"], {"default": "否"}),
                "audio_format": (["mp3", "aac", "m4a", "wav"], {"default": "mp3"}),
                "get_video_info": (["否", "是"], {"default": "否"}),
                "progress_callback": ("PROGRESS_CALLBACK",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "video_info")
    FUNCTION = "download_video"
    CATEGORY = "Video/Utility"
    
    def get_video_info(self, video_url):
        """获取视频信息"""
        if not ytdl_path:
            raise RuntimeError(
                "未找到 yt-dlp 或 youtube-dl。\n"
                "请按以下步骤安装：\n"
                "1. 打开终端\n"
                "2. 运行: pip3 install yt-dlp\n"
                "3. 如果上述命令不起作用，请尝试：\n"
                "   - macOS: brew install yt-dlp\n"
                "   - Linux: sudo apt install yt-dlp\n"
                "   - Windows: 请确保Python的Scripts目录在系统PATH中"
            )
            
        cmd = [
            ytdl_path,
            "--dump-json",
            "--no-playlist",
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取视频信息失败: {e.stderr}")
        except json.JSONDecodeError:
            raise RuntimeError("解析视频信息失败")
    
    def download_video(self, video_url, output_dir, filename, format="best", quality="最高", 
                      extract_audio="否", audio_format="mp3", get_video_info="否", progress_callback=None):
        # 验证下载工具是否可用
        if not ytdl_path:
            raise RuntimeError(
                "未找到 yt-dlp 或 youtube-dl。\n"
                "请按以下步骤安装：\n"
                "1. 打开终端\n"
                "2. 运行: pip3 install yt-dlp\n"
                "3. 如果上述命令不起作用，请尝试：\n"
                "   - macOS: brew install yt-dlp\n"
                "   - Linux: sudo apt install yt-dlp\n"
                "   - Windows: 请确保Python的Scripts目录在系统PATH中"
            )
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取视频信息（如果需要）
        video_info = None
        if get_video_info == "是":
            try:
                video_info = self.get_video_info(video_url)
                if progress_callback:
                    progress_callback(10, "已获取视频信息")
            except Exception as e:
                if progress_callback:
                    progress_callback(0, f"获取视频信息失败: {str(e)}")
                raise
        
        # 替换文件名中的时间戳占位符
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename.format(timestamp=timestamp)
        
        # 构建完整输出路径
        output_path = os.path.join(output_dir, filename)
        
        # 根据质量设置选择格式
        quality_map = {
            "最高": "best",
            "高": "best[height<=1080]",
            "中": "best[height<=720]",
            "低": "best[height<=480]"
        }
        format_spec = quality_map.get(quality, "best")
        
        # 构建下载命令
        cmd = [
            ytdl_path,
            "--format", f"{format_spec}+bestaudio/best" if format == "best" else format,
            "--output", output_path,
            "--no-playlist",
            "--no-warnings",
            "--prefer-ffmpeg",
            video_url
        ]
        
        # 如果需要提取音频
        if extract_audio == "是":
            cmd.extend(["--extract-audio", "--audio-format", audio_format])
        
        # 执行下载
        try:
            if progress_callback:
                progress_callback(20 if get_video_info == "是" else 0, "开始下载视频...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 监控下载进度
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if "[download]" in output and "%" in output:
                        try:
                            percent = float(output.split("%")[0].split()[-1])
                            if progress_callback:
                                progress_callback(
                                    20 + int(percent * 0.8) if get_video_info == "是" else int(percent),
                                    f"下载进度: {percent:.1f}%"
                                )
                        except:
                            pass
            
            if process.returncode != 0:
                error_msg = process.stderr.read()
                raise RuntimeError(f"下载失败: {error_msg}")
            
            if progress_callback:
                progress_callback(100, "视频下载完成")
            
            return (output_path, json.dumps(video_info, ensure_ascii=False) if video_info else "")
            
        except Exception as e:
            error_msg = f"下载失败: {str(e)}"
            if progress_callback:
                progress_callback(0, error_msg)
            raise RuntimeError(error_msg)

# 定义节点列表
NODE_CLASS_MAPPINGS = {
    "URLVideoDownloader": URLVideoDownloader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "URLVideoDownloader": "从URL下载视频"
}