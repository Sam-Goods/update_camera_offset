import sys

from vicon_dssdk.ViconDataStream import DataStreamException

try:
    from vicon_dssdk import ViconDataStream
except ImportError:
    print("vicon_dssdk not found. Please ensure the Vicon Datastream SDK package is installed")


# connect to the DSSDK
def dssdk_connect(host_name):
    try:
        client = ViconDataStream.Client()
        client.Connect(host_name)

        if client.IsConnected:
            print("Connected to DSSDK client using:", host_name)
        else:
            print("Client failed to connect")

        client.SetBufferSize(1)

        client.EnableSegmentData()
        #print("Segments enabled:", client.IsSegmentDataEnabled())

        client.SetStreamMode(ViconDataStream.Client.StreamMode.EServerPush)

        return client
    except ViconDataStream.DataStreamException as e:
        print('Handled data stream error', e)


def dssdk_get_frame(client):
    # grabbing a few frames to ensure that the buffer is updated to the latest subject name
    Frames = 0
    while Frames < 15:
        try:
            client.GetFrame()
            Frames += 1
        except ViconDataStream.DataStreamException as e:
            print("Cannot get frame from the datastream. Please ensure data is streaming and try running the script again")
            sys.exit()
    try:
        print("Frame number:", client.GetFrameNumber())
    except DataStreamException:
        print("Unable to get frame from DSSDK - please check data is streaming and try running the script again")
        sys.exit()


def dssdk_check_occluded(subject, segment_name, client):
    result = client.GetSegmentGlobalTranslation(subject, segment_name)

    if result[1]:
        return True
    else:
        return False


# get pose infomation for a subject from the DSSDK
def dssdk_get_pose(host_name, subject):
    client = dssdk_connect(host_name)

    occluded = True
    timer = 0
    while occluded:
        dssdk_get_frame(client)

        try:
            segment_name = client.GetSubjectRootSegmentName(subject)

            occluded = dssdk_check_occluded(subject, segment_name, client)
            timer += 1
            print("Attempting to get", subject, "transform")
            if timer == 10:
                print("Exiting program.", subject, "has been occluded for 10 attempts. Please ensure", subject,
                    "is tracking before executing this script")
                sys.exit()
        except DataStreamException:
            print("Unable to find subject name in Datastream, please ensure the correct subject name is input and try running the script again")
            sys.exit()

        

    # get required transforms
    segment_name = client.GetSubjectRootSegmentName(subject)
    subject_global_trans = client.GetSegmentGlobalTranslation(subject, segment_name)
    subject_global_rot_matrix = client.GetSegmentGlobalRotationMatrix(subject, segment_name)

    # get first tuple element and convert the contents to a list for bob's magic
    global_translation_list = list(subject_global_trans[0])
    print(subject, segment_name, "global_translation:", global_translation_list)
    global_rotm_list = [list(subject_global_rot_matrix[0][0]), list(subject_global_rot_matrix[0][1]), list(subject_global_rot_matrix[0][2])]
    print(subject, segment_name, 'global rotation(Matrix):', global_rotm_list)

    # house keeping
    if client.IsConnected:
        client.Disconnect()

    return (global_translation_list, global_rotm_list)
