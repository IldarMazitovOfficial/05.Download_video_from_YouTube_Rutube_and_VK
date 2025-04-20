# ютюб best 4к 2к 1080 480 360 240 144 mp3    https://www.youtube.com/watch?v=e6pxeEXNelw
# рутюб best 4к 2к 1080 480 360 240* 144 mp3*         https://rutube.ru/video/c9a3f7d4c6db1c6cb86c1dcc6fefc938/
# вк best 4к 2к 1080 480 360 240 144 mp3              https://vkvideo.ru/video-223532369_456239398
# https://rutube.ru/video/f3db24872caf7e47a6b060732ec6d3c5/

import yt_dlp
import os
import getpass
import re


def get_download_path():
    user = getpass.getuser()
    return os.path.join("C:\\Users", user, "Downloads")


def get_platform(url):
    url = url.lower()
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "vk.com" in url or "vkvideo.ru" in url or "video.vk.com" in url:
        return "vk"
    if "rutube.ru" in url:
        return "rutube"
    return "unknown"

def show_available_resolutions(formats):
    print("\n📺 Доступные форматы:")
    for f in formats:
        print(f"- id: {f.get('format_id')}, height: {f.get('height')}, note: {f.get('format_note')}, ext: {f.get('ext')}")

def show_quality_menu():
    print("\nЧто Вы хотите скачать?")
    print("0. Просто ЛУЧШЕЕ качество видео, которое существует")
    print("1. 4K")
    print("2. 2K")
    print("3. 1080p")
    print("4. 720p")
    print("5. 480p")
    print("6. 360p")
    print("7. 240p")
    print("8. 144p")
    print("9. MP3")
    print("10. НАЗАД")


def show_available_resolutions(formats):
    resolutions = sorted(set(f.get("height") for f in formats if f.get("height")), reverse=True)


def get_format_by_choice(choice, is_rutube=False):
    base_fmt = "best[height={h}]" if is_rutube else "bestvideo[height={h}]+bestaudio"

    video_formats = {
        "0": ("bestvideo+bestaudio/best", "BEST"),
        "1": (base_fmt.format(h=2160), "2160p"),
        "2": (base_fmt.format(h=1440), "1440p"),
        "3": (base_fmt.format(h=1080), "1080p"),
        "4": (base_fmt.format(h=720), "720p"),
        "5": (base_fmt.format(h=480), "480p"),
        "6": (base_fmt.format(h=360), "360p"),
        "7": (base_fmt.format(h=240), "240p"),
        "8": (base_fmt.format(h=144), "144p"),
        "9": ("bestaudio", "mp3"),
    }

    ext_map = {
        "9": "mp3"
    }

    if choice == "10":
        return None, None, None

    format_str, quality_suffix = video_formats.get(choice, ("best", ""))
    extension = ext_map.get(choice, "mp4")
    return format_str, extension, quality_suffix

def get_available_formats(url):
    try:
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        ydl_opts = {
            'quiet': True,
            'cookiefile': cookies_path if os.path.exists(cookies_path) else None
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            if not formats:
                raise yt_dlp.utils.DownloadError("Форматы видео не найдены (возможно, видео приватное или защищено).")
            return formats, info.get("title", "video")
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Ошибка при получении информации о видео:\n{e}")
        return [], "video"




def is_format_available(formats, selected_format):
    if selected_format in ["best", "bestvideo+bestaudio/best"]:
        return True
    if selected_format == "bestaudio":
        return any(f.get("acodec") != "none" for f in formats)

    # height-based check
    match = re.search(r"height=(\d+)", selected_format)
    if match:
        target_height = int(match.group(1))
        for f in formats:
            if f.get("height") == target_height:
                return True

        # ➕ Дополнительная проверка для RuTube — через format_note
        height_map = {
            144: "low",
            240: "low",
            360: "medium",
            480: "medium",
            720: "high",
            1080: "ultra",
            1440: "ultra",
            2160: "ultra",
        }
        note = height_map.get(target_height)
        if note:
            return any(note in (f.get("format_note") or "").lower() for f in formats)

    return False

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def download_video(url, selected_format, extension, quality_suffix, video_title):
    download_path = get_download_path()
    safe_title = sanitize_filename(video_title)
    base_filename = f"{safe_title}_{'[' + quality_suffix + ']' if quality_suffix else ''}".strip("_")

    ydl_opts = {
        'format': selected_format,
        'outtmpl': os.path.join(download_path, base_filename + '.%(ext)s'),
        'noplaylist': True,
        'merge_output_format': extension,
    }

    if extension == "mp3":
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    print("Скачивание началось...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Файл сохранён как: {base_filename}.{extension}\n→ Путь: {download_path}")
    except yt_dlp.utils.DownloadError as e:
        print(f"Ошибка при скачивании: {e}")


if __name__ == "__main__":
    while True:
        video_url = input("\nВведите ссылку на видео (YouTube, VK, RuTube): ").strip()
        if video_url.lower() == "exit":
            break

        if not video_url.startswith("http"):
            print("⚠ Некорректная ссылка.")
            continue

        platform = get_platform(video_url)
        if platform == "unknown":
            print("⚠ Сайт не поддерживается.")
            continue

        formats, title = get_available_formats(video_url)
        if not formats:
            print("⚠ Пропускаем ссылку. Форматы не найдены.")
            continue

        show_available_resolutions(formats)

        while True:
            show_quality_menu()
            choice = input("Введите номер (0–10): ").strip()
            is_rutube = platform == "rutube"
            selected_format, extension, quality_suffix = get_format_by_choice(choice, is_rutube=is_rutube)

            if selected_format is None:
                print("Возврат к вводу ссылки.")
                break

            if is_format_available(formats, selected_format):
                download_video(video_url, selected_format, extension, quality_suffix, title)
                break
            else:
                print("⚠ Такого качества нет. Попробуйте выбрать другой вариант.")