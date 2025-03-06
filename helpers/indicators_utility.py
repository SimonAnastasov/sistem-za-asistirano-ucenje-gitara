import cv2
import time


def draw_song_completition_indicator(image, song_title, song_author, start_time):
    from .songs_utility import get_song_tempo, get_song_lyrics

    time_elapsed = time.time() - start_time

    time_elapsed -= 3

    if time_elapsed < 0:
        return image

    song_tempo = get_song_tempo(song_title, song_author)

    if song_tempo == 0:
        return image

    beats_per_second = song_tempo / 60

    song_lyrics = get_song_lyrics(song_title, song_author)

    total_song_seconds = sum([song_lyrics[3] for song_lyrics in song_lyrics]) / beats_per_second

    song_completed_percentage = time_elapsed / total_song_seconds

    if song_completed_percentage > 1.1:
        return image

    x_completed = image.shape[1] * song_completed_percentage
    x_completed = int(x_completed)

    cv2.line(image, (0, image.shape[0]-5), (x_completed, image.shape[0]-5), (0, 255, 0), 5)

    return image


def draw_next_chord_preview(image, next_chord_image, alpha=0.2, padding_x=10, padding_y=180):
    height, width = next_chord_image.shape[:2]
    image_height = image.shape[0]

    # Adjust padding_y if there's overflow
    if padding_y + height > image_height:
        return image

    # Add next chord image with padding
    overlay = image[padding_y:padding_y+height, padding_x:width+padding_x]
    next_chord_image = cv2.addWeighted(overlay, 1-alpha, next_chord_image, alpha, 0)

    image[padding_y:padding_y+height, padding_x:width+padding_x] = next_chord_image

    return image


def draw_chord_completition_indicator(image, percentage_time_to_next_chord, frets, fret_max_index_preview):
    padding_x, padding_y = 15, 15
    x, y, width, height = frets[0][0]-padding_x, frets[0][1]+padding_y, frets[fret_max_index_preview][0]-frets[0][0]+2*padding_x, frets[0][3]-frets[0][1]

    # Add progress bar in the padding area
    progress_bar_height = 5
    progress_bar_y = y+padding_y+height
    progress_width = int(width * percentage_time_to_next_chord)

    # Draw progress bar
    cv2.rectangle(image, (x, progress_bar_y), (x+progress_width, progress_bar_y + progress_bar_height), (0, 255, 0), -1)

    return image
