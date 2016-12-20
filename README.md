# REI Garage Sale Finder
 
## Introduction

This script can be used to automate finding new REI Garage Sales at REI Saratoga.

If a new Garage Sale is found, it'll send you an email, and then remember that date, so that it won't keep pestering you about that date.

This is ideally intended to be setup as a unix cronjob, but you can automate it however you like. If you do plan to use it with crontab, you'll need to edit `crontabREI` to first change into this local directory before running the python command. E.g.:
```0 3 * * * cd /path/to/REIGarageSaleFinder && python REIGarageSaleFinder.py 1>log 2>&1```


Requires:
- [Selenium](http://docs.seleniumhq.org/download/) for python
	- Expects [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/), but it can be re-configured to use other browsers
	