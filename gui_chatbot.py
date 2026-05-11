import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import requests

API_BASE = "http://127.0.0.1:8000"

state = None
data = {}

# =========================
# CHAT LOGIC
# =========================
def handle_chat(user_input):
    global state, data

    if user_input.lower() == "exit":
        root.quit()

    # START FLOW - 'Update Exception' Feature
    if "update exception" in user_input.lower():
        state = "ask_control"
        return "Select recon from dropdown below"

    # STEP 1 (CONTROL comes from dropdown)
    if state == "ask_control":
        return "Choose recon from dropdown and click send"

    # STEP 2 - Date and Age Check
    if state == "ask_date":
        try:
            trade_date, age = user_input.split(",")
            data["trade_date"] = trade_date.strip()
            data["age"] = int(age.strip())
        except:
            return "Invalid format (use: 2024-09-11, 587)"

        res = requests.get(
            f"{API_BASE}/check_record",
            params=data
        )
        # If record doesn't exist
        if not res.json()["exists"]:
            return "Record not found"

        state = "ask_codes"
        return "Enter reason and resolution codes for Exception (R1, RES1)"

    # STEP 3 -- Update Exception with Reason and Resolution Codes
    if state == "ask_codes":
        try:
            reason, resolution = user_input.split(",")
            data["reason"] = reason.strip()
            data["resolution"] = resolution.strip()
        except:
            return "Invalid format"

        res = requests.post(
            f"{API_BASE}/update_exception",
            json=data
        )

        state = None
        return res.json()["message"]

    # OLD FEATURE - Exception COUNT Feature
    text = user_input.lower()

    for name in ["akhil", "rajesh", "rahul", "siddharth"]:
        if name in text and "exception" in text:
            res = requests.get(f"{API_BASE}/exceptions/{name}")
            return f"Exception count for {name} is {res.json()['exception_count']}"

    return "I didn't understand could you please rephrase?"


# =========================
# SEND MESSAGE
# =========================
def send_message(event=None):
    global state, data

    user_input = entry.get()
    if not user_input:
        return

    chat_area.insert(tk.END, "You: " + user_input + "\n")
    entry.delete(0, tk.END)

    # Handle dropdown selection
    if state == "ask_control":
        selected = recon_var.get()
        data["control"] = selected

        res = requests.get(f"{API_BASE}/validate_control/{selected}")

        if res.status_code != 200:
            chat_area.insert(tk.END, "Bot: Invalid user\n\n")
            return

        state = "ask_date"
        chat_area.insert(tk.END, f"Bot: Selected {selected}\n")
        chat_area.insert(tk.END, "Bot: Enter trade_date and Exception age Example:(YYYY-MM-DD, 7)\n\n")
        return

    response = handle_chat(user_input)
    chat_area.insert(tk.END, "Bot: " + response + "\n\n")


# =========================
# GUI DESIGN
# =========================
root = tk.Tk()
root.title("Recon Chatbot")
root.geometry("500x500")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20)
chat_area.pack(padx=10, pady=10)

# Dropdown
recon_var = tk.StringVar()
recon_dropdown = ttk.Combobox(root, textvariable=recon_var)
recon_dropdown['values'] = ("akhil", "rajesh", "rahul", "siddharth")
recon_dropdown.pack(pady=5)
recon_dropdown.set("Select Recon")

# Input + Button Frame
frame = tk.Frame(root)
frame.pack(pady=10)

entry = tk.Entry(frame, width=40)
entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)

# 🔥 ENTER KEY SUPPORT
root.bind('<Return>', send_message)

root.mainloop()