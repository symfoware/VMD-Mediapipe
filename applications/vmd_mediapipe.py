#!/usr/bin/env python3
#
# vmd_mediapipe.py - estimate 3D pose by Mediapipe, and convert the pose data to VMD
#

def usage(prog):
    print('usage: ' + prog + ' IMAGE_FILE VMD_FILE')
    sys.exit()


import argparse
import os
import cv2
import mediapipe as mp

from VmdWriter import VmdWriter
#from adjust_center import adjust_center
import posisions as ps
import pos2vmd

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
            print(ex)
            continue

        pose_2d = pose_landmarker_result.pose_landmarks
        pose_3d = pose_landmarker_result.pose_world_landmarks
        if not pose_2d or not pose_3d:
            frame_num += 1
            continue
    
        #ps.dump(pose_3d, pose_2d)
        positions = ps.convert(pose_3d, pose_2d)
        #adjust_center(pose_2d, positions, image)
        positions_list.append(positions)
        
        print('frame_num: ', frame_num)
        frame_num += 1
        
        
    # close model
    landmarker.close()
    
    ps.refine(positions_list)
    bone_frames = []
    frame_num = 0
    for positions in positions_list:
        if positions is None:
            frame_num += 1
            continue
        frames = pos2vmd.positions_to_frames(positions['position'], frame_num)
        if center_enabled:
            ps.center(positions, frames, frame_num)

        bone_frames.extend(frames)
        frame_num += 1

    showik_frames = pos2vmd.make_showik_frames()
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
    # python3 applications/vmd_mediapipe.py applications/debug/pose.jpg applications/debug/test.vmd
    # python3 applications/vmd_mediapipe.py applications/debug/dummy.png applications/debug/test.vmd
    # python3 applications/vmd_mediapipe.py applications/debug/sample.mp4 applications/debug/test.vmd
    

