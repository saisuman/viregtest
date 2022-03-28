import logging
import config
import runner
import json
import chevron

from absl import app, flags

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "config_file", "config.json",
    "The configuration file for running visual regression tests.")
flags.DEFINE_string(
    "report_template",
    "report.mustache.html", "The mustache template file for generating HTML reports.")
flags.DEFINE_string("report_file", "report.html",
    "The path to place the report file in.")


logging.basicConfig(
    format="%(asctime)s %(filename)s.%(funcName)s %(message)s",
    level=logging.INFO)


def main(args):
    report = runner.create_runner(
        config.read_config(filename=FLAGS.config_file)).run()
    open(FLAGS.report_file, "w").write(
        chevron.render(open(FLAGS.report_template).read(),
        report.to_dict()))
    logging.info("Finished all runs, report saved in report.html.")


if __name__ == "__main__":
    app.run(main)