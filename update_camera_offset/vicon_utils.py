import xml.etree.ElementTree as ET

def get_element(root_element, tag, attribute):

    attribute_values = []
    for element in root_element.iter(tag):
        attribute_values.append(element.get(attribute))

    return attribute_values
	
def is_float(string):
    """
    takes a string input
    returns True if string can be converted to a float
    :param string:
    :return boolean:
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_camera_positions(root_element):
    """
    return a list of camera positions
    each camera position is a list of 3 float elements
    """
    camera_positions = []
    camera_positions_str = get_element(root_element, 'KeyFrame', 'POSITION')
    for position in camera_positions_str:
        camera_position = []
        for val in position.split(' '):
            if is_float(val):
                val = float(val)
            camera_position.append(val)
        camera_positions.append(camera_position)

    return camera_positions


def get_camera_quaternions(root_element):
    """
    return a list of camera quaternions
    each camera quaternion is a list of 4 elements
    """
    camera_quaternions = []
    camera_quaternions_str = get_element(root_element, 'KeyFrame', 'ORIENTATION')
    for quaternion in camera_quaternions_str:
        camera_quaternion = []
        for val in quaternion.split(' '):
            if is_float(val):
                val = float(val)
            camera_quaternion.append(val)
        camera_quaternions.append(camera_quaternion)

    return camera_quaternions


def get_camera_display_types(root_element):
    """
    return a list of camera display types

    """

    camera_display_types = get_element(root_element, 'Camera', 'DISPLAY_TYPE')

    return camera_display_types

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_markers_from_vsk(vsk_file):
    tree = ET.parse(vsk_file)
    root = tree.getroot()

    # get a list of the Parameters' NAME and VALUE
    parameter_names_from_parameters = get_element(root, 'Parameter', 'NAME')
    parameter_values = get_element(root, 'Parameter', 'VALUE')

    # get a list of parameter names and values
    parameters = []
    for i in range(len(parameter_names_from_parameters)):
        parameters.append([parameter_names_from_parameters[i], float(parameter_values[i])])

    # get a list of targets, marker name and position
    markers = get_element(root, 'TargetLocalPointToWorldPoint', 'MARKER')

    if len(markers) == 0:  # no targets, check if v2.5 vsk
        markers = get_element(root, 'Marker', 'NAME')
        positions_from_targets = get_element(root, 'Marker', 'POSITION')

    else:  # v3 vsk
        positions_from_targets = get_element(root, 'TargetLocalPointToWorldPoint', 'POSITION')

    marker_positions = []

    for i in range(len(markers)):

        positions = positions_from_targets[i]
        positions = str(positions).split(' ')

        marker_positions.append([0.0] * 3)

        for j in range(3):
            position = positions[j].strip('\'')

            if is_float(position):
                marker_positions[i][j] = float(position)
            else:
                position.strip('\'')
                index = 0
                for parameter in parameters:
                    if parameter[0] == position:
                        marker_positions[i][j] = parameter[1]
                        parameters.pop(index)
                        break

                index += 1

    return markers, marker_positions


def get_parameter_value(root_element, param_name):
    for parameter in root_element.iter('Parameter'):

        if parameter.get('NAME') == param_name:
            param_value = parameter.get('VALUE')

    return param_value


def set_parameter_value(root_element, param_name, param_value):
    for parameter in root_element.iter('Parameter'):

        if parameter.get('NAME') == param_name:
            parameter.set('VALUE', str(param_value))
            parameter.set('PRIOR', str(param_value))


def remove_parameter(root_element, param_name):
    for parameter_list in root_element.iter('Parameters'):
        for parameter in parameter_list.iter('Parameter'):
            if parameter.get('NAME') == param_name:
                parameter_list.remove(parameter)


def get_parameters_for_marker(root_element, marker_name):
    parameters = []
    for target in root_element.iter('TargetLocalPointToWorldPoint'):
        if target.get('MARKER') == marker_name:
            positions = target.get('POSITION')
            parameters = positions.split(' ')

    index = 0
    for parameter in parameters:
        parameters[index] = parameter[1:-1]
        index += 1

    return parameters


def remove_target(root_element, marker_name):
    for target_list in root_element.iter('Targets'):
        for target in target_list.iter('TargetLocalPointToWorldPoint'):
            if target.get('MARKER') == marker_name:
                target_list.remove(target)


def remove_stick(root_element, marker_name):
    # works but inefficient
    loop = True
    while (loop):
        loop = False
        for stick_list in root_element.iter('Sticks'):
            for stick in stick_list.iter('Stick'):
                if stick.get('MARKER1') == marker_name or stick.get('MARKER2') == marker_name:
                    stick_list.remove(stick)
                    loop = True


def remove_marker(root_element, marker_name):
    for marker_list in root_element.iter('Markers'):
        for marker in marker_list.iter('Marker'):
            if marker.get('NAME') == marker_name:
                marker_list.remove(marker)


def remove_all(root_element, marker_name):
    remove_marker(root_element, marker_name)
    remove_stick(root_element, marker_name)
    parameters = get_parameters_for_marker(root_element, marker_name)
    remove_target(root_element, marker_name)

    for parameter in parameters:
        remove_parameter(root_element, parameter)


def set_marker_positions(root_element, marker_names, marker_positions):
    i = 0
    for marker in marker_names:
        params = get_parameters_for_marker(root_element, marker)
        j = 0
        for param in params:
            set_parameter_value(root_element, param, marker_positions[i][j])
            j += 1
        i += 1

def globalise_rigid_using_rotation_matrix(local_points, world_pose_rotation_matrix, world_pose_translation):
    # given a world pose, globalise the rigid points
    # world_pose_rotation_matrix - World rotation matrix
    # world_pose_translation - World translation in mm (3 elements)

    global_points = []

    for local in local_points:

        globalised_point = [0] * 3
        for i in range(3):
            for j in range(3):
                globalised_point[i] = globalised_point[i] + (world_pose_rotation_matrix[i][j] * local[j])
        for i in range(3):
            globalised_point[i] = globalised_point[i] + world_pose_translation[i]

        global_points.append(globalised_point)

    return global_points


def localise_rigid_using_rotation_matrix(global_points, world_pose_rotation_matrix, world_pose_translation):

    # negate matrix
    neg_rotmat = [[0] * 3 for x in range(3)]
    for i in range(3):
        for j in range(3):
            neg_rotmat[i][j] = world_pose_rotation_matrix[i][j] * -1

    new_translation = [0] * 3
    for i in range(3):
        for j in range(3):
            new_translation[i] = new_translation[i] + (neg_rotmat[j][i] * world_pose_translation[j])

    local_points = []

    for global_point in global_points:

        # localise the point
        localised_point = [0] * 3
        for i in range(3):
            for j in range(3):
                localised_point[i] = localised_point[i] + (world_pose_rotation_matrix[j][i] * global_point[j])
        for i in range(3):
            localised_point[i] = localised_point[i] + new_translation[i]

        local_points.append(localised_point)

    return local_points


def rotation_matrix_from_quaternion(quaternion):
    # Extract the values from Quaternion
    # Vicon quaternions have real part in 4th element
    # this function expects q = q0 + q1i + q2j + q3k

    q0 = quaternion[3]
    q1 = quaternion[0]
    q2 = quaternion[1]
    q3 = quaternion[2]

    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    rotation_matrix = [[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]]

    return rotation_matrix
	
def transpose_matrix3(matrix):

    transposed = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(matrix[j][i])
        transposed.append(row)

    return transposed
