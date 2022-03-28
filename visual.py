import io
from PIL import Image
from PIL import ImageChops

RESULT_PERFECT_MATCH = 1
RESULT_MATCH_WITHIN_TOLERANCE = 2
RESULT_REGRESSION_FOUND = 3
RESULT_RUN_INCOMPLETE = 4

_RESULT_NAMES = {
    RESULT_PERFECT_MATCH: "RESULT_PERFECT_MATCH",
    RESULT_REGRESSION_FOUND: "RESULT_REGRESSION_FOUND",
    RESULT_MATCH_WITHIN_TOLERANCE: "RESULT_MATCH_WITHIN_TOLERANCE",
    RESULT_RUN_INCOMPLETE: "RESULT_RUN_INCOMPLETE"
}


def check_diff(baseline_img, test_img):
    diffimg = ImageChops.difference(baseline_img, test_img)
    dbytes = diffimg.tobytes()  # Converted to RGB earlier, default is raw encoding with 3Bpp.
    diffcount = 0
    for i in range(diffimg.height * diffimg.width):
        r, g, b = dbytes[i * 3], dbytes[i * 3 + 1], dbytes[i * 3 + 2]
        if r + g + b != 0:
            diffcount += 1
    return diffcount

class VisualReport(object):
    """A report of a single visual regression test case."""
    def __init__(self, config, baseline_screenshot, test_screenshot):
        if baseline_screenshot is None or test_screenshot is None:
            self.result = RESULT_RUN_INCOMPLETE
            return
        bimg = Image.open(baseline_screenshot).convert('RGB')
        timg = Image.open(test_screenshot).convert('RGB')
        diffcount = check_diff(bimg, timg)
        self.diff_percentage = diffcount * 100.0 / bimg.width / bimg.height
        if self.diff_percentage == 0.0:
            self.result = RESULT_PERFECT_MATCH
        elif self.diff_percentage  < config.environment.max_diff_percentage:
            self.result = RESULT_MATCH_WITHIN_TOLERANCE
        else:
            self.result = RESULT_REGRESSION_FOUND        
        self.diff_percentage = diffcount * 100.0 / bimg.width / bimg.height
    
    def to_dict(self):
        return {
            "result": _RESULT_NAMES[self.result],
            "diff_percentage": "%0.2f" % self.diff_percentage
        }
    
    def __str__(self):
        return str(self.to_dict())
