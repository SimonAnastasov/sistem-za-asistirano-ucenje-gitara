import cv2
import math

def get_chord_circles(frets, strings, chord_name, chord_type, circle_radius):
    if chord_type == "Major":
        if chord_name == "C":
            return get_chord_circles_coordinates(["X", 3, 2, 0, 1, 0], frets, strings, circle_radius)
        if chord_name == "D":
            return get_chord_circles_coordinates(["X", "X", 0, 2, 3, 2], frets, strings, circle_radius)
        elif chord_name == "F":
            return get_chord_circles_coordinates([1, 3, 3, 2, 1, 1], frets, strings, circle_radius)
        elif chord_name == "G":
            return get_chord_circles_coordinates([3, 2, 0, 0, 0, 3], frets, strings, circle_radius)
    elif chord_type == "Minor":
        if chord_name == "E":
            return get_chord_circles_coordinates([0, 2, 2, 0, 0, 0], frets, strings, circle_radius)
        if chord_name == "A":
            return get_chord_circles_coordinates(["X", 0, 2, 2, 1, 0], frets, strings, circle_radius)

    return []


def get_chord_circles_coordinates(chord_rules, frets, strings, circle_radius):
    from .math_functions import find_intersection_of_two_lines

    if frets is None or strings is None or len(frets) == 0 or len(strings) == 0:
        return []

    circles = []

    for i in range(0, len(chord_rules)):
        if chord_rules[i] == "X":
            fret_line = frets[-1]
            string_line = strings[i]
            move_right = 0
            special_mark = "X"
        else:
            fret_line = frets[-1-chord_rules[i]]
            string_line = strings[i]
            move_right = circle_radius*2
            special_mark = ""
            if chord_rules[i] == 0:
                move_right = 0
                special_mark = "-"

        intersection = find_intersection_of_two_lines(string_line, fret_line)

        x, y = intersection
        circle_x = x + move_right
        circle_y = y

        circles.append([[int(circle_x), int(circle_y)], special_mark])

    return circles


def draw_chord_circles(image, chord_circles, circles_radius):
    from .drawing_functions import draw_an_x

    for circle in chord_circles:
        if circle[1] == "X":
            draw_an_x(image, (circle[0][0], circle[0][1]), (0, 0, 255), circles_radius*2+5, 3)
        elif circle[1] == "-":
            pass
        else:
            cv2.circle(image, (circle[0][0], circle[0][1]), circles_radius, (0, 255, 0), 3, cv2.LINE_AA)

    return image
