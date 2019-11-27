import requests
import shutil

from PIL import Image
from ftfy import fix_text
from lxml import html
from pytesseract import pytesseract


def getCaseHistory_casewise(casetype, caseyear, caseno):
    data = {}
    error_found = True
    attempts = 0
    while (attempts < 30):
        session = requests.Session()
        response = session.get(url='http://164.100.68.118/case/captcha_code_file.php?rand=32477', stream=True)
        with open('img.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        a = Image.open('img.png')
        s = (pytesseract.image_to_string(a))
        payload = {
            "ctype": str(casetype),
            "regno": str(caseno),
            "regyr": str(caseyear),
            "6_letters_code": s,
            "Submit": "Submit"}
        r = session.post(url="http://164.100.68.118/case/s_adv.php", data=payload)
        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)
        error_found = [x.replace('\xa0', ' ') for x in tree.xpath('//*[@id="form3"]/table[1]/*//text()') if
                       len(x.strip()) > 0]
        attempts += 1
        if (len(error_found) > 0):
            data['status'] = "successfull"
            data['Case No'] = tree.xpath('//*[@id="form3"]/table[1]/tr[1]/td[2]/font/text()')[0]
            data['Status'] = tree.xpath('//*[@id="form3"]/table[1]/tr[5]/td[2]/font/text()')[0]
            data['Refile Detial'] = "http://164.100.68.118/case/" + \
                                    tree.xpath('//*[@id="form3"]/table[1]/tr[6]/td[2]/font/a/@href')[0] if len(
                tree.xpath('//*[@id="form3"]/table[1]/tr[6]/td[2]/font/a/@href')) > 0 else None
            data['Date of filling'] = tree.xpath('//*[@id="form3"]/table[1]/tr[1]/td[5]/font/text()')[0]
            data['Date of registraion'] = tree.xpath('//*[@id="form3"]/table[1]/tr[3]/td[5]/font/text()')[0]
            data['Date of disposal'] = tree.xpath('//*[@id="form3"]/table[1]/tr[5]/td[5]/font/text()')[0]
            data['Vs'] = tree.xpath('//*[@id="form3"]/table[2]/tr[1]/td/font/b/text()')[0] + '  ' + \
                         tree.xpath('//*[@id="form3"]/table[2]/tr[1]/td/font/b/text()')[1] + '  ' + \
                         tree.xpath('//*[@id="form3"]/table[2]/tr[2]/td/font/b/text()')[0]
            data['Dealing assistant'] = tree.xpath('//*[@id="layer1"]/center/table[3]/tr[1]/td[2]/font/text()')[0]
            data['Filing advocate'] = tree.xpath('//*[@id="layer1"]/center/table[3]/tr[3]/td[2]/font/text()')[0]
            data[tree.xpath('//*[@id="layer1"]/center/table[3]/tr[5]/td[1]/font/b/text()')[0]] = \
                tree.xpath('//*[@id="layer1"]/center/table[3]/tr[5]/td[2]/font/text()')[0]
            data['Details'] = {}
            try:
                i = 4
                while (len(tree.xpath('//*[@id="layer1"]/center/table[{:d}]//text()'.format(i))[0]) != 0):
                    info = tree.xpath('//*[@id="layer1"]/center/table[{:d}]//text()'.format(i))
                    data['Details'][info[0]] = {
                        'date': info[1],
                        'data': info[2]
                    }
                    i += 1

            except:
                return (data)
        elif ("Unable to Find the Record for..." in tree.xpath('//*/center/blockquote/p/b/font//text()')):
            data['status'] = "unsuccessfull"
            return (data)

print(getCaseHistory_casewise(caseno=12,caseyear=2018, casetype="BAIL APPLN."))

