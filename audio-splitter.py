import os
import wave
import librosa
import argparse
import numpy as np

RATE = 44000 # Time resolution of the recording device (Hz)
CHANNELS = 1 # default value
SAMPLE_WIDTH = 2 # default value
MINIMUM_AMPLITUDE = 0.025 # This number influencing the audio detection accuracy
SMOOTHER_FACTOR = 30 # This number account for smoothing the audio and not splitting it too aggressively
MINIMUM_AUDIO_CHUNKS = 200 + SMOOTHER_FACTOR # Ignore sounds that are very short in (milliseconds)
AUDIO_SEGMENT_DURATION = 3000 # milliseconds
CHUNK_SIZE = RATE // 1000 # Number of samples in 1ms

# This coefficient used to convert Librosa array float32 into a valid int16  array that fits Wave expectations
LIBROSA_COEFFICIENT = 32767

ERROR_FILE_NOT_FOUND = "file %s does not exists"


def split_chunks(chunks):
    """
        split_chunks(chunks) -> Return list of audio segments (chunks)
    """

    audio_segments = []
    i = 0
    while i < len(chunks):
        if i < len(chunks) and abs(sum(chunks[i])) > MINIMUM_AMPLITUDE:
            start = i
            s_count = 0
            while s_count < SMOOTHER_FACTOR:
                if i < len(chunks) and abs(sum(chunks[i])) > MINIMUM_AMPLITUDE:
                    s_count = 0
                    while abs(sum(chunks[i])) > MINIMUM_AMPLITUDE:
                        i += 1
                s_count += 1
                i += 1
            # if an audio segments length is not more than , we will ignore it since its too short
            if i - start >= MINIMUM_AUDIO_CHUNKS:
                audio_segments.append(chunks[max(0, start):i])
        i += 1

    return audio_segments


def fit_audio_segments(audio_segments):
    """
        fit_audio_segments(audio_segments: list) -> add "silent frames" for each audio segments buffer to make fixed length
    """
    l = []
    for i, audio in enumerate(audio_segments):
        if len(audio) <= RATE // CHUNK_SIZE * (AUDIO_SEGMENT_DURATION//1000):
            l.append(np.vstack((audio, np.zeros((RATE // CHUNK_SIZE * (AUDIO_SEGMENT_DURATION//1000) - len(audio),
                                                 CHUNK_SIZE), dtype=np.float32))))

    return l


def get_args():
    parser = argparse.ArgumentParser(description='Splitting a wav file into multiple short wavs of all audio segments '
                                                 'detected')
    parser.add_argument('-d', '--dst', help='Destination folder to save the results in')
    parser.add_argument('-f', '--fit', action='store_true',
                        help='This argument cause the script to add \"no sound\" frames to the audio segments, their '
                             'duration will be fixed')
    parser.add_argument('file_path')
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(ERROR_FILE_NOT_FOUND % args.file_path)

    return args


def main():
    args = get_args()

    if os.path.exists(args.dst):
        try:
            last_file_id = max([int(i.split(".")[0]) for i in os.listdir(args.dst)])
        except ValueError as e:
            # an error might be raised if the directory is empty
            last_file_id = 0
    else:
        os.mkdir(args.dst)
        last_file_id = 0

    wav_buffer, frame_rate = librosa.load(args.file_path, sr=RATE)

    # add some "no sound" frames
    wav_buffer = np.hstack((wav_buffer, np.zeros(CHUNK_SIZE - int(len(wav_buffer) % CHUNK_SIZE))))

    chunks = wav_buffer.reshape(len(wav_buffer) // CHUNK_SIZE, CHUNK_SIZE)
    audio_segments = split_chunks(chunks)

    if args.fit:
        audio_segments = fit_audio_segments(audio_segments)
    print("%s audio segments detected" % len(audio_segments))
    for audio in audio_segments:
        last_file_id += 1
        wf = wave.open("%s/%s.wav" % (args.dst, last_file_id), "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(RATE)
        wf.writeframes((audio * LIBROSA_COEFFICIENT).astype(np.int16))
        wf.close()


if __name__ == "__main__":
    main()
