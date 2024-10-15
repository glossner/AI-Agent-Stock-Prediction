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




if __name__ == "__main__":
    root = tk.Tk()
    gui = StockAlertGUI(root)
    root.mainloop()
