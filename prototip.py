# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# =================================================================================================================================================================================================================================================================================================================================================

import cv2
import time

import helpers

COUNT_ALLOWED_CONSECUTIVE_FAILED_YOLO_DETECTIONS = 10
COUNT_ALLOWED_CONSECUTIVE_FAILED_FRETS_DETECTIONS = 10
COUNT_ALLOWED_CONSECUTIVE_FAILED_STRINGS_DETECTIONS = 10
COUNT_RUN_DO_MAGIC_ON_EVERY_NTH_FRAME = 4
COUNT_RUN_YOLO_ON_EVERY_NTH_FRAME = 1

globals = {
    "original": {},
    "last_successful": {},
    "rotated": {},
    "flipped": {},
    "neck": {},
    "result": {},
    "next_chord_image": {},
    "_count_iterations_frames": 0,
    "_count_consecutive_failed_yolo_detections": 0,
    "_count_consecutive_failed_frets_detection": 0,
    "_count_consecutive_failed_strings_detection": 0,
    "yolo_detections_constants": {
        "classes": [],
    },
    "cv2": {
        "windows": {
            "main": "Main Window",
            "neck": "Neck Window",
        }
    },
    "song_playback_control": {
        "song_title": "Perfect",
        "song_author": "Ed Sheeran",
    }
}

# Model weights paths
model_weights = "best.pt"  # This is the model that was trained on the dataset with the neck and nut classes (Performs very well)


