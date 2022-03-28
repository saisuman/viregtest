import datetime
from statusinfo import StatusInfo
import statusinfo
import time
import visual

DATE_FORMAT = "%Y-%d-%m:%H:%M.%sZ"
def fmtdate(ts):
    return datetime.datetime.fromtimestamp(ts).strftime(DATE_FORMAT)

class RunInfo(object):
    """Contains all information around a single run.
    
    Please note that this might also be a failed run, so it is important
    to check the status field before assuming that any of the other fields are
    sensibly populated."""
    def __init__(self, run_input):
        self.baseline_start = 0.0
        self.test_start = 0.0
        self.baseline_runtime = 0.0
        self.test_runtime = 0.0
        self.run_start_timestamp = 0.0
        self.run_end_timestamp = 0.0
        self.test_status = None
        self.baseline_status = None
        self.test_screenshot = None
        self.baseline_screenshot = None
        self.status = statusinfo.StatusInfo()
        self.report = None

    def to_dict(self):
        return {
            'baseline_runtime': "%d seconds" % self.baseline_runtime,
            'test_runtime': fmtdate(self.test_runtime),
            'run_start_timestamp': fmtdate(self.run_start_timestamp),
            'run_end_timestamp': fmtdate(self.run_end_timestamp),
            'test_status': self.test_status.to_dict(),
            'baseline_status': self.baseline_status.to_dict(),
            'test_screenshot': self.test_screenshot,
            'baseline_screenshot': self.baseline_screenshot,
            'report': {} if self.report == None else self.report.to_dict(),
        }

    def __str__(self):
        return str(self.to_dict())

    def start(self):
        if self.run_start_timestamp != 0.0:
            raise RuntimeError("start() has already been called.")
        self.failed = False
        self.run_start_timestamp = time.time()

    def start_baseline(self):
        self.baseline_start = time.time()

    def end_baseline(self, screenshot=None, status=None):
        if self.baseline_start == 0.0:
            raise RuntimeError("Call start_baseline first.")
        self.baseline_runtime = time.time() - self.baseline_start
        self.baseline_start = 0.0
        self.baseline_status = StatusInfo(statusinfo.OK) if status == None else status
        self.baseline_screenshot = screenshot

    def start_test(self):
        self.test_start = time.time()

    def end_test(self, screenshot=None, status=None):
        if self.test_start == 0.0:
            raise RuntimeError("Call end_baseline first.")
        self.test_runtime = time.time() - self.test_start
        self.test_start = 0.0
        self.test_status = StatusInfo(statusinfo.OK) if status == None else status
        self.test_screenshot = screenshot

    def end(self):
        if self.run_start_timestamp == 0.0:
            raise RuntimeError("start() must be called first.")
        self.run_end_timestamp = time.time()
        if not self.baseline_status.ok():
            self.status.message += "BASELINE FAILED (%s)\n" % self.baseline_status.message
        if not self.test_status.ok():
            self.status.message += "TEST FAILED (%s)\n" % self.test_status.message
        if self.test_status.ok() and self.baseline_status.ok():
            self.status.code = statusinfo.OK
        else:
            self.status.code = statusinfo.UNKNOWN_ERROR


class RunInput(object):
    """Contains the information required to start one url pair from one scenario."""
    def __init__(self, test_case_set_name, scenario, baseline_url, test_url, count):
        self.test_case_set_name = test_case_set_name
        self.scenario = scenario
        self.baseline_url = baseline_url
        self.test_url = test_url
        self.count = count

    def to_dict(self):
        return {
            'test_case_set_name': self.test_case_set_name,
            'scenario': self.scenario,
            'baseline_url': self.baseline_url,
            'test_url': self.test_url,
            'count': self.count,
        }

    def __str__(self):
        return "%s, %s, %s, %s, %s" % (
            self.test_case_set_name, self.scenario, self.baseline_url,
            self.test_url, self.count)

    def run_name(self, prefix=""):
        return "%s_%s_%05d" % (self.test_case_set_name, self.scenario, self.count)


class CompleteRun(object):
    """Contains information around a single run.
    
    There might be more than one RunInfo even if there is always exactly one
    RunInput because failures may cause retries."""
    def __init__(self, run_input, run_infos):
        self.run_input = run_input
        self.run_infos = run_infos

    def to_dict(self):
        return {
            'run_input': self.run_input.to_dict(),
            'run_infos': [x.to_dict() for x in self.run_infos]
        }


class CompleteReport(object):
    """Contains all the information around a visual regression test across all runs."""
    def __init__(self, config):
        self.config = config
        self.runs = []
        self.total_runs = 0
        self.total_in_tolerance = 0
        self.total_run_failures = 0
        self.total_perfect_matches = 0
        self.total_visual_regressions = 0

    def add_complete_run(self, complete_run):
        self.runs.append(complete_run)
        # TODO: We're ignoring all but the last run. Hence, the -1.
        r = complete_run.run_infos[-1]
        if r.report == None:
            self.total_run_failures += 1
        elif r.report.result == visual.RESULT_MATCH_WITHIN_TOLERANCE:
            self.total_in_tolerance+=1
        elif r.report.result == visual.RESULT_PERFECT_MATCH:
            self.total_perfect_matches +=1
        elif r.report.result == visual.RESULT_REGRESSION_FOUND:
            self.total_visual_regressions +=1
        elif r.report.result == visual.RESULT_RUN_INCOMPLETE:
            self.total_run_failures +=1
        self.total_runs += 1

    def to_dict(self):
        return {
            "config": self.config.to_dict(),
            "runs": [x.to_dict() for x in self.runs],
            "total_runs": self.total_runs,
            "total_in_tolerance": self.total_in_tolerance,
            "total_run_failures": self.total_run_failures,
            "total_perfect_matches": self.total_perfect_matches,
            "total_visual_regressions": self.total_visual_regressions,
        }
