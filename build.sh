#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create the downloads folder just in case
mkdir -p static/downloads

# Render-specific FFmpeg installation
# This downloads a static Linux binary of FFmpeg
if [ ! -f ffmpeg ]; then
  echo "Downloading FFmpeg..."
  curl -L https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-linux-64.zip -o ffmpeg.zip
  unzip ffmpeg.zip
  rm ffmpeg.zip
  chmod +x ffmpeg
  chmod +x ffprobe
fi