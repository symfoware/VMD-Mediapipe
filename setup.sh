#!/bin/bash

mkdir -p data/saved_sessions
cd data/saved_sessions

# fallback to curl if wget not available (e.g. git bash in Windows)
WGET='wget'
if ! [ -x "$(command -v git)" ]; then
	WGET='curl -O'
fi

echo 'Downloading models...'
${WGET} https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
cd ../..

echo 'Installing dependencies...'
pip install -r requirements.txt

echo 'Done'
