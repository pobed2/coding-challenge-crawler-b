import re

from selenium.common.exceptions import TimeoutException

from crawlers.model import Stop

MAX_RETRIES = 3
coordinates_xpath = "//form[@id='ctl01']/script[11]"
destination_select_id = "confirm1_ddlTravellingTo"
location_description_xpath = "//div[@id='mapSelectArrowFrom']/div[@id='divFrom']/p[1]"
location_btn_id = "confirm1_hlFrom"
origin_select_id = "confirm1_ddlLeavingFromMap"
search_btn_id = "confirm1_btnSearch"


class StopCrawler:
    def __init__(self, driver):
        self._driver = driver
        self._coordinates_regex = re.compile(r"Microsoft.Maps.Location\((-?\d+\.\d+),(-?\d+\.\d+)\)")
        self._location_fallback_regex = re.compile(r"new simpleInfo\('(.*)','(.*)'\)")

    def find(self):
        stops = []

        self._driver.reload()
        self._driver.pass_landing_page()

        select = self.get_leaving_from_select()
        nb_of_options = len(select.options)

        for stop_option_index in range(1, nb_of_options):
            stop = self._extract_stop(stop_option_index)
            stops.append(stop)

        self._driver.quit()
        return stops

    def _extract_stop(self, stop_option_index):
        for _ in range(MAX_RETRIES):
            try:
                #Reloading page to fix problem with option choosing
                self._driver.reload()
                select = self.get_leaving_from_select()
                option = select.options[stop_option_index]
                if option.text != u"Select":
                    #Select 'from'
                    name = option.text
                    option.click()
                    #Select 'to'
                    self._select_first_destination()
                    self._click_search_button()

                    location = self._extract_location()
                    latitude, longitude = self._extract_coordinates()

                    return Stop(name, location, latitude, longitude)
            except TimeoutException:
                print "Timeout Exception: " + str(_) + ". Retrying."

        print "Could not get stop. Skipping."

    def get_leaving_from_select(self):
        return self._driver.find_select_by_id(origin_select_id)

    def _select_first_destination(self):
        select_to = self._driver.find_select_by_id(destination_select_id)
        select_to.options[1].click()

    def _click_search_button(self):
        search_btn = self._driver.find_element_by_id(search_btn_id)
        search_btn.click()

    def _extract_location(self):
        location_element = self._get_location_element()
        if location_element.text:
            return location_element.text
        else:
            return self._extract_location_with_fallback_element()

    def _get_location_element(self):
        location_btn = self._driver.find_element_by_id(location_btn_id)
        location_btn.click()
        return self._driver.find_element_by_xpath(location_description_xpath)

    def _extract_location_with_fallback_element(self):
        location_fallback = self._driver.find_unclickable_element_by_xpath(coordinates_xpath)
        html = location_fallback.get_attribute("innerHTML")
        match = self._location_fallback_regex.search(html)
        return u"{}. {}".format(match.group(1).strip(), match.group(2).strip())

    def _extract_coordinates(self):
        coordinate_script = self._driver.find_unclickable_element_by_xpath(coordinates_xpath)
        html = coordinate_script.get_attribute("innerHTML")
        match = self._coordinates_regex.search(html)
        return match.group(1), match.group(2)