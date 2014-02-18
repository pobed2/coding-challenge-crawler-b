import json

from utils import StandardEncoder
from drivers import PhantomJsSingleUrlNonGreedyDriver
from crawlers.departures import DepartureCrawler
from crawlers.route import RouteCrawler
from crawlers.station import StopCrawler


def download_stops(file):
    driver = PhantomJsSingleUrlNonGreedyDriver("http://ca.megabus.com/BusStops.aspx")
    crawler = StopCrawler(driver)
    stations = crawler.find()
    write_to_json(stations, file)


def download_routes(file):
    driver = PhantomJsSingleUrlNonGreedyDriver("http://ca.megabus.com/BusStops.aspx")
    crawler = RouteCrawler(driver)
    routes = crawler.find()
    write_to_json(routes, file)


def download_departures(file, start_date, end_date):
    driver = PhantomJsSingleUrlNonGreedyDriver("http://ca.megabus.com/BusStops.aspx")
    crawler = DepartureCrawler(driver)
    departures = crawler.find(start_date, end_date)
    write_to_json(departures, file)


def write_to_json(data, file):
    json.dump(data, file, cls=StandardEncoder)

