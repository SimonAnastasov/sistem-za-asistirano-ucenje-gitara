def extend_or_shrink_nut_if_needed(neck_points_xyxyxyxy, nut_points_xyxyxyxy):
    new_top_y = max(nut_points_xyxyxyxy[0][1], neck_points_xyxyxyxy[0][1])
    new_bottom_y = min(nut_points_xyxyxyxy[2][1], neck_points_xyxyxyxy[2][1])

    if nut_points_xyxyxyxy[2][1] < neck_points_xyxyxyxy[2][1] - (neck_points_xyxyxyxy[2][1]-neck_points_xyxyxyxy[0][1])//3:
        top_distance = new_top_y - neck_points_xyxyxyxy[0][1]
        new_bottom_y = neck_points_xyxyxyxy[2][1] - top_distance

    nut_points_xyxyxyxy[0][1], nut_points_xyxyxyxy[1][1], nut_points_xyxyxyxy[2][1], nut_points_xyxyxyxy[3][1] = new_top_y, new_top_y, new_bottom_y, new_bottom_y

    return nut_points_xyxyxyxy