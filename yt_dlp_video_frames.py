# %%
import os
import re
import json
import yt_dlp
import ssl
import urllib.request
import cv2  # Ensure OpenCV is installed (pip install opencv-python)

# Directory setup
OUTPUT_DIR = "downloads"
VIDEO_DIR = "video"
METADATA_DIR = "metadata"
LOG_DIR = "logs"
FRAMES_DIR = "frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "rejected_videos.log")
TARGET_FPS = 5


def log_rejected_video(video_url, reason):
    """Log rejected videos for tracking."""
    with open(LOG_FILE, "a") as log:
        log.write(f"{video_url} - {reason}\n")
    print(f"❌ Skipping video: {video_url} | Reason: {reason}")


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


def clean_title(title):
    """
    Clean the title to create a safe filename.
    
    Removes characters that can cause issues in file names and replaces spaces with underscores.
    """
    # Remove any character that is not alphanumeric, a space, underscore or hyphen.
    cleaned = re.sub(r'[\\/*?:"<>|!]', "", title)
    # Further replace spaces with underscores.
    return cleaned.strip().replace(" ", "_")


def extract_frames(video_path, frames_dir, target_fps=TARGET_FPS):
    """
    Extract frames from the given video file at a reduced frame rate.
    
    Uses the video's original FPS to determine how many frames to skip so that the resulting frames approximate target_fps.
    Each saved frame is named with the format 'frame_XXXXXX.jpg'.
    """
    os.makedirs(frames_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return

    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Original video FPS: {orig_fps}")
    
    # Calculate the interval: how many frames to skip between saved frames.
    frame_interval = 1
    if orig_fps > 0 and target_fps > 0:
        frame_interval = int(round(orig_fps / target_fps))
        if frame_interval < 1:
            frame_interval = 1

    count = 0
    saved_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Save only frames that fall on the computed interval.
        if count % frame_interval == 0:
            frame_filename = os.path.join(frames_dir, f"frame_{saved_frames:06d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frames += 1
        count += 1

    cap.release()
    print(f"🎞️ Extracted {saved_frames} frames to {frames_dir} (target ~{target_fps} FPS)")

def download_youtube_video(url):
    """Download video from YouTube and save metadata; only allows Creative Commons licensed content."""
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{VIDEO_DIR}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",  # Merge video and audio into one file
        "noplaylist": True,           # Ensure only a single video is downloaded
        "geo_bypass": True,           # Bypass geo-restrictions safely
        "http_headers": {"User-Agent": "Mozilla/5.0"},  # Mimic browser requests
        "quiet": True,                # Suppress yt_dlp warnings and logs
        "no_warnings": True,          # Suppress warnings
    }

    # Ensure we are connecting to a valid YouTube page
    check_youtube_ssl()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        
        # Check if the video has a Creative Commons license
        license_type = info_dict.get("license")
        print(f"License type: {license_type}")
        if license_type != "Creative Commons Attribution license (reuse allowed)":
            log_rejected_video(url, "Non-Creative Commons video (Copyrighted)")
            return None  # Skip downloading

        print(f"✅ Downloading allowed video: {info_dict['title']}")
        # Download the video file
        info_dict = ydl.extract_info(url, download=True)

        # Clean title to create safe filenames
        safe_title = clean_title(info_dict["title"])
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

        # Save metadata
        with open(metadata_filename, "w") as f:
            json.dump(metadata, f, indent=4)

        return metadata


if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    metadata = download_youtube_video(video_url)

    if metadata:
        # Create a dedicated frames folder for this video using cleaned title
        safe_title = clean_title(metadata["title"])
        frames_output_dir = os.path.join(FRAMES_DIR, safe_title)
        video_filename = os.path.join(VIDEO_DIR, metadata["title"] + ".mp4")
        # Extract frames from the downloaded video
        extract_frames(video_filename, frames_output_dir)

        print(f"🎵 Video saved as mp4 in {VIDEO_DIR}, metadata saved in {METADATA_DIR}, and frames extracted in {frames_output_dir}")
