> Just a quick side project

---------------

## inter-morse.py

This script has 2 feature, one is a decoder, the other one is an unnecessary one, noise reduction feature, that uses `sox` *nix utility.

### Usage

```bash
usage: python -m inter_morse [-h] [-l LEVEL] {clean,decode} ... file

positional arguments:
  {clean,decode}        Commands for the decoder
    clean               Clean up the audio
    decode              Decode morse code
  file                  Input file name

optional arguments:
  -h, --help            show this help message and exit
  -l LEVEL, --level LEVEL
                        Verbosity level
```

### Morse Audio Decoder

This feature takes in a `.wav` file and does the following.

1. With `pydub` transforms it into an audio segment
2. Coverts all the values that are above the `max - (max * max_threshhold)` to 1 and others to 0
3. Iterated through all the binary values, when the value switches to a different one:
- Length is calculated in milliseconds and then based on the length, the morse code symbol is determined.

```python
DIH = 100  # On default and the same length for symbol space
DAH = DIH * 3  # The same length is assigned for letter spacing space
SPACE = DIH * 7  # The space between words
```

4. Reads the `codes.csv` file and assigns it to a dictionary.
5. Finally the characters separated by the Character space are compared against the dictionary and translated
- Unknown characters are assigned `?`
- Word spaces are translated to a space and letter space is assigned to an empty string

### Options

`-d | --dih` - The length of DIH symbol in ms (will implement a detection for this) \

- 100ms is good enough for 15 WPM (tested for PARIS)
- 50-60ms - 20 WPM
- 25ms can do 50 WPM

`-l | --level` - The verbosity of the output, haven't done much thinking with this, but 0 is for all output.

### Audio De-noiser

I thought I needed this feature, but will maybe improve it later, haven't tested it much, but all it does is

1. Takes a `.wav` file
2. Finds all 'silence' segments what are passed a given threshold ('-33 dBFS' on default)
2. Runs `sox` on every segment to create a noise profile
3. Passes the input file through all of the generated profiles
4. Exports a cleaned version of the audio file in `export` directory

## To Do

- [	] Improve the code for better detection
- [	] Add an encoder from text to sound
- [	] Add comparison option for testing
- [ ] Add Dynamic WPM detection (so you don't have to change `-d` manually)


## Resources

- [Good online decoder](https://morsecode.world/international/decoder/audio-decoder-adaptive.html) also explains how it works.
- [Morse code generator](https://morsecode.world/international/translator.html) that I used for generating some samples.
- [In depth about Morse code](https://en.wikipedia.org/wiki/Morse_code#:~:text=For%20instance%2C%20%22Q%22%20in,%22Did%20she%20like%20it.%22)
