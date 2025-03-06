# import cv2
# import mediapipe as mp
#
#
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles
# mp_hands = mp.solutions.hands
#
#
# def find_fingers_and_extend_or_shrink_nut_if_needed(image, neck_points_xyxyxyxy, nut_points_xyxyxyxy):
#     fingers_points = get_fingers_keypoints_coordinates(image)
#
#     new_top_y = max(nut_points_xyxyxyxy[0][1], neck_points_xyxyxyxy[0][1])
#     new_bottom_y = min(nut_points_xyxyxyxy[2][1], neck_points_xyxyxyxy[2][1])
#
#     CONSTANT_X = 5
#     CONSTANT_Y = 20
#
#     fingers_points = [finger_points for finger_points in fingers_points if finger_points[0] > neck_points_xyxyxyxy[0][0]-CONSTANT_X and finger_points[0] < neck_points_xyxyxyxy[1][0]+CONSTANT_X and finger_points[1] > neck_points_xyxyxyxy[0][1] and finger_points[1] < neck_points_xyxyxyxy[2][1]+CONSTANT_Y]
#
#     if fingers_points is not None:
#         top_distance = new_top_y - neck_points_xyxyxyxy[0][1]
#         new_bottom_y = neck_points_xyxyxyxy[2][1] - top_distance
#
#     nut_points_xyxyxyxy[0][1], nut_points_xyxyxyxy[1][1], nut_points_xyxyxyxy[2][1], nut_points_xyxyxyxy[3][1] = new_top_y, new_top_y, new_bottom_y, new_bottom_y
#
#     return nut_points_xyxyxyxy
#
#
# def get_fingers_keypoints_coordinates(image):
#     hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5)
#
#     results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#
#     # Print handedness and draw hand landmarks on the image.
#     if not results.multi_hand_landmarks:
#         return None
#
#     hand_points = []
#
#     image_height, image_width, _ = image.shape
#     annotated_image = image.copy()
#     for hand_landmarks in results.multi_hand_landmarks:
#         for landmark in hand_landmarks.landmark:
#             hand_points.append([landmark.x * image_width, landmark.y * image_height])
#
#         # print(
#         #     f'Index finger tip coordinates: (',
#         #     f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
#         #     f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
#         # )
#         # mp_drawing.draw_landmarks(
#         #     annotated_image,
#         #     hand_landmarks,
#         #     mp_hands.HAND_CONNECTIONS,
#         #     mp_drawing_styles.get_default_hand_landmarks_style(),
#         #     mp_drawing_styles.get_default_hand_connections_style()
#         # )
#
#     return hand_points
