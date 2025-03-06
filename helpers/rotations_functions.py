import cv2
import numpy as np


def rotate_lines(frets, strings, rotation_matrix, invert_rotation_matrix_flag=False):
    if invert_rotation_matrix_flag:
        rotation_matrix = invert_rotation_matrix(rotation_matrix)

    # Rotate all frets
    rotated_frets = []
    for x1, y1, x2, y2 in frets:
        p1_rotated = rotate_point((x1, y1), rotation_matrix)
        p2_rotated = rotate_point((x2, y2), rotation_matrix)
        rotated_frets.append([p1_rotated[0], p1_rotated[1], p2_rotated[0], p2_rotated[1]])

    # Rotate all strings
    rotated_strings = []
    for x1, y1, x2, y2 in strings:
        p1_rotated = rotate_point((x1, y1), rotation_matrix)
        p2_rotated = rotate_point((x2, y2), rotation_matrix)
        rotated_strings.append([p1_rotated[0], p1_rotated[1], p2_rotated[0], p2_rotated[1]])

    rotated_frets = [[int(point) for point in line] for line in rotated_frets]
    rotated_strings = [[int(point) for point in line] for line in rotated_strings]

    return rotated_frets, rotated_strings


def rotate_points(points, rotation_matrix, invert_rotation_matrix_flag=False):
    if invert_rotation_matrix_flag:
        rotation_matrix = invert_rotation_matrix(rotation_matrix)

    rotated_points = []
    for x1, y1 in points:
        rotated_point = rotate_point((x1, y1), rotation_matrix)
        rotated_points.append([rotated_point[0], rotated_point[1]])

    rotated_points = [[int(point) for point in line] for line in rotated_points]

    return rotated_points


def rotate_image_and_points_based_on_neck_rotation(image, best_neck, best_nut, classes):
    from .points_functions import simplify_and_sort_xyxyxyxy_points

    # Get the image dimensions and find the rotation matrix
    h, w = image.shape[:2]

    rotation_angle = 0

    # Process the best neck object for rotation if it exists
    if best_neck:
        xywhr = best_neck.xywhr[0]
        rotation_angle = np.degrees(xywhr[4].numpy())
        if rotation_angle > 90:
            rotation_angle = rotation_angle - 180

    # Get the image center and calculate the rotation matrix
    x_center = w // 2
    y_center = h // 2
    rotation_matrix = cv2.getRotationMatrix2D((x_center, y_center), rotation_angle, 1.0)

    # Apply the rotation to the image
    rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))
    neck_points_xyxyxyxy, nut_points_xyxyxyxy = None, None

    for result in [best_neck, best_nut]:
        # Extract the normalized bounding box points
        xyxyxyxyn = result.xyxyxyxyn[0]  # Normalized coordinates (4 points)
        cls = int(result.cls)  # Class ID
        class_name = classes[cls]  # Class name

        # Denormalize the bounding box coordinates
        points = np.array([
            [xyxyxyxyn[0][0] * w, xyxyxyxyn[0][1] * h],
            [xyxyxyxyn[1][0] * w, xyxyxyxyn[1][1] * h],
            [xyxyxyxyn[2][0] * w, xyxyxyxyn[2][1] * h],
            [xyxyxyxyn[3][0] * w, xyxyxyxyn[3][1] * h],
        ], dtype=np.int32)

        # Apply the rotation transformation to the bounding box points
        rotated_points = cv2.transform(np.array([points]), rotation_matrix)[0]

        rotated_points = simplify_and_sort_xyxyxyxy_points(rotated_points)

        if class_name == "neck":
            neck_points_xyxyxyxy = rotated_points
        elif class_name == "nut":
            nut_points_xyxyxyxy = rotated_points

    return rotated_image, neck_points_xyxyxyxy, nut_points_xyxyxyxy, rotation_matrix


def invert_rotation_matrix(rotation_matrix):
    # Extract components from rotation matrix
    r11, r12, tx = rotation_matrix[0]
    r21, r22, ty = rotation_matrix[1]

    # Invert the rotation part (transpose the upper 2x2)
    inverse_rotation = np.array([[r11, r21],
                                 [r12, r22]])

    # Invert the translation
    inverse_translation = -np.dot(inverse_rotation, np.array([tx, ty]))

    # Construct the inverse matrix
    inverted_matrix = np.hstack((inverse_rotation, inverse_translation.reshape(2, 1)))
    return inverted_matrix


def rotate_point(point, matrix):
    # Convert point to homogeneous coordinates: (x, y) -> [x, y, 1]
    x, y = point
    transformed_point = np.dot(matrix, [x, y, 1])
    return transformed_point[:2]
