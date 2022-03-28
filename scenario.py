import logging
from random import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

class Scenario(object):
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def run(self):
        return NotImplementedError("Please derive from this class.")
    
    def run_baseline(self):
        self.run()
    
    def run_test(self):
        self.run()

    def driver(self):
        return self.webdriver

class DefaultScenario(Scenario):
    """Simply waits till a body tag appears and then proceeds."""
    def __init__(self, webdriver):
        super().__init__(webdriver)
    
    def run(self):
        wait = WebDriverWait(self.driver(), 5)
        wait.until(presence_of_element_located((By.TAG_NAME, "body")))
        # This line removes the random banner that is mistaken for a visual regression.
        self.driver().execute_script("try { mw.centralNotice.hideBanner(); } catch(e) {}")


class TamperScenario(DefaultScenario):
    """Tampers with the test run in random ways, but leaves the baseline run alone."""
    def __init__(self, driver):
        super().__init__(driver)
        logging.warn("RUNNING A TAMPER SCENARIO. THIS SHOULD ONLY BE USED FOR CREATING TEST DATA.")
        self.inject_js_contents = open("tweak.js", "r").read()

    def run_test(self):
        logging.warn("Tampering with page.")
        super().run_test()
        tamper = int(random() * 3)
        if tamper == 0:
            self.driver().execute_script(self.inject_js_contents + "\ntamperShowSomethingAdditional();")
            logging.warn("Added random overlay.")
        elif tamper == 1:
            self.driver().execute_script(self.inject_js_contents + "\ntamperAddRandomPadding();")
            logging.warn("Added random padding.")
        elif tamper == 2:
            self.driver().execute_script(self.inject_js_contents + "\ntamperAddText();")
            logging.warn("Added text.")
    

SCENARIOS = {
    "tamper": TamperScenario,
    "default": DefaultScenario
}

def get_scenario(name, driver):
    return SCENARIOS[name](driver)