def do_magic(image):
    global globals

    globals["original"]["image"] = image.copy()
    globals["result"]["image"] = image.copy()

    if globals["_count_iterations_frames"] % COUNT_RUN_YOLO_ON_EVERY_NTH_FRAME != 0 and "best_neck" in globals["last_successful"]:
        globals["original"]["best_neck"], globals["original"]["best_nut"] = None, None
    else:
        globals["original"]["best_neck"], globals["original"]["best_nut"], globals["yolo_detections_constants"]["classes"] = helpers.run_yolo_and_get_neck_and_nut(image, model_weights)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Decide whether to use the detections from the original image, the last successful image, or none of them
    use_detections_with_key = "none"

    if globals["original"]["best_neck"] is not None and globals["original"]["best_nut"] is not None:
        globals["last_successful"]["best_neck"], globals["last_successful"]["best_nut"] = globals["original"]["best_neck"], globals["original"]["best_nut"]
        globals["_count_consecutive_failed_yolo_detections"] = 0
        use_detections_with_key = "original"
    else:
        globals["_count_consecutive_failed_yolo_detections"] += 1

        if globals["_count_consecutive_failed_yolo_detections"] > COUNT_ALLOWED_CONSECUTIVE_FAILED_YOLO_DETECTIONS:
            globals["last_successful"]["best_neck"], globals["last_successful"]["best_nut"] = None, None

        if "best_neck" in globals["last_successful"] and globals["last_successful"]["best_neck"] is not None and globals["last_successful"]["best_nut"] is not None:
            use_detections_with_key = "last_successful"
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # If both nut and neck are not detected for more than 10 consecutive frames, reset the global variables and show a warning message on the image
    if use_detections_with_key == "none":
        globals["original"]["image"] = helpers.put_text_on_an_image(globals["original"]["image"], "[X] Please remove large obstructions in front of the neck and nut.", (255, 255, 255), (0, 0, 255))
        cv2.imshow(globals["cv2"]["windows"]["main"], globals["original"]["image"])

        return
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Rotate the image and points based on the neck rotation
    globals["rotated"]["image"], globals["rotated"]["neck_points_xyxyxyxy"], globals["rotated"]["nut_points_xyxyxyxy"], globals["rotated"]["rotation_matrix"] = helpers.rotate_image_and_points_based_on_neck_rotation(globals["original"]["image"], globals[use_detections_with_key]["best_neck"], globals[use_detections_with_key]["best_nut"], globals["yolo_detections_constants"]["classes"])

    # globals["rotated"]["image"] = helpers.draw_xyxyxyxy_points_on_image(globals["rotated"]["image"], globals["rotated"]["neck_points_xyxyxyxy"], (0, 0, 255))
    # globals["rotated"]["image"] = helpers.draw_xyxyxyxy_points_on_image(globals["rotated"]["image"], globals["rotated"]["nut_points_xyxyxyxy"], (0, 255, 0))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Flip the image and points if nut is on the left side of the neck
    globals["flipped"]["image"], globals["flipped"]["neck_points_xyxyxyxy"], globals["flipped"]["nut_points_xyxyxyxy"], globals["flipped"]["is_flipped"] = helpers.flip_image_and_points_if_neck_position_is_to_the_left(globals["rotated"]["image"], globals["rotated"]["neck_points_xyxyxyxy"], globals["rotated"]["nut_points_xyxyxyxy"])

    # Extend or shrink the X values of the 2 rightmost points of the neck to the 2 leftmost points of nut
    globals["flipped"]["neck_points_xyxyxyxy"][1][0], globals["flipped"]["neck_points_xyxyxyxy"][3][0] = globals["flipped"]["nut_points_xyxyxyxy"][0][0], globals["flipped"]["nut_points_xyxyxyxy"][2][0]

    # Extend or shrink kthe Y values of the nut if it's too short or too long
    globals["flipped"]["nut_points_xyxyxyxy"] = helpers.extend_or_shrink_nut_if_needed(globals["flipped"]["neck_points_xyxyxyxy"], globals["flipped"]["nut_points_xyxyxyxy"])

    # Crop the neck area as a separate image
    globals["neck"]["image"] = (globals["flipped"]["image"].copy())[globals["flipped"]["neck_points_xyxyxyxy"][0][1]:globals["flipped"]["neck_points_xyxyxyxy"][-1][1], globals["flipped"]["neck_points_xyxyxyxy"][0][0]:globals["flipped"]["neck_points_xyxyxyxy"][-1][0]]

    globals["flipped"]["image"] = helpers.draw_xyxyxyxy_points_on_image(globals["flipped"]["image"], globals["flipped"]["neck_points_xyxyxyxy"], (255, 0, 0))
    globals["flipped"]["image"] = helpers.draw_xyxyxyxy_points_on_image(globals["flipped"]["image"], globals["flipped"]["nut_points_xyxyxyxy"], (0, 255, 0))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Get frets and either show an error message or draw the frets on the neck image
    neck_frets = helpers.detect_frets_on_neck_image(globals["neck"]["image"])

    if neck_frets is None:
        globals["_count_consecutive_failed_frets_detection"] += 1

        if globals["_count_consecutive_failed_frets_detection"] > COUNT_ALLOWED_CONSECUTIVE_FAILED_FRETS_DETECTIONS:
            globals["neck"]["frets"] = None
            globals["flipped"]["frets"] = None
    else:
        globals["neck"]["frets"] = neck_frets
        globals["flipped"]["frets"] = helpers.move_lines_coordinates_by_x_and_y_values(globals["neck"]["frets"], globals["flipped"]["neck_points_xyxyxyxy"][0][0], globals["flipped"]["neck_points_xyxyxyxy"][0][1])

        globals["_count_consecutive_failed_frets_detection"] = 0

    if "frets" not in globals["neck"] or globals["neck"]["frets"] is None:
        globals["original"]["image"] = helpers.put_text_on_an_image(globals["original"]["image"], "[X] Could not detect the frets. Try bringing the guitar closer in frame.", (255, 255, 255), (0, 0, 255))
        cv2.imshow(globals["cv2"]["windows"]["main"], globals["original"]["image"])

        return

    globals["neck"]["image"] = helpers.draw_lines_on_image(globals["neck"]["image"], globals["neck"]["frets"], (0, 255, 0))
    globals["flipped"]["image"] = helpers.draw_lines_on_image(globals["flipped"]["image"], globals["flipped"]["frets"], (0, 255, 0))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Get strings and either show an error message or draw the strings on the neck image
    nut_line_neck = helpers.move_lines_coordinates_by_x_and_y_values([[globals["flipped"]["nut_points_xyxyxyxy"][0][0], globals["flipped"]["nut_points_xyxyxyxy"][0][1], globals["flipped"]["nut_points_xyxyxyxy"][2][0], globals["flipped"]["nut_points_xyxyxyxy"][2][1]]], -globals["flipped"]["neck_points_xyxyxyxy"][0][0], -globals["flipped"]["neck_points_xyxyxyxy"][0][1])[0]
    neck_strings = helpers.detect_strings_on_neck_image(globals["neck"]["image"], nut_line_neck)

    if neck_strings is None:
        globals["_count_consecutive_failed_strings_detection"] += 1

        if globals["_count_consecutive_failed_strings_detection"] > COUNT_ALLOWED_CONSECUTIVE_FAILED_STRINGS_DETECTIONS:
            globals["neck"]["strings"] = None
            globals["flipped"]["strings"] = None
    else:
        globals["neck"]["strings"] = neck_strings
        globals["flipped"]["strings"] = helpers.move_lines_coordinates_by_x_and_y_values(globals["neck"]["strings"], globals["flipped"]["neck_points_xyxyxyxy"][0][0], globals["flipped"]["neck_points_xyxyxyxy"][0][1])

        globals["_count_consecutive_failed_strings_detection"] = 0

    if "strings" not in globals["neck"] or globals["neck"]["strings"] is None:
        globals["original"]["image"] = helpers.put_text_on_an_image(globals["original"]["image"], "[X] Could not detect the strings. Try bringing the guitar closer in frame.", (255, 255, 255), (0, 0, 255))
        cv2.imshow(globals["cv2"]["windows"]["main"], globals["original"]["image"])

        return

    globals["neck"]["strings"] = neck_strings
    globals["flipped"]["strings"] = helpers.move_lines_coordinates_by_x_and_y_values(globals["neck"]["strings"], globals["flipped"]["neck_points_xyxyxyxy"][0][0], globals["flipped"]["neck_points_xyxyxyxy"][0][1])

    globals["neck"]["image"] = helpers.draw_lines_on_image(globals["neck"]["image"], globals["neck"]["strings"], (0, 0, 255))
    globals["flipped"]["image"] = helpers.draw_lines_on_image(globals["flipped"]["image"], globals["flipped"]["strings"], (0, 0, 255))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Draw chords to a song
    globals["result"]["circle_radius"] = globals["neck"]["image"].shape[0] // 8

    globals["song_playback_control"]["current_lyric"], globals["song_playback_control"]["current_chord"], globals["song_playback_control"]["next_lyric"], globals["song_playback_control"]["next_chord"], globals["song_playback_control"]["percentage_time_to_next_chord"] = helpers.get_text_and_chords_based_on_song(globals["song_playback_control"]["song_title"], globals["song_playback_control"]["song_author"], globals["song_playback_control"]["start_time"])

    if globals["song_playback_control"]["current_chord"] is not None:
        globals["flipped"]["chord_circles"] = helpers.get_chord_circles(globals["flipped"]["frets"], globals["flipped"]["strings"], globals["song_playback_control"]["current_chord"][0], globals["song_playback_control"]["current_chord"][1], globals["result"]["circle_radius"])
        globals["flipped"]["image"] = helpers.draw_chord_circles(globals["flipped"]["image"], globals["flipped"]["chord_circles"], globals["result"]["circle_radius"])

    if globals["song_playback_control"]["next_chord"] is not None:
        globals["next_chord_image"]["chord_circles"] = helpers.get_chord_circles(globals["flipped"]["frets"], globals["flipped"]["strings"], globals["song_playback_control"]["next_chord"][0], globals["song_playback_control"]["next_chord"][1], globals["result"]["circle_radius"])
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Re-flip frets and strings and chord_circles and save to rotated image
    globals["rotated"]["frets"], globals["rotated"]["strings"] = helpers.flip_lines_if_needed(globals["flipped"]["image"], globals["flipped"]["frets"], globals["flipped"]["strings"], globals["flipped"]["is_flipped"])

    if globals["song_playback_control"]["current_chord"] is not None:
        globals["rotated"]["chord_circles"] = [[(helpers.flip_points_if_needed(globals["flipped"]["image"], [center], globals["flipped"]["is_flipped"]))[0], special_mark] for center, special_mark in globals["flipped"]["chord_circles"]]
        globals["rotated"]["image"] = helpers.draw_chord_circles(globals["rotated"]["image"], globals["rotated"]["chord_circles"], globals["result"]["circle_radius"])

    if globals["song_playback_control"]["next_chord"] is not None:
        globals["next_chord_image"]["chord_circles"] = [[(helpers.flip_points_if_needed(globals["flipped"]["image"], [center], globals["flipped"]["is_flipped"]))[0], special_mark] for center, special_mark in globals["next_chord_image"]["chord_circles"]]

    globals["rotated"]["image"] = helpers.draw_lines_on_image(globals["rotated"]["image"], globals["rotated"]["frets"], (0, 255, 0))
    globals["rotated"]["image"] = helpers.draw_lines_on_image(globals["rotated"]["image"], globals["rotated"]["strings"], (0, 0, 255))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Reverse rotate frets and strings and chord_circles and save to original image
    globals["original"]["frets"], globals["original"]["strings"] = helpers.rotate_lines(globals["rotated"]["frets"], globals["rotated"]["strings"], globals["rotated"]["rotation_matrix"], True)
    globals["original"]["frets"] = sorted(globals["original"]["frets"], key=lambda line: helpers.line_left_point_first(line))
    globals["original"]["strings"] = sorted(globals["original"]["strings"], key=lambda line: helpers.line_top_point_first(line))

    if globals["song_playback_control"]["current_chord"] is not None:
        globals["original"]["chord_circles"] = [[(helpers.rotate_points([center], globals["rotated"]["rotation_matrix"], True))[0], special_mark] for center, special_mark in globals["rotated"]["chord_circles"]]
        globals["original"]["image"] = helpers.draw_chord_circles(globals["original"]["image"], globals["original"]["chord_circles"], globals["result"]["circle_radius"])

    if globals["song_playback_control"]["next_chord"] is not None:
        globals["next_chord_image"]["chord_circles"] = [[(helpers.rotate_points([center], globals["rotated"]["rotation_matrix"], True))[0], special_mark] for center, special_mark in globals["next_chord_image"]["chord_circles"]]

    globals["original"]["image"] = helpers.draw_lines_on_image(globals["original"]["image"], globals["original"]["frets"], (0, 255, 0))
    globals["original"]["image"] = helpers.draw_lines_on_image(globals["original"]["image"], globals["original"]["strings"], (0, 0, 255))
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Draw chord circles and text
    globals["next_chord_image"]["image"] = globals["result"]["image"].copy()

    if globals["song_playback_control"]["current_chord"] is not None:
        globals["result"]["chord_circles"] = globals["original"]["chord_circles"]
        globals["result"]["image"] = helpers.draw_chord_circles(globals["result"]["image"], globals["result"]["chord_circles"], globals["result"]["circle_radius"])

    if globals["song_playback_control"]["next_chord"] is not None:
        globals["next_chord_image"]["image"] = helpers.draw_chord_circles(globals["next_chord_image"]["image"], globals["next_chord_image"]["chord_circles"], globals["result"]["circle_radius"])

        padding_next_chord_image = 20
        fret_max_index_preview = 3
        if globals["flipped"]["is_flipped"]:
            globals["next_chord_image"]["image"] = (globals["next_chord_image"]["image"].copy())[globals["original"]["frets"][0][1]-padding_next_chord_image:globals["original"]["frets"][0][3]+padding_next_chord_image, globals["original"]["frets"][0][0]-padding_next_chord_image*3:globals["original"]["frets"][fret_max_index_preview][0]+padding_next_chord_image*3]
        else:
            globals["next_chord_image"]["image"] = (globals["next_chord_image"]["image"].copy())[globals["original"]["frets"][-fret_max_index_preview-1][1]-padding_next_chord_image:globals["original"]["frets"][-fret_max_index_preview-1][3]+padding_next_chord_image, globals["original"]["frets"][-fret_max_index_preview-1][0]-padding_next_chord_image*3:globals["original"]["frets"][-1][0]+padding_next_chord_image*3]

        globals["result"]["image"] = helpers.put_text_on_an_image(globals["result"]["image"], globals["song_playback_control"]["next_lyric"], (255, 255, 255), (0, 200, 0), 0, 1, 0.2, globals["original"]["frets"][0][0]-30, globals["original"]["frets"][0][3]-50)

        globals["result"]["image"] = helpers.draw_next_chord_preview(globals["result"]["image"], globals["next_chord_image"]["image"], 0.5, globals["original"]["frets"][0][0]-20, globals["original"]["frets"][0][3]+140)
        globals["result"]["image"] = helpers.draw_chord_completition_indicator(globals["result"]["image"], globals["song_playback_control"]["percentage_time_to_next_chord"], globals["original"]["frets"], fret_max_index_preview)

    if globals["song_playback_control"]["current_lyric"] is not None:
        globals["result"]["image"] = helpers.put_text_on_an_image(globals["result"]["image"], globals["song_playback_control"]["current_lyric"], (255, 255, 255), (0, 200, 0), 0, 0, 0.8, globals["original"]["frets"][0][0]-30, globals["original"]["frets"][0][1]-100)
        globals["result"]["image"] = helpers.put_text_on_an_image(globals["result"]["image"], f'{globals["song_playback_control"]["song_title"]} - {globals["song_playback_control"]["song_author"]}', (255, 255, 255), (0, 200, 0), 1)

    globals["result"]["image"] = helpers.draw_song_completition_indicator(globals["result"]["image"], globals["song_playback_control"]["song_title"], globals["song_playback_control"]["song_author"], globals["song_playback_control"]["start_time"])
