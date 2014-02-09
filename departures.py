# -*- coding: UTF-8 -*-

from datetime import timedelta, datetime, date, time
import json
from json import JSONEncoder
import re
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException


class Departure:
    def __init__(self, origin, destination, departure_time, arrival_time, duration, price):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration
        self.price = price

    def __str__(self):
        return "{} {} {} {} {} {}".format(self.origin ,self.destination,self.departure_time , self.arrival_time,self.duration, self.price)

class DepartureCrawler:

    def __init__(self, driver):
        self.driver = driver
        self.url = "http://ca.megabus.com/Default.aspx"

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)


    def find_departures(self, start_date, end_date):
        departures = []

        with open("routes.json") as routes_file:
            routes = json.load(routes_file)
            
        for route in routes:
            for single_date in self.daterange(start_date, end_date + timedelta(1)):
                self.driver.get(self.url)
                self._pass_landing_page()

                origin = self._get_origin_select()
                origin.select_by_visible_text(route["origin"])

                destination = self._get_destination_select()
                destination.select_by_visible_text(route["destination"])

                outbound_date = self._get_outbound_date_element()
                outbound_date.clear()               

                WebDriverWait(self.driver, 10).until_not(EC.element_to_be_clickable((By.ID,"JourneyPlanner_btnSearch")))
                outbound_date = self._get_outbound_date_element()
                
                outbound_date.send_keys(self._pretty_date(single_date))
                outbound_date.send_keys(Keys.ENTER)

                self._click_search_button()

                lines = self.driver.find_elements_by_xpath("//div[@id='JourneyResylts_OutboundList_main_div']/ul")

                #skip first line
                if(len(lines)>1):
                    iterlines = iter(lines)
                    next(iterlines)
                    for line in iterlines:
                        elements = line.find_elements_by_xpath("li")
                        departure_regex = r"Departs (\d\d):(\d\d)"
                        arrival_regex = r"Arrives (\d\d):(\d\d)"
                        duration_regex = r"(\d*)hrs (\d*)mins"

                        
                        arrival_time = re.search(arrival_regex, elements[1].text)
                        arrival_date = datetime.combine(single_date, time()).replace(hour=int(arrival_time.group(1)), minute=int(arrival_time.group(2)))

                        
                        departure_time = re.search(departure_regex, elements[1].text)
                        departure_date = datetime.combine(single_date, time()).replace(hour=int(departure_time.group(1)), minute=int(departure_time.group(2)))

                        if(arrival_date < departure_date):
                            arrival_date = arrival_date + timedelta(days=1)

                        duration = re.search(duration_regex, elements[2].text)
                        pretty_duration = "{}:{}".format(duration.group(1), duration.group(2))
                        price = float(re.sub('\$', '', elements[5].text))                       
                    
                        departure = Departure(route["origin"], route["destination"], departure_date, arrival_date, pretty_duration, price)
                        print departure

        self.driver.quit
        return departures

    def _pretty_date(self, date):
        return "{}/{}/{}".format(date.day, date.month, date.year)

    def _pass_landing_page(self):
        if "landingcanada" in self.driver.current_url :
            self.driver.find_element_by_id("btnEnglishCanada").click()

    def _get_origin_select(self):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"JourneyPlanner_ddlLeavingFrom")))
        return Select(element)

    def _get_destination_select(self):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"JourneyPlanner_ddlTravellingTo")))
        return Select(element)

    def _get_outbound_date_element(self):
        return WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"JourneyPlanner_txtOutboundDate")))

    def _click_search_button(self):
        try:
            searchBtn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"JourneyPlanner_btnSearch")))
            searchBtn.click()
        except StaleElementReferenceException:
            searchBtn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID,"JourneyPlanner_btnSearch")))
            searchBtn.click()

if __name__ == "__main__":
    driver = webdriver.Firefox()
    crawler = DepartureCrawler(driver)
    departures = crawler.find_departures(date.today()+ timedelta(days=10), date.today() + timedelta(days=13))
