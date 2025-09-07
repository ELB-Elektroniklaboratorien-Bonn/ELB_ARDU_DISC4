"""
Example that sets default values and sweeps delay and pulse width.

Demonstration:
- Connect testpulser output to an oscilloscope and an input.
- Connect the Logic Output to the oscilloscope.

Configuration:
- Polarity: Pos
- Ranges: Unset all jumpers.
- Inhibit: Set B,C. Unset A
- Delay: Use
- Logic: Set all to OR.

"""

from elb_ardu_disc import ELBArduDisc

if __name__ == "__main__":
    ead = ELBArduDisc(serial_port="COM4")
    ead._scpi.testpulser.switch_testpulser(on=True)

    for i in range(4):
        ead.channel_control.set_threshold_v(i,0.05)
        ead.channel_control.set_hysteresis(i,500)

        ead.timing_control.set_channel_delay_current(i, 512)
        ead.timing_control.set_channel_delay_threshold(i, 512)
        ead.timing_control.set_channel_pulse_width_current(i, 512)
        ead.timing_control.set_channel_pulse_width_threshold(i, 512)
    for i in range(2):
        ead.timing_control.set_logic_delay_current(i, 512)
        ead.timing_control.set_logic_delay_threshold(i, 512)
        ead.timing_control.set_logic_pulse_width_current(i, 512)
        ead.timing_control.set_logic_pulse_width_threshold(i, 512)

    for j in range(350, 900):
        for i in range(4):
            ead.timing_control.set_channel_delay_threshold(i, j)
            ead.timing_control.set_channel_pulse_width_threshold(i, j)
