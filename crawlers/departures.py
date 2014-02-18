# -*- coding: UTF-8 -*-

import json
import re

from datetime import timedelta, datetime, time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from crawlers.model import Departure


class DepartureCrawler:
    def __init__(self, driver):
        self.driver = driver

    def find(self, start_date, end_date):
        departures = []

        #TODO handle file that doesnt exist
        with open("routes.json") as routes_file:
            routes = json.load(routes_file)

        for route in routes:
            for route_date in self._daterange(start_date, end_date + timedelta(1)):
                route_departures = self._extract_departure(route, route_date)
                departures.extend(route_departures)

        self.driver.quit()
        return departures

    def _extract_departure(self, route, route_date):
        max_retries = 3
        departure_regex = re.compile(r"Departs (\d\d):(\d\d)")
        arrival_regex = re.compile(r"Arrives (\d\d):(\d\d)")
        duration_regex = re.compile(r"(\d*)hrs (\d*)mins")

        for _ in range(max_retries):
            try:
                departures = []
                self.driver.reload()
                self.driver.pass_landing_page()
                self._enter_origin_and_destination(route)
                self._enter_outbound_date(route_date)
                self._click_departures_search_button()
                departure_lines = self.driver.find_unclickable_elements_by_xpath(
                    "//div[@id='JourneyResylts_OutboundList_main_div']/ul")
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

                return departures

            except TimeoutException, e:
                print "Timeout Exception: " + str(_)

        return departures

    def _daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def _enter_origin_and_destination(self, route):
        origin = self._get_origin_select()
        origin.select_by_visible_text(route["origin"])
        destination = self._get_destination_select()
        destination.select_by_visible_text(route["destination"])

    def _enter_outbound_date(self, single_date):
        outbound_date = self._get_outbound_date_element()
        outbound_date.clear()
        outbound_date = self._get_outbound_date_element()
        outbound_date.send_keys(self._pretty_date(single_date))
        outbound_date.send_keys(Keys.TAB)

    def _pretty_date(self, date):
        return "{}/{}/{}".format(date.day, date.month, date.year)

    def _get_origin_select(self):
        return self.driver.find_select_by_id("JourneyPlanner_ddlLeavingFrom")

    def _get_destination_select(self):
        return self.driver.find_select_by_id("JourneyPlanner_ddlTravellingTo")

    def _get_outbound_date_element(self):
        return self.driver.find_element_by_id("JourneyPlanner_txtOutboundDate")

    #FIXME
    def _click_departures_search_button(self):
        try:
            search_btn = self.driver.find_element_by_id("JourneyPlanner_btnSearch")
            search_btn.click()
        except StaleElementReferenceException:
            search_btn = self.driver.find_element_by_id("JourneyPlanner_btnSearch")
            search_btn.click()

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