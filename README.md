# alias8

This is an Ableton Live 10 remote script for Livid Alias 8 control surface.

If you use Live, but you don't have an Alias 8, you might find this useful as an example for creating your own remote scripts.

## How to install

If you have a Mac, you may be able to install by typing `make install` in the shell. It will attempt to guess the location of your remote scripts, but I suppose it could easily guess wrong.

If my script guesses wrong, or if you use Windows, you should find your `MIDI Remote Scripts` directory and copy the `alias8` directory in there.

To use the encoder for scrolling through tracks, you'll need to configure the encoder knob to "relative" mode (out of the box, it's set to "absolute" mode). Use the editor supplied by Livid to do this.

## Credits

Thanks to everyone who has published information about Ableton's undocumented Python framework, including:

- Julien Bayle
- Michael Chenetz
- Hanz Petrov
