# snHC1kJKDB4eiTwOmF67lHtnw8FC4VB0

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from kiteconnect import KiteConnect
from PIL import Image, ImageTk
import threading
import time
import requests
import os

class StockWishlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Wishlist")
        self.root.geometry("800x600")

        self.credentials_list = self.load_credentials_list()  # Load credentials list from file
        self.buy_kite_instances = []
        self.sell_kite_instances = []

        # Initialize KiteConnect instances for all credentials
        for creds in self.credentials_list:
            buy_kite = KiteConnect(api_key=creds["api_key"])
            sell_kite = KiteConnect(api_key=creds["api_key"])
            buy_kite.set_access_token(creds["access_token"])
            sell_kite.set_access_token(creds["access_token"])
            self.buy_kite_instances.append(buy_kite)
            self.sell_kite_instances.append(sell_kite)


        # GUI components
        self.logo_photo = None
        self.search_entry = None
        self.suggestion_listbox = None
        self.notebook = None
        self.stock_trees = []
        self.buy_sell_frame = None
        self.quantity_label = None
        self.quantity_entry = None
        self.remove_button = None
        self.add_account_button = None  # Button to add account

        self.result_label = None
        
        # Initialize stock prices
        self.stock_prices = {}
        self.subscribed_instruments = [[] for _ in range(10)]  # List of lists for 10 wishlists

        # Create a separate thread for real-time updates
        self.update_thread = threading.Thread(target=self.update_stock_prices_thread, daemon=True)
        self.update_thread.start()

        # Fetch all instruments from Kite API
        self.all_instruments = self.get_all_instruments()

        self.create_widgets()
        self.update_suggestions()
        
        # Load subscribed instruments from JSON files
        self.load_subscribed_instruments()

        

    def create_widgets(self):
        self.create_logo_and_text()
        self.create_wishlist_tabs()
        self.create_search_bar()
        self.create_buy_sell_frame()
        self.create_result_label()
        self.create_remove_button()
        # self.create_add_account_button()  # Create Add Account button
        self.create_footer()


