from crawlers.model import Route

destination_select_id = "confirm1_ddlTravellingTo"

origin_select_id = "confirm1_ddlLeavingFromMap"


class RouteCrawler:
    def __init__(self, driver):
        self.driver = driver

    def find(self):
        routes = []

        self.driver.reload()
        self.driver.pass_landing_page()

        select = self._get_leaving_from_select()
        nb_of_from_options = len(select.options)

        for fromOptionNb in range(1, nb_of_from_options):
            #Reloading page to fix problem with option choosing
            self.driver.reload()

            from_select = self._get_leaving_from_select()
            from_option = from_select.options[fromOptionNb]

            #Select 'from'
            origin = from_option.text
            from_option.click()

            #Get all the to options
            to_select = self._get_going_to_select()
            nb_of_to_options = len(to_select.options)

            for toOptionNb in range(1, nb_of_to_options):
                destination = to_select.options[toOptionNb].text
                route = Route(origin, destination)
                routes.append(route)

        self.driver.quit()
        return routes

    def _get_leaving_from_select(self):
        return self.driver.find_select_by_id(origin_select_id)

    def _get_going_to_select(self):
        return self.driver.find_select_by_id(destination_select_id)