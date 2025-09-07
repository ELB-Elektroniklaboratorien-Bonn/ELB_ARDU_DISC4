from typing import List
from enum import Enum

from .spi import SpiIO

"""
DACs used:
10 bit: MCP48FVB14T-20E/ST
12 bit: MCP48FVB24-20E/ST
"""
LOGIC_ANALYZER_DEV_MODE = True  # if true, don't check if the answer of the dac was correct. this allows development with logic analyzer and without ardudisc


class DacAddrV(Enum):
    Channel: List[int] = [0x00, 0x08, 0x10, 0x18]
    Vref: int = 0x40
    PowerDown: int = 0x48
    GainStatus: int = 0x50
    CmdWrite: int = 0x00
    CmdRead: int = 0x06


class DacVrefOptions(Enum):
    ExtBuffered: int = 0b11
    ExtUnbuffered: int = 0b10
    Internal_1V22: int = 0b01
    VDD: int = 0b00


def _spi_io_error(spi_answer: List[int]):
    if spi_answer[0] == 1 and spi_answer[1] == 0xFF and spi_answer[2] == 0xFF:
        return False
    else:
        return True


class DacMCP48FXBX4:
    def __init__(self, spi: SpiIO, cs_index: int = -1):
        self.spi = spi
        self.cs_index = cs_index
        self.channels = -1
        self.resolution = -1

    def set_refs(self, ref_settings: List[DacVrefOptions]):
        if len(ref_settings) != 4:
            raise ValueError(
                f"set_refs: wrong number reference selection settings given {len(ref_settings)}"
            )

        data_word: int = 0
        for i, setting in enumerate(ref_settings):
            data_word |= (setting.value) << (i * 2)
        cmd_byte = DacAddrV.CmdWrite.value | DacAddrV.Vref.value

        self._spi_w(command_byte=cmd_byte, data_word=data_word)

    def set_all_refs_same(self, ref_setting: DacVrefOptions):
        ref_settings = [ref_setting] * self.channels
        self.set_refs(ref_settings)

    def set_channel(self, channel: int, setting: int):
        if channel < 0 or channel >= self.channels:
            raise ValueError(f"Invalid channel {channel}")
        if setting < 0 or setting >= 2**self.resolution:
            raise ValueError(f"Invalid dac value {setting}")

        cmd_byte: bytes = DacAddrV.CmdWrite.value
        cmd_byte |= DacAddrV.Channel.value[channel]
        self._spi_w(command_byte=cmd_byte, data_word=setting)

    def get_channel(self):
        raise NotImplementedError("This method is not implemented yet")

    def get_refs(self):
        raise NotImplementedError("This method is not implemented yet")

    def set_power_down(self):
        raise NotImplementedError("This method is not implemented yet")

    def _execute_spi(self, command_byte: int, data_word: int):
        bytes_to_send: List[int] = [command_byte]
        bytes_to_send.append((data_word & 0xFF00) >> 8)
        bytes_to_send.append((data_word & 0xFF))
        answer: List[int] = self.spi.do_io_24(bytes_to_send, self.cs_index)
        return answer

    def _spi_w(self, command_byte: int, data_word: int):
        spi_answer = self._execute_spi(command_byte=command_byte, data_word=data_word)
        if not LOGIC_ANALYZER_DEV_MODE:
            if _spi_io_error(spi_answer=spi_answer):
                raise IOError(f"SPI Communication Error. Answer was {spi_answer}")


class DacMCP48FVB14(DacMCP48FXBX4):
    def __init__(self, spi, cs_index: int = -1):
        super().__init__(spi, cs_index)
        self.channels = 4
        self.resolution = 10


class DacMCP48FVB24(DacMCP48FXBX4):
    def __init__(self, spi, cs_index: int = -1):
        super().__init__(spi, cs_index)
        self.channels = 4
        self.resolution = 12
