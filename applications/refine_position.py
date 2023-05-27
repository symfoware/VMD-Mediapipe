# refine_position.py - refine bone position data

import numpy as np
from scipy.fftpack import fft, ifft, fftfreq
from PyQt6.QtGui import QVector3D

def interpolate(vec):
    last_index = None
    last_val = None
    for i in range(0, len(vec)):
        if vec[i] is not None:
            if last_index is not None:
                for j in range(last_index + 1, i):
                    vec[j] = last_val + (vec[i] - last_val) * (j - last_index) / (i - last_index)
            else:
                for j in range(0, i):
                    vec[j] = vec[i]
            last_index = i
            last_val = vec[i]

    for i in range(last_index + 1, len(vec)):
        vec[i] = last_val
            
def lowpass_filter(vec):
    cutoff_freq = 5
    sample_freq = 30
    cutoff_idx = cutoff_freq * len(vec) / sample_freq
    signal = np.array(vec)
    transformed = fft(signal)
    for i in range(cutoff_idx, len(vec)):
        transformed[i] = 0
    filterd_signal = np.real(ifft(transformed))
    for i in range(0, len(vec)):
        vec[i] = filterd_signal[i]
    
def smooth_position(positions_list):
    minimum_length = 3
    total_length = len(positions_list)
    if total_length < minimum_length:
        return

    joint = []
    for i in range(0, 17):
        joint.append([[], [], []])

    for pos in positions_list:
        for i in range(0, 17):
            if len(pos) < i + 1:
                joint[i][0].append(None)
                joint[i][1].append(None)
                joint[i][2].append(None)
            else:
                joint[i][0].append(pos[i].x())
                joint[i][1].append(pos[i].y())
                joint[i][2].append(pos[i].z())

    for i in range(0, 17):
        for j in range(0, 3):
            interpolate(joint[i][j])
            #lowpass_filter(joint[i][j])
                                   
    for i in range(0, total_length):
        positions_list[i] = []
        for j in range(0, 17):
            p = QVector3D(joint[j][0][i], joint[j][1][i], joint[j][2][i])
            positions_list[i].append(p)
            
            
def normalize_for_vmd(positions_list):
    center_offset = QVector3D(0, 0, 0)
    spine_len = 0
    ground_y = float("inf")
    count = 0
    for pos in positions_list:
        if len(pos) < 17:
            continue
        if pos[3].y() < ground_y:
            ground_y = pos[3].y() # 右足首
        if pos[6].y() < ground_y:
            ground_y = pos[6].y() # 左足首
        center_offset += pos[7]
        spine_len = spine_len + (pos[8] - pos[7]).length()
        count += 1

    center_offset /= count
    spine_len /= count
    scale = 3.2 / spine_len

    for pos in positions_list:
        for p in pos:
            #p -= center_offset
            p *= scale

def refine_position(positions_list):
    smooth_position(positions_list)
    #normalize_for_vmd(positions_list)
