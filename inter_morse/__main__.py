# __main__.py

from pydub import AudioSegment, silence
from pydub.playback import play
import matplotlib.pyplot as plt
import argparse
import sys
import os
import csv
import time
import subprocess


# ======== Constants ======== #
SCRIPT_DIR = os.path.dirname(__file__)
# PROFILE_DIR = os.path.join(SCRIPT_DIR, 'profiles')
# EXPORT_DIR = os.path.join(SCRIPT_DIR, 'export')
PROFILE_DIR = 'profiles'
EXPORT_DIR = 'export'

DIRS = [PROFILE_DIR, EXPORT_DIR]

CODES = os.path.join(SCRIPT_DIR, 'codes.csv')

SILENCE_PROFILE = "silence.prof"

# MINIMUM_VOLUME_FILTER = -60
# MAXIMUM_VOLUME_FILTER = -30
# VOLUME_TRESHOLD       = 200

DI_CHAR = ''
DAH_CHAR = '-'
DIT_CHAR = '.'  # Symbol space
CHAR_SPACE = ' '  # 3 * DIT of 0 values
WORD_SPACE = '   '
SYMBOL_SPACE = ''

# ======== Argument Parser ======== #
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='Commands for the decoder', dest='action')

parser.add_argument('file', help='Input file name')
parser.add_argument('-l', '--level', help='Verbosity level', type=int, default=2)

clean_group = subparsers.add_parser('clean', help='Clean up the audio')
decode_group = subparsers.add_parser('decode', help='Decode morse code')
decode_group.add_argument('-d', '--dit', help='DIT value in milliseconds', type=int, default=100)
decode_group.add_argument('-p', '--plot', help='Plot the pulses.', action='store_true')

# ======== Some Functions ======== #
def makedirs(dirs):
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)


def makedir(dir):
    os.makedirs(dir, exist_ok=True)


def myprint(str, level=0):
    if (level >= PRINT_LEVEL):
        print(str)


class MorseDecoder():
    def __init__(self, audio_file, format="wav"):
        self.audio_file = audio_file
        self.format = format
        self.sound = AudioSegment.from_file(self.audio_file, format=self.format)
        self.decoded_audio = []
        self.translated_audio = ''
        self.decoded_morse = []
        self.length_treshhold = 0.5
        self.peak_threshold = 0.8

        # To Do:
        self.wpm = 14  # Max that this hard coded thing can detect
        self.wpm_word = 'PARIS'  # Somehow apply this later
        self.frequency = 500  # Detect this

    def set_lengths(self, DIT=100.0, wpm=14):
        self.DIT = float(DIT)
        self.DAH = self.DIT * 3.0
        self.SPACE = self.DIT * 7.0  # Word space

    def get_lengths(self):
        return self.DIT, self.DAH, self.SPACE

    def translate_to_binary(self):
        myprint(f"> Translating {os.path.basename(self.audio_file)}.", 2)
        binary = []

        sound = self.sound
        peak = sound.max  # Max of something
        myprint(f"Peak: {peak}", 2)
        peak = sound.max - (sound.max * self.peak_threshold)

        myprint("> Getting binary values.", 0)
        for ms, s in enumerate(sound):
            if s.rms > peak:
                binary.append(1)
            else:
                binary.append(0)

        return binary

    def decode_from_audio(self):
        binary = self.translate_to_binary()

        current = 0
        ms = 0
        myprint("> Translating values to morse code.", 2)
        while ms < len(binary)-1:
            try:
                current = ms
                s = binary[ms]  # current value

                while s == 0:
                    s = binary[ms]  # current value
                    if s != 0:
                        length = ms - current
                        self.translate_length(length, 0)
                        current = ms
                        break
                    ms += 1

                while s == 1:
                    s = binary[ms]  # current value
                    if s != 1:
                        length = ms - current
                        self.translate_length(length, 1)
                        current = ms
                        break
                    ms += 1
            except:
                ms += 1
                pass

        myprint("[+] Done.", 2)

        self.translated_audio = "".join(self.get_decoded_audio())
        myprint(f"[=] Translated audio:\n{self.translated_audio}", 2)
        self.binary = binary
        return self.translated_audio

    def decode_morse_code(self, morse_code, codes):
        character_list = self.get_word_list(morse_code)
        myprint(character_list, 0)

        for i, char in enumerate(character_list):
            symbol_list = [s for s in char.split(CHAR_SPACE) if s]
            if char:
                for symbol in symbol_list:
                    if symbol in codes:
                        self.decoded_morse.append(codes[symbol])
                    else:
                        self.decoded_morse.append("?")

                if len(symbol_list) > 1:
                    self.decoded_morse.append(" ")

        return "".join(self.decoded_morse)

    def translate_length(self, length, value):
        DIT, DAH, SPACE = self.get_lengths()
        thresh = self.length_treshhold  # Word space == 1.1 # Char space 500

        if value == 1:
            if length > DAH - (DIT * thresh):
                myprint(f"{length}ms of {value} > {DAH - (DIT * thresh)} | DAH", 0)
                self.decoded_audio.append(DAH_CHAR)
            else:
                myprint(f"{length}ms of {value} | DIT", 0)
                self.decoded_audio.append(DIT_CHAR)
        else:
            if length > SPACE - (SPACE * thresh):
                myprint(f"{length}ms of {value} > {SPACE - (SPACE * thresh)} | Word space", 0)
                self.decoded_audio.append(WORD_SPACE)
            elif length > DAH - (DAH * thresh):
                myprint(f"{length}ms of {value} | Character space", 0)
                self.decoded_audio.append(CHAR_SPACE)
            else:
                myprint(f"{length}ms of {value} | Symbol space", 0)

    def get_word_list(self, morse_code):
        return morse_code.split(WORD_SPACE)

    def get_character_list(self, morse_code):
        word_list = "".join(self.get_word_list(morse_code))
        return word_list.split(DI_CHAR)

    def detect_wpm(self):
        pass

    def detect_high(self):
        pass

    def get_decoded_audio(self):
        return self.decoded_audio

    def get_binary(self):
        return self.binary


