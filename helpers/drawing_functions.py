import cv2
import math

# Function:
# Draws an X on the given image
def draw_an_x(image, center, color, size, thickness):
    angle_radians = math.radians(45)
    half_size = size // 2
    x, y = center

    # Calculate the points for the first rotated line
    dx = half_size * math.cos(angle_radians)
    dy = half_size * math.sin(angle_radians)

    line1_start = (int(x - dx), int(y - dy))
    line1_end = (int(x + dx), int(y + dy))

    # Calculate the points for the perpendicular line
    angle_perpendicular = angle_radians + math.pi / 2
    dx_perp = half_size * math.cos(angle_perpendicular)
    dy_perp = half_size * math.sin(angle_perpendicular)

    line2_start = (int(x - dx_perp), int(y - dy_perp))
    line2_end = (int(x + dx_perp), int(y + dy_perp))

    # Draw the two rotated lines
    cv2.line(image, line1_start, line1_end, color, thickness, cv2.LINE_AA)
    cv2.line(image, line2_start, line2_end, color, thickness, cv2.LINE_AA)


# Function:
# Draws lines on an image
def draw_lines_on_image(image, lines, color):
    if image is None or lines is None:
        return

    for i in range(0, len(lines)):
        l = lines[i]

        cv2.line(image, (l[0], l[1]), (l[2], l[3]), color, 3, cv2.LINE_AA)

    return image


def draw_xyxyxyxy_points_on_image(image, points, color):
    if image is None or points is None:
        return

    cv2.rectangle(image, (points[0][0], points[0][1]), (points[-1][0], points[-1][1]), color, 3, cv2.LINE_AA)

    return image
