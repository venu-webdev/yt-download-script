import os
import threading
import time
from tkinter import (
    Tk, Label, Entry, Button, StringVar, filedialog, messagebox, Text, Scrollbar, HORIZONTAL, VERTICAL, RIGHT, BOTTOM, Y, X, BOTH, Frame, ttk
)
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import requests
from io import BytesIO


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.progress_var = StringVar(value="Progress will be displayed here")
        self.title_var = StringVar(value="Video Title: None")
        self.size_var = StringVar(value="File Size: N/A")

        self.build_gui()

    def build_gui(self):
        """Builds the GUI for the application."""
        Label(self.root, text="YouTube URL:").pack(pady=5)

        self.url_entry = Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        Label(self.root, textvariable=self.progress_var).pack(pady=5)

        Button(self.root, text="Download Video", command=self.start_download).pack(pady=5)

        # Frame for log box
        log_box_container = Frame(self.root, padx=10, pady=10)
        log_box_container.pack(pady=5, fill=BOTH, expand=True)

        # Log box with scrollbars
        self.log_box = Text(log_box_container, wrap="none", height=7)
        self.log_box.pack(side="top", fill=BOTH, expand=True)

        scrollbar_horizontal = Scrollbar(log_box_container, orient=HORIZONTAL, command=self.log_box.xview)
        scrollbar_horizontal.pack(side="bottom", fill=X)

        scrollbar_vertical = Scrollbar(log_box_container, orient=VERTICAL, command=self.log_box.yview)
        scrollbar_vertical.pack(side=RIGHT, fill=Y)

        self.log_box.config(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

        self.thumbnail_label = Label(self.root, text="Thumbnail will appear here", width=300, height=200)
        self.thumbnail_label.pack(pady=5)

        Label(self.root, textvariable=self.title_var).pack(pady=2)
        Label(self.root, textvariable=self.size_var).pack(pady=2)

    def log_message(self, message, newline=True):
        """Logs messages to the log box."""
        self.log_box.insert('end', message + '\n' if newline else message)
        self.log_box.see('end')
        self.root.update_idletasks()

    def update_thumbnail(self, thumbnail_url):
        """Updates the video thumbnail in the UI."""
        try:
            response = requests.get(thumbnail_url, stream=True)
            response.raise_for_status()
            image_data = Image.open(BytesIO(response.content))
            image_data.thumbnail((300, 200))
            thumbnail_img = ImageTk.PhotoImage(image_data)
            self.thumbnail_label.config(image=thumbnail_img)
            self.thumbnail_label.image = thumbnail_img
        except Exception as e:
            self.log_message(f"Failed to load thumbnail: {e}")
            self.thumbnail_label.config(text="Thumbnail failed to load")

    def download_video_threaded(self):
        """Handles video downloading in a separate thread."""
        youtube_url = self.url_entry.get().strip()
        if not youtube_url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        output_dir = filedialog.askdirectory(title="Select Download Folder")
        if not output_dir:
            return

        # Initialize shared variables
        download_info = {
            "start_time": None,
            "file_name": "",
        }

        def progress_hook(d):
            if d['status'] == 'downloading':
                if download_info["start_time"] is None:
                    download_info["start_time"] = time.time()

                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)
                elapsed_time = time.time() - download_info["start_time"]
                speed = d.get('speed', None)

                percentage = (downloaded_bytes / total_bytes) * 100
                speed_display = f"Speed: {speed / 1048576:.2f} MB/s" if speed else "Speed: 0 MB/s"
                eta = (total_bytes - downloaded_bytes) / speed if speed and speed > 0 else 0
                eta_str = f"ETA: {time.strftime('%H:%M:%S', time.gmtime(eta))}"

                progress_message = (
                    f"Downloaded: {percentage:.2f}% | {speed_display} | "
                    f"Time: {elapsed_time:.2f}s | {eta_str}"
                )

                self.progress_var.set(progress_message)
                self.root.update_idletasks()

            elif d['status'] == 'finished':
                self.progress_var.set("Download complete!")
                self.log_message("Download complete!")

        try:
            ydl_opts = {
                "format": "bestvideo[ext=mp4][vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]",
                "merge_output_format": "mp4",
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True,
                "noplaylist": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                self.log_message("Video Metadata:")
                self.log_message(str(info_dict))

                video_title = info_dict.get("title", "Unknown Title")
                thumbnail_url = info_dict.get("thumbnail", "")
                download_info["file_name"] = ydl.prepare_filename(info_dict)

                self.title_var.set(f"Video Title: {video_title}")
                self.update_thumbnail(thumbnail_url)

                # Perform the actual download
                ydl.download([youtube_url])

                # Get the actual file size after the download
                try:
                    actual_file_size = os.path.getsize(download_info["file_name"])
                    self.size_var.set(f"File Size: {actual_file_size / 1048576:.2f} MB")
                except Exception as e:
                    self.size_var.set("File Size: Unknown")
                    self.log_message(f"Failed to get file size: {e}")

            # Show success dialog and close the application on confirmation
            if messagebox.showinfo("Success", "Download completed!"):
                self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.log_message(f"Error: {e}")




    def start_download(self):
        """Starts the video download in a new thread."""
        download_thread = threading.Thread(target=self.download_video_threaded)
        download_thread.start()


if __name__ == "__main__":
    root = Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
