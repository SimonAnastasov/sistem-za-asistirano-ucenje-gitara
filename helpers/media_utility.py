import cv2
import os


def extract_frames(video_file, output_folder, frames_to_save=10, interval=-1, resizeTo=None, flipImage=False, startFrom=0):
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_file)

    # Get video properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps

    print(f"Total Frames: {frame_count}, FPS: {fps}, Duration: {duration} seconds")

    # Calculate intervals
    if interval <= 0:
        interval = frame_count // frames_to_save

    # Save frames
    for i in range(frames_to_save):
        frame_idx = i * interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)  # Jump to the specific frame
        ret, frame = cap.read()
        if ret:
            frame_filename = os.path.join(output_folder, f"{startFrom + i + 1:02d}.jpeg")

            if resizeTo:
                frame = resize_with_padding(frame, resizeTo)

            if flipImage:
                frame = cv2.flip(frame, 1)

            cv2.imwrite(frame_filename, frame)
            print(f"Saved {frame_filename}")
        else:
            print(f"Failed to read frame at index {frame_idx}")

    cap.release()
    print("Done!")


def resize_with_padding(image, target_size=(512, 512)):
    h, w = image.shape[:2]
    scale = min(target_size[0] / h, target_size[1] / w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_w = (target_size[1] - new_w) // 2
    pad_h = (target_size[0] - new_h) // 2

    padded_image = cv2.copyMakeBorder(
        resized_image, pad_h, target_size[0] - new_h - pad_h,
        pad_w, target_size[1] - new_w - pad_w,
        borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0)  # Black padding
    )
    return padded_image
