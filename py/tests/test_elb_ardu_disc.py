import unittest
from unittest.mock import patch

from elb_ardu_disc import DacMCP48FVB14, DacMCP48FVB24
from elb_ardu_disc import DacAddrV, DacVrefOptions
from elb_ardu_disc import SpiIO


class GenericDacTest:
    def test_set_channel_invalid(self):
        with self.assertRaises(ValueError):
            self.dac.set_channel(-1, 0)
        with self.assertRaises(ValueError):
            self.dac.set_channel(4, 0)

    def test_set_invalid_value(self):
        invalid_values = [-1, 2**self.dac.resolution, 100000]
        for value in invalid_values:
            with self.assertRaises(ValueError):
                self.dac.set_channel(0, value)

    @patch("elb_ardu_disc.DacMCP48FXBX4._execute_spi")
    def test_set_all_refs_identical(self, mock_execute_spi):
        mock_execute_spi.return_value = [1, 0xFF, 0xFF]
        self.dac.set_all_refs_same(DacVrefOptions.ExtBuffered)

        expected_cmd_byte = 0b01000000
        expected_data_word = 0xFF

        mock_execute_spi.assert_called_with(
            command_byte=expected_cmd_byte, data_word=expected_data_word
        )

    @patch("elb_ardu_disc.DacMCP48FXBX4._execute_spi")
    def test_set_channel_calls_execute_spi_correctly(self, mock_execute_spi):

        for channel in range(self.dac.channels):
            for setting in range(2**self.dac.resolution):

                mock_execute_spi.return_value = [1, 0xFF, 0xFF]

                self.dac.set_channel(channel, setting)

                expected_cmd_byte = DacAddrV.CmdWrite.value
                expected_cmd_byte |= DacAddrV.Channel.value[channel]

                expected_data_word = setting

                mock_execute_spi.assert_called_with(
                    command_byte=expected_cmd_byte, data_word=expected_data_word
                )


class TestDacMCP48FVB14(unittest.TestCase, GenericDacTest):

    def setUp(self):
        self.spi = SpiIO()
        self.dac = DacMCP48FVB14(spi=self.spi)

    def test_channels_and_resolution(self):
        self.assertEqual(self.dac.channels, 4)
        self.assertEqual(self.dac.resolution, 10)


class TestDacMCP48FVB24(unittest.TestCase, GenericDacTest):

    def setUp(self):
        self.spi = SpiIO()
        self.dac = DacMCP48FVB24(spi=self.spi)

    def test_channels_and_resolution(self):
        self.assertEqual(self.dac.channels, 4)
        self.assertEqual(self.dac.resolution, 12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
