import run
import json
import logging
from collections.abc import Iterable

# TODO: Replace all the validation here with a JSON schema instead.

def read_config(filename=None, contents=''):
    """Reads a config from either a given filename or the contents of a config file."""
    if not (filename or contents):
        raise ValueError("One of filename or contents must be specivied.")
    if filename:
        with open(filename, 'r') as f:
            return Config(f.read())
    return Config(contents)


class UrlPair(object):
    """Encapsulates a single visual regression test case involving two URLs."""
    def __init__(self, jsonobj):
        self.baseline_url = jsonobj["baseline_url"]
        self.test_url = jsonobj["test_url"]
    
    def to_dict(self):
        return {
            "baseline_url": self.baseline_url,
            "test_url": self.test_url
        }
    
    def __str__(self):
        return "  Baseline: %s vs Test: %s" % (self.baseline_url, self.test_url)


class Scenarios(object):
    """A Scenario is a configuiration that describes how to run the test.
    
    If there are interactions with the browser, or any flows and so on, these are
    encapsulated in the Scenario. Practically, these are names of Webdriver scripts.
    """
    def __init__(self, scenario_list):
        if not scenario_list or not isinstance(scenario_list, Iterable):
            raise ValueError("At least one scenario must be specified. Use 'default' in doubt.")
        self.scenarios = [str(x).strip() for x in scenario_list if len(x.strip()) != 0]
    
    def to_dict(self):
        return self.scenarios

    def __str__(self):
        return "  Scenarios: %s" % ",".join(self.scenarios)

        
class TestCaseSet(object):
    """Encapsulates a set of test cases that all share the same scenarios."""
    def __init__(self, case_set_dict):
        self.name = case_set_dict.get("name")
        self.scenarios = Scenarios(case_set_dict.get("scenarios"))
        self.url_pairs = [UrlPair(u) for u in case_set_dict.get("url_pairs")]

    def to_dict(self):
        return {
            "name": self.name,
            "scenarios": self.scenarios.to_dict(),
            "url_pairs": [x.to_dict() for x in self.url_pairs]
        }

    def __str__(self):
        return "TestCaseSet: %s\n%s" % (self.scenarios, "\n".join([str(x) for x in self.url_pairs]))

class Environment(object):
    """Catch-all for all configuration information that isn't specific to a test case."""
    def __init__(self, dict):
        self.name = dict.get("name", "Visual Regression Test"                                                                                                                                                                 )
        self.max_retries = dict.get("max_retries", 2)
        self.max_diff_percentage = dict.get("max_diff_percentage", 1.0)
        self.output_directory = dict.get("output_directory", ".")
    
    def to_dict(self):
        return {
            "name": self.name,
            "max_retries": self.max_retries,
            "max_diff_percentage": self.max_diff_percentage,
            "output_directory": self.output_directory,
        }


class Config(object):
    """Encapsulates a visual regression test config."""
    def __init__(self, contents=''):
        config_dict = json.loads(contents)
        logging.info("Loaded %d bytes into dict.", len(contents))
        self.environment = Environment(config_dict.get("environment", {}))
        self.test_case_sets = [TestCaseSet(t) for t in config_dict.get("test_case_sets")]
        logging.info("Config loaded: \n %s", json.dumps(self.to_dict(), indent=4))

    
    def to_dict(self):
        return {
            "environment": self.environment.to_dict(),
            "test_case_sets": [x.to_dict() for x in self.test_case_sets]
        }
    
    def test_cases_by_scenario(self, resume_from=0):
        """Helps iterate over all test cases by scenario."""
        counter = 0
        for tc in self.test_case_sets:
            for sc in tc.scenarios.scenarios:
                for up in tc.url_pairs:
                    if resume_from > counter:
                        counter += 1
                        continue
                    yield run.RunInput(tc.name, sc, up.baseline_url, up.test_url, counter)
                    counter += 1

    def __str__(self):
        return "Config \n%s" % ("\n".join([str(tc) for tc in self.test_case_sets]))
