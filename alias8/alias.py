from __future__ import with_statement

DEBUG = False

import Live
import MidiRemoteScript

from _Framework import TrackEQComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from _Framework.MixerComponent import MixerComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.TransportComponent import TransportComponent

CHANNEL = 0

def button(notenr, name=None):
  rv = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, notenr)
  if name:
    rv.name = name
  return rv

def fader(notenr):
  rv = SliderElement(MIDI_CC_TYPE, CHANNEL, notenr)
  return rv 

def knob(cc):
  return EncoderElement(MIDI_CC_TYPE, 0, cc, Live.MidiMap.MapMode.absolute)

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
    with self.component_guard():
      self._set_suppress_rebuild_requests(True)
      self.init_session()
      self.init_mixer() 
      
      # connect mixer to session
      self.session.set_mixer(self.mixer)
      self.session.update()
      self.set_highlighting_session_component(self.session)
      self._set_suppress_rebuild_requests(False)

  def init_session(self):
    self.session = SessionComponent(self.num_tracks, 1)
    self.session.name = 'Session'
    self.session.update()

  def init_mixer(self):
    self.mixer = MixerComponent(self.num_tracks, 0)
    self.mixer.id = 'Mixer' 
    self.song().view.selected_track = self.mixer.channel_strip(0)._track
    for i in range(self.num_tracks):
      self.mixer.channel_strip(i).set_volume_control(
          fader(self.faders[i]))
      self.mixer.channel_strip(i).set_solo_button(
          button(self.buttons_top[i]))
      self.mixer.channel_strip(i).set_arm_button(
          button(self.buttons_bottom[i]))
      self.mixer.channel_strip(i).set_pan_control(
          knob(self.knobs_bottom[i]))
    self.mixer.master_strip().set_volume_control(fader(self.master_fader))
    self.mixer.update()
