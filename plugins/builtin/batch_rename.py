# Wtyczka: presety audio i lekkiej kompresji H.265.

PRESETS = {
    "Audio: MP3 320 kbps": {
        "label": "MP3 320 kbps",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-vn", "-c:a", "libmp3lame", "-b:a", "320k",
            "{output}",
        ],
        "ext": "mp3",
    },
    "Audio: FLAC (bezstratny)": {
        "label": "FLAC",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-vn", "-c:a", "flac",
            "{output}",
        ],
        "ext": "flac",
    },
    "Wideo: H.265 bardzo mały plik": {
        "label": "H.265 mały",
        "cmd": [
            "ffmpeg", "-y", "-i", "{input}",
            "-c:v", "libx265", "-preset", "slow", "-crf", "28",
            "-c:a", "aac", "-b:a", "96k",
            "{output}",
        ],
        "ext": "mp4",
    },
}