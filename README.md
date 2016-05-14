# GOES NEXUS Interview Checker
 
## Introduction

This script can be used to automate checking of GOES NEXUS interview times. It will find the earliest interview available at your location. If that location falls within your acceptable range of dates, and is not in your list of excluded dates, it will reschedule your interview. If your interview is rescheduled, you will be emailed, and it will stop looking for new interviews.

Requires:
- [Selenium](http://docs.seleniumhq.org/download/) for python
	- Expects [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/), but it can be re-configured to use other browsers
