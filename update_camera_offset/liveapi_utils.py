import time
import sys

import vicon_core_api
from vicon_core_api.client import RPCError

try:
    from vicon_core_api import Client
except ImportError:
    print("vicon_core_api not found. Please ensure this package is installed. It can be found in the Shogun install directory")

try:
    from shogun_live_api import CameraCalibrationServices
    from shogun_live_api.interfaces import SubjectServices, CaptureServices
except ImportError:
     print("shogun_live_api not found. Please ensure this package is installed. It can be found in the Shogun install directory")

# connect to Shogun Live API
def shogun_connect(host_name):
    try:
        client = Client(host_name)
        time.sleep(1)

        return client
    except RPCError:
        print("Cannot connect to Shogun Live, please ensure Shogun Live is running and run the script again")
        sys.exit()

#export XCP from Shogun Live
def export_xcp(client, export_path):
    calibration_services = CameraCalibrationServices(client)

    result = calibration_services.export_camera_calibration(export_path)

    if result:
        print('Succesfully exported camera calibration to: ' + export_path)

#export VSK from Shogun Live
def export_vsk(client, subject_name, subject_path):
    subject_services = SubjectServices(client)

    result = subject_services.export_subject(subject_name, subject_path, True)

    if result:
        print("Successfully exported prop " + subject_name + " to: " + subject_path)

#import VSK into Shogun Live
def import_vsk(client, subject_name, subject_path):
    subject_services = SubjectServices(client)
    rigid_object_type = SubjectServices.ESubjectType.ERigidObject

    result = subject_services.import_subject(subject_path, subject_name, rigid_object_type)

    if result:
        print("Successfully imported", subject_name, "from:", subject_path)

#get capture folder path from Shogun Live
def get_capture_folder(client):
    try:
        capture_services = CaptureServices(client)

        cap_folder = capture_services.capture_folder()[1]

        return(cap_folder)
    except RPCError:
        print("Cannot connect to Shogun Live, please ensure Shogun Live is running and run the script again")
        sys.exit()
