import numpy as np
import scipy.fftpack
from PyQt6.QtGui import QVector3D
from VmdWriter import VmdBoneFrame

""" Lifting from the Deepでの番号
# jointの番号と説明 (3Dの番号, 2Dの番号, 説明)
joint = [(0, None, "腰"),
         (1, 8, "右脚付け根"),
         (2, 9, "右ひざ"),
         (3, 10, "右足首"),
         (4, 11, "左脚付け根"),
         (5, 12, "左ひざ"),
         (6, 13, "左足首"),
         (7, None, "胴体の中心"),
         (8, 1, "首の付け根"),
         (9, None, "あご"),
         (10, 0, "頭頂"),
         (11, 5, "左肩"),
         (12, 6, "左ひじ"),
         (13, 7, "左手首"),
         (14, 2, "右肩"),
         (15, 3, "右ひじ"),
         (16, 4, "右手首")]
"""

NAMES = {
    0: 'nose',
    1: 'left_eye_inner',
    2: 'left_eye',
    3: 'left_eye_outer',
    4: 'right_eye_inner',
    5: 'right_eye',
    6: 'right_eye_outer',
    7: 'left_ear',
    8: 'right_ear',
    9: 'mouth_left',
    10: 'mouth_right',
    11: 'left_shoulder',
    12: 'right_shoulder',
    13: 'left_elbow',
    14: 'right_elbow',
    15: 'left_wrist',
    16: 'right_wrist',
    17: 'left_pinky',
    18: 'right_pinky',
    19: 'left_index',
    20: 'right_index',
    21: 'left_thumb',
    22: 'right_thumb',
    23: 'left_hip',
    24: 'right_hip',
    25: 'left_knee',
    26: 'right_knee',
    27: 'left_ankle',
    28: 'right_ankle',
    29: 'left_heel',
    30: 'right_heel',
    31: 'left_foot_index',
    32: 'right_foot_index',
}

# -----------------------------------------------------------------
# QVector3Dへコンバート
def convert(pose_3d, pose_2d):
    positions = {
        'position': {},
        'extends': {}
    }
    if not pose_3d:
        return positions
    
    # TODO: Multi person support
    poses = pose_3d[0]
    position = {}
    for idx, pose in enumerate(poses):
        position[NAMES[idx]] = QVector3D(pose.x, pose.y*-1, pose.z)

    positions['position'] = position
    positions['extends'][NAMES[23]] = pose_2d[0][23]
    positions['extends'][NAMES[24]] = pose_2d[0][24]

    return positions


# -----------------------------------------------------------------
# refine関連
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
    transformed = scipy.fftpack.fft(signal)
    for i in range(cutoff_idx, len(vec)):
        transformed[i] = 0
    filterd_signal = np.real(scipy.fftpack.ifft(transformed))
    for i in range(0, len(vec)):
        vec[i] = filterd_signal[i]
    
def smooth_position(positions_list):
    minimum_length = 3
    total_length = len(positions_list)
    if total_length < minimum_length:
        return

    joint = []
    for i, _ in enumerate(NAMES):
        joint.append([[], [], []])

    for info in positions_list:
        pos = info['position']
        for i, _ in enumerate(NAMES):
            if len(pos) < i + 1:
                joint[i][0].append(None)
                joint[i][1].append(None)
                joint[i][2].append(None)
            else:
                joint[i][0].append(pos[NAMES[i]].x())
                joint[i][1].append(pos[NAMES[i]].y())
                joint[i][2].append(pos[NAMES[i]].z())

    for i, _ in enumerate(NAMES):
        for j in range(0, 3):
            interpolate(joint[i][j])
            #lowpass_filter(joint[i][j])
                                   
    for i in range(0, total_length):
        for j, _ in enumerate(NAMES):
            p = QVector3D(joint[j][0][i], joint[j][1][i], joint[j][2][i])
            positions_list[i]['position'][NAMES[j]] = p
            
            
def normalize_for_vmd(positions_list):
    spine_len = 0
    ground_y = float('inf')
    count = 0
    for info in positions_list:
        pos = info['position']
        if len(pos) < len(NAMES):
            continue
        if pos['right_ankle'].y() < ground_y: # 右足首
            ground_y = pos['right_ankle'].y()
        if pos['left_ankle'].y() < ground_y: # 左足首
            ground_y = pos['left_ankle'].y()
        
        # 首の座標 右肩と左肩の中間とする
        neck = (pos['right_shoulder'] + pos['left_shoulder']) / 2
        # 腰の座標 右のヒップと左のヒップの中間とする
        waist = (pos['right_hip'] + pos['left_hip']) / 2
        
        spine_len = spine_len + (neck - waist).length()
        count += 1

    if not count:
        return

    spine_len /= count
    scale = 3.2 / spine_len

    for info in positions_list:
        pos = info['position']
        for key in pos:
            pos[key] *= scale

def refine(positions_list):
    smooth_position(positions_list)
    normalize_for_vmd(positions_list)



# -----------------------------------------------------------------
# 位置補正
def center(positions, frames, frame_num):
    # left_hip, right_hip
    p2d = positions['extends']
    x = (p2d['left_hip'].x + p2d['right_hip'].x) / 2
    y = (p2d['left_hip'].y + p2d['right_hip'].y) / 2
    # 0.5, 0.5がセンターとする
    x -= 0.5
    y -= 0.5
    
    bf = VmdBoneFrame()
    bf.name = 'センター'
    bf.frame = frame_num
    bf.position = QVector3D(x*22.5, y*-22.5, 0)
    frames.append(bf)


# -----------------------------------------------------------------
# 解析したポーズのダンプ
def dump(pose_3d, pose_2d):
    for p2d, p3d in zip(pose_2d, pose_3d):
        print('-' * 60)
        print('NAME, 説明, Visibility, X(2D), Y(2D), X(3D), Y(3D), Z(3D)')
        print('-' * 60)
        for i in range(len(p2d)):
            print('%i,%s,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f' % (
                i, NAMES[i], p3d[i].visibility,
                p2d[i].x, p2d[i].y,
                p3d[i].x, p3d[i].y, p3d[i].z,
            ))
