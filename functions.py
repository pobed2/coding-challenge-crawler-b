import json
from crawler import Crawler, StandardEncoder
from selenium import webdriver


def download_stops(file):
    driver = webdriver.PhantomJS()
    crawler = Crawler(driver)
    stations = crawler.find_stations()
    json.dump(stations, file, cls=StandardEncoder)

def download_routes(file):
    driver = webdriver.PhantomJS()
    crawler = Crawler(driver)
    routes = crawler.find_routes()
    json.dump(routes, file, cls=StandardEncoder)

def download_departures(file, start_date, end_date):
    driver = webdriver.Firefox()
    crawler = Crawler(driver)
    departures = crawler.find_departures(start_date, end_date)
    json.dump(departures, file, cls=StandardEncoder)
