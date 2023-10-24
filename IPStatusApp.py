import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import os
import json
import threading

# Config values
TITLE = "IP Status Checker"
REFRESH_RATE_MS = 10000  # Refresh rate in milliseconds
FONT_SIZE = 14
PING_COUNT = 1  # Number of pings
INITIAL_SIZE = "800x600"
SAVE_DATAFILE_NAME = "ip_data.json"
IP_ADDRESS_LABEL = "IP Address:"
NAME_LABEL = "Name:"
ADD_IP_LABEL = "Add IP"
USERNAME_LABEL = "Username:"
CLEAN_BUTTON_LABEL = "Clear Search"
SHOW_DOWN_LABEL = "Show Only Down"
SHOW_ALL_LABEL = "Show All"


class IPStatusApp:
    def __init__(self, root):
        self.root = root
        self.root.title(TITLE)

        # Load saved IPs
        self.data_file = SAVE_DATAFILE_NAME
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                self.ip_list = json.load(file)
        else:
            self.ip_list = []

        self.ip_statuses = {ip: 'unknown' for ip, _, _ in self.ip_list}  # Set default status

        # GUI setup
        self.setup_gui()

        # Load and display the icon
        self.load_icon()

        # "About" information button setup
        self.about_button = tk.Button(self.root, text="?", command=self.show_about_info)
        self.about_button.grid(row=4, column=3, pady=5)  # Adjust grid parameters as needed

        # Start the update loop
        self.update_ip_statuses()

    def setup_gui(self):
        tk.Label(self.root, text=IP_ADDRESS_LABEL).grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry_var = tk.StringVar()
        self.ip_entry = tk.Entry(self.root, textvariable=self.ip_entry_var)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.root, text=NAME_LABEL).grid(row=1, column=0, padx=5, pady=5)
        self.name_entry_var = tk.StringVar()
        self.name_entry = tk.Entry(self.root, textvariable=self.name_entry_var)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.add_button = tk.Button(self.root, text=ADD_IP_LABEL, command=self.add_ip, state=tk.DISABLED)
        self.add_button.grid(row=2, columnspan=2, padx=5, pady=5)

        # Triggering the button state check whenever the text changes
        self.ip_entry_var.trace_add("write", self.check_entries)
        self.name_entry_var.trace_add("write", self.check_entries)

        # Listbox setup
        self.listbox = tk.Listbox(self.root, font=("Arial", FONT_SIZE))
        self.listbox.grid(row=3, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Making the list box scrollable
        scrollbar = tk.Scrollbar(self.root, command=self.listbox.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Adjusting row and column scaling
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # PuTTY connection
        tk.Label(self.root, text=USERNAME_LABEL).grid(row=0, column=2, padx=5, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.root, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Search and filter functionality
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_listbox())
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var, font=("Arial", FONT_SIZE))
        self.search_entry.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Button to clear the search
        self.clear_search_button = tk.Button(self.root, text=CLEAN_BUTTON_LABEL, command=self.clear_search)
        self.clear_search_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

        # Button to show only down IPs
        self.show_down_var = tk.BooleanVar(value=False)
        self.show_down_button = tk.Button(self.root, text=SHOW_DOWN_LABEL, command=self.toggle_show_down_state)
        self.show_down_button.grid(row=5, column=1, padx=5, pady=5)  # Adjust grid parameters accordingly

        # Bind double-clicking and right-clicking on the listbox
        self.listbox.bind("<Double-Button-1>", self.on_double_click)
        self.listbox.bind("<Button-3>", self.on_right_click)

        # Update the listbox with the current IP list
        self.update_listbox()

    def load_icon(self):
        # The icon's filename should be 'icon.png' or change to match your file
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")

        image = tk.PhotoImage(file=icon_path)

        # Numbers reflect the value by which the image is divided by
        image = image.subsample(6, 6)

        icon_label = tk.Label(self.root, image=image)
        icon_label.image = image
        icon_label.grid(row=3, column=3, padx=5, pady=5)

    def show_about_info(self):
        about_info = (
            "This program was made by Igor Kheisson - October 2023\n"
            "For issues and requests please contact me!"
        )
        messagebox.showinfo("About IP Status Checker", about_info)

    def check_entries(self, *args):
        ip = self.ip_entry_var.get()
        name = self.name_entry_var.get()

        # Enable the 'Add IP' button if both fields are filled, else keep it disabled
        if ip and name:
            self.add_button.config(state=tk.NORMAL)
        else:
            self.add_button.config(state=tk.DISABLED)

    def add_ip(self):
        ip = self.ip_entry_var.get()
        name = self.name_entry_var.get()

        # Add the new IP to the list and save
        self.ip_list.append((ip, name, 'unknown'))  # 'unknown' as the status for new entries
        self.ip_statuses[ip] = 'unknown'

        with open(self.data_file, 'w') as file:
            json.dump(self.ip_list, file)

        # Clear the entry fields after adding
        self.ip_entry_var.set('')
        self.name_entry_var.set('')

        # Update listbox to reflect the addition
        self.update_listbox()

    def ping_ip(self, ip):
        try:
            response = subprocess.run(['ping', '-c', str(PING_COUNT), ip], capture_output=True, timeout=10)
            success = response.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            success = False

        new_status = 'green' if success else 'red'
        self.ip_colors[ip] = new_status

        # Update the listbox on the main thread
        self.root.after(0, self.update_listbox)

    def update_ip_statuses(self):
        for ip, _, _ in self.ip_list:
            threading.Thread(target=self.check_ip_status, args=(ip,), daemon=True).start()

        # Schedule the next update after a certain interval
        self.root.after(REFRESH_RATE_MS, self.update_ip_statuses)

    def check_ip_status(self, ip):
        try:
            response = subprocess.run(['ping', '-n', str(PING_COUNT), ip], capture_output=True, text=True, timeout=10)
            success = response.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            success = False

        # Update the status dictionary
        new_status = 'up' if success else 'down'
        self.ip_statuses[ip] = new_status

        # Update the listbox on the main thread
        self.root.after(0, self.update_listbox)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)  # Clear current listbox content

        search_term = self.search_var.get().lower()
        show_only_down = self.show_down_var.get()

        for ip, name, _ in self.ip_list:
            status = self.ip_statuses[ip]
            # Prepare the text to be displayed for each entry in the listbox
            entry_text = f"{name} ({ip}) - {status.upper()}"

            # Check the conditions to decide whether to display this entry
            if show_only_down and status != 'down':
                continue  # Skip non-down IPs when "Show Only Down" is active

            if search_term and search_term not in entry_text.lower():
                continue  # Skip entries that don't match the search term

            # If the entry meets the conditions, display it in the listbox
            color = 'green' if status == 'up' else 'red'
            self.listbox.insert(tk.END, entry_text)
            self.listbox.itemconfig(tk.END, {'bg': color})

    def on_double_click(self, event):
        selection_index = self.listbox.curselection()
        if selection_index:
            ip, _, _ = self.ip_list[selection_index[0]]
            username = self.username_var.get()
            putty_command = f"putty -ssh {username}@{ip}" if username else f"putty -ssh {ip}"

            try:
                subprocess.Popen(putty_command, shell=True)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_right_click(self, event):
        try:
            # Determine the item clicked and ask for deletion confirmation
            selection_index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(selection_index)
            ip, _, _ = self.ip_list[selection_index]

            if messagebox.askyesno("Confirmation", f"Do you want to remove {ip}?"):
                # Remove the item from the list and save the file
                del self.ip_list[selection_index]
                del self.ip_statuses[ip]

                with open(self.data_file, 'w') as file:
                    json.dump(self.ip_list, file)

                self.update_listbox()  # Reflect the deletion in the listbox
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_search(self):
        self.search_var.set('')
        self.update_listbox()

    def toggle_show_down_state(self):
        if self.show_down_var.get():
            # If currently showing only down IPs, switch to showing all IPs
            self.show_down_var.set(False)
            self.show_down_button.config(text=SHOW_DOWN_LABEL)
        else:
            # If currently showing all IPs, switch to showing only down IPs
            self.show_down_var.set(True)
            self.show_down_button.config(text=SHOW_ALL_LABEL)

        # Update the listbox based on the new state
        self.update_listbox()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(INITIAL_SIZE)
    app = IPStatusApp(root)
    root.mainloop()
