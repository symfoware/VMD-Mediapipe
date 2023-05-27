#!/usr/bin/env python3
#
# dump_positions.py - dump 2D & 3D joint positions estimated by Lifting from the Deep

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

def dump_positions(pose_2d, pose_3d):
    print("ID, 説明, Visibility, X(2D), Y(2D), X(3D), Y(3D), Z(3D)")
    for p2d, p3d in zip(pose_2d, pose_3d):
        for i in range(len(joint)):
            idx_2d = joint[i][1]
            desc = joint[i][2]
            if idx_2d is None:
                v = ""
                x2d = ""
                y2d = ""
            else:
                x2d = str(p2d[idx_2d, 1])
                y2d = str(p2d[idx_2d, 0])
            x3d = str(p3d[0, i])
            y3d = str(p3d[2, i])
            z3d = str(p3d[1, i])
            print(",".join([str(i), desc, v, x2d, y2d, x3d, y3d, z3d]))
