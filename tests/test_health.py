import os
import sys
import threading
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, ROOT)
os.environ["STATUS_FAIL"] = "0"
os.environ["PORT"] = "18080"

import main as app  # noqa: E402


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = app.HTTPServer(("127.0.0.1", 18080), app.Handler)
        t = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        t.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def test_health_ok(self):
        with urlopen("http://127.0.0.1:18080/health") as r:
            self.assertEqual(r.status, 200)
            self.assertIn(b"ok", r.read())

    def test_metrics(self):
        with urlopen("http://127.0.0.1:18080/metrics") as r:
            body = r.read().decode()
            self.assertIn("northfield_health", body)
            self.assertIn("northfield_up 1", body)

    def test_health_fail_mode(self):
        app.FAIL = True
        try:
            with self.assertRaises(HTTPError) as ctx:
                urlopen("http://127.0.0.1:18080/health")
            self.assertEqual(ctx.exception.code, 503)
        finally:
            app.FAIL = False


if __name__ == "__main__":
    unittest.main()
