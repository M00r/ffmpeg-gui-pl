# Wtyczka: presety pod YouTube, Twitter/X, Instagram.

PRESETS = {
    "YouTube 1080p (MP4/H.264)": {
        "label": "YouTube 1080p",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "20",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
                   "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "{output}",
        ],
        "ext": "mp4",
    },
    "Twitter/X 720p (MP4/H.264)": {
        "label": "Twitter/X 720p",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease",
            "-c:a", "aac", "-b:a", "128k",
            "{output}",
        ],
        "ext": "mp4",
    },
    "Instagram Reels (MP4/H.264, 9:16)": {
        "label": "Instagram Reels",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
                   "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "aac", "-b:a", "128k",
            "{output}",
        ],
        "ext": "mp4",
    },
}