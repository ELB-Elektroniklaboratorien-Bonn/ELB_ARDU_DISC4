## Description

Arduino Uno Firmware to control the ELB_ARDU_DISC4.

It implements an SCPI-like interface on the serial port.

Commands:
  *IDN?
    Gets the instrument's identification string
  
  SYSTem:SPI:SENd <index>, <command>, <payload>
    Send 24 bit of data via SPI.
    Use chip select <index>, 8 bit <command>, and 16 bit <payload>.
    Answer:
    SPIRESP,<index>,<command>,<payload>,<data_read_from_spi>

  SYSTem:PULser:ENAble
    Enble the integrated testpulser.

  SYSTem:PULser:DISable
    Disable the integrated testpulser.


## License and Attributions

This firmware is released under the MIT License (see LICENSE file).

This firmware depends on the following open-source libraries:
- [Vrekrer_SCPI_Parser](https://github.com/Vrekrer/Vrekrer_scpi_parser) (MIT License, Victor Pérez)
- [TimerOne](https://github.com/PaulStoffregen/TimerOne) (licensed under the Creative Commons Attribution 3.0 United States License, Paul Stoffregen)
- [ArduinoLog](https://github.com/thijse/Arduino-Log) (MIT License, Jeroen S. C.)  

This firmware is built on the Arduino framework (https://www.arduino.cc/), which is open-source software.
