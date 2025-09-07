from enum import Enum
from typing import List
import time

from .dacs import DacMCP48FVB14, DacMCP48FVB24, DacVrefOptions
from .spi import ELBArduDiscSCPI


class DacCs(Enum):
    LOGIC_TIMING_I: int = 0
    PULSE_I: int = 1
    DELAY_I: int = 2
    CHANNEL_HYS: int = 3
    CHANNEL_THR: int = 4
    LOGIC_TIMING_TH: int = 5
    PULSE_TH: int = 6
    DELAY_TH: int = 7

class ELBArduDisc:
    def __init__(self, serial_port):
        self._scpi = ELBArduDiscSCPI(port=serial_port, reset=True)
        self._dac_control = ELBArduDiscDacControl(self._scpi)
        self.channel_control = ELBArduDiscChannelControl(self._dac_control)
        self.timing_control = ELBArduDiscTimingControl(self._dac_control)
        self.testpulser_control = ELBArduDiscPulserControl(self, self._scpi)

class ELBArduDiscPulserControl:
    def __init__(self, scpi: ELBArduDiscSCPI):
        self.scpi = scpi
    def set_pulser(self, on : bool = True):
        self.scpi.testpulser.switch_testpulser(on=on)


class ELBArduDiscDacControl:
    def __init__(self, scpi: ELBArduDiscSCPI):
        self.scpi = scpi
        self.channel_threshold_dac = DacMCP48FVB24(
            self.scpi.spi, DacCs.CHANNEL_THR.value
        )

        self.channel_threshold_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)

        self.channel_hysteresis_dac = DacMCP48FVB14(
            self.scpi.spi, DacCs.CHANNEL_HYS.value
        )
        self.channel_hysteresis_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)

        self.channel_delay_i_dac = DacMCP48FVB14(self.scpi.spi, DacCs.DELAY_I.value)
        self.channel_delay_i_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)
        self.channel_delay_th_dac = DacMCP48FVB14(self.scpi.spi, DacCs.DELAY_TH.value)
        self.channel_delay_th_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)

        self.channel_pulse_i_dac = DacMCP48FVB14(self.scpi.spi, DacCs.PULSE_I.value)
        self.channel_pulse_i_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)
        self.channel_pulse_th_dac = DacMCP48FVB14(self.scpi.spi, DacCs.PULSE_TH.value)
        self.channel_pulse_th_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)

        self.logic_timing_i_dac = DacMCP48FVB14(
            self.scpi.spi, DacCs.LOGIC_TIMING_I.value
        )
        self.logic_timing_i_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)
        self.logic_timing_th_dac = DacMCP48FVB14(
            self.scpi.spi, DacCs.LOGIC_TIMING_TH.value
        )
        self.logic_timing_th_dac.set_all_refs_same(DacVrefOptions.ExtBuffered)


class ELBArduDiscChannelControl:
    def __init__(self, dac_control: ELBArduDiscDacControl):
        self.dac_control = dac_control
        self.min_threshold_v = -2.5
        self.max_threshold_v = 2.5
        self.attenuation_factor = 0.72

    def set_threshold(self, channel: int, value: int):
        self.dac_control.channel_threshold_dac.set_channel(channel, value)

    def set_threshold_v(self, channel: int, value: float):
        # dac value 0 -> -2.5V
        # dac value 0xfff -> +2.5V
        range = (self.max_threshold_v - self.min_threshold_v) / self.attenuation_factor
        if value < -range / 2 or value > range / 2:
            raise ValueError(
                f"Invalid threshold: {value} V. Allowed Range: {-range/2} V ... {range/2} V."
            )
        max_dac = (1 << self.dac_control.channel_threshold_dac.resolution) - 1

        dac_setting = int((value + range / 2) / range * max_dac)

        # truncate in case of rounding errors
        if dac_setting < 0:
            dac_setting = 0

        if dac_setting > max_dac:
            dac_setting = max_dac

        self.set_threshold(channel, dac_setting)

    def set_hysteresis(self, channel: int, value: int):
        self.dac_control.channel_hysteresis_dac.set_channel(channel, value)

    def set_hysteresis_v(self, channel: int, value: float):
        raise NotImplementedError("This method is not implemented yet")


class ELBArduDiscTimingControl:
    def __init__(self, dac_control: ELBArduDiscDacControl):
        self.dac_control = dac_control

    def set_channel_delay_current(self, channel: int, value: int):
        self.dac_control.channel_delay_i_dac.set_channel(channel, value)

    def set_channel_delay_threshold(self, channel: int, value: int):
        self.dac_control.channel_delay_th_dac.set_channel(channel, value)

    def set_channel_pulse_width_current(self, channel: int, value: int):
        self.dac_control.channel_pulse_i_dac.set_channel(channel, value)

    def set_channel_pulse_width_threshold(self, channel: int, value: int):
        self.dac_control.channel_pulse_th_dac.set_channel(channel, value)

    def set_logic_delay_current(self, channel: int, value: int):
        # DAC channel 0 = Delay CH 01
        # DAC channel 1 = PulseWidth CH 01
        # DAC channel 2 = Delay CH 23
        # DAC channel 3 = PulseWidth CH 23
        if channel < 0 or channel > 1:
            raise ValueError("Invalid Timing Channel {channel}")
        self.dac_control.logic_timing_i_dac.set_channel(channel * 2, value)

    def set_logic_delay_threshold(self, channel: int, value: int):
        if channel < 0 or channel > 1:
            raise ValueError("Invalid Timing Channel {channel}")
        self.dac_control.logic_timing_th_dac.set_channel(channel * 2, value)

    def set_logic_pulse_width_current(self, channel: int, value: int):
        if channel < 0 or channel > 1:
            raise ValueError("Invalid Timing Channel {channel}")
        self.dac_control.logic_timing_i_dac.set_channel(channel * 2 + 1, value)

    def set_logic_pulse_width_threshold(self, channel: int, value: int):
        if channel < 0 or channel > 1:
            raise ValueError("Invalid Timing Channel {channel}")
        self.dac_control.logic_timing_th_dac.set_channel(channel * 2 + 1, value)


if __name__ == "__main__":
    ead = ELBArduDisc(serial_port="COM4")

    for i in range(4):
        ead.channel_control.set_threshold_v(i, 1)


"""
todo:
- add aux input
- testpulsercontrol: make it like the dac control
- update example
"""
