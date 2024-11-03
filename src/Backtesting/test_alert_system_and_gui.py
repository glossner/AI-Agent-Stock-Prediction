import unittest
from unittest.mock import patch, MagicMock
from src.Agents.Alert_agent.alert_agent import AlertAgent
from src.Helpers.notification import send_email_alert, send_sms_alert, send_sms_alert_curl
from src.UI.stock_alert_system import StockAlertSystem
from src.UI.stock_alert_gui import StockAlertGUI
import tkinter as tk
import os


# Unit tests for the AlertAgent class
class TestAlertAgent(unittest.TestCase):
    def setUp(self):
        self.alert_agent = AlertAgent()
        print(f"Starting {self._testMethodName} in {self.__class__.__name__}")

    def test_analyze_stock_changes(self):
        # Test if analyze_stock_changes correctly processes stock data
        stock_data = {'close': [100, 105, 102, 108, 110]}
        response = self.alert_agent.analyze_stock_changes(stock_data)
        self.assertIsNotNone(response)
        self.assertIn("Analyze", response)

    def tearDown(self):
        print(f"Completed {self._testMethodName} in {self.__class__.__name__}")


# Unit tests for the notification functions
class TestNotification(unittest.TestCase):

    def setUp(self):
        print(f"Starting {self._testMethodName} in {self.__class__.__name__}")

    @patch("src.Helpers.notification.smtplib.SMTP")
    def test_send_email_alert(self, mock_smtp):
        subject = "Test Subject"
        message = "Test Message"
        recipient_email = "example@gmail.com"
        send_email_alert(subject, message, recipient_email)
        self.assertTrue(mock_smtp.called)

    @patch("src.Helpers.notification.Client")
    def test_send_sms_alert(self, mock_twilio_client):
        message = "Test SMS Message"
        recipient_phone = "+18777804236"
        send_sms_alert(message, recipient_phone)
        self.assertTrue(mock_twilio_client.called)

    @patch("src.Helpers.notification.os.system")
    def test_send_sms_alert_curl(self, mock_os_system):
        message = "Test SMS via curl"
        recipient_phone = "+18777804236"
        send_sms_alert_curl(message, recipient_phone)
        expected_command = f"curl 'https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json' -X POST --data-urlencode 'To={recipient_phone}' --data-urlencode 'From={os.getenv('TWILIO_PHONE_NUMBER')}' --data-urlencode 'Body={message}' -u {os.getenv('TWILIO_ACCOUNT_SID')}:{os.getenv('TWILIO_AUTH_TOKEN')}"
        mock_os_system.assert_called_once_with(expected_command)

    def tearDown(self):
        print(f"Completed {self._testMethodName} in {self.__class__.__name__}")


# Unit tests for the StockAlertGUI class
class TestStockAlertGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.gui = StockAlertGUI(self.root)
        print(f"Starting {self._testMethodName} in {self.__class__.__name__}")

    def test_initial_setup(self):
        self.assertEqual(self.gui.status_label.cget("text"), "Status: Idle")

    def test_start_monitoring_button_disabled(self):
        self.gui.start_monitoring()
        self.assertEqual(self.gui.button_start['state'], tk.DISABLED)
        self.assertEqual(self.gui.button_stop['state'], tk.NORMAL)

    @patch("tkinter.messagebox.showwarning")
    def test_start_monitoring_missing_input(self, mock_showwarning):
        self.gui.entry_stock.delete(0, tk.END)
        self.gui.entry_threshold.delete(0, tk.END)
        self.gui.start_monitoring()
        mock_showwarning.assert_called_once()

    def test_stop_monitoring(self):
        self.gui.start_monitoring()
        self.gui.stop_monitoring()
        self.assertEqual(self.gui.status_label.cget("text"), "Status: Stopped")
        self.assertEqual(self.gui.button_start['state'], tk.NORMAL)
        self.assertEqual(self.gui.button_stop['state'], tk.DISABLED)

    def test_email_alert_enabled(self):
        self.gui.var_email.set(True)
        self.assertTrue(self.gui.var_email.get())

    def test_sms_alert_enabled(self):
        self.gui.var_sms.set(True)
        self.assertTrue(self.gui.var_sms.get())


    def test_stock_input_case_insensitivity(self):
        self.gui.entry_stock.insert(0, "aapl")
        self.gui.start_monitoring()
        self.assertEqual(self.gui.entry_stock.get(), "AAPL")

    @patch("tkinter.messagebox.showwarning")
    def test_stock_input_special_characters(self, mock_showwarning):
        self.gui.entry_stock.insert(0, "AAPL$%^")
        self.gui.start_monitoring()
        mock_showwarning.assert_called_once_with("Input Error", "Please enter a valid stock ticker.")

    def tearDown(self):
        print(f"Completed {self._testMethodName} in {self.__class__.__name__}")
        self.root.destroy()


if __name__ == "__main__":
    unittest.main()
