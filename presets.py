# Presety jakości, rozdzielczości, FPS i kodeków.
# Używane w oknie konwersji.

QUALITY_PRESETS = {
    "Bezstratny (CRF 0)":       {"crf": "0",  "preset": "veryslow"},
    "Bardzo wysoka (CRF 15)":   {"crf": "15", "preset": "slow"},
    "Wysoka (CRF 18)":          {"crf": "18", "preset": "medium"},
    "Standardowa (CRF 23)":     {"crf": "23", "preset": "medium"},
    "Niska (CRF 28)":           {"crf": "28", "preset": "fast"},
    "Bardzo niska (CRF 32)":    {"crf": "32", "preset": "veryfast"},
}

RESOLUTION_PRESETS = {
    "Bez zmiany":       None,
    "3840x2160 (4K)":   "3840:2160",
    "2560x1440 (2K)":   "2560:1440",
    "1920x1080 (FHD)":  "1920:1080",
    "1280x720 (HD)":    "1280:720",
    "854x480 (SD)":     "854:480",
    "640x360 (360p)":   "640:360",
    "320x240 (240p)":   "320:240",
}

FPS_PRESETS = {
    "Bez zmiany": None,
    "60 fps": 60, "30 fps": 30, "25 fps": 25, "24 fps": 24,
    "15 fps": 15, "10 fps": 10,
}

VIDEO_CODECS = {
    "H.264 (libx264)":          "libx264",
    "H.265 / HEVC (libx265)":   "libx265",
    "VP9 (libvpx-vp9)":         "libvpx-vp9",
    "AV1 (libaom-av1)":         "libaom-av1",
    "MPEG-4 (mpeg4)":           "mpeg4",
    "Kopiuj (bez rekompresji)": "copy",
}

AUDIO_CODECS = {
    "AAC":                "aac",
    "MP3 (libmp3lame)":   "libmp3lame",
    "Opus (libopus)":     "libopus",
    "Vorbis (libvorbis)": "libvorbis",
    "FLAC (bezstratny)":  "flac",
    "Kopiuj":             "copy",
    "Brak audio":         None,
}

AUDIO_BITRATES = {
    "Bez zmiany": None, "96 kbps": "96k", "128 kbps": "128k",
    "192 kbps": "192k", "256 kbps": "256k", "320 kbps": "320k",
}