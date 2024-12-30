import logging
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox as mb

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Feel free to remove the logging module if you don't need it
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use the commented function below to hardcode the data you need
'''def get_infos():
    link = "https://tiromed.med.unipi.it/mod/reservation/view.php?id=22665"
    username = 606763
    password = "JordanRetro01!"
    note = ""
    return username, password, link, note'''


def get_infos():
    def submit():
        nonlocal link, username, password, note
        link = link_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        root.destroy()
        ask_for_note()

    def ask_for_note():
        if mb.askyesno("Leave a Note", "Do you want to leave a message in the note section?"):
            note_window()

    def note_window():
        note_root = tk.Tk()
        note_root.title("Leave a Note")
        note_root.attributes('-topmost', True)

        tk.Label(note_root, text="Enter the text:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        note_entry = tk.Entry(note_root, width=40)
        note_entry.grid(row=0, column=1, padx=10, pady=5)

        note_entry.focus_set()
        note_root.bind("<Return>", lambda event: submit_note())

        def submit_note():
            nonlocal note
            note = note_entry.get().strip()
            note_root.destroy()

        tk.Button(note_root, text="Submit", command=submit_note).grid(row=1, column=0, columnspan=2, pady=10)

        note_root.update_idletasks()
        width = note_root.winfo_width()
        height = note_root.winfo_height()
        x = (note_root.winfo_screenwidth() // 2) - (width // 2)
        y = (note_root.winfo_screenheight() // 2) - (height // 2)
        note_root.geometry(f'{width}x{height}+{x}+{y}')
        note_root.mainloop()

    link = username = password = note = None

    root = tk.Tk()
    root.title("Preliminary information")
    root.after(1, lambda: link_entry.focus_set())

    tk.Label(root, text="URL to the internship:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    link_entry = tk.Entry(root, width=40)
    link_entry.grid(row=0, column=1, padx=10, pady=5)
    link_entry.bind("<Return>", lambda event: username_entry.focus_set())

    tk.Label(root, text="Your username:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    username_entry = tk.Entry(root, width=40)
    username_entry.grid(row=1, column=1, padx=10, pady=5)
    username_entry.bind("<Return>", lambda event: password_entry.focus_set())

    tk.Label(root, text="Your password:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    password_entry = tk.Entry(root, width=40)
    password_entry.grid(row=2, column=1, padx=10, pady=5)
    password_entry.bind("<Return>", lambda event: submit())

    tk.Button(root, text="Submit", command=submit).grid(row=3, column=0, columnspan=2, pady=10)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.mainloop()

    return username, password, link, note


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    logging.info("Driver initialized.")
    return webdriver.Chrome(options=options)


def login(driver, username, password, link):
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        logging.info("Login successful.")
    except Exception as e:
        logging.error(f"Check your credentials\nLogin failed: {e}")
        driver.quit()
        raise


def get_registration_start_date(driver):
    try:
        date_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='box generalbox boxaligncenter boxwidthwide']")))
        date_text = date_element.text.split("Reservation start on:")[1].split("Reservation end on:")[0].strip()
        start_date = datetime.strptime(date_text, "%A, %d %B %Y, %I:%M %p")
        logging.info(f"Registration start date extracted: {start_date}")
        return start_date
    except Exception as e:
        logging.error(f"Failed to extract registration start date: {e}")
        driver.quit()
        raise


def reserve(driver, start_date, note):
    try:
        while datetime.now() < start_date:
            time.sleep(0.1)

        if note:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "note"))).send_keys(note)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "reserve"))).click()
        root = tk.Tk()
        root.lift()
        root.title("Reservation status")
        tk.Label(root, text="Reservation successful!", padx=20, pady=20).pack()
        tk.Button(root, text="OK", command=root.destroy).pack(pady=10)
        root.mainloop()
        logging.info("Reservation successful.")
    except Exception as e:
        root = tk.Tk()
        root.lift()
        root.title("Reservation status")
        root.attributes('-topmost', True)
        tk.Label(root, text="Reservation failed :(", padx=20, pady=20).pack()
        tk.Button(root, text="OK", command=root.destroy).pack(pady=10)
        root.mainloop()
        logging.error(f"Reservation failed: {e}")
        driver.quit()
        raise


def main():
    username, password, link, note = get_infos()
    driver = initialize_driver()
    try:
        login(driver, username, password, link)
        start_date = get_registration_start_date(driver)
        reserve(driver, start_date, note)
    finally:
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    main()
