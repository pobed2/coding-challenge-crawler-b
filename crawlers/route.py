from selenium.common.exceptions import TimeoutException

from crawlers.model import Route


MAX_RETRIES = 3
origin_select_id = "confirm1_ddlLeavingFromMap"
destination_select_id = "confirm1_ddlTravellingTo"


class RouteCrawler:
    def __init__(self, driver):
        self._driver = driver

    def find(self):
        routes = []

        self._driver.reload()
        self._driver.pass_landing_page()

        select = self._get_leaving_from_select()
        nb_of_from_options = len(select.options)

        for origin_option_index in range(1, nb_of_from_options):
            route_from_destination = self._extract_routes(origin_option_index)
            routes.extend(route_from_destination)

        self._driver.quit()
        return routes

    def _extract_routes(self, origin_option_index):
        for _ in range(MAX_RETRIES):
            try:
                routes = []

                #Reloading page to fix problem with option choosing
                self._driver.reload()
                origin_select = self._get_leaving_from_select()
                origin_option = origin_select.options[origin_option_index]

                #Select 'from'
                origin = origin_option.text
                origin_option.click()

                #Get all the destination options
                destination_select = self._get_going_to_select()
                nb_of_destination_options = len(destination_select.options)

                for destination_option_index in range(1, nb_of_destination_options):
                    destination = destination_select.options[destination_option_index].text
                    route = Route(origin, destination)
                    routes.append(route)
                return routes
            except TimeoutException:
                print "Timeout Exception: " + str(_)

        print "Could not get route. Skipping."

    def _get_leaving_from_select(self):
        return self._driver.find_select_by_id(origin_select_id)

    def _get_going_to_select(self):
        return self._driver.find_select_by_id(destination_select_id)