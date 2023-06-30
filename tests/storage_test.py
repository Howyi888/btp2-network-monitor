from datetime import datetime
import unittest
from btp2_monitor.storage import Storage, ConnectionState

class TestStorageTest(unittest.TestCase):
    def test_connection_state(self):
        s = Storage()
        cs = s.get_connection_state('a', 'b')
        self.assertIsNone(cs)
        cs2: ConnectionState = {
            'id': None,
            'tx_state': 'unknown',
            'tx_seq': None,
            'tx_ts': None,
            'tx_height': None,
            'rx_state': 'unknown',
            'rx_seq': None,
            'rx_ts': None,
            'rx_height': None,
        }

        s.set_connection_state('a', 'b', cs2)
        cs = s.get_connection_state('a', 'b')
        self.assertEqual(cs2, cs)

        cs3 = cs2.copy()
        cs3['tx_state'] = 'online'

        s.set_connection_state('a', 'b', cs3)
        cs = s.get_connection_state('a', 'b')
        self.assertEqual(cs3, cs)
        self.assertEqual(cs2['id'], cs3['id'])

    def test_tx_history(self):
        s = Storage()
        cs: ConnectionState = {
            'id': None,
            'tx_state': 'unknown',
            'tx_seq': None,
            'tx_ts': None,
            'tx_height': None,
            'rx_state': 'unknown',
            'rx_seq': None,
            'rx_ts': None,
            'rx_height': None,
        }
        s.set_connection_state('a', 'b', cs)

        records = s.get_tx_records(cs['id'])
        self.assertEquals(0, len(list(records)))

        now = datetime.now()
        rec1 = s.add_tx_record(cs['id'], 3, now)
        records = s.get_tx_records(cs['id'])
        self.assertListEqual([rec1], list(records))

        now = datetime.now()
        rec2 = s.add_tx_record(cs['id'], 4, now)
        records = s.get_tx_records(cs['id'])
        self.assertListEqual([rec1, rec2], list(records))

        s.delete_tx_record(rec1.sn)
        s.delete_tx_record(rec2.sn)
        records = s.get_tx_records(cs['id'])
        self.assertEquals(0, len(list(records)))

    def test_batch(self):
        s = Storage()
        cs: ConnectionState = {
            'id': None,
            'tx_state': 'unknown',
            'tx_seq': None,
            'tx_ts': None,
            'tx_height': None,
            'rx_state': 'unknown',
            'rx_seq': None,
            'rx_ts': None,
            'rx_height': None,
        }

        def do_update():
            s.set_connection_state('a', 'b', cs)
            now = datetime.now()
            s.add_tx_record(cs['id'], 3, now)
        
        def raise_after_update():
            do_update()
            raise Exception()

        try:
            s.do_batch(raise_after_update)
            self.fail('NoException')
        except:
            pass
        cs2 = s.get_connection_state('a', 'b')
        self.assertIsNone(cs2)

        try:
            s.do_batch(do_update)
        except:
            self.fail('Exception')
        cs2 = s.get_connection_state('a', 'b')
        self.assertEqual(cs, cs2)
