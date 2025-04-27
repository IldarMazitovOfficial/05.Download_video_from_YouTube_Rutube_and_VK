import yt_dlp
import os
import sys
import re
import getpass
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("MazitovFASTdownloader v.1.0")
app.geometry("700x450")

formats = []
title = ""
status_text = ctk.StringVar()
status_text.set("")

downloading = False  # глобальный флаг для анимации

def create_entry_with_context_menu(master, **kwargs):
    entry = ctk.CTkEntry(master, **kwargs)
    menu = tk.Menu(entry, tearoff=0)
    menu.add_command(label="Вставить", command=lambda: entry.event_generate('<<Paste>>'))
    def do_popup(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    entry.bind("<Button-3>", do_popup)
    return entry

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_available_formats(url):
    try:
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        ydl_opts = {
            'quiet': True,
            'cookiefile': cookies_path if os.path.exists(cookies_path) else None
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("formats", []), info.get("title", "video")
    except yt_dlp.utils.DownloadError as e:
        status_text.set("❌ Ошибка загрузки информации")
        return [], ""

def start_download():
    threading.Thread(target=_start_download).start()

def _start_download():
    global downloading
    url = url_entry.get().strip()
    selected_quality = quality_combobox.get()

    if not url:
        status_text.set("⚠ Введите ссылку на видео")
        return

    platform = get_platform(url)
    if platform == "unknown":
        status_text.set("⚠ Сайт не поддерживается")
        return

    if selected_quality == "Выберите качество":
        status_text.set("⚠ Выберите качество")
        return

    formats, title = get_available_formats(url)
    if not formats:
        status_text.set("⚠ Форматы не найдены")
        return

    selected_format = format_mapping.get(selected_quality, "best")
    extension = "mp4" if selected_quality != "MP3" else "mp3"
    quality_suffix = selected_quality

    download_path = get_download_path()
    safe_title = sanitize_filename(title)
    base_filename = f"{safe_title}_{'[' + quality_suffix + ']' if quality_suffix else ''}".strip("_")

    ydl_opts = {
        'format': selected_format,
        'outtmpl': os.path.join(download_path, base_filename + '.%(ext)s'),
        'noplaylist': True,
        'merge_output_format': extension,
        'progress_hooks': [progress_hook],
    }

    if extension == "mp3":
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

    ffmpeg_path = resource_path('ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    try:
        downloading = True
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        downloading = False
        status_text.set("✅ Скачивание завершено! Ищите файл в папке 'Загрузки'. ✅")
        progress_bar.configure(progress_color="green")
        progress_bar.set(1)
    except yt_dlp.utils.DownloadError as e:
        downloading = False
        status_text.set(f"❌ Ошибка при скачивании")
        progress_bar.configure(progress_color="red")
        progress_bar.set(0)

def fetch_formats():
    global formats, title
    url = url_entry.get().strip()

    if not url:
        status_text.set("⚠ Введите ссылку на видео!")
        return

    formats, title = get_available_formats(url)
    if not formats:
        status_text.set("⚠ Не найдены форматы")
        return

    available_qualities = ["Лучшее качество", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", "MP3"]
    quality_combobox.configure(values=available_qualities)
    quality_combobox.set("Лучшее качество")

def paste_from_clipboard():
    clipboard_text = pyperclip.paste()
    url_entry.delete(0, tk.END)
    url_entry.insert(0, clipboard_text)
    fetch_formats()

def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('_percent_str', '0.0%')
        downloaded = downloaded.strip().replace('%', '')
        try:
            progress_bar.set(float(downloaded) / 100)
        except:
            pass

def animate_progress():
    # Плавная анимация при скачивании
    while True:
        if downloading:
            current = progress_bar.get()
            progress_bar.set(min(current + 0.002, 1))
        time.sleep(0.02)

# Интерфейс
frame = ctk.CTkFrame(app, fg_color="transparent")
frame.pack(expand=True)

url_label = ctk.CTkLabel(frame, text="ВВЕДИТЕ ССЫЛКУ НА ВИДЕО:", font=("Arial", 30))
url_label.pack(pady=(0, 0))

url_label = ctk.CTkLabel(frame, text="(youtube.com, rutube.com, vkvideo.ru)", font=("Arial", 13))
url_label.pack(pady=(1, 1))

url_entry = create_entry_with_context_menu(frame, width=450, height=35)
url_entry.pack(pady=(5, 10))

progress_bar = ctk.CTkProgressBar(frame, width=450, height=12, progress_color="red")
progress_bar.set(0)
progress_bar.pack(pady=(0, 20))

paste_button = ctk.CTkButton(frame, text="Вставить ссылку", command=paste_from_clipboard, width=200, height=35)
paste_button.pack(pady=(0, 15))

quality_combobox = ctk.CTkComboBox(frame, width=300, height=35, values=[
    "Лучшее качество", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", "MP3"
])
quality_combobox.set("Выберите качество")
quality_combobox.pack(pady=(0, 15))

start_button = ctk.CTkButton(frame, text="Скачать", command=start_download, width=200, height=40)
start_button.pack(pady=(0, 15))

status_label = ctk.CTkLabel(frame, textvariable=status_text, font=("Arial", 16))
status_label.pack(pady=(10, 10))

format_mapping = {
    "Лучшее качество": "bestvideo+bestaudio/best",
    "2160p": "bestvideo[height=2160]+bestaudio",
    "1440p": "bestvideo[height=1440]+bestaudio",
    "1080p": "bestvideo[height=1080]+bestaudio",
    "720p": "bestvideo[height=720]+bestaudio",
    "480p": "bestvideo[height=480]+bestaudio",
    "360p": "bestvideo[height=360]+bestaudio",
    "240p": "bestvideo[height=240]+bestaudio",
    "144p": "bestvideo[height=144]+bestaudio",
    "MP3": "bestaudio"
}

# Запускаем анимацию прогресс-бара
threading.Thread(target=animate_progress, daemon=True).start()

app.mainloop()
