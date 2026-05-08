import requests

def get_control(user_input):
    user_input = user_input.lower()

    if "akhil" in user_input:
        return "akhil"
    elif "rajesh" in user_input:
        return "rajesh"
    elif "rahul" in user_input:
        return "rahul"
    elif "siddharth" in user_input:
        return "siddharth"
    
    return None


#def chatbot():
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        control = get_control(user_input)

        if not control:
            print("Bot: Control not recognized")
            continue

        if "exception" in user_input.lower():
            res = requests.get(f"http://127.0.0.1:8000/exceptions/{control}")
            count = res.json()["exception_count"]

            print(f"Bot: Exception count for {control} is {count}")
        else:
            print("Bot: I didn't understand")
#if __name__ == "__main__":
    chatbot()




def chatbot():
    state = None
    data = {}

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        # START UPDATE FLOW
        if "update exception" in user_input.lower():
            state = "ask_control"
            print("Bot: Which Recon/Control to update Exception?")
            continue

        # STEP 1
        if state == "ask_control":
            data["control"] = user_input.lower()

            res = requests.get(f"http://127.0.0.1:8000/validate_control/{data['control']}")

            if res.status_code != 200:
                print("Bot: User not found")
                continue

            state = "ask_date"
            print("Bot: Enter trade date and exception age (example: 2024-09-11, 7)")
            continue

        # STEP 2
        if state == "ask_date":
            try:
                trade_date, age = user_input.split(",")
                data["trade_date"] = trade_date.strip()
                data["age"] = int(age.strip())
            except:
                print("Bot: Invalid format")
                continue

            res = requests.get(
                "http://127.0.0.1:8000/check_record",
                params=data
            )

            if not res.json()["exists"]:
                print("Bot: Record not found")
                continue

            state = "ask_codes"
            print("Bot: Enter Reason and Resolution Codes for the exception (RE, RES code)")
            continue

        # STEP 3
        if state == "ask_codes":
            try:
                reason, resolution = user_input.split(",")
                data["reason"] = reason.strip()
                data["resolution"] = resolution.strip()
            except:
                print("Bot: Invalid format")
                continue

            res = requests.post(
                "http://127.0.0.1:8000/update_exception",
                json=data
            )

            print("Bot:", res.json()["message"])

            state = None
            continue

        # EXCEPTION COUNT FEATURE
        control = get_control(user_input)

        if not control:
            print("Bot: Control not recognized")
            continue

        if "exception" in user_input.lower():
            res = requests.get(f"http://127.0.0.1:8000/exceptions/{control}")
            count = res.json()["exception_count"]

            print(f"Bot: Exception count for {control} is {count}")
        else:
            print("Bot: I didn't understand")
if __name__ == "__main__":
    chatbot()