# IP Status Checker

The IP Status Checker is a Python desktop application built using the Tkinter library. It allows you to manage and monitor the status of a list of IP addresses, and it can run PuTTY with user login when you double-click an entry in the list.

## Features

- Add new IP addresses along with a name and user login.
- Monitor the reachability of IP addresses by sending periodic pings.
- Visual indication of IP status with color-coded entries in the list.
- Double-click to run PuTTY with the selected IP address and user login.

## Usage

1. **Add IP Address:**
   - Enter the IP address in the "IP Address" field.
   - Enter a name for the IP address in the "Name" field.
   - Enter the user login in the "User Login" field.
   - Click the "Add IP" button to add the IP address to the list.

2. **Monitor IP Status:**
   - The list displays the name, IP address, and user login.
   - The background color of each entry indicates the status (green for reachable, red for unreachable).

3. **Run PuTTY:**
   - Double-click on an entry to run PuTTY with the selected IP address and user login.

4. **Auto-Update:**
   - The application periodically pings each IP address to update its status.
   - The status is updated every 30 seconds.

## Requirements

- Python 3.6+
- Tkinter (usually included with Python)
- PuTTY (for running PuTTY; make sure it's in the system's PATH)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ip-status-checker.git