# =================================================================================================================================================================================================================================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    cv2.imshow(globals["cv2"]["windows"]["main"], globals["result"]["image"])
    # cv2.imshow(globals["cv2"]["windows"]["main"], globals["original"]["image"])
    # cv2.imshow(globals["cv2"]["windows"]["main"], globals["rotated"]["image"])
    # cv2.imshow(globals["cv2"]["windows"]["main"], globals["flipped"]["image"])
    # cv2.imshow(globals["cv2"]["windows"]["neck"], globals["neck"]["image"])
    # if "image" in globals["next_chord_image"]:
    #     cv2.imshow(globals["cv2"]["windows"]["main"], globals["next_chord_image"]["image"])
# =================================================================================================================================================================================================================================================================================================================================================


def main_video(video_path, start_second=0):
    # Read frames from video and run YOLO on each frame
    global globals

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    cap.set(cv2.CAP_PROP_POS_MSEC, start_second * 1000)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30

    frame_delay = int(1000 / fps)

    globals["song_playback_control"]["start_time"] = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        globals["_count_iterations_frames"] += 1

        if globals["_count_iterations_frames"] % COUNT_RUN_DO_MAGIC_ON_EVERY_NTH_FRAME != 0:
            continue

        do_magic(frame)

        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main_webcam():
    global globals

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    globals["song_playback_control"]["start_time"] = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        globals["_count_iterations_frames"] += 1

        frame = cv2.flip(frame, 1)
        do_magic(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Uncomment this line if you want to see how this works on a pre-recorded video
# main_video('media_videos/00.mov', 10)

# Uncomment this line if you want to see how this works live on camera
main_webcam()