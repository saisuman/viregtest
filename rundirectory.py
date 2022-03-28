import config
import os
import json
import logging
import hashlib

from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "screenshot_dir", "screenshots",
    "The directory to place screenshots in. Created if missing.")
flags.DEFINE_string("runinfo_dir", "runinfo",
    "The directory to place runinfo files in. Created if missing.")


class RunDirectory(object):
    """Functionality for managing a run directory and the files written therein."""

    def __init__(self, config):
        self.config = config
        self.dir = config.environment.output_directory
        if not self.dir:
            self.dir = os.getcwd()
        self.complete = False
        logging.info("Using %s as a run directory.", self.dir)
        self.screenshot_dir = os.path.join(self.dir, FLAGS.screenshot_dir)
        self.runinfo_dir = os.path.join(self.dir, FLAGS.runinfo_dir)
        self.check_or_init_dirs()
        logging.info("Writing screenshots to %s.", self.screenshot_dir)
        logging.info("Writing run info to %s.", self.runinfo_dir)

    def check_or_init_dirs(self):
        dirs = [self.dir, self.runinfo_dir, self.screenshot_dir]
        for d in dirs:
            if os.path.lexists(d) and not os.path.isdir(d):
                raise RuntimeError("%s exists and is not a directory.", d)
            if not os.path.lexists(d):
                os.mkdir(d)

    def get_screenshot_file(self, prefix, run_input):
        return os.path.join(self.screenshot_dir, "%s_%s.png" % (prefix, run_input.run_name()))

    def write_run_info(self, complete_run):
        open(self.get_run_info_filename(complete_run.run_input),
             "w").write(json.dumps(complete_run.to_dict(), indent=4))
    
    def get_run_info_filename(self, run_input):
        return os.path.join(self.runinfo_dir, run_input.run_name() + ".json")
