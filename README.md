# ELB_ARDU_DISC4

This repository contains the **ELB_ARDU_DISC4 system**, including both the **Python library** and the **Arduino firmware** required to control the module.

## Repository Structure

```ELB_ARDU_DISC4/
├── py/ # Python library to control the module
├── ardu/ # Arduino firmware for the module
└── README.md # This file
```

### `py/` — Python Library

The Python library allows controlling the ELB_ARDU_DISC4 module via USB/serial.  
It supports:

- Setting thresholds, hysteresis, delays, and pulse width
- Interactive GUI example
- Minimalistic examples for default configuration

See [`py/README.md`](py/README.md) for detailed installation instructions, usage examples, and license/attribution information.

### `ardu/` — Arduino Firmware

The Arduino firmware runs on an **Arduino Uno** and implements an SCPI-like serial interface to control the ELB_ARDU_DISC4.  

It supports commands such as:

- `*IDN?` — Get instrument identification
- `SYSTem:SPI:SENd <index>, <command>, <payload>` — Send SPI data
- `SYSTem:PULser:ENAble` / `DISable` — Control integrated test pulser

See [`ardu/README.md`](ardu/README.md) for detailed firmware instructions, dependencies, and license/attribution information.

## Quick Start

1. Clone the repository:

git clone https://github.com/ELB-Elektroniklaboratorien-Bonn/ELB_ARDU_DISC4
cd ELB_ARDU_DISC4

2. Follow the instructions in the subproject you want to use:

Python library: py/README.md

Arduino firmware: ardu/README.md

## License

This repository contains both the Python library and Arduino firmware.

Python library: MIT License (see py/LICENSE)

Arduino firmware: MIT License (see ardu/LICENSE)

Third-party libraries are credited in each subproject's README.

## Notes

It is recommended to use a Python virtual environment when installing the Python library.

The Arduino firmware depends on open-source Arduino libraries. See ardu/README.md for details.
The python code depends on open-source libraries. See py/README.md for details.
