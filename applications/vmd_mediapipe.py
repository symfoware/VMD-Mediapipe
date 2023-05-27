#!/usr/bin/env python3
#
# vmdlifting.py - estimate 3D pose by Mediapipe, and convert the pose data to VMD
#

def usage(prog):
    print('usage: ' + prog + ' IMAGE_FILE VMD_FILE')
    sys.exit()


import os
import cv2
import mediapipe as mp

from pos2vmd import positions_to_frames, make_showik_frames, convert_position
from VmdWriter import VmdWriter
from refine_position import refine_position
from adjust_center import adjust_center
#from dump_positions import dump_positions
import argparse;

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.realpath(DIR_PATH + '/..')
MODEL_PATH = os.path.join(PROJECT_PATH, 'data/saved_sessions/pose_landmarker_full.task')

def vmd_convert(image_file, vmd_file, center_enabled=False):
    image_file_path = os.path.realpath(image_file)
    cap = cv2.VideoCapture(image_file_path)

    # Mediapipe setting
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO)

    landmarker = PoseLandmarker.create_from_options(options)

    positions_list = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps:
        print('fps is noset.')
    frame_num = 0

    print('pose estimation start. fps:%.1f' % (fps))
    
    while (cap.isOpened()):
        ret, image = cap.read()
        if not ret:
            break

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        # pose estimation
        try:
            pose_landmarker_result = landmarker.detect_for_video(mp_image, int((frame_num / fps) * 1000))
        except Exception as ex:
            frame_num +=1
            print('error')
            print(ex)
            continue

        pose_2d = pose_landmarker_result.pose_landmarks
        pose_3d = pose_landmarker_result.pose_world_landmarks
        if not pose_2d or not pose_3d:
            frame_num += 1
            continue
    
        #dump_positions(pose_2d, pose_3d)
        positions = convert_position(pose_3d)
        #adjust_center(pose_2d, positions, image)
        positions_list.append(positions)
        
        print("frame_num: ", frame_num)
        frame_num += 1
        
        
    # close model
    landmarker.close()

    
    #refine_position(positions_list)
    bone_frames = []
    frame_num = 0
    for positions in positions_list:
        if positions is None:
            frame_num += 1
            continue
        bf = positions_to_frames(positions, frame_num, center_enabled)
        bone_frames.extend(bf)
        frame_num += 1

    showik_frames = make_showik_frames()
    writer = VmdWriter()
    writer.write_vmd_file(vmd_file, bone_frames, showik_frames)
    


   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='estimate 3D pose and generate VMD motion')
    parser.add_argument('--center', action='store_true', help='move center bone (experimental)')
    parser.add_argument('IMAGE_FILE')
    parser.add_argument('VMD_FILE')
    
    arg = parser.parse_args()
    vmd_convert(arg.IMAGE_FILE, arg.VMD_FILE, arg.center)

    # ex)
    # python3 applications/vmd_mediapipe.py applications/debug/b71_01.jpg applications/debug/test.vmd
    # python3 applications/vmd_mediapipe.py applications/debug/sample.mp4 applications/debug/test.vmd
    