class Codes():
    def __init__(self, path=CODES):
        self.data = csv.DictReader(open(path), delimiter=',', fieldnames=["char", "code"])
        self.codes = {}

        for entry in self.data:
            self.codes[entry["code"]] = entry["char"]

    def get_codes(self):
        return self.codes


class AudioCleaner():
    def __init__(self, audio_file, format="wav"):
        self.audio_file = audio_file
        self.format = format

        self.sound = AudioSegment.from_file(self.audio_file, format=self.format)

    def find_silence(self, thresh=-34):
        silence_dict = {}
        try:
            detected_silence = silence.detect_silence(self.sound, silence_thresh=thresh)
            myprint(f"[  ] Silence segments found.", 2)

            silence_segments = [self.sound[min:max] for min, max in detected_silence]
            # final_silence = silence_segments[0][0]

            makedir(PROFILE_DIR)

            for i, seg in enumerate(silence_segments):
                silence_file = os.path.join(PROFILE_DIR, f"silence-{i}-{self.audio_file}")
                silence_dict[silence_file] = seg
                seg.export(silence_file, format="wav")

                # final_silence = final_silence.append(seg, crossfade=0)
                # final_silence.export('final.silence', format="wav")

            return silence_dict

        except Exception as e:
            myprint(e, 2)
            sys.exit()

    def sox_denoise(self):
        silence_segments = self.find_silence()
        out_file = ''

        # segment_length_sec = len(silence_segments) / 1000.0
        # file = 'final.silence'
        # cmd = f"sox '{file}' -n trim 0 {segment_length_sec} noiseprof '{SILENCE_PROFILE}'"

        # myprint(cmd, 2)
        # myprint(subprocess.check_output(cmd, shell=True), 2)

        # out_file = os.path.join(EXPORT_DIR, f"cleaned-{self.audio_file}")
        # cmd = f"sox '{self.audio_file}' '{out_file}' noisered {SILENCE_PROFILE} 0.3"
        # myprint(cmd, 0)
        # myprint(subprocess.check_output(cmd, shell=True), 2)


        # Iterate through all the generated segments and apply all segments
        for file, seg in silence_segments.items():
            prefix = os.path.basename(file).split('-')[1]

            # Generate a noise profile
            """
            This command is run on an audio segment that contains noise and
            `noisered` using the generated profile can find the noisy spots and clean them
            `segment_length_sec` - how much noise should be removed in seconds
            """
            segment_length_sec = len(seg) / 1000.0
            cmd = f"sox '{file}' -n trim 0 {segment_length_sec} noiseprof '{SILENCE_PROFILE}'"

            myprint(cmd, 2)
            output = subprocess.check_output(cmd, shell=True)
            myprint(output, 1)

            makedir(EXPORT_DIR)
            out_file = os.path.join(EXPORT_DIR, f"{prefix}-cleaned-{self.audio_file}")
            myprint(f"> Exporting -> {out_file}", 2)

            # Clean the file
            cmd = f"sox '{self.audio_file}' '{out_file}' noisered {SILENCE_PROFILE} 0.3"
            myprint(cmd, 2)
            output = subprocess.check_output(cmd, shell=True)
            myprint(output, 1)

        self.set_cleaned_file(out_file)

    def set_cleaned_file(self, cleaned_file):
        self.cleaned_file = cleaned_file

    def get_cleaned_file(self):
        return self.cleaned_file



def main():
    audio_file = args.file

    if args.action == 'clean':
        ac = AudioCleaner(audio_file)
        ac.sox_denoise()

    elif args.action == 'decode':
        codes = Codes().get_codes()
        md = MorseDecoder(audio_file)
        md.set_lengths(DIT=args.dit)


        morse_code = md.decode_from_audio()
        decoded_morse_code = md.decode_morse_code(morse_code, codes)
        print(decoded_morse_code)

        if args.plot:
            binary = md.get_binary()

            plt.plot(binary)
            plt.ylabel('Pulse')
            plt.xlabel('Time')
            plt.show()

if __name__ == '__main__':
    args = parser.parse_args()
    #print(args)
    PRINT_LEVEL = args.level
    main()


"""
Specifying the dot duration - 50ms
unually speeds are stated in WPM

choose a dot duration that would send a typical word the desired number of times in one minute

Dot length
Dash - 3 dots

Spacings are in number of dot lengths

PARIS - 20 WPM is 60 milliseconds
CODEX - 20 WPM is 50 milliseconds

https://en.wikipedia.org/wiki/Morse_code#:~:text=For%20instance%2C%20%22Q%22%20in,%22Did%20she%20like%20it.%22

1 dah == 3 dih
1 space == 7 dih

az.wav
- dih = 100ms
- dah = 300ms
"""
