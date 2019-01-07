import unittest
import sys, os
from chaosdb.influx import configure_control, before_activity_control, after_activity_control

class TestControl( unittest.TestCase ):

    @classmethod
    def setUpClass(cls):
        os.system('./scripts/influxd.sh')
#   some initialization...


    def test_before_activity_control(self):

        self.assertEqual(configure_control({
            "influx_host": "localhost",
            "influx_port": 8086,
            "influx_http_endpoint": "/write",
            "influx_database": "chaostoolkit"
        }, {} ), 1)

        context =  {
        "type": "action",
        "name": "test action",
        "provider": {
          "type": "python",
          "module": "foo",
          "func": "bar"
          }
        }
        self.assertEqual( before_activity_control(context, {}), True )


    def test_after_activity_control(self):

        self.assertEqual(configure_control({
            "influx_host": "localhost",
            "influx_port": 8086,
            "influx_http_endpoint": "/write",
            "influx_database": "chaostoolkit"
        }, {} ), 1)

        context =  {
        "type": "action",
        "name": "test action",
        "provider": {
          "type": "python",
          "module": "foo",
          "func": "bar"
          }
        }
        self.assertEqual( after_activity_control(context, {}), True )


if __name__ == "__main__":
    unittest.main()
