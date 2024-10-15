import tkinter as tk
from tkinter import messagebox
import threading
from src.UI.stock_alert_system import StockAlertSystem

class StockAlertGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Alert System")

        # Stock ticker input
        self.label_stock = tk.Label(root, text="Enter Stock Ticker:")
        self.label_stock.grid(row=0, column=0, padx=10, pady=10)
        self.entry_stock = tk.Entry(root)
        self.entry_stock.grid(row=0, column=1, padx=10, pady=10)

        # Threshold input
        self.label_threshold = tk.Label(root, text="Enter Threshold (%):")
        self.label_threshold.grid(row=1, column=0, padx=10, pady=10)
        self.entry_threshold = tk.Entry(root)
        self.entry_threshold.grid(row=1, column=1, padx=10, pady=10)

        # Email/SMS alert options
        self.var_email = tk.BooleanVar()
        self.checkbox_email = tk.Checkbutton(root, text="Email Alert", variable=self.var_email)
        self.checkbox_email.grid(row=2, column=0, padx=10, pady=10)

        self.var_sms = tk.BooleanVar()
        self.checkbox_sms = tk.Checkbutton(root, text="SMS Alert", variable=self.var_sms)
        self.checkbox_sms.grid(row=2, column=1, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Start button
        self.button_start = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.button_start.grid(row=4, column=0, padx=10, pady=10)

        # Stop button
        self.button_stop = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.button_stop.grid(row=4, column=1, padx=10, pady=10)

        self.monitoring = False
        self.alert_thread = None

    def start_monitoring(self):
        stock = self.entry_stock.get().upper()
        threshold = self.entry_threshold.get()
        notify_email = self.var_email.get()
        notify_sms = self.var_sms.get()

        if not stock or not threshold:
            messagebox.showwarning("Input Error", "Please enter stock ticker and threshold.")
            return

        try:
            threshold = float(threshold)
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for the threshold.")
            return

        self.status_label.config(text="Status: Monitoring...")
        self.monitoring = True
        self.button_start.config(state=tk.DISABLED)
        self.button_stop.config(state=tk.NORMAL)

        # Run the alert system in a separate thread
        self.alert_thread = threading.Thread(target=self.run_alert_system, args=(stock, threshold, notify_email, notify_sms))
        self.alert_thread.start()


    def stop_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="Status: Stopped")
        self.button_start.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.DISABLED)

    def run_alert_system(self, stock, threshold, notify_email, notify_sms):
        alert_system = StockAlertSystem(stock, threshold, notify_email, notify_sms)

        while self.monitoring:
            alert_system.monitor_stock()
            self.status_label.config(text=f"Status: Monitoring {stock} for changes >= {threshold}%")
        
        self.status_label.config(text="Status: Stopped")

if __name__ == "__main__":
    root = tk.Tk()
    gui = StockAlertGUI(root)
    root.mainloop()
