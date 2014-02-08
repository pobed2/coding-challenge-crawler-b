import json
import io
from stations import StationCrawler, StandardEncoder
from selenium import webdriver

def download_stops(file):
	driver = webdriver.PhantomJS()
	crawler = StationCrawler(driver)
	stations = crawler.find_stations()
	json.dump(stations, file, cls=StandardEncoder)
