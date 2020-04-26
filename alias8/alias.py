# Alias 8 remote script for Ableton Live 10.
# by Kevin Ferguson (http://www.ofrecordings.com/)

from __future__ import with_statement

g_logger = None
DEBUG = True

def log(msg):
    global g_logger
    if DEBUG:
        if g_logger is not None:
            g_logger(msg)

import Live
import MidiRemoteScript

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from _Framework.MixerComponent import MixerComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement

CHANNEL = 0

# Channel strip mapping:
# knobs -> first 2 controls on first device on the channel
# fader -> channel volume
# top button -> channel mute
# bottom button -> channel arm

# master fader -> master volume
# encoder -> move grid

# Alias 8 color map.
WHITE = 2
CYAN = 4
MAGENTA = 8
RED = 16
BLUE = 32
YELLOW = 64
GREEN = 127

def button(notenr, name=None, color=None):
    if color is None:
        rv = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, notenr)
    else:
        rv = ColorButton(True, MIDI_NOTE_TYPE, CHANNEL, notenr, color)
    if name:
        rv.name = name
    return rv


def fader(notenr):
    rv = SliderElement(MIDI_CC_TYPE, CHANNEL, notenr)
    return rv


def knob(cc):
    return EncoderElement(MIDI_CC_TYPE, 0, cc, Live.MidiMap.MapMode.absolute)


class ColorButton(ButtonElement):
    """A ButtonElement with a custom on color."""
    def __init__(self, is_momentary, msg_type, channel, identifier, color):
        super(ColorButton, self).__init__(
                is_momentary, msg_type, channel, identifier)
        self.button_value = color

    def turn_on(self):
        log('ColorButton turn on ' + str(self.button_value))
        self.send_value(self.button_value)


class MixerWithDevices(MixerComponent):
    def __init__(self, *args, **kwargs):
        self.devices = []
        super(MixerWithDevices, self).__init__(*args, **kwargs)
        for i in range(len(self._channel_strips)):
            dev = {
                "component": DeviceComponent(),
                "cb": None,
                "track": None
            }
            self.devices.append(dev)
            self.register_components(dev["component"])
        self._reassign_tracks()

    def get_active_tracks(self):
        tracks_to_use = self.tracks_to_use()
        num_tracks = len(self._channel_strips)
        return tracks_to_use[
            self._track_offset:self._track_offset + num_tracks
        ]

    def _reassign_tracks(self):
        super(MixerWithDevices, self)._reassign_tracks()
        # assign each DeviceComponent to the first device on its track
        # this could be called before we construct self.devices
        if self.devices:
            log("reassigning tracks")
            tracks_to_use = self.get_active_tracks()
            log("tracks_to_use has %d elements" % len(tracks_to_use))
            log("devices has %d" % len(self.devices))
            for i, dev in enumerate(self.devices):
                if i < len(tracks_to_use):
                    log("device %d gets a track %s" % (
                        i, tracks_to_use[i].name))
                    self.assign_device_to_track(tracks_to_use[i], i)
                else:
                    log("device %d gets no track" % i)
                    self.assign_device_to_track(None, i)

    def assign_device_to_track(self, track, i):
        # nuke existing listener
        dev = self.devices[i]
        if dev["track"]:
            dev["track"].remove_devices_listener(dev["cb"])
            dev["track"] = None
            dev["cb"] = None
            dev["component"].set_device(None)

        if track is not None:
            # listen for changes to the device chain
            def dcb():
                return self._on_device_changed(i)
            dev["cb"] = dcb
            dev["track"] = track
            track.add_devices_listener(dcb)
            # force an update to attach to any existing device
            dcb()

    def _on_device_changed(self, i):
        log("_on_device_changed %d" % i)
        # the device chain on track i changed-- reassign device if needed
        track = self.devices[i]["track"]
        device_comp = self.devices[i]["component"]
        if not track.devices:
            device_comp.set_device(None)
        else:
            device_comp.set_device(track.devices[0])
            self.update()

    def set_device_controls(self, track_nr, controls):
        device_comp = self.devices[track_nr]["component"]
        device_comp.set_parameter_controls(controls)
        device_comp.update()


class Alias8(ControlSurface):
    num_tracks = 8
    knobs_top = [1, 2, 3, 4, 5, 6, 7, 8]
    knobs_bottom = [9, 10, 11, 12, 13, 14, 15, 16]
    faders = [17, 18, 19, 20, 21, 22, 23, 24]
    master_fader = 25
    encoder = 42
    buttons_top = [0, 1, 2, 3, 4, 5, 6, 7]
    buttons_bottom = [8, 9, 10, 11, 12, 13, 14, 15]

    def __init__(self, instance):
        super(Alias8, self).__init__(instance, False)
        global g_logger
        g_logger = self.log_message
        with self.component_guard():
            self._set_suppress_rebuild_requests(True)
            self.init_session()
            self.init_mixer()

            # Connect mixer to session.
            self.session.set_mixer(self.mixer)
            self.session.update()
            # New in Live 9: must explicitly activate session component.
            self.set_highlighting_session_component(self.session)
            self._set_suppress_rebuild_requests(False)

    def init_session(self):
        self.session = SessionComponent(self.num_tracks, 1)
        self.session.name = 'Alias 8 Session'
        self.session.update()

        # Connect the encoder to track scroller.
        def scroll_cb(value):
            if value == 1:
                self.session._horizontal_banking.scroll_down()
            elif value == 127:
                self.session._horizontal_banking.scroll_up()
        self.track_encoder = EncoderElement(
            MIDI_CC_TYPE,
            0,
            self.encoder,
            Live.MidiMap.MapMode.absolute
        )
        self.track_encoder.add_value_listener(scroll_cb)

    def init_mixer(self):
        self.mixer = MixerWithDevices(self.num_tracks, 0)
        self.mixer.id = 'Mixer'
        self.song().view.selected_track = self.mixer.channel_strip(0)._track
        for i in range(self.num_tracks):
            self.mixer.channel_strip(i).set_volume_control(
                    fader(self.faders[i]))
            self.mixer.channel_strip(i).set_mute_button(
                    button(self.buttons_top[i], color=YELLOW))
            self.mixer.channel_strip(i).set_invert_mute_feedback(True)
            self.mixer.channel_strip(i).set_arm_button(
                    button(self.buttons_bottom[i], color=RED))
            self.mixer.set_device_controls(
                i,
                (
                    knob(self.knobs_top[i]),
                    knob(self.knobs_bottom[i])
                )
            )
        self.mixer.master_strip().set_volume_control(fader(self.master_fader))
        self.mixer.update()
