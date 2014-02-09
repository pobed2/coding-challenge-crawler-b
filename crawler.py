# -*- coding: UTF-8 -*-

import json
import re

from datetime import timedelta, datetime, time
from json import JSONEncoder
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from model import Station, Route, Departure


class StandardEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.url = "http://ca.megabus.com/BusStops.aspx"

    def find_stations(self):
        stations = []

        self.driver.get(self.url)
        self._pass_landing_page()

        select = self._get_leaving_from_select()
        nb_of_options = len(select.options)

        for optionNb in range(1, nb_of_options):
            #Reloading page to fix problem with option choosing
            self.driver.get(self.url)
            select = self._get_leaving_from_select()
            option = select.options[optionNb]

            if option.text != u"Select":
                #Select 'from'
                name = option.text
                option.click()
                #Select 'to'
                self._select_first_destination()
                self._click_search_button()

                location = self._extract_location()
                latitude, longitude = self._extract_coordinates()

                station = Station(name, location, latitude, longitude)
                stations.append(station)

        self.driver.quit
        return stations

    def find_routes(self):
        routes = []

        self.driver.get(self.url)
        self._pass_landing_page()

        select = self._get_leaving_from_select()
        nb_of_from_options = len(select.options)

        for fromOptionNb in range(1, nb_of_from_options):
            #Reloading page to fix problem with option choosing
            self.driver.get(self.url)

            from_select = self._get_leaving_from_select()
            from_option = from_select.options[fromOptionNb]

            #Select 'from'
            origin = from_option.text
            from_option.click()

            #Get all the to options
            self.driver.implicitly_wait(1)
            to_select = self._get_going_to_select()
            nb_of_to_options = len(to_select.options)

            for toOptionNb in range(1, nb_of_to_options):
                destination = to_select.options[toOptionNb].text
                route = Route(origin, destination)
                routes.append(route)

        self.driver.quit
        return routes

    def find_departures(self, start_date, end_date):
        departures = []

        departure_regex = re.compile(r"Departs (\d\d):(\d\d)")
        arrival_regex = re.compile(r"Arrives (\d\d):(\d\d)")
        duration_regex = re.compile(r"(\d*)hrs (\d*)mins")

        with open("routes.json") as routes_file:
            routes = json.load(routes_file)

        for route in routes:
            for route_date in self.daterange(start_date, end_date + timedelta(1)):
                self.driver.get(self.url)
                self._pass_landing_page()

                self._enter_origin_and_destination(route)
                self._enter_outbound_date(route_date)
                self._click_departures_search_button()

                departure_lines = self.driver.find_elements_by_xpath("//div[@id='JourneyResylts_OutboundList_main_div']/ul")


                if len(departure_lines) > 1:
                    #skip first line
                    iterlines = iter(departure_lines)
                    next(iterlines)
                    for line in iterlines:
                        departure_line = line.find_elements_by_xpath("li")

                        departure_date = self._extract_departure_date(route_date, departure_line, departure_regex)
                        arrival_date = self._extract_arrival_date(departure_line, route_date, arrival_regex)
                        arrival_date = self._verify_arrival_day(arrival_date, departure_date)
                        pretty_duration = self._extract_duration(departure_line, duration_regex)
                        price = self._extract_price(departure_line)

                        departure = Departure(route["origin"], route["destination"], departure_date, arrival_date,
                                              pretty_duration, price)
                        departures.append(departure)
                        print departure

        self.driver.quit
        return departures

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def _pass_landing_page(self):
        if "landingcanada" in self.driver.current_url:
            self.driver.find_element_by_id("btnEnglishCanada").click()

    def _get_leaving_from_select(self):
        element = self.wait.until(EC.element_to_be_clickable((By.ID, "confirm1_ddlLeavingFromMap")))
        return Select(element)

    def _get_going_to_select(self):
        element = self.wait.until(EC.element_to_be_clickable((By.ID, "confirm1_ddlTravellingTo")))
        return Select(element)

    def _select_first_destination(self):
        element_to = self.wait.until(EC.element_to_be_clickable((By.ID, "confirm1_ddlTravellingTo")))
        select_to = Select(element_to)
        select_to.options[1].click()

    def _click_search_button(self):
        search_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "confirm1_btnSearch")))
        search_btn.click()

    def _extract_location(self):
        location_element = self._get_location_element()
        return self._removed_unused_text(u"The bus stop is located at the ", unicode(location_element.text))

    def _get_location_element(self):
        location_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "confirm1_hlFrom")))
        location_btn.click()
        return self.driver.find_element_by_xpath("//div[@id='mapSelectArrowFrom']/div[@id='divFrom']/p[1]")

    def _removed_unused_text(self, to_remove, text):
        return re.sub(to_remove, '', text)

    def _extract_coordinates(self):
        script = self.driver.find_element_by_xpath("//form[@id='ctl01']/script[11]").get_attribute("innerHTML")
        lineToMatch = r"Microsoft.Maps.Location\((-?\d+\.\d+),(-?\d+\.\d+)\)"
        match = re.search(lineToMatch, script);
        return match.group(1), match.group(2)

    def _pretty_date(self, date):
        return "{}/{}/{}".format(date.day, date.month, date.year)

    def _get_origin_select(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "JourneyPlanner_ddlLeavingFrom")))
        return Select(element)

    def _get_destination_select(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "JourneyPlanner_ddlTravellingTo")))
        return Select(element)

    def _get_outbound_date_element(self):
        return WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "JourneyPlanner_txtOutboundDate")))

    def _click_departures_search_button(self):
        try:
            search_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "JourneyPlanner_btnSearch")))
            search_btn.click()
        except StaleElementReferenceException:
            search_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "JourneyPlanner_btnSearch")))
            search_btn.click()

    def _enter_origin_and_destination(self, route):
        origin = self._get_origin_select()
        origin.select_by_visible_text(route["origin"])
        destination = self._get_destination_select()
        destination.select_by_visible_text(route["destination"])

    def _enter_outbound_date(self, single_date):
        outbound_date = self._get_outbound_date_element()
        outbound_date.clear()
        WebDriverWait(self.driver, 10).until_not(
            EC.element_to_be_clickable((By.ID, "JourneyPlanner_btnSearch")))
        outbound_date = self._get_outbound_date_element()
        outbound_date.send_keys(self._pretty_date(single_date))
        outbound_date.send_keys(Keys.ENTER)

    def _extract_arrival_date(self, departure_line, current_date, arrival_regex):
        arrival_time = arrival_regex.search(departure_line[1].text)
        arrival_date = datetime.combine(current_date, time()).replace(hour=int(arrival_time.group(1)),
                                                                      minute=int(arrival_time.group(2)))
        return arrival_date

    def _extract_departure_date(self, current_date, departure_line, departure_regex):
        departure_time = departure_regex.search(departure_line[1].text)
        departure_date = datetime.combine(current_date, time()).replace(
            hour=int(departure_time.group(1)), minute=int(departure_time.group(2)))
        return departure_date

    def _verify_arrival_day(self, arrival_date, departure_date):
        if arrival_date < departure_date:
            arrival_date = arrival_date + timedelta(days=1)
        return arrival_date

    def _extract_price(self, departure_line):
        price = float(re.sub('\$', '', departure_line[5].text))
        return price

    def _extract_duration(self, departure_line, duration_regex):
        duration = duration_regex.search(departure_line[2].text)
        pretty_duration = "{}:{}".format(duration.group(1), duration.group(2))
        return pretty_duration
