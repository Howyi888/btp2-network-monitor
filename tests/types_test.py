import unittest
from btp2_monitor.types import NetworkID

class TestNetworkID(unittest.TestCase):
    def test_class(self):
        id = NetworkID('abc-def')
        self.assertTrue(isinstance(id, NetworkID))
        self.assertEqual(id.address,'btp://abc/def')
        id2 = NetworkID.from_address(id.address)
        self.assertEqual(id, id2)
