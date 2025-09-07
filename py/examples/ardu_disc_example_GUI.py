"""
GUI to test parameters interacively.

Demonstration:
- Connect testpulser output to an oscilloscope and an input.
- Connect the Logic Output to the oscilloscope.

Configuration:
- Polarity: Pos
- Ranges: Unset all jumpers.
- Inhibit: Set B, C. Unset A
- Delay: Use
- Logic: Set all to OR.

"""

import tkinter as tk
from tkinter import ttk
import logging

logging.basicConfig(level=logging.INFO)

from elb_ardu_disc import ELBArduDisc
from typing import List

ead = ELBArduDisc(serial_port="COM4")

NUM_OF_CHANNELS = 4


class VarManager:
    def __init__(self, ead: ELBArduDisc):
        self.ead = ead
        self.threshold = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.hysteresis = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.channel_delay_current = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.channel_delay_threshold = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.channel_pulse_current = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.channel_pulse_threshold = [tk.DoubleVar() for _ in range(NUM_OF_CHANNELS)]
        self.logic_delay_current = [tk.DoubleVar() for _ in range(2)]
        self.logic_delay_threshold = [tk.DoubleVar() for _ in range(2)]
        self.logic_pulse_current = [tk.DoubleVar() for _ in range(2)]
        self.logic_pulse_threshold = [tk.DoubleVar() for _ in range(2)]

        for i in range(NUM_OF_CHANNELS):

            def update_threshold(*args, index: int = i):
                new_threshold: float = self.threshold[index].get()
                ead.channel_control.set_threshold_v(index, self.threshold[index].get())
                logging.info(f"Setting Threshold {index} to {new_threshold}")

            self.threshold[i].trace_add("write", update_threshold)

            def update_hysteresis(*args, index: int = i):
                new_hysteresis = int(self.hysteresis[index].get())
                ead.channel_control.set_hysteresis(index, new_hysteresis)
                logging.info(f"Setting Hysteresis {index} to {new_hysteresis}")

            self.hysteresis[i].trace_add("write", update_hysteresis)

            def update_ch_del_cur(*args, index: int = i):
                new_cur = int(self.channel_delay_current[index].get())
                ead.timing_control.set_channel_delay_current(index, new_cur)
                logging.info(f"Setting Channel {index} Delay Current to {new_cur}")

            self.channel_delay_current[i].trace_add("write", update_ch_del_cur)

            def update_ch_del_thr(*args, index: int = i):
                new_cur = int(self.channel_delay_threshold[index].get())
                ead.timing_control.set_channel_delay_threshold(index, new_cur)
                logging.info(f"Setting Channel {index} Delay Threshold to {new_cur}")

            self.channel_delay_threshold[i].trace_add("write", update_ch_del_thr)

            def update_ch_pu_cur(*args, index: int = i):
                new_cur = int(self.channel_pulse_current[index].get())
                ead.timing_control.set_channel_pulse_width_current(index, new_cur)
                logging.info(f"Setting Channel {index} Pulse Current to {new_cur}")

            self.channel_pulse_current[i].trace_add("write", update_ch_pu_cur)

            def update_ch_pu_thr(*args, index: int = i):
                new_cur = int(self.channel_pulse_threshold[index].get())
                ead.timing_control.set_channel_pulse_width_threshold(index, new_cur)
                logging.info(f"Setting Channel {index} Pulse Threshold to {new_cur}")

            self.channel_pulse_threshold[i].trace_add("write", update_ch_pu_thr)

        # Logic Timing
        for i in range(2):

            def update_lo_del_cur(*args, index: int = i):
                new_cur = int(self.logic_delay_current[index].get())
                ead.timing_control.set_logic_delay_current(index, new_cur)
                logging.info(f"Setting Logic {index} Delay Current to {new_cur}")

            self.logic_delay_current[i].trace_add("write", update_lo_del_cur)

            def update_lo_del_thr(*args, index: int = i):
                new_cur = int(self.logic_delay_threshold[index].get())
                ead.timing_control.set_logic_delay_threshold(index, new_cur)
                logging.info(f"Setting Logic {index} Delay Threshold to {new_cur}")

            self.logic_delay_threshold[i].trace_add("write", update_lo_del_thr)

            def update_lo_pu_cur(*args, index: int = i):
                new_cur = int(self.logic_pulse_current[index].get())
                ead.timing_control.set_logic_pulse_width_current(index, new_cur)
                logging.info(f"Setting Logic {index} Pulse Current to {new_cur}")

            self.logic_pulse_current[i].trace_add("write", update_lo_pu_cur)

            def update_lo_pu_thr(*args, index: int = i):
                new_cur = int(self.logic_pulse_threshold[index].get())
                ead.timing_control.set_logic_pulse_width_threshold(index, new_cur)
                logging.info(f"Setting Logic {index} Pulse Threshold to {new_cur}")

            self.logic_pulse_threshold[i].trace_add("write", update_lo_pu_thr)

    def set_defaults(self):
        for i in range(NUM_OF_CHANNELS):
            self.threshold[i].set(0.05)
            self.hysteresis[i].set(500)
            self.channel_delay_current[i].set(500)
            self.channel_delay_threshold[i].set(500)
            self.channel_pulse_current[i].set(500)
            self.channel_pulse_threshold[i].set(500)
        for i in range(2):
            self.logic_delay_current[i].set(500)
            self.logic_delay_threshold[i].set(500)
            self.logic_pulse_current[i].set(500)
            self.logic_pulse_threshold[i].set(500)


