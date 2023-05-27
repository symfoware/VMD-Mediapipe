# pos2vmd.py - convert joint position data to VMD

from PyQt6.QtGui import QQuaternion, QVector3D
from VmdWriter import VmdBoneFrame, VmdInfoIk, VmdShowIkFrame

def positions_to_frames(pos, frame_num=0):
    """convert positions to bone frames"""
    frames = []

    # 解析結果から直接得られない座標の推定
    # 首の座標 右肩と左肩の中間とする
    neck = (pos['right_shoulder'] + pos['left_shoulder']) / 2
    # 腰の座標 右のヒップと左のヒップの中間とする
    waist = (pos['right_hip'] + pos['left_hip']) / 2
    # 頭の中心座標
    head_center = (pos['right_ear'] + pos['left_ear']) / 2

    # 上半身
    bf = VmdBoneFrame()
    bf.name = '上半身'
    bf.frame = frame_num
    
    direction = neck - waist # 首の付け根 - 腰
    up = QVector3D.crossProduct(direction, (pos['right_shoulder'] - pos['left_shoulder'])).normalized() # 右肩 左肩
    upper_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(0, 0, 1))
    bf.rotation = upper_body_orientation * initial.inverted()
    frames.append(bf)
    upper_body_rotation = bf.rotation

    # 下半身
    bf = VmdBoneFrame()
    bf.name = '下半身'
    bf.frame = frame_num
    direction = waist - neck # 腰 - 首の付け根
    up = QVector3D.crossProduct(direction, (pos['left_hip'] - pos['right_hip']))
    lower_body_orientation = QQuaternion.fromDirection(direction, up)
    initial = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(0, 0, 1))
    bf.rotation = lower_body_orientation * initial.inverted()
    lower_body_rotation = bf.rotation
    frames.append(bf)


    # 首は回転させず、頭のみ回転させる
    # 頭
    bf = VmdBoneFrame()
    bf.name = '頭'
    bf.frame = frame_num
    # 頭頂は右耳、左耳の中間座標で代価
    # あごは回転角が知りたいだけなので、鼻で判定
    direction = head_center - neck
    up = QVector3D.crossProduct((pos['nose'] - neck), (head_center - pos['nose']))
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, 1, 0), QVector3D(1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = upper_body_rotation.inverted() * rotation
    frames.append(bf)


    # -------------------------------------------------------------------------------------------------
    # 上半身左
    # -------------------------------------------------------------------------------------------------
    # 左腕
    bf = VmdBoneFrame()
    bf.name = '左腕'
    bf.frame = frame_num
    direction = pos['left_elbow'] - pos['left_shoulder'] # 左ひじ - 左肩
    up = QVector3D.crossProduct((pos['left_elbow'] - pos['left_shoulder']), (pos['left_wrist'] - pos['left_elbow'])) # 左ひじ - 左肩, 左手首 - 左ひじ
    orientation = QQuaternion.fromDirection(direction, up)
    # ボーンの初期状態による　手を45度下向きにしている場合はx:1を指定
    #initial_orientation = QQuaternion.fromDirection(QVector3D(1.73, -1, 0), QVector3D(1, 1.73, 0))
    initial_orientation = QQuaternion.fromDirection(QVector3D(1, -1, 0), QVector3D(1, 1, 0))
    rotation = orientation * initial_orientation.inverted()
    # 左腕ポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * bf.rotation = rotation なので、
    bf.rotation = upper_body_rotation.inverted() * rotation
    left_arm_rotation = bf.rotation # 後で使うので保存しておく
    frames.append(bf)
    
    # 左ひじ
    bf = VmdBoneFrame()
    bf.name = '左ひじ'
    bf.frame = frame_num
    direction = pos['left_wrist'] - pos['left_elbow'] #左手首 - 左ひじ
    up = QVector3D.crossProduct((pos['left_elbow'] - pos['left_shoulder']), (pos['left_wrist'] - pos['left_elbow'])) # 左ひじ - 左肩, 左手首 - 左ひじ

    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(1, -1, 0), QVector3D(1, 1, 0))
    rotation = orientation * initial_orientation.inverted()
    # 左ひじポーンの回転から親ボーンの回転を差し引いてbf.rotationに格納する。
    # upper_body_rotation * left_arm_rotation * bf.rotation = rotation なので、
    bf.rotation = left_arm_rotation.inverted() * upper_body_rotation.inverted() * rotation
    # bf.rotation = (upper_body_rotation * left_arm_rotation).inverted() * rotation # 別の表現
    frames.append(bf)


    # -------------------------------------------------------------------------------------------------
    # 上半身右
    # -------------------------------------------------------------------------------------------------
    # 右腕
    bf = VmdBoneFrame()
    bf.name = '右腕'
    bf.frame = frame_num
    direction = pos['right_elbow'] - pos['right_shoulder'] # 右ひじ - 右肩
    up = QVector3D.crossProduct((pos['right_elbow'] - pos['right_shoulder']), (pos['right_wrist'] - pos['right_elbow'])) # 右ひじ - 右肩, 右手首 - 右ひじ
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1, -1, 0), QVector3D(1, -1, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = upper_body_rotation.inverted() * rotation
    right_arm_rotation = bf.rotation
    frames.append(bf)
    
    # 右ひじ
    bf = VmdBoneFrame()
    bf.name = '右ひじ'
    bf.frame = frame_num
    direction = pos['right_wrist'] - pos['right_elbow'] # 右手首 - 右ひじ
    up = QVector3D.crossProduct((pos['right_elbow'] - pos['right_shoulder']), (pos['right_wrist'] - pos['right_elbow'])) # 右ひじ - 右肩, 右手首 - 右ひじ
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(-1, -1, 0), QVector3D(1, -1, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = right_arm_rotation.inverted() * upper_body_rotation.inverted() * rotation
    frames.append(bf)


    # -------------------------------------------------------------------------------------------------
    # 下半身左
    # -------------------------------------------------------------------------------------------------
    # 左足
    bf = VmdBoneFrame()
    bf.name = '左足'
    bf.frame = frame_num
    direction = pos['left_knee'] - pos['left_hip'] # 左ひざ - 左脚付け根
    up = QVector3D.crossProduct((pos['left_knee'] - pos['left_hip']), (pos['left_ankle'] - pos['left_knee'])) # 左ひざ - 左脚付け根, 左足首 - 左ひざ

    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = lower_body_rotation.inverted() * rotation
    left_leg_rotation = bf.rotation
    frames.append(bf)
    
    # 左ひざ
    bf = VmdBoneFrame()
    bf.name = '左ひざ'
    bf.frame = frame_num
    direction = pos['left_ankle'] - pos['left_knee'] # 左足首 - 左ひざ
    up = QVector3D.crossProduct((pos['left_knee'] - pos['left_hip']), (pos['left_ankle'] - pos['left_knee'])) # 左ひざ - 左脚付け根, 左足首 - 左ひざ
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = left_leg_rotation.inverted() * lower_body_rotation.inverted() * rotation
    frames.append(bf)
    

    # -------------------------------------------------------------------------------------------------
    # 下半身右
    # -------------------------------------------------------------------------------------------------
    # 右足
    bf = VmdBoneFrame()
    bf.name = '右足'
    bf.frame = frame_num
    direction = pos['right_knee'] - pos['right_hip'] # 右ひざ - 右脚付け根
    up = QVector3D.crossProduct((pos['right_knee'] - pos['right_hip']), (pos['right_ankle'] - pos['right_knee'])) # 右ひざ - 右脚付け根, 右足首 - 右ひざ
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = lower_body_rotation.inverted() * rotation
    right_leg_rotation = bf.rotation
    frames.append(bf)
    
    # 右ひざ
    bf = VmdBoneFrame()
    bf.name = '右ひざ'
    bf.frame = frame_num
    direction = pos['right_ankle'] - pos['right_knee'] # 右足首 - 右ひざ
    up = QVector3D.crossProduct((pos['right_knee'] - pos['right_hip']), (pos['right_ankle'] - pos['right_knee'])) # 右ひざ - 右脚付け根, 右足首 - 右ひざ
    orientation = QQuaternion.fromDirection(direction, up)
    initial_orientation = QQuaternion.fromDirection(QVector3D(0, -1, 0), QVector3D(-1, 0, 0))
    rotation = orientation * initial_orientation.inverted()
    bf.rotation = right_leg_rotation.inverted() * lower_body_rotation.inverted() * rotation
    frames.append(bf)
    

    return frames

def make_showik_frames():
    frames = []
    sf = VmdShowIkFrame()
    sf.show = 1
    sf.ik.append(VmdInfoIk('左足ＩＫ', 0))
    sf.ik.append(VmdInfoIk('右足ＩＫ', 0))
    sf.ik.append(VmdInfoIk('左つま先ＩＫ', 0))
    sf.ik.append(VmdInfoIk('右つま先ＩＫ', 0))
    frames.append(sf)
    return frames


