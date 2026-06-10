Simon Parker

Synth works with the vmpk. Code is set to connect to the first MIDI input, not a specific named connection.
Right now it plays a sawtooth wave

I haven't done any of the bonus features.

Overall this went pretty well. The hardest part was transitioning to using python and learning how audio output worked for that.
I was looking into what it would take to do this project in C, and it seemed way too much work for the amount of time I had.

--verbose flag will output the events as they come in.

setup (for mac):  
Set vmpk MIDI OUT driver to CoreMIDI (this will be different for different systems)  
python -m venv venv  
source venv/bin/activate  
pip install sounddevice mido python-rtmidi numpy  
python synth.py
