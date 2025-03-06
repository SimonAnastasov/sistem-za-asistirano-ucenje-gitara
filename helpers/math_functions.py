import math


def line_top_point_first(line):
    if line[1] > line[3]:
        return [line[2], line[3], line[0], line[1]]
    else:
        return line


def line_left_point_first(line):
    if line[0] > line[2]:
        return [line[2], line[3], line[0], line[1]]
    else:
        return line


def calculate_distance(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    dist1 = math.sqrt((x1 - x3)**2 + (y1 - y3)**2)
    dist2 = math.sqrt((x1 - x4)**2 + (y1 - y4)**2)
    dist3 = math.sqrt((x2 - x3)**2 + (y2 - y3)**2)
    dist4 = math.sqrt((x2 - x4)**2 + (y2 - y4)**2)

    return min(dist1, dist2, dist3, dist4)


def calculate_angle_deg_vertical_lines(line):
    x1, y1, x2, y2 = line_top_point_first(line)

    delta_x = x2 - x1
    delta_y = y2 - y1
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)

    return angle_deg


def calculate_angle_deg_horizontal_lines(line):
    x1, y1, x2, y2 = line_left_point_first(line)

    delta_x = x2 - x1
    delta_y = y2 - y1
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)

    return angle_deg


def find_intersection_of_two_lines(line1, line2):
    [x1, y1, x2, y2] = line1
    [x3, y3, x4, y4] = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Lines are parallel

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return px, py
