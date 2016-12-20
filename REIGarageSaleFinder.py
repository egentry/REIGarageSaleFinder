from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, datetime, os
from multiprocessing import Pool
import smtplib
from email.mime.text import MIMEText

#####
# Authors: Mike Adler - May 3, 2013
#          Eric Gentry - May 2016
#
# GOESInterviewChecker - Used to automate checking and rescheduling GOES interview.
#
# This program will log in to your GOES account with the set values below,
# and will read the earliest date at your preferred enrollment center. 
# 
# If an opening exists within a given range,  and is not found in `excluded_dates`
# it will reschedule your appointment to the earliest opening and send you an email.
#
# If it reschedules your interview, it will create the file "rescheduled_interview"
#
# If it finds the file "rescheduled_interview" it will not keep checking the website.
#
#####

class GOESInterviewChecker(unittest.TestCase):
	
	# GOES Account Info
	# Set these values
	# Note: Preferred enrollment center value is the text value in the enrollment center dropdown menu
	from usernames_and_passwords import GOES_USERNAME, GOES_PASSWORD
	GOES_BASE_URL = "https://goes-app.cbp.dhs.gov/" 
	GOES_PREFERRED_ENROLLMENT_CENTER = "San Francisco Global Entry Enrollment Center - San Francisco International Airport, San Francisco, CA 94128, US"
	
	# Email Info
	# Set these values
	from usernames_and_passwords import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_TO
	EMAIL_SUBJECT = "GOES - New Interview Scheduled!"
	SMTP_SERVER = "smtp.gmail.com" 
	SMTP_PORT = 465
	
	default_date_format = "%B %d, %Y"
	# **Must be in the format: "June 1, 2013"
	before_this_date_str = "December 10, 2016" 
	before_this_date = datetime.datetime.strptime(before_this_date_str,
												 default_date_format)

	# **Must be in the format: "June 1, 2013"
	after_this_date_str = "January 1, 2000" 
	after_this_date = datetime.datetime.strptime(after_this_date_str,
												 default_date_format)

	excluded_dates = [
		"January 1, 2000",
		"February 1, 2000",
		"March 1, 2000",
	]
	for i in range(len(excluded_dates)):
		# because list comprehensions won't work in class definitions
		excluded_dates[i] = datetime.datetime.strptime(excluded_dates[i],
													   default_date_format)
	
	#########
	# Custom functions to process GOES Website Information
	#########
	def test_g_o_e_s_interview_checker(self):

		if os.path.exists("rescheduled_interview"):
			return

		driver = self.driver
		driver.get(self.GOES_BASE_URL + "/main/goes")
		time.sleep(2)
		# driver.find_element_by_id("user").clear()
		driver.find_element_by_id("user").send_keys(self.GOES_USERNAME)
		# driver.find_element_by_id("password").clear()
		driver.find_element_by_id("password").send_keys(self.GOES_PASSWORD)
		driver.find_element_by_id("SignIn").click()
		driver.find_element_by_link_text("Enter").click()
		time.sleep(2)
		driver.find_element_by_name("manageAptm").click()
		driver.find_element_by_name("reschedule").click()
				
		dropdown = driver.find_element_by_id("selectedEnrollmentCenter")
		
		# select preferred enrollment center
		for option in dropdown.find_elements_by_tag_name('option'):
			if option.text == self.GOES_PREFERRED_ENROLLMENT_CENTER:
				option.click() 
				break
				
		driver.find_element_by_name("next").click()

		available_datetime_str = driver.find_element_by_class_name("entry").get_attribute("onmouseup")
		available_datetime_str = available_datetime_str.split("'")[-2]

		available_date = datetime.datetime(int(available_datetime_str[0:4]),
										   int(available_datetime_str[4:6]),
										   int(available_datetime_str[6:-4]))
		available_time = available_datetime_str[-4:]

		if    (available_date > self.before_this_date) \
		   or (available_date < self.after_this_date) \
		   or (available_date in self.excluded_dates):
			print("No better dates found.")
			driver.find_element_by_link_text("Log off").click()
			return

		driver.find_element_by_class_name("entry").click()
		try:
			driver.find_element_by_id("comments").send_keys("Better date")
		except NoSuchElementException:
			driver.find_element_by_link_text("Log off").click()
			return

		driver.find_element_by_id("Confirm").click()

		time.sleep(5)
		driver.find_element_by_link_text("Log off").click()

		available_date_str = available_date.strftime(self.default_date_format)
		new_appointment = "{}:{} {}".format(available_time[0:2], 
											available_time[2:],
											available_date_str)

		with open("rescheduled_interview", mode="w") as f:
			f.write(new_appointment)

		print("Better Date Found!")
		print("Sending Email Message: {}".format(new_appointment))
		self.sendEmail(new_appointment)
		
		
	def sendEmail(self, message):
		# Create a text/plain message
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
		
	def is_element_present(self, how, what):
		try: self.driver.find_element(by=how, value=what)
		except NoSuchElementException: return False
		return True

	def is_alert_present(self):
		try: self.driver.switch_to_alert()
		except NoAlertPresentException: return False
		return True

	def close_alert_and_get_its_text(self):
		try:
			alert = self.driver.switch_to_alert()
			alert_text = alert.text
			if self.accept_next_alert:
				alert.accept()
			else:
				alert.dismiss()
			return alert_text
		finally: self.accept_next_alert = True

	def tearDown(self):
		# self.driver.quit()
		self.assertEqual([], self.verificationErrors)

######
# Main - initiates the program
######
if __name__ == "__main__":
	unittest.main()
	