# New Account Entry Fields
        api_key_frame = tk.Frame(self.root)
        api_key_frame.pack(pady=5)

        self.api_key_label = tk.Label(api_key_frame, text="API Key")
        self.api_key_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.api_key_entry = tk.Entry(api_key_frame, width=30)
        self.api_key_entry.pack(side=tk.LEFT, padx=5, pady=5)

        api_secret_frame = tk.Frame(self.root)
        api_secret_frame.pack(pady=5)

        self.api_secret_label = tk.Label(api_secret_frame, text="API Secret")
        self.api_secret_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.api_secret_entry = tk.Entry(api_secret_frame, width=30)
        self.api_secret_entry.pack(side=tk.LEFT, padx=5, pady=5)

        access_token_frame = tk.Frame(self.root)
        access_token_frame.pack(pady=5)

        self.access_token_label = tk.Label(access_token_frame, text="Access Token")
        self.access_token_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.access_token_entry = tk.Entry(access_token_frame, width=30)
        self.access_token_entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_account_button = tk.Button(self.root, text="Add New Account", command=self.add_new_account)
        self.add_account_button.pack(pady=10)

    def add_new_account(self):
        api_key = self.api_key_entry.get().strip()
        api_secret = self.api_secret_entry.get().strip()
        access_token = self.access_token_entry.get().strip()

        if api_key and api_secret and access_token:
            new_credentials = {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token
            }
            self.credentials_list.append(new_credentials)
            self.save_credentials_list(self.credentials_list)
            self.initialize_kite_connect(new_credentials)
            self.update_suggestions()

            # Update KiteConnect instances for buying and selling with new credentials
            buy_kite = KiteConnect(api_key=new_credentials["api_key"])
            sell_kite = KiteConnect(api_key=new_credentials["api_key"])

            # Set access tokens
            buy_kite.set_access_token(new_credentials["access_token"])
            sell_kite.set_access_token(new_credentials["access_token"])

            # Append to the list of KiteConnect instances
            self.buy_kite_instances.append(buy_kite)
            self.sell_kite_instances.append(sell_kite)

            # Clear the textboxes after adding the account
            self.api_key_entry.delete(0, tk.END)
            self.api_secret_entry.delete(0, tk.END)
            self.access_token_entry.delete(0, tk.END)

            messagebox.showinfo("Account Added", "New account credentials added successfully.")
        else:
            messagebox.showinfo("Error", "Please fill in all fields.")

    def create_footer(self):
        # Create a frame for the footer
        footer_frame = tk.Frame(self.root, bg="black", height=30)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        # Add content to the footer frame
        footer_label = tk.Label(footer_frame, text="© 2024 BlauStocks. All rights reserved.", font=('Helvetica', 12), fg="white", bg="black")
        footer_label.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X)

    
    def add_new_account(self):
        api_key = self.api_key_entry.get().strip()
        api_secret = self.api_secret_entry.get().strip()
        access_token = self.access_token_entry.get().strip()

        if api_key and api_secret and access_token:
            new_credentials = {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token
            }
            self.credentials_list.append(new_credentials)
            self.save_credentials_list(self.credentials_list)
            self.initialize_kite_connect(new_credentials)
            self.update_suggestions()

            # Update KiteConnect instances for buying and selling with new credentials
            buy_kite = KiteConnect(api_key=new_credentials["api_key"])
            sell_kite = KiteConnect(api_key=new_credentials["api_key"])

            # Set access tokens
            buy_kite.set_access_token(new_credentials["access_token"])
            sell_kite.set_access_token(new_credentials["access_token"])

            # Append to the list of KiteConnect instances
            self.buy_kite_instances.append(buy_kite)
            self.sell_kite_instances.append(sell_kite)

            # Clear the textboxes after adding the account
            self.api_key_entry.delete(0, tk.END)
            self.api_secret_entry.delete(0, tk.END)
            self.access_token_entry.delete(0, tk.END)

            messagebox.showinfo("Account Added", "New account .credentials added successfully.")
        else:
            messagebox.showinfo("Error", "Please fill in all fields.")


    def add_existing_account(self):
        if self.credentials:
            access_token = simpledialog.askstring("Access Token", "Please enter your access token:")
            if access_token:
                self.credentials["access_token"] = access_token
                self.save_credentials(self.credentials)
                self.initialize_kite_connect(self.credentials)
                self.update_suggestions()  # Update suggestions after adding an existing account
        else:
            messagebox.showinfo("Error", "No existing account found. Please add a new account.")



    def initialize_kite_connect(self, credentials):
        # Initialize KiteConnect instances for buying and selling
        self.buy_kite = KiteConnect(api_key=credentials["api_key"])
        self.sell_kite = KiteConnect(api_key=credentials["api_key"])

        # Set access tokens
        self.buy_kite.set_access_token(credentials["access_token"])
        self.sell_kite.set_access_token(credentials["access_token"])

        messagebox.showinfo("Account Added", "Account credentials added successfully. Application is now ready to use.")

    def create_logo_and_text(self):
        # Load logo image
        logo_image = Image.open("logo.jpg").resize((150, 70), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        # Create a frame for the title
        title_frame = tk.Frame(self.root, bg="#3498db")
        title_frame.pack(side=tk.TOP, fill=tk.X)

        # Title label
        title_label = tk.Label(title_frame, text="BLAUSTOCKS", font=('Consolas', 20, 'bold'), fg="white", bg="#3498db")
        title_label.grid(row=0, column=0, padx=20, pady=10)

        # Logo label
        logo_label = tk.Label(title_frame, image=self.logo_photo, bg="#17202A", font=('Consolas', 85, 'bold'))
        logo_label.grid(row=0, column=1, padx=1150, pady=10)

        ## footer part##

    def create_search_bar(self):
        search_frame = ttk.Frame(self.root)
        search_frame.pack(side=tk.LEFT, padx=30, pady=80, anchor='n')

        self.search_entry = ttk.Entry(search_frame, font=('Consolas', 12))
        self.search_entry.pack(side=tk.TOP, padx=0, pady=0)

        self.suggestion_listbox = tk.Listbox(search_frame, font=('Consolas', 12), height=15, width=35)
        self.suggestion_listbox.pack(side=tk.TOP, padx=0, pady=0)
        self.suggestion_listbox.bind('<ButtonRelease-1>', self.add_selected_instrument)
        self.search_entry.bind('<KeyRelease>', self.update_suggestions)

    def update_suggestions(self, event=None):
        query = self.search_entry.get().strip().upper()
        suggestions = [instrument for instrument in self.all_instruments if query in instrument.upper()]

        if query:
            self.suggestion_listbox.pack(side=tk.TOP, padx=0, pady=0)
        else:
            self.suggestion_listbox.pack_forget()

        self.suggestion_listbox.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestion_listbox.insert(tk.END, suggestion)

    def add_selected_instrument(self, event):
        selected_instrument = self.suggestion_listbox.get(tk.ACTIVE)
        if selected_instrument:
            wishlist_index = self.prompt_for_wishlist_tab()
            if wishlist_index is not None:
                if len(self.subscribed_instruments[wishlist_index]) < 30:
                    self.add_instrument(selected_instrument, wishlist_index)
                else:
                    messagebox.showinfo("Limit Reached", "You have reached the maximum limit of 30 instruments for this wishlist tab.")


    def prompt_for_wishlist_tab(self):
        response = simpledialog.askinteger("Select Wishlist Tab", "Enter the Wishlist Tab number (1 to 10):",
                                        parent=self.root, minvalue=1, maxvalue=10)
        if response is not None:
            return response - 1
        else:
            return None

    def update_note_label(self):
        for i in range(10):
            if len(self.subscribed_instruments[i]) >= 30:
                self.note_label.config(text="Note: Maximum 30 instruments reached for some wishlist tabs. You can't add more.")
                break
        else:
            self.note_label.config(text="Note: Maximum 30 instruments can be added per wishlist tab.")


    def add_instrument(self, instrument, wishlist_index):
        if instrument not in self.subscribed_instruments[wishlist_index]:
            self.subscribed_instruments[wishlist_index].append(instrument)
            self.save_subscribed_instruments(wishlist_index)
            self.show_result(f"{instrument} added to Wishlist {wishlist_index + 1}.")
            self.update_treeview(wishlist_index)
            self.update_note_label()

    def create_wishlist_tabs(self):
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, padx=30, pady=80, fill=tk.BOTH)

        self.notebook = ttk.Notebook(left_frame, width=600, height=500)  # Adjust the width and height as needed
        self.notebook.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=True)  # Expanded to occupy all available space

        for i in range(10):
            wishlist_tab = ttk.Frame(self.notebook)
            self.notebook.add(wishlist_tab, text=f"WISHLIST {i + 1}".upper(), padding=10)  # Convert text to uppercase
            # Adjust padding as needed

            columns = ("Stock", "Price")
            stock_tree = ttk.Treeview(wishlist_tab, columns=columns, show="headings", height=6)  # Adjusted height to 5
            stock_tree.heading("Stock", text="Stock")
            stock_tree.heading("Price", text="Price")
            stock_tree.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=True)  # Expanded to occupy all available space
            stock_tree.bind('<Double-1>', self.show_wishlist_options)
            self.stock_trees.append(stock_tree)

        self.note_label = ttk.Label(left_frame, text="Note: Maximum 30 instruments can be added per wishlist tab.", font=('Consolas', 10), foreground='gray')
        self.note_label.pack(side=tk.BOTTOM, pady=0,)  # Fill the available horizontal space

    def update_stock_prices_thread(self):
        self.load_subscribed_instruments()
        while True:
            self.update_stock_prices()
            time.sleep(1)

    def show_wishlist_options(self, event):
        selected_index = self.notebook.index(self.notebook.select())
        selected_stock = self.get_selected_stock(selected_index)
        if selected_stock:
            price = self.stock_prices.get(selected_stock, 0)
            self.show_result(f"Selected Stock: {selected_stock}, Price: {price}")
            # Open details window
            self.show_instrument_details(selected_stock, price)

    def create_buy_sell_frame(self):
        self.buy_sell_frame = ttk.Frame(self.root)
        self.buy_sell_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # self.quantity_label = ttk.Label(self.buy_sell_frame, text="Quantity:", font=('Helvetica', 12))
        # self.quantity_label.grid(row=0, column=0, padx=10, pady=10)

        # self.quantity_entry = ttk.Entry(self.buy_sell_frame, font=('Helvetica', 12))
        # self.quantity_entry.grid(row=0, column=1, padx=10, pady=10)

    def create_result_label(self):
        self.result_label = ttk.Label(self.root, text="", font=('Helvetica', 12))
        self.result_label.pack(side=tk.TOP, pady=10)

    def update_stock_prices(self):
        for stock_list in self.subscribed_instruments:
            for stock in stock_list:
                try:
                    ticker_data = self.buy_kite.ltp(["NSE:" + stock, "NFO:" + stock])
                    last_price = ticker_data["NSE:" + stock]["last_price"] if "NSE:" + stock in ticker_data else ticker_data["NFO:" + stock]["last_price"]
                    self.stock_prices[stock] = last_price
                except Exception as e:
                    print(f"Failed to fetch price for {stock}: {str(e)}")

        self.update_treeview()

    def update_treeview(self, wishlist_index=None):
        if wishlist_index is not None:
            stock_tree = self.stock_trees[wishlist_index]
            selected_stock_before_update = self.get_selected_stock(wishlist_index)

            subscribed_instruments_for_tab = self.load_subscribed_instruments_from_file(wishlist_index)

            existing_items = [(stock_tree.item(item, 'values')[0], item) for item in stock_tree.get_children()]

            for item in stock_tree.get_children():
                stock_tree.delete(item)

            for stock in subscribed_instruments_for_tab:
                price = self.stock_prices.get(stock, 0)
                stock_tree.insert("", "end", values=(stock, price))

            if selected_stock_before_update:
                for item in stock_tree.get_children():
                    if stock_tree.item(item, 'values')[0] == selected_stock_before_update:
                        stock_tree.selection_set(item)
                        break
        else:
            for index, stock_tree in enumerate(self.stock_trees):
                self.update_treeview(index)

    def buy_stock(self):
        selected_index = self.notebook.index(self.notebook.select())
        selected_stock = self.get_selected_stock(selected_index)
        quantity = self.quantity_entry.get()

        if not selected_stock or not quantity.isdigit() or int(quantity) <= 0:
            self.show_result("Please select a stock and enter a valid quantity.")
            return

        order_id = self.place_order(selected_stock, int(quantity), "BUY")

        if order_id is not None:
            self.show_result(f"Order placed successfully for {selected_stock}. Order ID: {order_id}")
        else:
            self.show_result("Order placement failed.")

    def sell_stock(self):
        selected_index = self.notebook.index(self.notebook.select())
        selected_stock = self.get_selected_stock(selected_index)
        quantity = self.quantity_entry.get()

        if not selected_stock or not quantity.isdigit() or int(quantity) <= 0:
            self.show_result("Please select a stock and enter a valid quantity.")
            return

        order_id = self.place_order(selected_stock, int(quantity), "SELL")

        if order_id is not None:
            self.show_result(f"Order placed successfully for {selected_stock}. Order ID: {order_id}")
        else:
            self.show_result("Order placement failed.")


    def remove_stock(self):
        selected_index = self.notebook.index(self.notebook.select())
        selected_stock = self.get_selected_stock(selected_index)
        if selected_stock:
            self.subscribed_instruments[selected_index].remove(selected_stock)
            self.save_subscribed_instruments(selected_index)
            self.update_treeview(selected_index)
            self.show_result(f"{selected_stock} removed from Wishlist {selected_index + 1}.")
            self.update_note_label()
        else:
            self.show_result("Please select a stock to remove from the wishlist.")

    def place_order(self, stock_symbol, quantity, transaction_type):
        kite_instances = self.buy_kite_instances if transaction_type == "BUY" else self.sell_kite_instances

        for kite_instance in kite_instances:
            try:
                order_id = kite_instance.place_order(
                    tradingsymbol=stock_symbol,
                    exchange=kite_instance.EXCHANGE_NSE,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=self.stock_prices[stock_symbol],
                    variety=kite_instance.VARIETY_REGULAR,
                    order_type=kite_instance.ORDER_TYPE_LIMIT,
                    product=kite_instance.PRODUCT_CNC
                )
                print(f"Order placed successfully for {stock_symbol}. Order ID is: {order_id}")
                return order_id
            except Exception as e:
                print(f"Order placement failed for {stock_symbol} with this account: {str(e)}")

        print(f"Order placement failed for {stock_symbol} with all accounts.")
        return None


    def get_selected_stock(self, wishlist_index):
        stock_tree = self.stock_trees[wishlist_index]
        selected_item = stock_tree.selection()

        if selected_item:
            return stock_tree.item(selected_item, 'values')[0]
        else:
            return None

    def show_result(self, message):
            self.result_label.config(text=message)
            # Display message box with the given message for 3 seconds
            threading.Timer(3.0, self.close_message_box).start()

    def close_message_box(self):
        self.result_label.config(text="")  # Clear the result label

    def save_subscribed_instruments(self, wishlist_index):
        tab_filename = f"wishlist_tab_{wishlist_index + 1}.json"
        with open(tab_filename, "w") as file:
            json.dump(self.subscribed_instruments[wishlist_index], file)

    def load_subscribed_instruments_from_file(self, wishlist_index):
        tab_filename = f"wishlist_tab_{wishlist_index + 1}.json"
        try:
            with open(tab_filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def load_subscribed_instruments(self):
        for i in range(10):
            self.subscribed_instruments[i] = self.load_subscribed_instruments_from_file(i)

    def get_all_instruments(self):
        try:
            nse_equity_instruments = self.buy_kite.instruments("NSE")
            nse_nfo_instruments = self.buy_kite.instruments("NFO")
            nse_equity_symbols = [instrument['tradingsymbol'] for instrument in nse_equity_instruments]
            nse_nfo_symbols = [instrument['tradingsymbol'] for instrument in nse_nfo_instruments]

            all_instruments = nse_equity_symbols + nse_nfo_symbols
            return all_instruments

        except Exception as e:
            print(f"Failed to fetch all instruments: {str(e)}")
            return []

    def create_styles(self):
        self.root.style = ttk.Style()
        self.root.style.configure("Green.TButton", foreground="green")
        self.root.style.configure("Red.TButton", foreground="red")

    def create_remove_button(self):
        self.remove_button = ttk.Button(self.buy_sell_frame, text="Remove", command=self.remove_stock)
        self.remove_button.grid(row=2, column=0, columnspan=2, pady=10)

    # def create_add_account_button(self):
    #     self.add_account_button = ttk.Button(self.buy_sell_frame, text="Add Account", command=self.choose_account_option)
    #     self.add_account_button.grid(row=3, column=0, columnspan=2, pady=10)



    def show_instrument_details(self, stock_symbol, initial_price):
        # Create a new window for showing instrument details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"{stock_symbol} Details")

        

        # Historical information display
        historical_info_label = tk.Label(details_window, text=f"{stock_symbol}", font=('Helvetica', 14, 'bold'))
        historical_info_label.pack(pady=10)

        # Real-time update of price
        price_label = tk.Label(details_window, text=f"Price: {initial_price}", font=('Helvetica', 12))
        price_label.pack()

        # # Open, close, previous close, market depth display
        # open_label = tk.Label(details_window, text=f"Open: {initial_price}", font=('Helvetica', 12))
        # open_label.pack()
        
        # # Assuming you have variables containing the values for each label
        # close_value = 100.00
        # prev_close_value = 98.50
        # market_depth_value = "High"

        # # Update the labels with the values
        # close_label = tk.Label(details_window, text=f"Close: {close_value}", font=('Helvetica', 12))
        # close_label.pack()

        # prev_close_label = tk.Label(details_window, text=f"Previous Close: {prev_close_value}", font=('Helvetica', 12))
        # prev_close_label.pack()

        # market_depth_label = tk.Label(details_window, text=f"Market Depth: {market_depth_value}", font=('Helvetica', 12))
        # market_depth_label.pack()


        # Quantity box, buy and sell buttons
        quantity_label = tk.Label(details_window, text="Quantity:", font=('Consolas', 12))
        quantity_label.pack(pady=10)
        
        quantity_entry = ttk.Entry(details_window, font=('Consolas', 12))
        quantity_entry.pack()
        
        buy_button = ttk.Button(details_window, text="Buy", command=lambda: self.buy_stock_details(stock_symbol, quantity_entry.get()), style="Green.TButton")
        buy_button.pack(pady=10)
        
        sell_button = ttk.Button(details_window, text="Sell", command=lambda: self.sell_stock_details(stock_symbol, quantity_entry.get()), style="Red.TButton")
        sell_button.pack(pady=10)
        

        def update_price():
            while True:
                try:
                    ticker_data = self.buy_kite.ltp(["NSE:" + stock_symbol, "NFO:" + stock_symbol])
                    current_price = ticker_data["NSE:" + stock_symbol]["last_price"] if "NSE:" + stock_symbol in ticker_data else ticker_data["NFO:" + stock_symbol]["last_price"]
                    price_label.config(text=f"Price: {current_price}")
                    time.sleep(1)  # Update every second
                except Exception as e:
                    print(f"Failed to fetch price for {stock_symbol}: {str(e)}")

        # Start a thread for updating the price
        price_update_thread = threading.Thread(target=update_price, daemon=True)
        price_update_thread.start()

    def buy_stock_details(self, stock_symbol, quantity):
        if not stock_symbol or not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        order_id = self.place_order(stock_symbol, int(quantity), "BUY")

        if order_id is not None:
            messagebox.showinfo("Success", f"Order placed successfully for {stock_symbol}. Order ID: {order_id}")
        else:
            messagebox.showerror("Error", "Order placement failed.")

    def sell_stock_details(self, stock_symbol, quantity):
        if not stock_symbol or not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        order_id = self.place_order(stock_symbol, int(quantity), "SELL")

        if order_id is not None:
            messagebox.showinfo("Success", f"Order placed successfully for {stock_symbol}. Order ID: {order_id}")
        else:
            messagebox.showerror("Error", "Order placement failed.")

    def save_credentials_list(self, credentials_list):
        with open("credentials.json", "w") as file:
            json.dump(credentials_list, file)

    def load_credentials_list(self):
        try:
            with open("credentials_list.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
  # Return an empty dictionary if the file is empty
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file doesn't exist
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in credentials file.")
            return {}  # Return an empty dictionary if JSON decoding fails


class AccountDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Account")
        self.top.geometry("300x200")
        self.credentials = None

        # Label and entry for API key
        ttk.Label(self.top, text="API Key:").pack(pady=5)
        self.api_key_entry = ttk.Entry(self.top)
        self.api_key_entry.pack(pady=5)

        # Label and entry for API secret
        ttk.Label(self.top, text="API Secret:").pack(pady=5)
        self.api_secret_entry = ttk.Entry(self.top)
        self.api_secret_entry.pack(pady=5)

        # Label and entry for Access Token
        ttk.Label(self.top, text="Access Token:").pack(pady=5)
        self.access_token_entry = ttk.Entry(self.top)
        self.access_token_entry.pack(pady=5)

        # Button to submit credentials
        ttk.Button(self.top, text="Submit", command=self.submit_credentials).pack(pady=10)

    def submit_credentials(self):
        # Get credentials from entries
        api_key = self.api_key_entry.get().strip()
        api_secret = self.api_secret_entry.get().strip()
        access_token = self.access_token_entry.get().strip()

        # Check if all fields are filled
        if api_key and api_secret and access_token:
            self.credentials = (api_key, api_secret, access_token)
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Please fill all fields.")


class AccountOptionDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Choose Account Option")
        self.top.geometry("300x100")
        self.option = None

        # Label and button for adding new account
        ttk.Label(self.top, text="Choose Account Option:").pack(pady=5)
        ttk.Button(self.top, text="New Account", command=self.choose_new_account).pack(pady=5)

        # Label and button for existing account
        ttk.Button(self.top, text="Existing Account", command=self.choose_existing_account).pack(pady=5)

    def choose_new_account(self):
        self.option = "New Account"
        self.top.destroy()

    def choose_existing_account(self):
        self.option = "Existing Account"
        self.top.destroy()

# Other classes and methods remain the same

if __name__ == "__main__":
    root = tk.Tk()
    app = StockWishlistApp(root)
    root.mainloop()