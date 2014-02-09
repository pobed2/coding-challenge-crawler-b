import json
import io
from stations import StationCrawler, StandardEncoder
from routes import RouteCrawler
from departures import DepartureCrawler
from selenium import webdriver

def download_stops(file):
	driver = webdriver.PhantomJS()
	crawler = StationCrawler(driver)
	stations = crawler.find_stations()
	json.dump(stations, file, cls=StandardEncoder)

def download_routes(file):
	driver = webdriver.PhantomJS()
	crawler = RouteCrawler(driver)
	routes = crawler.find_routes()
	json.dump(routes, file, cls=StandardEncoder)

def download_departures(file, start_date, end_date):
	driver = webdriver.Firefox()
	crawler = DepartureCrawler(driver)
	departures = crawler.find_departures(start_date, end_date)
	json.dump(departures, file, cls=StandardEncoder)