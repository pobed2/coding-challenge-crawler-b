# -*- coding: UTF-8 -*-

import json
from json import JSONEncoder
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class StandardEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__ 

class Station:
    def __init__(self, name, location, latitude, longitutde):
        self.name = unicode(name)
        self.location = unicode(location)
        self.lat = unicode(latitude)
        self.long = unicode(longitutde)

    def __str__(self):
        return self.name + " " + self.location + " " + self.lat + " " + self.long

class StationCrawler:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.url = "http://ca.megabus.com/BusStops.aspx"

    def find_stations(self):
        stations = []

        self.driver.get(self.url)
        self._pass_landing_page()

        select = self._get_leaving_from_select()
        nbOfOptions =  len(select.options)

        for optionNb in range(1, nbOfOptions):
            #Reloading page to fix problem with option choosing
            self.driver.get(self.url)
            select = self._get_leaving_from_select()
            option = select.options[optionNb]

            if(option.text != u"Select"):
                #Select 'from'
                name = option.text
                option.click()
                #Select 'to'
                self._select_first_destination()
                self._click_search_button()

                location = self._extract_location()
                latitude, longitutde = self._extract_coordinates()

                station = Station(name, location, latitude, longitutde)
                #print station
                stations.append(station)

        self.driver.quit
        print json.dumps(stations, cls=StandardEncoder)
        return stations

    def _pass_landing_page(self):
        if "landingcanada" in self.driver.current_url :
            self.driver.find_element_by_id("btnEnglishCanada").click()

    def _get_leaving_from_select(self):
        element = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_ddlLeavingFromMap")))
        return Select(element)

    def _select_first_destination(self):
        elementTo = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_ddlTravellingTo")))
        selectTo = Select(elementTo)
        selectTo.options[1].click()


    def _click_search_button(self):
        searchBtn = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_btnSearch")))
        searchBtn.click()

    def _extract_location(self):
        locationElement = self._get_location_element()
        return self._removed_unused_text(u"The bus stop is located at the ", unicode(locationElement.text))  

        

    def _get_location_element(self):
        locationBtn  = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_hlFrom")))
        locationBtn.click()
        return self.driver.find_element_by_xpath("//div[@id='mapSelectArrowFrom']/div[@id='divFrom']/p[1]")

    def _removed_unused_text(self, toRemove, text):
        return re.sub(toRemove, '', text)

    def _extract_coordinates(self):
        script = self.driver.find_element_by_xpath("//form[@id='ctl01']/script[11]").get_attribute("innerHTML")
        lineToMatch = r"Microsoft.Maps.Location\((-?\d+\.\d+),(-?\d+\.\d+)\)"
        match = re.search(lineToMatch, script);
        return match.group(1), match.group(2)
