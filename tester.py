# import selenium

URL = 'http://services.ecourts.gov.in/ecourtindia/cases/case_no.php?state=D&state_cd=26&dist_cd=6'

case_no = '12'
rgyear = '2017'

import pytesseract
import sys
import argparse

try:
    import Image
except ImportError:
    from PIL import Image
from subprocess import check_output


def resolve(path):
    print("Resampling the Image")
    check_output(['convert', path, '-resample', '600', path])
    return pytesseract.image_to_string(Image.open(path))


text = resolve("securimage_show-1.png")
print(text)