def add_mousewheel_support(slider, var):
    f = slider.cget("from")
    t = slider.cget("to")
    inverted = f < t

    def on_mousewheel(event):
        delta = (
            (event.delta / 120)
            if hasattr(event, "delta")
            else (1 if event.num == 4 else -1)
        )
        SHIFT_MASK = 0x0001
        if event.state & SHIFT_MASK:
            delta *= 10

        # Invert delta direction if slider range is inverted
        if inverted:
            delta = -delta
        newval = var.get() + delta * slider.cget("resolution")
        # Clamp value within the slider's range regardless of inversion
        min_val, max_val = min(f, t), max(f, t)
        newval = max(min_val, min(max_val, newval))
        var.set(newval)

    slider.bind("<MouseWheel>", on_mousewheel)
    slider.bind("<Button-4>", on_mousewheel)
    slider.bind("<Button-5>", on_mousewheel)


def add_threshold_sliders(
    frame: tk.Frame, threshold_vars: List[tk.DoubleVar], row0: int = 0, col0: int = 0
):
    heading = ttk.Label(frame, text="Threshold Channel", font=("Arial", 12))
    heading.grid(row=0 + row0, column=0 + col0, columnspan=4, pady=(10, 20))
    sliders: List[tk.Scale] = []
    for i in range(NUM_OF_CHANNELS):
        label = ttk.Label(frame, text=f"{i}", font=("Arial", 12))
        label.grid(row=1 + row0, column=i + col0, padx=10)
        sliders.append(
            tk.Scale(
                frame,
                from_=3.47,
                to=-3.47,
                resolution=0.001,
                orient=tk.VERTICAL,
                variable=threshold_vars[i],
                length=300,
            )
        )
        sliders[i].grid(row=2 + row0, column=i + col0, padx=5)
        add_mousewheel_support(sliders[i], threshold_vars[i])


def add_hysteresis_sliders(
    frame: tk.Frame, tkvars: List[tk.DoubleVar], row0: int = 0, col0: int = 0
):
    heading = ttk.Label(frame, text="Hysteresis Channel", font=("Arial", 12))
    heading.grid(row=0 + row0, column=0 + col0, columnspan=4, pady=(10, 20))
    sliders: List[tk.Scale] = []
    for i in range(NUM_OF_CHANNELS):
        label = ttk.Label(frame, text=f"{i}", font=("Arial", 12))
        label.grid(row=1 + row0, column=i + col0, padx=10)
        sliders.append(
            tk.Scale(
                frame,
                from_=1023,
                to=0,
                resolution=1,
                orient=tk.VERTICAL,
                variable=tkvars[i],
                length=300,
            )
        )
        sliders[i].grid(row=2 + row0, column=i + col0, padx=5)
        add_mousewheel_support(sliders[i], tkvars[i])


def add_timing_slider(
    frame: tk.Frame, tkvar: tk.DoubleVar, row0: int = 0, col0: int = 0
) -> tk.Scale:
    slider = tk.Scale(
        frame,
        from_=0,
        to=1023,
        resolution=1,
        orient=tk.HORIZONTAL,
        variable=tkvar,
        length=300,
    )
    slider.grid(row=row0, column=col0)
    add_mousewheel_support(slider, tkvar)
    return slider


