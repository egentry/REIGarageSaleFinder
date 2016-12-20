from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, datetime, os
import smtplib
from email.mime.text import MIMEText


#####
# Authors: Mike Adler - May 3, 2013 (from github:mike200015/goes-interview-checker)
#          Eric Gentry - May 2016 & Dec 2016
#
# REIGarageSaleFinder - Used to automatically check for new REI Garage Sale events
#
# At my REI (Saratoga), they sometimes post Garage Sale listings on their
# website, but not in their regular emails. This program will automatically
# check their website for you.  If it finds a new Garage Sale, it'll email
# you to let you know.  It'll also keep track of Garage Sales it's already
# seen, so that it doesn't keep emailing you about the same event.
#
#####

class REIGarageSaleFinder(unittest.TestCase):
    
    BASE_URL = "https://www.rei.com/stores/saratoga.html" 
    
    # Email Info
    # Set these values
    from usernames_and_passwords import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_TO
    EMAIL_SUBJECT = "New REI Garage Sale Listing"
    SMTP_SERVER = "smtp.gmail.com" 
    SMTP_PORT = 465
    
    default_date_format = "%m/%d/%Y"
    # Expects the format: "6/1/2013" for June 1 (can be, but need not be zero padded)


    #########
    # Custom function to process REI website
    #########
    def test_garage_sale_finder(self):

        known_dates_filename = "known_dates"
        known_dates = set()
        if os.path.exists(known_dates_filename):
            with open(known_dates_filename, mode="r+") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    date = datetime.datetime.strptime(line, self.default_date_format)
                    known_dates.add(date)
                if raw_line[-1] not in {"\n", "\r"}:
                    #ensure last line is empty, so we print directly to a clean line later
                    print("", file=f)

        print("known dates: ", known_dates)

        driver = self.driver
        driver.get(self.BASE_URL)
        time.sleep(3)

        pages_text = driver.find_element_by_class_name("event-search-pages").text
        num_pages = int(pages_text.replace("Page","").replace("of", "").split()[-1])

        print("num_pages: ", num_pages)

        found_event_dates = []
        for i in range(num_pages):
            # get list of all events
            events = driver.find_elements_by_class_name("event-search-list-item")
            
            for event in events:

                # check if it has the correct event title
                event_name = event.find_element_by_xpath('.//a[@class="link-explore"]').text
                if "Garage Sale" in event_name:
                    date_text = event.find_element_by_xpath('.//p[@data-ui="event-details-date"]').text
                    print("event: ", event_name, " on ", date_text)
                    found_event_dates.append(datetime.datetime.strptime(date_text, self.default_date_format))

            if i+1 < num_pages:
                button_wrapper = driver.find_element_by_class_name("event-search-pages-forward")
                button_wrapper.find_element_by_xpath('.//a[@data-ui="event-search-pages-next"]').click()
                print("Going to page {} of {}".format(i+2, num_pages ))
                time.sleep(5)

        new_dates = [date for date in found_event_dates if date not in known_dates]
        for new_date in new_dates:
                print("new date:", new_date)
                with open(known_dates_filename, mode="a") as f:
                    f.write(new_date.strftime(self.default_date_format))


        if len(new_dates) > 0:
            print("Sending email of new date[s] to self")
            self.sendEmail(new_dates)
        
        
    def sendEmail(self, new_dates):
        # Create a text/plain message

        message = "Dates: \n"
        for date in new_dates:
            message += date.strftime(self.default_date_format) + "\n"

        message += "\n" + self.BASE_URL + "\n"

        msg = MIMEText(message)

        msg['Subject'] = self.EMAIL_SUBJECT
        msg['From'] = self.EMAIL_SENDER
        msg['To'] = self.EMAIL_TO

        # Send the message via provided server
        session = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT)
        
        # Login to the smtp server
        # session.ehlo()
        # session.starttls()
        # session.ehlo()
        session.login(self.EMAIL_SENDER, self.EMAIL_PASSWORD)
        
        session.sendmail(self.EMAIL_SENDER, [self.EMAIL_TO], msg.as_string())
        session.quit()
        
    #######
    # Selenium Functions - DO NOT MODIFY
    ######
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(60)
        self.verificationErrors = []
        self.accept_next_alert = True

######
# Main - initiates the program
######
if __name__ == "__main__":
    unittest.main()
    
