# -*- coding: UTF-8 -*-

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class SingleUrlNonGreedyDriver(object):
    '''
    WebDriver that can only manage one url.
    Always waits for elements to be clickable before returning.
    '''

    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def reload(self):
        self.driver.get(self.url)

    def quit(self):
        self.driver.quit()

    #TODO Should not be in driver...
    def pass_landing_page(self):
        if "landingcanada" in self.driver.current_url:
            self.driver.find_element_by_id("btnEnglishCanada").click()

    def find_select_by_id(self, element_id):
        try:
            element = self._create_wait().until(EC.element_to_be_clickable((By.ID, element_id)))
            return Select(element)
        except StaleElementReferenceException:
            return self._handle_stale_element(self.find_select_by_id, element_id)

    def find_element_by_id(self, element_id):
        try:
            return self._create_wait().until(EC.element_to_be_clickable((By.ID, element_id)))
        except StaleElementReferenceException:
            return self._handle_stale_element(self.find_element_by_id, element_id)

    def find_element_by_xpath(self, element_xpath):
        try:
            return self._create_wait().until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
        except StaleElementReferenceException:
            return self._handle_stale_element(self.find_element_by_xpath, element_xpath)

    def find_unclickable_element_by_xpath(self, element_xpath):
        try:
            return self.driver.find_element_by_xpath(element_xpath)
        except StaleElementReferenceException:
            return self._handle_stale_element(self.find_unclickable_element_by_xpath, element_xpath)

    def find_unclickable_elements_by_xpath(self, elements_xpath):
        try:
            return self.driver.find_elements_by_xpath(elements_xpath)
        except StaleElementReferenceException:
            return self._handle_stale_element(self.find_unclickable_elements_by_xpath, elements_xpath)

    def _create_wait(self):
        return WebDriverWait(self.driver, 5)

    #FIXME probably doesn't work...
    def _handle_stale_element(self, func, *args):
        max_retries = 3
        for _ in range(max_retries):
            try:
                return func(*args)
            except StaleElementReferenceException:
                print "Handling stale element: " + str(_)
                if _ is max_retries:
                    raise
                return func(*args)


class PhantomJsSingleUrlNonGreedyDriver(SingleUrlNonGreedyDriver):
    '''
    PhantomJS WebDriver that can only manage one url.
    Always waits for elements to be clickable before returning.
    '''

    def __init__(self, url):
        super(PhantomJsSingleUrlNonGreedyDriver, self).__init__(webdriver.PhantomJS(), url)


class FirefoxSingleUrlNonGreedyDriver(SingleUrlNonGreedyDriver):
    '''
    Firefox WebDriver that can only manage one url.
    Always waits for elements to be clickable before returning.
    '''

    def __init__(self, url):
        super(FirefoxSingleUrlNonGreedyDriver, self).__init__(webdriver.Firefox(), url)


class ChromeSingleUrlNonGreedyDriver(SingleUrlNonGreedyDriver):
    '''
    Chrome WebDriver that can only manage one url.
    Always waits for elements to be clickable before returning.
    '''

    def __init__(self, url):
        super(ChromeSingleUrlNonGreedyDriver, self).__init__(webdriver.Chrome(), url)