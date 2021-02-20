"""Checks NYC COVID website every 30 seconds for available appointments
for a given location and will send an email when there
are availabilities.

NB for this to work you need to fill out the relevant consts to your system
settings and also put your gmail in low-security mode, so I recommend 
using a burner gmail for that.
"""
import time
import sys
import click
import pandas as pd
import smtplib
import logging
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from datetime import datetime


LOG = logging.getLogger(__name__)
output_file_handler = logging.FileHandler("output.log")
stdout_handler = logging.StreamHandler(sys.stdout)

LOG.addHandler(output_file_handler)
LOG.addHandler(stdout_handler)

# Scraping consts
NYC_COVID_WEBSITE_URL = "https://am-i-eligible.covid19vaccine.health.ny.gov/"
CHROMEDRIVER_PATH = "/Users/sanjeevsreetharan/Downloads/chromedriver"
COL_NAME_APPOINTMENTS = "Appointments Available"
COL_NAME_LOCATION = "Location Name"
NO_APPTS_AVAIL = "No Appointments Available Currently"
APPTS_AVAIL = "Appointments Available"

# Email consts
FROM_GMAIL_USER = ""
TO_GMAIL_USER = ""
GMAIL_PASSWORD = ""
SUBJECT = "COVID Vaccine Appointment status for "


def _html_soup_to_pandas_dataframe(table_soup):
    """Returns table in HTML soup if one (or more) exists
    """
    table = table_soup.find_all("table")
    return pd.read_html(str(table))[0]


def _init_chromedriver():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = Chrome(CHROMEDRIVER_PATH, options=options)
    return driver


def _return_vaccine_signup_status(pandas_df, location_name):
    return pandas_df[pandas_df[COL_NAME_LOCATION] == location_name][
        COL_NAME_APPOINTMENTS
    ][0]


def _init_email():
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(FROM_GMAIL_USER, GMAIL_PASSWORD)
    return server


def _send_email(server, from_addr, to_addr, email_text):
    try:
        server.sendmail(from_addr=from_addr, to_addrs=[to_addr], msg=email_text)
    except Exception as e:
        LOG.error(f"Error: {e}")


def _get_status_for_location(location_name):
    driver = _init_chromedriver()
    driver.get(NYC_COVID_WEBSITE_URL)
    time.sleep(10)
    vaccine_status_html_soup = BeautifulSoup(driver.page_source, "html5lib")
    df = _html_soup_to_pandas_dataframe(vaccine_status_html_soup)
    status = _return_vaccine_signup_status(df, location_name)
    return status


def _email_on_status_if_necessary(status, location_name):
    now = datetime.now()
    if status == APPTS_AVAIL:
        LOG.info(
            f"[{now}] Sending email for {location_name}: {status} to {TO_GMAIL_USER}"
        )
        server = _init_email()
        message = f"Subject: Appt avail for {location_name}: {NYC_COVID_WEBSITE_URL}\n\nSent by {__file__} at {now}"
        _send_email(server, FROM_GMAIL_USER, TO_GMAIL_USER, message)


@click.command()
@click.option(
    "--location_name",
    default="Javits Center",
    help="Name of location you want to check for",
)
def alert_on_vaccine_appointment_available(location_name):
    no_appointments_available = True
    while no_appointments_available:
        now = datetime.now()
        status = _get_status_for_location(location_name)
        print(f"[{now}] Vaccine status for {location_name}: {status}")
        _email_on_status_if_necessary(status, location_name)
        no_appointments_available = status != APPTS_AVAIL
        time.sleep(20)


if __name__ == "__main__":
    alert_on_vaccine_appointment_available()

