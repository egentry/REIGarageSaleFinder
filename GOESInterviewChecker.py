from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, datetime, os
import smtplib
from email.mime.text import MIMEText

#####
# Authors: Mike Adler - May 3, 2013
#          Eric Gentry - May 2016
#
# GOESInterviewChecker - Used to automate checking of GOES interview times.
#
# This program will log in to your GOES account with the set values below,
# and will read the earliest date at your preferred enrollment center. 
# 
# If an opening exists within a given range, it will send you an email.
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
	EMAIL_SUBJECT = "GOES - Earlier Interview Found!" #subject of the email notification
	SMTP_SERVER = "smtp.gmail.com" #smtp server address to use for email sending
	SMTP_PORT = 465 #smtp server port number
	
	# **Must be in the format: "June 1, 2013"
	before_this_date_str = "December 1, 2016" 
	before_this_date = datetime.datetime.strptime(before_this_date_str,
												  "%B %d, %Y")

	# **Must be in the format: "June 1, 2013"
	after_this_date_str = "January 1, 2000" 
	after_this_date = datetime.datetime.strptime(after_this_date_str,
												  "%B %d, %Y")

	
	#########
	# Custom functions to process GOES Website Information
	#########
	def test_g_o_e_s_interview_checker(self):

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

		elem = driver.find_elements_by_css_selector(".header[id^='scheduleForm:schedule1_header_']")[0]
		available_date_str = elem.get_attribute("id").split("_")[-1]

		time.sleep(5)
		# log-off of your GOES account
		driver.find_element_by_link_text("Log off").click()


		available_date = datetime.datetime(int(available_date_str[0:4]),
										   int(available_date_str[4:6]),
										   int(available_date_str[6:]))

		# build email message
		emailMessage = available_date.strftime("%B %d, %Y")
		
		# if there's earlier dates, send the email
		if     (available_date < self.before_this_date) \
		   and (available_date > self.after_this_date):
			print("Better Date Found!")
			print("Sending Email Message: {}".format(emailMessage))
			self.sendEmail(emailMessage)
		else:
			print("NO better dates found.")
		
		
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
	
