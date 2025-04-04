# %%

import os
import json
import yt_dlp
import ssl
import urllib.request

# Directory setup
OUTPUT_DIR = "downloads"
VIDEO_DIR = "video"
METADATA_DIR = "metadata"
LOG_DIR = "logs"


os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "rejected_videos.log")


def log_rejected_video(video_url, reason):
    """Log rejected videos for tracking."""
    with open(LOG_FILE, "a") as log:
        log.write(f"{video_url} - {reason}\n")
    print(f"❌ Skipping video: {video_url} | Reason: {reason}")


# Here we are checking if the SSL certificate is valid and if the connection is being redirected to a fake YouTube page.
def check_youtube_ssl():
    """Ensure we are connecting to a real YouTube server."""
    try:
        response = urllib.request.urlopen(
            "https://www.youtube.com", context=ssl.create_default_context()
        )
        if "youtube.com" not in response.geturl():
            print("⚠ WARNING: Unexpected redirect detected! Possible SSL interception.")
            print(f"Redirected to: {response.geturl()}")
            exit()
    except Exception as e:
        print(f"⚠ SSL check failed: {e}")
        print("Try using a VPN or different network.")
        exit()


# The function below downloads the audio from YouTube, trims it if needed, and converts it to WAV format.
def download_youtube_video(url):
    """Download audio from YouTube, optionally trim, and convert to WAV."""

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{VIDEO_DIR}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",  # Merge video and audio into one file
        # "postprocessors": [
        #     {
        #         "key": "FFmpegExtractAudio",
        #         "preferredcodec": "mp3",
        #         "preferredquality": "192",
        #     }
        # ],
        # "nocheckcertificate": True,  # Use only for YouTube downloads
        "noplaylist": True,  # Ensure only a single video is downloaded
        "geo_bypass": True,  # Bypass geo-restrictions safely
        "http_headers": {"User-Agent": "Mozilla/5.0"},  # Mimic browser requests
        "quiet": True,  # Suppress yt_dlp warnings and logs
        "no_warnings": True,  # Suppress warnings
    }

    # Ensure we are not being redirected to a fake YouTube page
    check_youtube_ssl()

    r"""
    These need to be removed if SSL certificate is not an issue.
        "nocheckcertificate": True,  # Use only for YouTube downloads
        "geo_bypass": True,  # Bypass geo-restrictions safely
        "http_headers": {"User-Agent": "Mozilla/5.0"},  # Mimic browser requests

        check_youtube_ssl()

        - Check for Fake YouTube Redirects
        - Limit nocheckcertificate=True to Only YouTube
        - If YouTube redirects to a suspicious URL. Adds a geo-bypass option to avoid using untrusted proxies.
        - The User-Agent header makes your request look like a real browser, avoiding detection as a bot.
        - 
    }
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # Extract metadata first

        # Check if the video has a Creative Commons license
        license_type = info_dict.get("license")
        print(f"License type: {license_type}")
        if license_type != "Creative Commons Attribution license (reuse allowed)":
            log_rejected_video(url, "Non-Creative Commons video (Copyrighted)")
            return None  # Skip downloading

        print(f"✅ Downloading allowed video: {info_dict['title']}")

        # Now, actually download the file since it's allowed
        info_dict = ydl.extract_info(url, download=True)

        # Define filenames
        safe_title = (
            info_dict["title"].replace(" ", "_").replace("/", "_")
        )  # Ensure valid filenames
        video_filename = f"{VIDEO_DIR}/{safe_title}.mp4"
        metadata_filename = f"{METADATA_DIR}/{safe_title}.json"

        # Extract metadata
        metadata = {
            "title": info_dict.get("title", "Unknown"),
            "uploader": info_dict.get("uploader", "Unknown"),
            "upload_date": info_dict.get("upload_date", "Unknown"),
            "duration": info_dict.get("duration", 0),
            "url": info_dict.get("webpage_url", url),
            "filename": video_filename,
        }

        # Save metadata with the same name as WAV file
        with open(metadata_filename, "w") as f:
            json.dump(metadata, f, indent=4)

        return metadata


if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")

    metadata = download_youtube_video(video_url)
    print(f"🎵 Video saved as mp4 in {VIDEO_DIR}, and metadata saved in {METADATA_DIR}")
