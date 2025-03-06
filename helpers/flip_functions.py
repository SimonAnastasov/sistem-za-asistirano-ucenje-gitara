import cv2
import numpy as np


def flip_lines_if_needed(image, frets, strings, is_flipped):
    if not is_flipped:
        return frets, strings

    frets = [[image.shape[1]-line[0], line[1], image.shape[1]-line[2], line[3]] for line in frets]
    strings = [[image.shape[1]-line[0], line[1], image.shape[1]-line[2], line[3]] for line in strings]

    return frets, strings


def flip_points_if_needed(image, points, is_flipped):
    if not is_flipped:
        return points

    points = [[image.shape[1]-point[0], point[1]] for point in points]

    return points


def flip_image_and_points_if_neck_position_is_to_the_left(image, neck_points_xyxyxyxy, nut_points_xyxyxyxy):
    from .points_functions import simplify_and_sort_xyxyxyxy_points

    image = image.copy()

    is_flipped = False

    x_distance_leftmost_point_of_nut_with_leftmost_point_of_neck = abs(nut_points_xyxyxyxy[0][0] - neck_points_xyxyxyxy[0][0])
    x_distance_leftmost_point_of_nut_with_rightmost_point_of_neck = abs(nut_points_xyxyxyxy[0][0] - neck_points_xyxyxyxy[1][0])

    if x_distance_leftmost_point_of_nut_with_leftmost_point_of_neck < x_distance_leftmost_point_of_nut_with_rightmost_point_of_neck:
        # Flip the image and points horizontally
        image = cv2.flip(image, 1)

        is_flipped = True

        # Flip the points horizontally
        neck_points_xyxyxyxy = np.array([
            [image.shape[1] - neck_points_xyxyxyxy[1][0], neck_points_xyxyxyxy[1][1]],
            [image.shape[1] - neck_points_xyxyxyxy[0][0], neck_points_xyxyxyxy[0][1]],
            [image.shape[1] - neck_points_xyxyxyxy[3][0], neck_points_xyxyxyxy[3][1]],
            [image.shape[1] - neck_points_xyxyxyxy[2][0], neck_points_xyxyxyxy[2][1]]
        ])

        neck_points_xyxyxyxy = simplify_and_sort_xyxyxyxy_points(neck_points_xyxyxyxy)

        nut_points_xyxyxyxy = np.array([
            [image.shape[1] - nut_points_xyxyxyxy[1][0], nut_points_xyxyxyxy[1][1]],
            [image.shape[1] - nut_points_xyxyxyxy[0][0], nut_points_xyxyxyxy[0][1]],
            [image.shape[1] - nut_points_xyxyxyxy[3][0], nut_points_xyxyxyxy[3][1]],
            [image.shape[1] - nut_points_xyxyxyxy[2][0], nut_points_xyxyxyxy[2][1]]
        ])

        nut_points_xyxyxyxy = simplify_and_sort_xyxyxyxy_points(nut_points_xyxyxyxy)

    return image, neck_points_xyxyxyxy, nut_points_xyxyxyxy, is_flipped
