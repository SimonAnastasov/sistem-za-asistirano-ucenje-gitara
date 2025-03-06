import math
import time


def get_text_and_chords_based_on_song(song_title, song_author, start_time):
    time_elapsed = time.time() - start_time

    time_elapsed -= 3

    if time_elapsed < 0:
        return str(abs(math.floor(time_elapsed))), None, None, None, None

    song_tempo = get_song_tempo(song_title, song_author)

    if song_tempo == 0:
        return None, None, None, None, None

    beats_per_second = song_tempo / 60
    beats_passed = math.floor(time_elapsed * beats_per_second)

    song_lyrics = get_song_lyrics(song_title, song_author)

    for i in range(len(song_lyrics)):
        song_lyric = song_lyrics[i]
        next_song_lyric = song_lyrics[(i + 1)] if i+1 < len(song_lyrics) else None

        beats_passed -= song_lyric[3]

        if beats_passed < 0:
            current_lyric = song_lyric[0]
            current_chord = [song_lyric[1], song_lyric[2]]

            if next_song_lyric:
                next_lyric = next_song_lyric[0]
                next_chord = [next_song_lyric[1], next_song_lyric[2]]

                # Calculate time until next chord
                current_beat_duration = song_lyric[3] / beats_per_second
                time_in_current_beat = time_elapsed % current_beat_duration
                percentage_time_to_next_chord = 1 - (time_in_current_beat / current_beat_duration)

                return current_lyric, current_chord, next_lyric, next_chord, percentage_time_to_next_chord

            return current_lyric, current_chord, None, None, None

    return None, None, None, None, None


def get_song_tempo(song_title, song_author):
    song_tempo = 0

    if song_author == "Ed Sheeran":
        if song_title == "Perfect":
            song_tempo = 64

    return max(song_tempo - 5, 0)


def get_song_lyrics(song_title, song_author):
    if song_author == "Ed Sheeran":
        if song_title == "Perfect":
            return [
                ["Baby,", None, None, 2],
                ["[Em] I'm", "E", "Minor", 2],
                ["[C] dancing in the", "C", "Major", 2],
                ["[G] dark, with", "G", "Major", 2],
                ["[D] you between my", "D", "Major", 2],
                ["[Em] arms", "E", "Minor", 2],
                ["[C] Barefoot on the", "C", "Major", 2],
                ["[G] grass,", "G", "Major", 2],
                ["[D] Listening to our", "D", "Major", 2],
                ["[Em] favourite song, When you", "E", "Minor", 2],
                ["[C] said you looked a", "C", "Major", 2],
                ["[G] mess, I whispered", "G", "Major", 2],
                ["[D] underneath my", "D", "Major", 2],
                ["[Em] breath, But you", "E", "Minor", 2],
                ["[C] heard it, darling", "C", "Major", 2],
                ["[G] you look", "G", "Major", 2],
                ["[D] perfect", "D", "Major", 2],
                ["to-[G]-night.", "G", "Major", 2]
            ]

    return []
