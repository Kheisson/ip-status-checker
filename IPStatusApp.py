import tkinter as tk
import subprocess

# Config values
REFRESH_RATE = 10000
FONT_SIZE = 14
PING_REPEAT = "1"

class IPStatusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Status Checker")

        # Create a list to hold IP, name, and user combinations
        self.ip_list = []

        # Create labels and entry fields for IP, Name, and User Login
        tk.Label(root, text="IP Address:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(root)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="User Login:").grid(row=2, column=0, padx=5, pady=5)
        self.user_entry = tk.Entry(root)
        self.user_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = tk.Button(root, text="Add IP", command=self.add_ip, state="disabled")
        self.add_button.grid(row=3, columnspan=2, padx=5, pady=5)

        listbox_font = ("Arial", FONT_SIZE)
        self.listbox = tk.Listbox(root, font=listbox_font, selectmode="SINGLE", bg="white")
        self.listbox.grid(row=4, columnspan=2, sticky="nsew")

        # Load saved entries from a file
        self.load_entries()

        # Create a timer to update the IP status
        self.update_timer()

        # Configure row and column weights to make elements resize with the window
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Bind the entry fields to an event handler to check for valid input
        self.ip_entry.bind("<KeyRelease>", self.validate_input)
        self.name_entry.bind("<KeyRelease>", self.validate_input)
        self.user_entry.bind("<KeyRelease>", self.validate_input)

        # Bind a double-click event to run PuTTY command on a selected entry
        self.listbox.bind("<Double-Button-1>", self.run_putty)

    def validate_input(self, event):
        # Enable the "Add IP" button only when both fields are filled
        ip_text = self.ip_entry.get()
        name_text = self.name_entry.get()
        if ip_text and name_text:
            self.add_button["state"] = "normal"
        else:
            self.add_button["state"] = "disabled"

    def add_ip(self):
        # Get IP and Name from the entry fields
        ip = self.ip_entry.get()
        name = self.name_entry.get()

        # Add to the list and clear entry fields
        self.ip_list.append((ip, name))
        self.listbox.insert(tk.END, f"{name} - {ip}")
        self.ip_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.update_ip_status(len(self.ip_list) - 1, ip)

        # Save the updated entries to a file
        self.save_entries()

    def update_timer(self):
        for i, (ip, name) in enumerate(self.ip_list):
            self.update_ip_status(i, ip)

        # Schedule the next update
        self.root.after(REFRESH_RATE, self.update_timer)

    def update_ip_status(self, index, ip):
        try:
            result = subprocess.run(["ping", "-n", PING_REPEAT, ip], capture_output=True, text=True, check=True)
            if "Reply from" in result.stdout:
                self.listbox.itemconfig(index, {'bg': 'green', 'selectbackground': 'green'})
        except subprocess.CalledProcessError:
            self.listbox.itemconfig(index, {'bg': 'red', 'selectbackground': 'red'})
            pass

    def load_entries(self):
        try:
            with open("ip_entries.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    name, ip = line.strip().split(" - ")
                    self.ip_list.append((ip, name))
                    self.listbox.insert(tk.END, line)
        except FileNotFoundError:
            # File doesn't exist, so create it
            with open("ip_entries.txt", "w") as file:
                pass

    def save_entries(self):
        with open("ip_entries.txt", "w") as file:
            for ip, name in self.ip_list:
                file.write(f"{name} - {ip}\n")

    def run_putty(self, event):
        selected_index = self.listbox.curselection()[0]
        ip, _ = self.ip_list[selected_index]  # Use user from the entry
        user = self.user_entry.get()

        # Use subprocess to run PuTTY with the selected IP address and user login
        try:
            subprocess.run(["putty", ip, "-l", user])
        except FileNotFoundError:
            # Handle PuTTY not found
            print("PuTTY is not installed or not in the system's PATH.")


if __name__ == "__main__":
    root = tk.Tk()
    app = IPStatusApp(root)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.mainloop()
