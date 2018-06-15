import unittest
import operators


class BaseSequence(unittest.TestCase):

    def setUp(self):
        self.manager = operators.Manager()
        self.dispatcher = operators.Dispatcher()

    def test_credit(self):
        pre_balance = self.manager.balance
        money = 10000000000
        self.manager.credit(money)
        post_balance = self.manager.balance
        self.assertEqual(pre_balance+money, post_balance)

    def test_transactions(self):
        pre_count_transactions = len(self.manager.transactions["data"])
        self.manager.credit(100)
        post_count_transactions = len(self.manager.transactions["data"])
        self.assertTrue(pre_count_transactions + 1 == post_count_transactions)

    def test_notifications(self):
        pre_count_notifications = len(self.manager.notifications["data"])
        self.dispatcher.flight(all_passengers=1, all_cargo=1)
        post_count_notifications = len(self.manager.notifications["data"])
        self.assertTrue(pre_count_notifications < post_count_notifications)

    def test_flights(self):
        pre_balance = self.manager.balance
        pre_flights = self.manager.airline_stat["data"][0]["flights"]
        self.dispatcher.flight(all_passengers=999, all_cargo=555)
        post_balance = self.manager.balance
        post_flights = self.manager.airline_stat["data"][0]["flights"]
        self.assertTrue(pre_balance < post_balance and pre_flights < post_flights)

    def test_reset(self):
        self.manager.reset()
        balance = self.manager.balance
        flights_count = self.manager.airline_stat["data"][0]["flights"]
        transactions_count = len(self.manager.transactions["data"])
        notification_count = len(self.manager.notifications["data"])
        self.assertTrue(int(balance)==flights_count==transactions_count==notification_count==0)

    def tearDown(self):
        pass