def add_ch_timing_sliders(frame: tk.Frame, tkvars: VarManager):
    timing_sliders = {}
    sl_ch_del_cur = []
    sl_ch_del_th = []

    heading = ttk.Label(frame, text="Channel Delay", font=("Arial", 12))
    heading.grid(row=0, column=1, columnspan=1, pady=(10, 20))

    for i in range(NUM_OF_CHANNELS):
        label = ttk.Label(frame, text=f"Current {i}", font=("Arial", 12))
        label.grid(row=i * 2 + 1, column=0, padx=10)

        slider_i = add_timing_slider(
            frame, tkvars.channel_delay_current[i], i * 2 + 1, 1
        )

        label = ttk.Label(frame, text=f"Threshold {i}", font=("Arial", 12))
        label.grid(row=i * 2 + 2, column=0, padx=10)

        slider_t = add_timing_slider(
            frame, tkvars.channel_delay_threshold[i], i * 2 + 2, 1
        )
        sl_ch_del_cur.append(slider_i)
        sl_ch_del_th.append(slider_t)

    timing_sliders["Channel Delay Current"] = sl_ch_del_cur
    timing_sliders["Channel Delay Threshold"] = sl_ch_del_th

    sl_ch_pu_cur = []
    sl_ch_pu_th = []

    heading = ttk.Label(frame, text="Channel Pulse", font=("Arial", 12))
    heading.grid(row=0, column=2, columnspan=1, pady=(10, 20))

    for i in range(NUM_OF_CHANNELS):

        slider_i = add_timing_slider(
            frame, tkvars.channel_pulse_current[i], i * 2 + 1, 2
        )

        slider_t = add_timing_slider(
            frame, tkvars.channel_pulse_threshold[i], i * 2 + 2, 2
        )
        sl_ch_pu_cur.append(slider_i)
        sl_ch_pu_th.append(slider_t)

    timing_sliders["Channel Pulse Current"] = sl_ch_pu_cur
    timing_sliders["Channel Pulse Threshold"] = sl_ch_pu_th

    return timing_sliders


def add_lo_timing_sliders(frame: tk.Frame, tkvars: VarManager):
    timing_sliders = {}
    sl_lo_del_cur = []
    sl_lo_del_th = []

    heading = ttk.Label(frame, text="Logic Delay", font=("Arial", 12))
    heading.grid(row=0, column=1, columnspan=1, pady=(10, 20))

    for i in range(2):
        label = ttk.Label(frame, text=f"Current {i}", font=("Arial", 12))
        label.grid(row=i * 2 + 1, column=0, padx=10)

        slider_i = add_timing_slider(frame, tkvars.logic_delay_current[i], i * 2 + 1, 1)

        label = ttk.Label(frame, text=f"Threshold {i}", font=("Arial", 12))
        label.grid(row=i * 2 + 2, column=0, padx=10)

        slider_t = add_timing_slider(
            frame, tkvars.logic_delay_threshold[i], i * 2 + 2, 1
        )
        sl_lo_del_cur.append(slider_i)
        sl_lo_del_th.append(slider_t)

    timing_sliders["Channel Delay Current"] = sl_lo_del_cur
    timing_sliders["Channel Delay Threshold"] = sl_lo_del_th

    sl_lo_pu_cur = []
    sl_lo_pu_th = []

    heading = ttk.Label(frame, text="Channel Pulse", font=("Arial", 12))
    heading.grid(row=0, column=2, columnspan=1, pady=(10, 20))

    for i in range(2):

        slider_i = add_timing_slider(frame, tkvars.logic_pulse_current[i], i * 2 + 1, 2)

        slider_t = add_timing_slider(
            frame, tkvars.logic_pulse_threshold[i], i * 2 + 2, 2
        )
        sl_lo_pu_cur.append(slider_i)
        sl_lo_pu_th.append(slider_t)

    timing_sliders["Channel Pulse Current"] = sl_lo_pu_cur
    timing_sliders["Channel Pulse Threshold"] = sl_lo_pu_th

    return timing_sliders



main_window = tk.Tk()
main_window.title("ELB_ARDU_DISC Control")

tvars = VarManager(ead=ead)

notebook = ttk.Notebook(main_window)

tab_threshold = ttk.Frame(notebook)
tab_channel_timing = ttk.Frame(notebook)
tab_logic_timing = ttk.Frame(notebook)


notebook.add(tab_threshold, text="Thresholds")
notebook.add(tab_channel_timing, text="Channel Timing")
notebook.add(tab_logic_timing, text="Logic Timing")

notebook.pack(expand=True, fill="both")


threshold_sliders = add_threshold_sliders(
    frame=tab_threshold, threshold_vars=tvars.threshold
)
hysteresis_sliders = add_hysteresis_sliders(
    frame=tab_threshold, tkvars=tvars.hysteresis, col0=4
)


channel_timing_sliders = add_ch_timing_sliders(frame=tab_channel_timing, tkvars=tvars)
logic_timing_sliders = add_lo_timing_sliders(frame=tab_logic_timing, tkvars=tvars)
ead.testpulser_control.set_pulser(on=True)

tvars.set_defaults()
main_window.mainloop()
