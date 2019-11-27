import requests
from lxml import html
import json
from PIL import Image
import pytesseract
import re

r = requests.session()


def getCaptchaText(captcha):
    rcaptcha = r.get(captcha)
    f = open('yourcaptcha.png', 'wb')
    f.write(rcaptcha.content)
    f.close()
    im = Image.open("yourcaptcha.png")
    text = pytesseract.image_to_string(im, lang='eng')
    if len(text) != 3:
        text = getCaptchaText()
    return text


def getCaseHistory(cno, cyear, ctype):
    url = "http://164.100.128.47/case/guiCaseWise.php"
    rurl = requests.get(url)

    htmlwa = (rurl.text)
    tree = html.fromstring(htmlwa)

    captcha = "http://164.100.128.47/case/" + tree.xpath('//img[@id="captchaimg"]/@src')[0]

    i = 1
    while i == 1:
        text = getCaptchaText(captcha)
        ctype = ctype
        regno = cno
        regyr = cyear
        letters_code = text.encode('UTF-8')
        data = [
            ('ctype', ctype),
            ('regno', regno),
            ('regyr', regyr),
            ('6_letters_code', letters_code),
            ('Submit', "Submit"), ]
        url = "http://164.100.128.47/case/s_adv.php"
        r2 = r.post(url=url, data=data)
        if "You had entered the wrong validation code" in r2.text:
            pass
        else:
            i += 1

    htmlwa = (r2.text)
    tree = html.fromstring(htmlwa)

    caseno = tree.xpath("//form/table[1]/tr[1]/td[2]/font/text()")[0]
    dateOfFiling = tree.xpath("//form/table[1]/tr[1]/td[5]/font/text()")[0]
    status = tree.xpath("//form/table[1]/tr[5]/td[2]/font/text()")[0]
    dateOfDisposal = tree.xpath("//form/table[1]/tr[5]/td[5]/font/text()")[0]
    dateOfRegistration = tree.xpath("//form/table[1]/tr[3]/td[5]/font/text()")[0]
    PetVsRes = tree.xpath("//form/table[2]/tr[1]/td/font/b/text()")[0] + " Vs " + \
               tree.xpath("//form/table[2]/tr[2]/td/font/b/text()")[0]
    FilingAdv = tree.xpath("//table[3]/tr[1]/td[2]/font/text()")[0]
    subject1 = tree.xpath("//table[3]/tr[3]/td[2]/font/text()")[0]

    details = []
    x = tree.xpath("//table")
    for i in range(4, len(x) - 1):
        try:
            temp = {}
            temp['date'] = tree.xpath("//table[{}]/tr/td[2]/font/text()".format(i))[0]
            temp['link'] = ''
            t = tree.xpath("//table[{}]/tr/td[3]/font/text()".format(i))[0].strip()
            temp['detail'] = re.sub(r'[^\x00-\x7F]+', ':', t)
            details.append(temp)
        except:
            temp = {}
            temp['date'] = tree.xpath("//table[{}]/tr/td[2]/font/a/text()".format(i))
            temp['link'] = tree.xpath("//table[{}]/tr/td[2]/font/a/@href".format(i))
            t = tree.xpath("//table[{}]/tr/td[3]/font/text()".format(i))[0].strip()
            temp['detail'] = re.sub(r'[^\x00-\x7F]+', ':', t)
            details.append(temp)

    ret_this = {}

    ret_this['details'] = details
    ret_this['caseno'] = caseno
    ret_this['dateOfFiling'] = dateOfFiling
    ret_this['status'] = status
    ret_this['dateOfDisposal'] = dateOfDisposal
    ret_this['dateOfRegistration'] = dateOfRegistration
    ret_this['PetVsRes'] = PetVsRes
    ret_this['FilingAdv'] = FilingAdv
    ret_this['subject1'] = subject1

    return json.dumps({"status": "successful", "CaseHistory": ret_this})
