#!/bin/bash
# run_workflow.sh - Example workflow script demonstrating how to use Founder Note Toolkit (FNT)

set -e

VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Astley - Never Gonna Give You Up (Classic Test URL)

echo "🎬 Step 1: Displaying video metadata and formats..."
fnt info "$VIDEO_URL"

echo -e "\n📥 Step 2: Downloading transcript..."
fnt transcript "$VIDEO_URL" --lang "en" --format "all"

# The output folder is based on the sanitized title. For test purposes, let's assume it is "Rick_Astley_-_Never_Gonna_Give_You_Up"
EPISODE_DIR="$HOME/Downloads/FounderNote/Rick_Astley_-_Never_Gonna_Give_You_Up"
TRANSCRIPT_JSON="$EPISODE_DIR/transcript.json"

if [ -f "$TRANSCRIPT_JSON" ]; then
    echo -e "\n🔍 Step 3: Searching transcript for occurrences of 'never'..."
    fnt search "$TRANSCRIPT_JSON" "never"

    echo -e "\n🧠 Step 4: Suggesting high-potential viral segments using AI or fallback engine..."
    fnt viral "$TRANSCRIPT_JSON"

    echo -e "\n✍️ Step 5: Generating viral titles for the first 60 seconds..."
    fnt titles "$TRANSCRIPT_JSON" --start "00:00:00" --end "00:01:00"
else
    echo -e "\n⚠️ Transcript JSON file not found at $TRANSCRIPT_JSON. Skipping search and analysis."
fi

echo -e "\n🎥 Step 6: Downloading a 30-second clip from the video..."
fnt clip --url "$VIDEO_URL" --start "00:00:10" --end "00:00:40" --name "my_fnt_clip"

echo -e "\n🎉 Workflow demo finished!"
