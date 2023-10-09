import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, parameterized_list

from parameterized import parameterized
import random

DEVICE_PREFIX = "RKNMNTR_01"


IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("RKNMNTR"),
        "macros": {},
        "emulator": "Rknmntr",
    },
]


TEST_MODES = [TestModes.RECSIM]

MAGNET_TAP_PAIRS = {
    "RQ1": [f"TAP{i:02d}" for i in range(1, 25)],
    "RQ2": [f"TAP{i:02d}" for i in range(1, 25)],
    "RB1": [f"TAP{i:02d}" for i in range(1, 13)],
}

class RknmntrTests(unittest.TestCase):
    """
    Tests for the Rknmntr IOC.
    """
    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Rknmntr", DEVICE_PREFIX)
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX)

    def _get_pv_for_magnet_tap(self, magnet, tap):
        return f"{magnet}:TAP{tap:02d}:"

    
    def test_GIVEN_ioc_running_THEN_all_pvs_exist(self):
        for magnet in MAGNET_TAP_PAIRS:
            for tap in MAGNET_TAP_PAIRS[magnet]:
                pv_magnet_tap = self._get_pv_for_magnet_tap(magnet, tap)
                self.ca.assert_that_pv_exists(f"{pv_magnet_tap}VOLT:RAW")
                self.ca.assert_that_pv_exists(f"{pv_magnet_tap}VOLT:ADC")
                self.ca.assert_that_pv_exists(f"{pv_magnet_tap}VOLT")
                self.ca.assert_that_pv_exists(f"{pv_magnet_tap}RES")
                self.ca.assert_that_pv_exists(f"{pv_magnet_tap}TEMP")

    @parameterized.expand(parameterized_list([
        # Magnet, gain, volt_raw
        ("RQ1", 10),
        # ("RQ2", 10),
        # ("RB1", 10),
    ]))
    def test_WHEN_voltage_changes_THEN_values_recalculated(self, _, magnet, volt_raw):
        self.ca.prefix = self.ca.host_prefix

        pv_magnet_curr = f"CS:SB:{magnet}_CURR"
        self.ca.set_pv_value(pv_magnet_curr, 1)

        for tap in MAGNET_TAP_PAIRS[magnet]:
            volt_raw = random.randrange(10, 100)

            # WHEN
            # Simulate a change in tap voltage
            pv = f"SCHNDR_01:{magnet}:TEMPMON:{tap}"
            self.ca.set_pv_value(pv, volt_raw)

            pv_magnet_tap = f"RKNMNTR_01:{magnet}:{tap}:"
            pv_raw = f"{pv_magnet_tap}VOLT:RAW"
            pv_volt_adc = f"{pv_magnet_tap}VOLT:ADC"
            pv_volt = f"{pv_magnet_tap}VOLT"
            pv_res = f"{pv_magnet_tap}RES"
            pv_temp = f"{pv_magnet_tap}TEMP"

            gain = self.ca.get_pv_value(f"{pv_volt}.B") # Retrieve gain for magnet from calc record B field (loaded in there from macro)
            curr = self.ca.get_pv_value(pv_magnet_curr)
            initial_res = self.ca.get_pv_value(f"{pv_temp}.B") # Retrieve initial resistance for magnet from calc record B field (loaded in there from macro)

            expected_volt_adc = volt_raw / ((2**12)-1)*10
            expected_volt = expected_volt_adc / gain
            expected_res = expected_volt / curr * 1000
            expected_temp = (((expected_res / initial_res) - 1) / 0.004041) + 23

            # ASSERT
            self.ca.assert_that_pv_is(pv_raw, volt_raw)
            self.ca.assert_that_pv_is(pv_volt_adc, expected_volt_adc)
            self.ca.assert_that_pv_is(pv_volt, expected_volt)
            self.ca.assert_that_pv_is(pv_res, expected_res)
            self.ca.assert_that_pv_is(pv_temp, expected_temp)
