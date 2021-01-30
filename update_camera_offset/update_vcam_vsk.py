#from vicon_xcp import get_camera_positions, get_camera_quaternions, get_camera_display_types
#from vicon_vsk import get_markers_from_vsk, set_marker_positions
#from vicon_angle import globalise_rigid_using_rotation_matrix, localise_rigid_using_rotation_matrix, rotation_matrix_from_quaternion

from update_camera_offset.vicon_utils import *

import os
import sys
import xml.etree.ElementTree as ET


def update_vcam(object_t, object_r_matrix, subject_path, calibration_path, subject_name):
    
    object_translation = object_t

    object_pose_rot_mat = object_r_matrix

    path = subject_path

    vsk = subject_name + ".vsk"

    xcp_file = calibration_path #os.path.join(path, xcp)
    xcp_xml_tree = ET.parse(xcp_file)

    cams = get_camera_display_types(xcp_xml_tree)

    cam_found = False
    index = 0
    for cam in cams:
        if cam == "DeckLink":
            cam_found = True
            break
        index += 1

    if not cam_found:
        print("SDI camera not found in calibration. Please ensure SDI camera is calibrated and present in the XCP")
        sys.exit()
		

    camera_quaternion = get_camera_quaternions(xcp_xml_tree)[index]
    camera_position = get_camera_positions(xcp_xml_tree)[index]
    print("Decklink global translation:", camera_position)
    print("Decklink global rotation(Quaternion):", camera_quaternion)

    vsk_file = os.path.join(path, vsk)

    marker_names, local_marker_positions = get_markers_from_vsk(vsk_file)

    global_marker_positions = globalise_rigid_using_rotation_matrix(local_marker_positions, object_pose_rot_mat, object_translation)

    camera_rot_mat = rotation_matrix_from_quaternion(camera_quaternion)
	
	# transpose the camera pose rot mat, not sure why
    camera_rot_mat_transposed = transpose_matrix3(camera_rot_mat)

    camera_local_marker_positions = localise_rigid_using_rotation_matrix(global_marker_positions, camera_rot_mat_transposed, camera_position)

    # current vicon rotation is (X up, y backwards)

    # rot1 for UE (X forwards, Z up) is -90 in Y
    rot_mat = [[0, 0, -1], [0, 1, 0], [1, 0, 0]]
    camera_local_marker_positions = localise_rigid_using_rotation_matrix(camera_local_marker_positions, rot_mat, [0, 0, 0])

    # rot2 for UE (X forwards, Z up) is +90 in X
    rot_mat = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
    camera_local_marker_positions = localise_rigid_using_rotation_matrix(camera_local_marker_positions, rot_mat, [0, 0, 0])
    print("Set axis to match UE4 CineCam")


    vsk_xml_tree = ET.parse(vsk_file)
    vsk_xml_tree_root = vsk_xml_tree.getroot()

    set_marker_positions(vsk_xml_tree_root, marker_names, camera_local_marker_positions)
    print("Aligned object pose with camera pose")

    vsk_file_rename = path + "\\" + subject_name + "_old.vsk"

    os.replace(vsk_file, vsk_file_rename)
    print("Renamed old VSK to:", subject_name, "_old")
    new_vsk_file = vsk_file

    vsk_xml_tree.write(new_vsk_file)
    print("New updated VSK written to:", new_vsk_file)
	
	

