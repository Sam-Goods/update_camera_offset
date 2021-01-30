import sys
import argparse
from pathlib import Path

from update_camera_offset.update_vcam_vsk import update_vcam
from update_camera_offset.liveapi_utils import shogun_connect, export_xcp, export_vsk, import_vsk, get_capture_folder
from update_camera_offset.dssdk_utils import dssdk_connect, dssdk_get_pose
        
def main():

    #set up parser arguments for user input
    parser = argparse.ArgumentParser()
    #parser.add_argument('--cal_path', help="Calibration file path, if not defined will use local folder", default=Path(__file__).parent.absolute())
    parser.add_argument('--propname', help="Name of the prop to update", required=True, type=str)
    parser.add_argument('--proppath', help="Prop file path, if not defined will use PublicDocuments\\Props", default="C:\\Users\\Public\\Documents\\Vicon\\Props")
    parser.add_argument('--host', help="Terminal server host IP address", default="localhost", type=str)
    parser.add_argument('--port', help="Terminal server port", default=52800, type=int)
    args = parser.parse_args(sys.argv[1:])

    #define some variables
    subject_name = args.propname
    #cal_arg = args.cal_path
    sub_arg = args.proppath
    sub_path = str(sub_arg)
    host_name = args.host
    
    #connect to Shogun
    api_client = shogun_connect(host_name)
    #dssdk_client = dssdk_connect(host_name)

    #set up path for xcp
    cal_path = get_capture_folder(api_client) + "\\" + subject_name + "_CameraCalibration.xcp"
    
    #export the xcp to capture directory
    export_xcp(api_client, cal_path)


    #export vsk to props directory
    export_vsk(api_client, subject_name, sub_path)
    
    #get required pose transforms from dssdk
    object_translation, object_pose_rot_mat = dssdk_get_pose(host_name, subject_name)

    #do bobs magic here
    update_vcam(object_translation, object_pose_rot_mat, sub_path, cal_path, subject_name)

    #reimport the tweaked vsk back to shogun live
    import_vsk(api_client, subject_name, sub_path)

    #profit 

if __name__ == "__main__":
    main()
