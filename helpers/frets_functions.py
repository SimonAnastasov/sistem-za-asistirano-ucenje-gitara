import cv2
import numpy as np


MIN_DISTANCE_BETWEEN_FRETS = 10
FRET_LENGTH_CONSTANT = 17.817

def detect_frets_on_neck_image(image):
    from .math_functions import calculate_angle_deg_vertical_lines

    # Get Hough Lines for frets
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 31), 0)
    edges = cv2.Canny(blurred, image.shape[0]-10, image.shape[0]//1.5)

    frets = cv2.HoughLinesP(edges, 1, np.pi / 180, image.shape[0]//4, None, 20, 5)

    if frets is None:
        return None

    # Convert frets format to not be double list
    frets = [line[0] for line in frets]

    # Append fret zero (multiple times to make sure it is not deleted by the next steps)
    for i in range(0, 3):
        frets.append([image.shape[1] - 3, 0, image.shape[1] - 3, image.shape[0]])

    # Make sure line angle is between 85 and 95 degrees
    frets = [line for line in frets if calculate_angle_deg_vertical_lines(line) > 85 and calculate_angle_deg_vertical_lines(line) < 95]

    # Make sure line is not too short
    frets = [line for line in frets if abs(line[1]-line[3]) > image.shape[0]//4]

    # Extend frets to be from top to bottom of neck
    frets = [[(line[0]+line[2])//2, 0, (line[0]+line[2])//2, image.shape[0]] for line in frets]

    # Sort frets by x coordinate (leftmost first)
    frets = sorted(frets, key=lambda line: line[0])

    # Group frets that are close to each other and take just one line from a group
    frets_groups = [[frets[0]]]
    frets_groups_index = 0

    for i in range(1, len(frets)):
        if frets[i][0] - frets_groups[frets_groups_index][-1][0] < MIN_DISTANCE_BETWEEN_FRETS:
            frets_groups[frets_groups_index].append(frets[i])
        else:
            frets_groups_index += 1
            frets_groups.append([frets[i]])

    frets = [[sum([line[0] for line in frets_group])//len(frets_group), 0, sum([line[0] for line in frets_group])//len(frets_group), image.shape[0]] if len(frets_group) > 1 else None for frets_group in frets_groups]
    frets = [fret for fret in frets if fret is not None]

    # Add missing frets
    if len(frets) > 2:
        i = 1
        while i < len(frets)-1 and i < 100:
            i += 1

            scale_length = calculate_scale_length_from_frets(frets[i-1][0], frets[i-2][0], image.shape[1])

            if scale_length > image.shape[1] * 2 or scale_length < image.shape[1]:
                continue

            x_position_of_next_fret = calculate_x_position_of_next_fret(frets[i-1][0], frets[i-2][0], image.shape[1])

            if frets[i-1][0] + (frets[i][0]-frets[i-1][0]) > x_position_of_next_fret+10:
                frets.insert(i, [x_position_of_next_fret, 0, x_position_of_next_fret, image.shape[0]])

    # Keep just first 6 frets
    frets = frets[-6:]

    # Return None if an error has been detected in the found frets
    for i in range(0, len(frets)-1):
        scale_length = calculate_scale_length_from_frets(frets[i+1][0], frets[i][0], image.shape[1])

        if scale_length > image.shape[1] * 2 or scale_length < image.shape[1]:
            return None

    # Return None if there are less than 6 found frets
    if len(frets) < 6:
        return None

    return frets


def calculate_scale_length_from_frets(x0, x1, image_width):
    scale_length_to_point = (x0-x1) * FRET_LENGTH_CONSTANT
    scale_length_extra_from_neck = scale_length_to_point - x0
    scale_length = image_width + scale_length_extra_from_neck

    return scale_length


def calculate_x_position_of_next_fret(x0, x1, image_width):
    scale_length_to_point = (x0-x1) * FRET_LENGTH_CONSTANT
    scale_length_extra_from_neck = scale_length_to_point - x0
    scale_length = image_width + scale_length_extra_from_neck

    x_position_of_next_fret = int(x0 + scale_length/FRET_LENGTH_CONSTANT)

    return x_position_of_next_fret
