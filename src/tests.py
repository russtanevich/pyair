"""Unit tests for PyAir."""
import os
import tempfile
import unittest
from unittest.mock import patch

if __package__:
    from . import cli, dbmake, operators, settings, utils, webui
    from .dbquery import DB
else:
    import cli
    import dbmake
    import operators
    import settings
    import utils
    import webui
    from dbquery import DB


class IsolatedDBTestCase(unittest.TestCase):
    """Base test case using a temporary SQLite database."""

    @classmethod
    def setUpClass(cls):
        cls._orig_db_file = DB.db_file
        cls._tmpdir = tempfile.TemporaryDirectory()
        DB.db_file = os.path.join(cls._tmpdir.name, "test_airbase.db")
        dbmake.main()
        cls.manager = operators.Manager()
        cls.dispatcher = operators.Dispatcher()

    @classmethod
    def tearDownClass(cls):
        DB.db_file = cls._orig_db_file
        cls._tmpdir.cleanup()

    def tearDown(self):
        self.manager.reset()


class BaseSequence(IsolatedDBTestCase):
    """Core airline operations tests."""

    def test_reset(self):
        self.manager.reset()
        balance = self.manager.balance
        flights_count = self.manager.airline_stat["data"][0]["flights"]
        transactions_count = len(self.manager.transactions["data"])
        notification_count = len(self.manager.notifications["data"])
        self.assertTrue(
            int(balance)
            == flights_count
            == transactions_count
            == notification_count
            == 0
        )

    def test_credit(self):
        pre_balance = self.manager.balance
        money = 10000000000
        self.manager.credit(money)
        post_balance = self.manager.balance
        self.assertEqual(pre_balance + money, post_balance)

    def test_credit_rejects_non_positive(self):
        with self.assertRaises(ValueError):
            self.manager.credit(0)
        with self.assertRaises(ValueError):
            self.manager.credit(-500)

    def test_transactions(self):
        pre_count_transactions = len(self.manager.transactions["data"])
        self.manager.credit(100)
        post_count_transactions = len(self.manager.transactions["data"])
        self.assertEqual(pre_count_transactions + 1, post_count_transactions)

    def test_notifications(self):
        pre_count_notifications = len(self.manager.notifications["data"])
        self.dispatcher.flight(all_passengers=1, all_cargo=1)
        post_count_notifications = len(self.manager.notifications["data"])
        self.assertLess(pre_count_notifications, post_count_notifications)

    def test_flights(self):
        pre_balance = self.manager.balance
        pre_flights = self.manager.airline_stat["data"][0]["flights"]
        self.dispatcher.flight(all_passengers=999, all_cargo=555)
        post_balance = self.manager.balance
        post_flights = self.manager.airline_stat["data"][0]["flights"]
        self.assertTrue(pre_balance < post_balance and pre_flights < post_flights)

    def test_buy_and_sell_plane(self):
        with self.assertRaises(ValueError):
            self.manager.buy_plane(1)

        self.manager.credit(500_000_000)
        pre_count = len(self.manager.planes["data"])
        self.manager.buy_plane(3)
        post_count = len(self.manager.planes["data"])
        self.assertEqual(pre_count + 1, post_count)

        owned_id = self.manager.planes["data"][-1]["id"]
        self.manager.sell_plane(owned_id)
        self.assertEqual(pre_count, len(self.manager.planes["data"]))

    def test_sell_missing_plane_raises(self):
        with self.assertRaises(ValueError):
            self.manager.sell_plane(999999)

    def test_flight_without_cargo_planes_does_not_crash(self):
        for plane in self.manager.cargo_planes["data"]:
            self.manager.sell_plane(plane["id"])
        self.dispatcher.flight(all_passengers=10, all_cargo=5)
        notes = [n["text"] for n in self.manager.notifications["data"]]
        self.assertTrue(any("NOT SERVED: 5.0 tons cargo" in n for n in notes))


class CLITests(IsolatedDBTestCase):
    """CLI and utility tests."""

    def test_validate_choice(self):
        self.assertTrue(cli.validate_choice("0", settings.MANAGER_CLI))
        self.assertFalse(cli.validate_choice("999", settings.MANAGER_CLI))
        self.assertFalse(cli.validate_choice("-1", settings.MANAGER_CLI))
        self.assertFalse(cli.validate_choice("abc", settings.MANAGER_CLI))

    def test_draw_table_and_choices(self):
        choices_text = utils.draw_choices(settings.DISPATCHER_CLI)
        self.assertIn("New FLIGHT", choices_text)
        table = utils.draw_table(self.manager.market_planes)
        self.assertIn("Airbus A330-300", str(table))

    def test_sort_result_cancel_vs_empty(self):
        # Index 9 is "Get CREDIT" in MANAGER_CLI
        with patch("builtins.input", return_value="n"):
            self.assertEqual(
                utils.sort_result(self.manager, settings.MANAGER_CLI, 9),
                "CANCELED",
            )
        with patch("builtins.input", return_value=""):
            with self.assertRaises(ValueError):
                utils.sort_result(self.manager, settings.MANAGER_CLI, 9)

    def test_date_filter(self):
        self.assertEqual(utils.date_filter(None), "")
        formatted = utils.date_filter(0)
        self.assertRegex(formatted, r"\d{4}-\d{2}-\d{2}  \d{2}:\d{2}")


class WebUITests(IsolatedDBTestCase):
    """Flask Web UI tests."""

    def setUp(self):
        webui.app.config["TESTING"] = True
        self.client = webui.app.test_client()

    def test_home_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"PyAIR Company", resp.data)

    def test_credit_and_flight_and_reset(self):
        resp = self.client.post(
            "/credit", data={"credit": "200000000"}, follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(self.manager.balance, 200000000)

        resp = self.client.post(
            "/flight",
            data={"passengers": "50", "cargo": "10.5"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get("/reset", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.manager.balance, 0.0)

    def test_buy_insufficient_funds_redirects_with_flash(self):
        resp = self.client.get("/buy_2", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"No money - no honey", resp.data)

    def test_invalid_credit_and_flight_do_not_500(self):
        resp = self.client.post(
            "/credit", data={"credit": "-10"}, follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Credit error", resp.data)

        resp = self.client.post(
            "/flight",
            data={"passengers": "bad", "cargo": "1"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Flight error", resp.data)


if __name__ == "__main__":
    unittest.main()
