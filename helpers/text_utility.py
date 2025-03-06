import cv2

def put_text_on_an_image(image, text, color, background_color=None, corner=0, skip_lines=0, alpha=0.8, padding_x=0, padding_y=0):
    font_face = cv2.FONT_HERSHEY_SIMPLEX

    font_scale = 0.7 + (image.shape[0]//500)*0.3
    text_color = color if color else (0, 0, 255)
    thickness = 2

    text_position = [10 + padding_x, 30 + (image.shape[0]//500)*10 + padding_y]

    if background_color:
        padding = 10
        text_position = [text_position[0]+padding, text_position[1]+padding]

        (text_width, text_height), baseline = cv2.getTextSize(text, font_face, font_scale, thickness)
        text_width, text_height = text_width + 2*padding, text_height + 2*padding

        if corner == 1:
            text_position[0] = image.shape[1]-text_position[0]-text_width+padding*2

        for i in range(skip_lines):
            text_position[1] += 2*text_height

        x, y = text_position[0]-padding, text_position[1]+padding
        rect_start = (x, y - text_height - baseline)
        rect_end = (x + text_width, y + baseline)

        # Draw alpha-transparent background
        overlay = image.copy()
        cv2.rectangle(overlay, rect_start, rect_end, background_color, -1)  # Rectangle behind text
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    cv2.putText(
        image,
        text,
        text_position,
        font_face,
        font_scale,
        text_color,
        thickness
    )

    return image
