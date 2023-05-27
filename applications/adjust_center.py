# adjust_center.py - adjust center position

import numpy as np
import cv2
from PyQt6.QtGui import QVector3D

center_idx = 7
idx_2d = [0, 1, 2, 3, 4, 5, 6, 7]
idx_3d = [10, 8, 14, 15, 16, 11, 12, 13]
camera_position = QVector3D(0, 0, -3600)

def adjust_center(positions_2d, positions_3d, image):
    # print(positions_2d)
    p2dlist = []
    # TODO: Multi person support
    p = positions_2d[0]
    for k in idx_2d:
        p2dlist.append((p[k, 1], p[k, 0]))

    p2d = np.array(p2dlist, dtype="double")
    print("p2d: ", p2d)
    
    p3dlist = []
    for k in idx_3d:
        p = QVector3D(positions_3d[k])
        p -= positions_3d[center_idx] # 胴体の中心を原点(0, 0, 0)とする
        p3dlist.append((p.x(), -p.y(), p.z()))

    p3d = np.array(p3dlist, dtype="double")
    print("p3d: ", p3d)
    
    focal_length = max([image.shape[0], image.shape[1]])
    camera = np.array([[focal_length, 0, image.shape[1] / 2],
                       [0, focal_length, image.shape[0] / 2],
                       [0, 0, 1]], dtype = "double")
    distortion = np.zeros((4, 1))
    #retval, rot_vec, trans_vec = cv2.solvePnP(p3d, p2d, camera, distortion,
    #                                              flags = cv2.SOLVEPNP_ITERATIVE)
    retval, rot_vec, trans_vec, inliers = cv2.solvePnPRansac(p3d, p2d, camera, distortion)
    
    center = QVector3D(trans_vec[0], trans_vec[1], trans_vec[2])
    if trans_vec[2] < 0:
        center = -center

    rot_mat = cv2.Rodrigues(rot_vec)[0]
    proj_mat = np.array([[rot_mat[0][0], rot_mat[0][1], rot_mat[0][2], 0],
                         [rot_mat[1][0], rot_mat[1][1], rot_mat[1][2], 0],
                         [rot_mat[2][0], rot_mat[2][1], rot_mat[2][2], 0]], dtype="double")
    eulerAngles = cv2.decomposeProjectionMatrix(proj_mat)[6]
    print("eulerAngles: \n", eulerAngles)
    print("trans_vec: ", trans_vec)
    print("center: ", center)
    offset = center - positions_3d[center_idx] + camera_position
    for i in range(len(positions_3d)):
        positions_3d[i] += offset

