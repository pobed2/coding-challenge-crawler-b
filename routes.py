# -*- coding: UTF-8 -*-

import json
from json import JSONEncoder
import re
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class Route:
    def __init__(self, origin, destination):
        self.origin = unicode(origin)
        self.destination = unicode(destination)

    def __str__(self):
        return self.origin + " " + self.destination

class RouteCrawler:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.url = "http://ca.megabus.com/BusStops.aspx"

    def find_routes(self):
        routes = []

        self.driver.get(self.url)
        self._pass_landing_page()

        select = self._get_leaving_from_select()
        nbOfFromOptions =  len(select.options)

        for fromOptionNb in range(1, nbOfFromOptions):
            #Reloading page to fix problem with option choosing
            print "RESTARTING"
            self.driver.get(self.url)

            fromSelect = self._get_leaving_from_select()
            fromOption = fromSelect.options[fromOptionNb]

            #Select 'from'
            origin = fromOption.text
            fromOption.click()

            #Get all the to options
            self.driver.implicitly_wait(1)
            toSelect = self._get_going_to_select()
            nbOfToOptions = len(toSelect.options)

            for toOptionNb in range(1, nbOfToOptions):                     
                #Create route
                destination = toSelect.options[toOptionNb].text
                route = Route(origin, destination)
                print route
                routes.append(route)

        self.driver.quit
        return routes

    def _pass_landing_page(self):
        if "landingcanada" in self.driver.current_url :
            self.driver.find_element_by_id("btnEnglishCanada").click()

    def _get_leaving_from_select(self):
        element = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_ddlLeavingFromMap")))
        return Select(element)

    def _get_going_to_select(self):
        element = self.wait.until(EC.element_to_be_clickable((By.ID,"confirm1_ddlTravellingTo")))
        return Select(element)

if __name__ == "__main__":
    driver = webdriver.PhantomJS()
    crawler = RouteCrawler(driver)
    stations = crawler.find_routes()
    #json.dump(stations, file, cls=StandardEncoder)
