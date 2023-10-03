import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim


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
    "RQ1": [i for i in range(1, 25)],
    "RQ2": [i for i in range(1, 25)],
    "RB1": [i for i in range(1, 13)],
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
