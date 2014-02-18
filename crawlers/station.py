import re

from crawlers.model import Stop

coordinates_xpath = "//form[@id='ctl01']/script[11]"
destination_select_id = "confirm1_ddlTravellingTo"
location_description_xpath = "//div[@id='mapSelectArrowFrom']/div[@id='divFrom']/p[1]"
location_btn_id = "confirm1_hlFrom"
origin_select_id = "confirm1_ddlLeavingFromMap"
search_btn_id = "confirm1_btnSearch"


class StopCrawler:
    def __init__(self, driver):
        self.driver = driver
        self.coordinates_regex = re.compile(r"Microsoft.Maps.Location\((-?\d+\.\d+),(-?\d+\.\d+)\)")

    def find(self):
        stops = []

        self.driver.reload()
        self.driver.pass_landing_page()

        select = self.get_leaving_from_select()
        nb_of_options = len(select.options)

        for optionNb in range(1, nb_of_options):
            #Reloading page to fix problem with option choosing
            self.driver.reload()
            select = self.get_leaving_from_select()
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

                stop = Stop(name, location, latitude, longitude)
                stops.append(stop)

        self.driver.quit()
        return stops

    def get_leaving_from_select(self):
        return self.driver.find_select_by_id(origin_select_id)

    def _select_first_destination(self):
        select_to = self.driver.find_select_by_id(destination_select_id)
        select_to.options[1].click()

    def _click_search_button(self):
        search_btn = self.driver.find_element_by_id(search_btn_id)
        search_btn.click()

    def _extract_location(self):
        location_element = self._get_location_element()
        return self._removed_unused_text(u"The bus stop is located at the ",
                                         unicode(location_element.text)) #FIXME Text is always different...

    def _get_location_element(self):
        location_btn = self.driver.find_element_by_id(location_btn_id)
        location_btn.click()
        return self.driver.find_element_by_xpath(location_description_xpath)

    def _removed_unused_text(self, to_remove, text):
        return re.sub(to_remove, '', text)

    def _extract_coordinates(self):
        coordinate_script = self.driver.find_unclickable_element_by_xpath(coordinates_xpath)
        html = coordinate_script.get_attribute("innerHTML")
        match = self.coordinates_regex.search(html)
        return match.group(1), match.group(2)