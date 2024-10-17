# src/UI/alert_system.py
import time
from yahooquery import Ticker
from src.Agents.Alert_agent.alert_agent import AlertAgent
from src.Helpers.notification import send_email_alert, send_sms_alert

class StockAlertSystem:
    def __init__(self, stock, threshold, notify_email=False, notify_sms=False):
        self.stock = stock
        self.threshold = threshold
        self.notify_email = notify_email
        self.notify_sms = notify_sms
        self.alert_agent = AlertAgent()

    def fetch_stock_data(self):
        ticker = Ticker(self.stock)
        return ticker.history(period='1d', interval='1m')

    def monitor_stock(self):
        previous_close = None
        while True:
            stock_data = self.fetch_stock_data()
            latest_price = stock_data['close'].iloc[-1]

            if previous_close:
                change = ((latest_price - previous_close) / previous_close) * 100
                if abs(change) >= self.threshold:
                    analysis = self.alert_agent.analyze_stock_changes(stock_data.tail(5).to_dict())
                    subject = f"Stock Alert for {self.stock}"
                    message = f"Price change of {self.stock}: {change:.2f}%\n{analysis}"
                    
                    if self.notify_email:
                        send_email_alert(subject, message, 'example@gmail.com')
                    
                    if self.notify_sms:
                        send_sms_alert(message, '+11111111111')
                    
                    print(f"Alert sent for {self.stock}")

            previous_close = latest_price
            time.sleep(60)


if __name__ == "__main__":
    stock = input("Enter the stock ticker: ")
    threshold = float(input("Enter the percentage change threshold for alerts: "))
    notify_email = input("Do you want email alerts? (yes/no): ").lower() == 'yes'
    notify_sms = input("Do you want SMS alerts? (yes/no): ").lower() == 'yes'
    alert_system = StockAlertSystem(stock, threshold, notify_email, notify_sms)

    
    alert_system = StockAlertSystem(stock, threshold, notify_email, notify_sms)
    alert_system.monitor_stock()
