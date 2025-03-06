import cv2
import numpy as np


IMAGE_DIVIDER_CONSTANT = 8
STRINGS_TAKE_SECOND_PART_FROM_BRACKET = 1

def detect_strings_on_neck_image(image, nut_line):
    return artificially_create_strings(image, nut_line)

    image_left = image.copy()[0:image.shape[0], 0:image.shape[1]//IMAGE_DIVIDER_CONSTANT]
    image_right = image.copy()[0:image.shape[0], image.shape[1]//IMAGE_DIVIDER_CONSTANT*STRINGS_TAKE_SECOND_PART_FROM_BRACKET:image.shape[1]//IMAGE_DIVIDER_CONSTANT*(STRINGS_TAKE_SECOND_PART_FROM_BRACKET+1)]

    strings_left = detect_strings_on_part_of_neck_image(image_left)
    strings_right = detect_strings_on_part_of_neck_image(image_right)

    if strings_left is None or strings_right is None:
        return None

    if len(strings_left) != 6 or len(strings_right) != 6:
        return None

    strings_right = [[string[0] + image.shape[1]//IMAGE_DIVIDER_CONSTANT*STRINGS_TAKE_SECOND_PART_FROM_BRACKET, string[1], string[2] + image.shape[1]//IMAGE_DIVIDER_CONSTANT*STRINGS_TAKE_SECOND_PART_FROM_BRACKET, string[3]] for string in strings_right]

    strings = []

    for i in range(0, len(strings_left)):
        slope = (strings_right[i][1] - strings_left[i][1]) / (strings_right[i][0] - strings_left[i][0])
        strings.append([0, strings_left[i][1], image.shape[1], int(strings_left[i][1] + slope * image.shape[1])])

    strings = strings_left + strings_right

    # Extend strings to be from left to right of neck
    # strings = [[0, (line[1] + line[3]) // 2, image.shape[1], (line[1] + line[3]) // 2] for line in strings]

    return strings


def detect_strings_on_part_of_neck_image(image):
    from .math_functions import calculate_angle_deg_horizontal_lines, line_left_point_first

    # Get Hough Lines for strings
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (31, 5), 0)
    edges = cv2.Canny(blurred, 0, 0)

    strings = cv2.HoughLinesP(edges, 1, np.pi / 180, 5, None, 5, 5)

    if strings is None:
        return None

    # Convert strings format to not be double list
    strings = [line[0] for line in strings]

    # Make sure line angle is between -5 and 5 degrees
    strings = [line for line in strings if calculate_angle_deg_horizontal_lines(line) > -5 and calculate_angle_deg_horizontal_lines(line) < 5]

    # Make left point of line be first
    strings = [line_left_point_first(line) for line in strings]

    # Sort strings by y coordinate (topmost first)
    strings = sorted(strings, key=lambda line: line[1])

    # Group strings in N brackets
    N = 6
    strings_groups = [[] for i in range(0, N)]

    for i in range(1, len(strings)):
        string_y = (strings[i][1] + strings[i][3]) // 2
        string_y = strings[i][1]

        for j in range(0, N):
            if string_y < image.shape[0] // N * (j + 1):
                strings_groups[j].append(string_y)
                break

    # Remove the groups that have the lowest number of strings
    # strings_groups = sorted(strings_groups, key=lambda strings_group: len(strings_group), reverse=True)
    # strings_groups = strings_groups[1:]

    strings = [[0, sum(strings_group) // len(strings_group), image.shape[1], sum(strings_group) // len(strings_group)] if len(strings_group) > 0 else None for strings_group in strings_groups]
    strings = [string for string in strings if string is not None]

    return strings


def artificially_create_strings(image, nut_line):
    from .math_functions import line_top_point_first

    N = 6

    height_padding_left = image.shape[0] // 10

    nut_line = line_top_point_first(nut_line)
    base_height_padding_right = nut_line[1]
    height_padding_right = (nut_line[3]-nut_line[1]) // 10
    height_right = (nut_line[3]-nut_line[1]) - height_padding_right

    step_size_left = (image.shape[0]-height_padding_left*2) / (N-1)
    y_values_left = [height_padding_left]
    for i in range(1, 5):
        y_values_left.append(height_padding_left + step_size_left*i)
    y_values_left.append(image.shape[0]-height_padding_left)

    step_size_right = ((nut_line[3]-nut_line[1]) - height_padding_right * 2) / (N - 1)
    y_values_right = [base_height_padding_right + height_padding_right]
    for i in range(1, 5):
        y_values_right.append(base_height_padding_right + height_padding_right + step_size_right * i)
    y_values_right.append(base_height_padding_right + (nut_line[3]-nut_line[1]) - height_padding_right)

    y_values_left = [int(y) for y in y_values_left]
    y_values_right = [int(y) for y in y_values_right]

    strings = [[0, y_values_left[i], image.shape[1], y_values_right[i]] for i in range(0, N)]

    return strings
