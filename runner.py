#!/usr/bin/python3
import logging
import config
from run import CompleteReport, CompleteRun
from run import RunInfo

import scenario
import statusinfo
from statusinfo import StatusInfo
from rundirectory import RunDirectory

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import WebDriverException

from visual import VisualReport


def create_runner(config):
    return Runner(config)

class Runner(object):
    def __init__(self, config):
        self.config = config
        self.rundir = RunDirectory(config)
        self.started = False
        self.case_counter = 0
        self.complete_report = CompleteReport(self.config)

    def run(self):
        if self.started:
            raise RuntimeError("This runner has already been started.")
        self.started = True
        
        with webdriver.Chrome() as driver:
            for run_input in self.config.test_cases_by_scenario():
                run_infos = self.run_url_pair(driver, run_input)
                complete_run = CompleteRun(run_input, run_infos)
                self.rundir.write_run_info(complete_run)
                self.complete_report.add_complete_run(complete_run)
        return self.complete_report

    def run_url_pair(self, driver, run_input):
        retries_left = self.config.environment.max_retries
        scen = scenario.get_scenario(run_input.scenario, driver)
        attempts = []
        while retries_left >= 0:
            failed = False
            r = RunInfo(run_input)
            r.start()
            try:
                r.start_baseline()
                driver.get(run_input.baseline_url)
                scen.run_baseline()
                base_ss_filename = self.rundir.get_screenshot_file("base", run_input)
                driver.save_screenshot(base_ss_filename)
                r.end_baseline(screenshot=base_ss_filename)
            except WebDriverException as w:
                retries_left -= 1
                failed = True
                r.end_baseline(status=StatusInfo(statusinfo.RETRIABLE_ERROR, w.msg))
            try:
                r.start_test()
                driver.get(run_input.test_url)
                scen.run_test()
                test_ss_filename = self.rundir.get_screenshot_file("test", run_input)                
                driver.save_screenshot(test_ss_filename)
                r.report = VisualReport(self.config, base_ss_filename, test_ss_filename)
                r.end_test(screenshot=test_ss_filename)
            except WebDriverException as w:
                failed = True
                retries_left -= 1
                r.end_test(status=StatusInfo(statusinfo.RETRIABLE_ERROR, w.msg))
            r.end()
            attempts.append(r)
            if not failed:
                break
        return attempts

