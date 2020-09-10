# audio-splitter
#### Description
This script allowing you very quickly split an audio file (WAV format specifficly)
 into small parts.<br>
This is super effiecent for creating your own audio data set.

#### HELP! (-h)

usage: audio-splitter.py [-h] [-d DST] [-f] file_path

Splitting a wav file into multiple short wavs of all audio segments detected

positional arguments:<br />
  file_path

optional arguments:<br />
  -h, --help         show this help message and exit.<br />
  -d DST, --dst DST  destination folder to save the results in.<br />
  -f, --fit          This argument cause the script to add "no sound" frames to the audio segments, so their duration 
                     will be fixed.<br />

Example: audio-splitter.py -d "/tmp" -f "/audio.wav"


#### Some more help
The way the script detect and crop the WAV buffer lays on a few constants announced at the beginning of the script,
you may change them for your own needs, but be gentle! :), even small change might cause big changes in the results.