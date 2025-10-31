
# YouTube Video Downloader with Metadata Extraction

This project is a simple Python script that downloads a YouTube video (only if it has a Creative Commons license) and saves it as an MP4 file along with its metadata in JSON format. It uses the [yt-dlp](https://github.com/yt-dlp/yt-dlp) library to handle video extraction and download.

## Update
- We add a new script `yt_dlp_video_frames.py`. In addition to the video as described below, this script also saves frames as images.

## Features

- **Video Download:** Downloads the best available video and audio streams and merges them into a single MP4 file.
- **Metadata Extraction:** Extracts metadata such as title, uploader, upload date, duration, and URL, saving it as a JSON file.
- **License Check:** Only downloads videos with a Creative Commons Attribution license (reuse allowed). Videos that do not meet this criterion are logged and skipped.
- **SSL Verification:** Checks for a valid YouTube SSL certificate to help ensure you are connecting to the genuine YouTube server.
- **Output Organization:** Saves downloaded videos, metadata, and any rejected video logs into separate directories.

## Requirements

- Python 3.6 or above
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Standard Python libraries: `os`, `json`, `ssl`, `opencv` and `urllib.request`

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/ai-mg/youtube_video_downloader.git
   cd youtube_video_downloader
   ```

## Usage

Run the script using your Python interpreter:

```bash
python your_script_name.py
```

When prompted, paste the YouTube video URL. The script will:

1. Check for a valid SSL connection to YouTube.
2. Extract metadata from the video.
3. Check if the video is licensed under Creative Commons Attribution.
   - If not, the video is skipped and logged.
4. Download the video into the `video` directory.
5. Save the video’s metadata in the `metadata` directory.

For example, after running the script you might see:

```
Enter YouTube video URL: https://www.youtube.com/watch?v=exampleID
License type: Creative Commons Attribution license (reuse allowed)
✅ Downloading allowed video: Example Video Title
🎵 Video saved as mp4 in video, and metadata saved in metadata
```

## Directory Structure

After running the script, the following directories will be created (if they do not already exist):

- **downloads:** (Not used if you update the template, but can be kept for future extensions)
- **video:** Contains the downloaded video files.
- **metadata:** Contains JSON files with metadata corresponding to each downloaded video.
- **logs:** Contains the log file (`rejected_videos.log`) with URLs that were skipped due to license issues.

## Customization

- **Output Template:**  
  By default, the output template for downloaded files is set to save in the `video` directory:
  ```python
  "outtmpl": f"{VIDEO_DIR}/%(title)s.%(ext)s",
  ```
  You can change this if needed.

- **Merge Format:**  
  The option `"merge_output_format": "mp4"` ensures that video and audio are merged into one MP4 file. You can adjust this setting based on your needs.

- **SSL and HTTP Headers:**  
  The script uses custom HTTP headers to mimic a browser and check the SSL certificate to avoid potential redirection to fake YouTube pages.

