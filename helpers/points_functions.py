import numpy as np

def simplify_and_sort_xyxyxyxy_points(points):
    # Simplify xyxyxyxy points with mins and maxs
    # Sort the points in the following order: top-left, top-right, bottom-left, bottom-right

    new_points = [
        [np.min(points[:, 0]), np.min(points[:, 1])],
        [np.max(points[:, 0]), np.min(points[:, 1])],
        [np.min(points[:, 0]), np.max(points[:, 1])],
        [np.max(points[:, 0]), np.max(points[:, 1])]
    ]

    return new_points


def move_lines_coordinates_by_x_and_y_values(lines, x, y):
    new_lines = []

    for line in lines:
        x1, y1, x2, y2 = line
        new_lines.append([x1 + x, y1 + y, x2 + x, y2 + y])

    return new_lines
