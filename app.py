import streamlit as st
import json
import re


# Import scraping functions
from webscraper import fetch_webpage, extract_slots, read_stored_slots, write_stored_slots, check_for_new_slots
# Sheduler logic imports
from apscheduler.schedulers.background import BackgroundScheduler
# Emailer logic imports
from emailer import send_email


# ------------------------- #
# Constant definitions      #
# ------------------------- #

url = "https://www.aurelienmuguet.com/sessionscme"
interval_seconds = 10
storage_file = "slots.json"
sender_email = "david.dedobbeleer@creativityquarks.com"  # Your registered Mailjet emai

# ------------------------- #
# Logic                     #
# ------------------------- #
# Function to save email to a file
def save_email(email):
    with open("emails.json", "a") as file:
        json.dump(email, file)
        file.write("\n")

def load_emails():
    try:
        with open("emails.json", "r") as file:
            return [json.loads(line) for line in file]
    except FileNotFoundError:
        return []

def build_email_string():
    email_list = load_emails()
    email_list_string = ""
    for e in email_list:
        email_list_string += e + " "
    return email_list_string

def clear_email_list():
    with open("emails.json", "w") as file:
        pass  # Opening in 'w' mode and closing will empty the file

# def is_valid_email(email):
#     return lambda email: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def run_scraper(url, storage_file, sender_email):        
    soup = fetch_webpage(url)
    current_slots = extract_slots(soup)
    stored_slots_list_of_lists = read_stored_slots(storage_file)
    stored_slots_list_of_tuples = [tuple(inner_list) for inner_list in stored_slots_list_of_lists]

    new_slots = check_for_new_slots(current_slots, stored_slots_list_of_tuples)

    if new_slots or not stored_slots_list_of_lists:  # If there are new slots or if it's the first run
        email_list = load_emails()
        for email in email_list:
            # example : send_email("recipient@example.com", "New Slot Available", "A new slot has become available: [Slot Details]")
            send_email(sender_email, email, "New Slot Available", f"A new slot has become available: {new_slots}")
            send_email_prompt_notif(new_slots, email)

    write_stored_slots(storage_file, current_slots)

# def launch_scheduler(url,interval_seconds):
    # Schedule job to run every interval_seconds
    # scheduler = BackgroundScheduler()
#     scheduler.add_job(lambda: run_scraper(url), 'interval', seconds=interval_seconds)
#     scheduler.start()

def send_email_prompt_notif(new_slots, email):
    # Implement your email sending logic here
    print(f"Sending email to {email} for new slots: {new_slots}")

# Initialize the scheduler and the st.session_state "scheduler_running"
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.add_job(lambda: run_scraper(url, storage_file, sender_email), 'interval', seconds=interval_seconds)
    st.session_state.scheduler_running = False

# ------------------------- #
# Streamlit UI              #
# ------------------------- #

st.title("Slot Availability Monitoring")
st.text(f"Target url: {url}")
st.text("Detecting any new slot with the \"RESERVATION\" keyword.")
st.text("Send an email with its time frames.")
st.text(f"Iteration every {interval_seconds} seconds")
        
email = st.text_input("Enter your email to get notified about new slots:")

if st.button("Subscribe"):
    is_valid_email = lambda email: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None
    email_list_string = build_email_string()
    if not is_valid_email(email):
        st.error("Please enter a valid email")
    elif email in email_list_string:
        st.error("Email already in emailing list")
    else:
        save_email(email)    
        st.success(f"Subscribed email: {email}")

if st.button("Show emailing list"):    
    email_list_string = build_email_string()
    # st.text(email_list_string)
    st.success(f"Subscribed email list: {email_list_string}")

if st.button("Delete emailing list"): 
    clear_email_list()

if st.button("Clear slots list"): 
    write_stored_slots(storage_file, [])  

# Start or stop the scheduler based on the button click
if st.button('Start Monitoring'):
    email_list = load_emails()
    if not bool(email_list):
        st.warning("The emailing list is empty.")
        pass
    if not st.session_state.scheduler_running:
        st.session_state.scheduler.start()
        st.session_state.scheduler_running = True
        st.success("Monitoring started.")
    elif st.session_state.scheduler_running:
        st.warning("Monitoring is already running.")
    print(f"st.session_state.scheduler_running: {st.session_state.scheduler_running}")

if st.button('Stop Monitoring'):
    if st.session_state.scheduler_running and st.session_state.scheduler.running:
        st.session_state.scheduler.shutdown(wait=False)
        st.session_state.scheduler_running = False
        st.error("Monitoring stopped.")
    else:
        st.warning("Monitoring is not running or was already stopped.")
    print(f"st.session_state.scheduler_running: {st.session_state.scheduler_running}")
        

# Shut down the scheduler when exiting the app to avoid leaving a hanging process
# st.on_session_end(lambda: scheduler.shutdown(wait=False))

####################


# email_list = load_emails()
# if st.button("Launch scraping") and bool(email_list):
#     print(bool(email_list))
#     for e in email_list:
#         st.success(f"Scheduler launched, {e} will be notififed if any change is observed")    
#     print("Scheduler launched")    
#     launch_scheduler(url,interval_seconds)


# # Optional: Button to manually trigger the scraper
# if st.button("Check for New Slots"):
#     run_scraper(url)
#     st.success("Checked for new slots and sent notifications if any were found.")



# # Keep the script running
# try:
#     while True:
#         pass
# except (KeyboardInterrupt, SystemExit):
#     scheduler.shutdown()

# # Button launching a schedule job to run every interval_seconds
# if st.button("Launch Scheduler"):
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(lambda: run_scraper(url), 'interval', seconds=interval_seconds)
#     scheduler.start()

# # if st.button("Stop Scheduler"):
# #     scheduler.shutdown(wait=False)