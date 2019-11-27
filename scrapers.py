# -*- coding: utf-8 -*-

import requests
from lxml import html, etree
import json
import re
from multiprocessing.dummy import Pool as ThreadPool
from ftfy import fix_text
from PIL import Image
import pytesseract
import shutil
import math
from bs4 import BeautifulSoup
import js2py

class Scrapers:
    def __init__(self):
        pass

    '''CAUSE LIST'''

    
    def displayBoardNew(self):
        display = []
        base_url = "http://delhihighcourt.nic.in/displayboard.asp"
        htmlwa = requests.get(base_url).text
        soup = BeautifulSoup(htmlwa)
        try:
            for index, i in enumerate(soup.findAll('button')):
                if index < 38:
                    ITM = soup.find("input", {"id": 'INPUT' + str(index+1)})['value']
                    CT = str(index+1)
                    js = """
                            function escramble_758(){
                            var d = new Date();
                            var time = d.getTime();
                            document.write(time)
                            }
                            escramble_758()
                            """.replace("document.write", "return ")

                    result = js2py.eval_js(js)
                    url = "http://delhihighcourt.nic.in/Court.asp?CT=" + CT + '&INPUT=' + ITM + '&FT=20&dt=' + str(result)
                    htmlwa1 = requests.get(url).text
                    soup1 = BeautifulSoup(htmlwa1)

                    display.append({
                        'status': soup1.find("font").text.strip(),
                        'session': re.sub('\s+', '', i.getText().replace(' ', '')),
                        'link': 'http://delhihighcourt.nic.in/' + i['onclick'].replace('location.href=', '').replace('\'',
                                                                                                                     '')
                    })
                else:
                    display.append({
                        'status': soup.find("div", {"id": 'DIV' + str(index + 1)}).text.strip(),
                        'session': re.sub('\s+', '', i.getText().replace(' ', '')),
                        'link': 'http://delhihighcourt.nic.in/' + i['onclick'].replace('location.href=', '').replace('\'',
                                                                                                                     '')
                    })
            return json.dumps({"status": "successful", "Display_Board": display})
        except Exception as e:
            print(e)
            return json.dumps({"status": "unsuccessful", "Display_Board": []})



    def getsession(self, url):
        response = requests.get(url).text
        htmlwa = (response)
        tree = html.fromstring(htmlwa)

        output = []
        # table1
        try:
            itemno = tree.xpath('//ul[@class="grid single-line"]//span[@class="pull-left width-33 ac sr-no"]/text()')
            result = tree.xpath('//ul[@class="grid single-line"]//span[2]/text()')
            for i in range(len(itemno)):
                temp = {}
                temp['item no'] = itemno[i].replace('\t', '').replace('\r', '').replace('\n', '')
                temp['result'] = result[i].replace('\t', '').replace('\r', '').replace('\n', '')
                output.append(temp)
            # print output
            # table2
            itemno = tree.xpath('//ul[@class="grid"]//span[@class="pull-left width-33 ac sr-no"]/text()')
            result = tree.xpath('//ul[@class="grid"]//span[2]/text()')
            for i in range(len(itemno)):
                temp = {}
                temp['item no'] = itemno[i].replace('\t', '').replace('\r', '').replace('\n', '')
                temp['result'] = result[i].replace('\t', '').replace('\r', '').replace('\n', '')
                output.append(temp)
            # print output
            return json.dumps({"status": "successful", "Display_Session": output})
        except:
            return json.dumps({"status": "unsuccessful", "Display_Board": []})



    def getCauseList(self):
        url = "http://delhihighcourt.nic.in/causelist_NIC_PDF.asp"
        base_url = "http://delhihighcourt.nic.in/"
        response = requests.get(url).text
        htmlwa = (response)
        tree = html.fromstring(htmlwa)
        number_of_list_tags = tree.xpath('count(//*[@id="InnerPageContent"]/ul/li)')
        # print number_of_list_tags

        all_path = {}
        all_path["total"] = int(number_of_list_tags)
        all_path["data"] = []
        # all_path["status"] = "successful"

        # iterate through the html DOM
        common_path = '//*[@id="InnerPageContent"]/ul/li'
        for z in range(1, int(number_of_list_tags + 1)):
            title_path = str(tree.xpath(common_path + "[" + str(z) + "]" + "/span[1]/text()")[0]).replace("\t",
                                                                                                          "").replace(
                "\r", "").replace("\n", "")
            pdf_path = base_url + str(tree.xpath(common_path + "[" + str(z) + "]" + "/span[2]/a/@href")[0])
            all_path["data"].append({str(z - 1): {"title": title_path, "pdf": pdf_path}})

        return ({"cause_list": all_path})


    # "ctype": "BAIL APPLN.",
    # "regno": "12",
    # "regyr": "2018",

    def getCaseHistory_casewise(self, casetype, caseyear, caseno):

        data = {}
        error_found = True
        attempts = 0
        while (attempts < 100):
            session = requests.Session()
            response = session.get(url='http://164.100.68.118/case/guiCaseWise.php')
            tree = html.fromstring(response.text)
            payload = {
            "ctype": str(casetype),
            "regno": str(caseno),
            "regyr": str(caseyear),
            "acode": str(tree.xpath('/html/body/form/table/tr[7]/td[2]/font/text()')[0]),
            "6_letters_code": str(tree.xpath('/html/body/form/table/tr[7]/td[2]/font/text()')[0]),
            "Submit": "Submit"
            }

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
                    return json.dumps(data)
            elif ("Unable to Find the Record for..." in tree.xpath('//*/center/blockquote/p/b/font//text()')):
                data['status'] = "unsuccessfull"
                return json.dumps(data)

    def getCaseStatus_petvsres(self, name, year):
        url2 = "http://delhihighcourt.nic.in/case.asp"
        r2 = requests.get(url2)
        htmlwa = (r2.text)
        tree = html.fromstring(htmlwa)
        text = re.findall(r'\d+', tree.xpath('//div[1]/div/article/div/div[2]/form[1]/label[4]/text()')[0])[0]
        payload = [
            ('party', str(name)),
            ('pyear', str(year)),
            ('hiddeninputdigit', text),
            ('inputdigit', text),
            ('sno', 2),
            ('SRecNo', '0')]
        r = requests.post(url="http://delhihighcourt.nic.in/dhc_case_status_list_new.asp", data=payload)
        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)
        data = {}
        if (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[1]/text()')) > 0):
            data['pages'] = math.ceil(int(
                re.sub('[^a-zA-Z0-9-_*.]', ' ',
                       tree.xpath('//*[@id="InnerPageContent"]/div/a/text()')[0].strip()).split(
                    ' ')[
                    -1]) / 8)
            data['details'] = []
            data['status'] = "successfull"
            try:
                i = 1
                while (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0]) != 0):
                    data['details'].append({
                        'index': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0],
                        'Diary No. / Case No.[STATUS]': re.sub('[^a-zA-Z0-9-_*.]', ' ', tree.xpath(
                            '//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/text()'.format(i))[0]),
                        'Listing Date / Court No.': re.sub('[^a-zA-Z0-9-_*.]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[4]//text()'.format(i)))),
                        'Petitioner Vs. Respondent': re.sub('[^a-zA-Z0-9-_*.]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[3]//text()'.format(i)))),
                        'Status': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/font/text()'.format(i))[0]
                    })
                    i += 1
            except:
                return json.dumps(data)
        else:
            data['status'] = "unsuccessfull"
            return json.dumps(data)


    # ('radiosel', str('O')),
    # ('p_name', str("malt")),
    # ('frdate', str("15/01/2018")),
    # ('todate', str("15/01/2019"))

    def getJudgmnet_petvsres(self, typeselected, name, frdate, todate):

        r1 = requests.get("http://lobis.nic.in/dhcindex.php?cat=1&hc=31")

        x = str([i for i in r1.cookies.values()][0])

        # print x

        data = [
            ('radiosel', str(typeselected)),
            ('p_name', str(name)),
            ('frdate', str(frdate)),
            ('todate', str(todate)),
            ('Submit', 'Submit'),
        ]
        url = "http://lobis.nic.in/title1.php"

        cookies = {
            'PHPSESSID': str(x),
        }

        params = (
            ('dc', '31'),
            ('fflag', '1'),
        )

        r2 = requests.post(url=url, params=params, cookies=cookies, data=data)

        htmlsource = r2.text
        tree = html.fromstring(htmlsource)
        judgement = {}

        if (len(tree.xpath('/html/body/div/table/tr[2]/td[1]/span/text()')) > 0):
            judgement['status'] = "successfull"
            try:
                i = 2
                while (len(tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]) != 0):
                    judgement[tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]] = {
                        'Case Number judgment link': "http://lobis.nic.in" +
                                                     tree.xpath('/html/body/div/table/tr[{}]/td[2]/a/@href'.format(i))[
                                                         0],
                        'Date of Judgment/Order': tree.xpath('/html/body/div/table/tr[{}]/td[3]/span/text()'.format(i))[
                            0],
                        'Party': ' '.join(tree.xpath('/html/body/div/table/tr[{}]/td[4]/span//text()'.format(i))),
                        'Corrigendum': tree.xpath('/html/body/div/table/tr[{}]/td[5]/span//text()'.format(i))[0]

                    }
                    i += 1
            except:
                return json.dumps(judgement)
        else:
            judgement['status'] = "unsuccessfull"
            return json.dumps(judgement)



    #
    # data = {
    #         "fil_adv": "Geeta",
    #         "Filing_date_from": "12/01/2016",
    #         "Filing_date_to": "15/01/2019",
    #         "side": "ALL",
    #         "diary_no": "",
    #         "diary_yr": "ALL",
    #         "ctype": "ALL",
    #         "no": "",
    #         "cyear": "ALL",
    #         "del": "ON",
    #         "B1": "Show+Details", }

    def getCertifiedCopiesAppliedby(self, appliedby, frdate, todate, side, diaryno, diaryyear, casetype, caseno, caseyear):
        url = 'http://delhihighcourt.nic.in/dhccerlist.asp'
        print(caseno)
        print(diaryno)
        data = {
            "fil_adv": str(appliedby),
            "Filing_date_from": str(frdate),
            "Filing_date_to": str(todate),
            "side": str(side),
            "diary_no": str(diaryno),
            "diary_yr": str(diaryyear),
            "ctype": str(casetype),
            "no": str(caseno),
            "cyear": str(caseyear),
            "del": "ON",
            "B1": "Show Details", }

        r = requests.post(url, data)

        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)

        # DATA FETCHING STARTS FROM HERE
        certified_copies = {}
        if (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[1]/text()'))):
            try:
                i = 1
                while (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0]) != 0):
                    certified_copies[
                        tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0].strip()] = {
                        'Diary No. / Case No.': re.sub('[^a-zA-Z0-9-_*.]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]//text()'.format(i)))).strip(),
                        'Applied By': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[3]/text()'.format(i))[
                            0].strip(),
                        'Status': re.sub('[^a-zA-Z0-9-_*.]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[4]//text()'.format(i)))).strip(),
                        'Amt. Bal.': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[5]/text()'.format(i))[
                            0].strip(),
                        'Date': re.sub('[^a-zA-Z0-9-_*.]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[6]//text()'.format(i)))).strip()
                    }
                    i += 1

            except:
                return json.dumps(certified_copies)
        else:
            certified_copies['status'] = "unsuccessfull"
            return json.dumps(certified_copies)


    #
    # payload = {
    #             "partyname": "ADARSH RAJ SINGH",
    #             "ptype": "S",
    #             "party": "0",
    #             "pyear1": "2018",
    #             "pyear2": "2018",
    #             "6_letters_code": s,
    #             "Submit": "Submit" }

    def getCaseHistory_petVSres(self, partyname, match, petvsres, fryear, toyear):

        data = {}
        error_found = True
        attempts = 0
        while (attempts < 100):
            session = requests.Session()
            response = session.get(url='http://164.100.68.118/case/search_party.php')
            tree = html.fromstring(response.text)

            payload = {
                "partyname": str(partyname),
                "ptype": str(match),
                "party": str(petvsres),
                "pyear1": str(fryear),
                "pyear2": str(toyear),
                "acode": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "6_letters_code": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "Submit": "Submit"}
            r = session.post(url="http://164.100.68.118/case/party_search.php", data=payload)
            htmlwa = (r.text)
            tree = html.fromstring(htmlwa)
            error_found = tree.xpath('//*/table[2]/tr[3]/td[1]/text()')
            attempts += 1
            if (len(error_found) > 0):
                data['Details'] = {}
                data['status'] = "successfull"
                try:
                    i = 3
                    while (len(tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]) != 0):
                        data['Details'][tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]] = {
                            'status': "successfull",
                            'Case No': tree.xpath('//*/table[2]/tr[{}]/td[2]/a/text()'.format(i))[0],
                            'Case link': "http://164.100.68.118/case/" + tree.xpath('//*/table[2]/tr[{}]/td[2]/a/@href'.format(i))[
                                0],
                            'Party': re.sub('[^a-zA-Z0-9-_*.]', ' ',
                                            ' '.join(tree.xpath('//*/table[2]/tr[{}]/td[3]//text()'.format(i)))),
                            'Advocate': tree.xpath('//*/table[2]/tr[{}]/td[4]/text()'.format(i))[0],
                            'Status': tree.xpath('//*/table[2]/tr[{}]/td[5]/text()'.format(i))[0]

                        }
                        i += 1
                except:
                    pass
                return json.dumps(data)
            else:
                data['status'] = "unsuccessfull"
                return json.dumps(data)


    #
    # payload = {
    #             "name": "HImanshu",
    #             "type": "E",
    #             "year": "2012",
    #             "year1": "2019",
    #             "6_letters_code": s,
    #             "Submit": "Submit" }

    def getCaseHistory_advocatename(self, advocatename, match, fryear, toyear):

        data = {}
        error_found = True
        attempts = 0
        while (attempts < 100):
            session = requests.Session()
            response = session.get(url='http://164.100.68.118/case/search_adv.php')
            tree = html.fromstring(response.text)
            payload = {
                "name": advocatename,
                "type": match,
                "year": fryear,
                "year1": toyear,
                "acode": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "6_letters_code": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "Submit": "Submit"}
            r = session.post(url="http://164.100.68.118/case/adv_search.php", data=payload)
            htmlwa = (r.text)
            tree = html.fromstring(htmlwa)
            error_found = tree.xpath('//*/table[2]/tr[3]/td[1]/text()')
            attempts += 1
            if (len(error_found) > 0):
                data['Details'] = {}
                data['status'] = "successfull"
                try:
                    i = 3
                    while (len(tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]) != 0):
                        

                        data['Details'][tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]] = {
                            'status': "successfull",
                            'Case No': tree.xpath('//*/table[2]/tr[{}]/td[2]/a/text()'.format(i))[0],
                            'Case link': "http://164.100.68.118/case/" + tree.xpath('//*/table[2]/tr[{}]/td[2]/a/@href'.format(i))[
                                0],
                            'Party': re.sub('[^a-zA-Z0-9-_*.]', ' ',
                                            ' '.join(tree.xpath('//*/table[2]/tr[{}]/td[3]//text()'.format(i)))),
                            'Advocate': tree.xpath('//*/table[2]/tr[{}]/td[4]/text()'.format(i))[0],
                            'Status': tree.xpath('//*/table[2]/tr[{}]/td[5]/text()'.format(i))[0]

                        }

                        i += 1
                except:
                    return json.dumps(data)
            else:
                data['status'] = "unsuccessfull"
                return json.dumps(data)



    # payload = [
    #         ('dno', "ARB. A. (COMM.)  1/2018"),
    #         ('dyear', "2018"),
    #         ('hiddeninputdigit', text),
    #         ('inputdigit', text),
    #         ('sno', 4),
    #         ('SRecNo',8)]

    def getCaseStatus_dairyno(self, dairyname, dairyyear, page):
        url2 = "http://delhihighcourt.nic.in/case.asp"
        r2 = requests.get(url2)
        htmlwa = (r2.text)
        tree = html.fromstring(htmlwa)
        text = re.findall(r'\d+', tree.xpath('//div[1]/div/article/div/div[2]/form[1]/label[4]/text()')[0])[0]
        payload = [
                ('dno', str(dairyname)),
                ('dyear', str(dairyyear)),
                ('hiddeninputdigit', text),
                ('inputdigit', text),
                ('sno', 4),
                ('SRecNo', int(page) * 8)]


        r = requests.post(url="http://delhihighcourt.nic.in/dhc_case_status_list_new.asp", data=payload)
        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)
        data = {}
        if (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[1]/text()')) > 0):
            data['pages'] = math.ceil(int(
                re.sub('[^a-zA-Z0-9-_*.]', ' ', tree.xpath('//*[@id="InnerPageContent"]/span/text()')[0].strip()).split(
                    ' ')[-1]) / 8)
            data['details'] = []
            data['status'] = "successfull"
            try:
                i = 1
                while (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0]) != 0):
                    data['details'].append({
                        'index': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0],
                        'Diary No. / Case No.[STATUS]': re.sub('[^a-zA-Z0-9-_*./]', ' ', tree.xpath(
                            '//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/text()'.format(i))[0]).strip(),
                        'Listing Date / Court No.': re.sub('[^a-zA-Z0-9-_*./]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[4]//text()'.format(i)))).strip(),
                        'Petitioner Vs. Respondent': re.sub('[^a-zA-Z0-9-_*./]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[3]//text()'.format(i)))).strip(),
                        'Status': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/font/text()'.format(i))[0].strip()
                    })
                    i += 1
            except:
                return json.dumps(data)
        else:
            data['status'] = "unsuccessfull"
            return json.dumps(data)



    #
    # payload = [
    #         ('adv', "Himanshu"),
    #         ('ayear', "2018"),
    #         ('hiddeninputdigit', text),
    #         ('inputdigit', text),
    #         ('sno', 3),
    #         ('SRecNo',0)]

    def CaseStatus_Advocate(self, advocatename, advocateyear, page):
        url2 = "http://delhihighcourt.nic.in/case.asp"
        r2 = requests.get(url2)
        htmlwa = (r2.text)
        tree = html.fromstring(htmlwa)
        text = re.findall(r'\d+', tree.xpath('//div[1]/div/article/div/div[2]/form[1]/label[4]/text()')[0])[0]
        payload = [
            ('adv', advocatename),
            ('ayear', advocateyear),
            ('hiddeninputdigit', text),
            ('inputdigit', text),
            ('sno', 3),
            ('SRecNo', int(page) * 8)]
        r = requests.post(url="http://delhihighcourt.nic.in/dhc_case_status_list_new.asp", data=payload)
        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)
        data = {}
        if (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[1]/text()')) > 0):
            data['pages'] = math.ceil(int(
                re.sub('[^a-zA-Z0-9-_*.]', ' ', tree.xpath('//*[@id="InnerPageContent"]/span/text()')[0].strip()).split(
                    ' ')[
                    -1]) / 8)
            data['details'] = []
            try:
                i = 1
                while (len(tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0]) != 0):
                    data['details'].append({
                        'index': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[1]/text()'.format(i))[0],
                        'Diary No. / Case No.[STATUS]': re.sub('[^a-zA-Z0-9-_*./]', ' ', tree.xpath(
                            '//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/text()'.format(i))[0]).strip(),
                        'links': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/button/@onclick'.format(i))[
                            0].strip(),
                        'Listing Date / Court No.': re.sub('[^a-zA-Z0-9-_*./]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[4]//text()'.format(i)))).strip(),
                        'Petitioner Vs. Respondent': re.sub('[^a-zA-Z0-9-_*./]', ' ', ' '.join(
                            tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[3]//text()'.format(i)))).strip(),
                        'Status': tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/font/text()'.format(i))[0],
                        'Order': "http://delhihighcourt.nic.in/" +
                                 tree.xpath('//*[@id="InnerPageContent"]/ul/li[{}]/span[2]/button/@onclick'.format(i))[
                                     0].rstrip(
                                     "'").lstrip("location.href='")
                    })
                    i += 1
            except:
                return json.dumps(data)
        else:
            data['status'] = "unsuccessfull"
            return json.dumps(data)


    #
    # data = [
    #         ('ctype', str("103")),
    #         ('frdate', str("15/01/2012")),
    #         ('todate', str("15/01/2019")),
    #         ('Submit', 'Submit'),
    #     ]

    def getJudgmnet_judge(self, judgename, fryear, toyear):

        r1 = requests.get("http://lobis.nic.in/dhcindex.php?cat=1&hc=31")

        x = str([i for i in r1.cookies.values()][0])

        # print x
        
        data = [
             ('ctype', str(judgename)),
             ('frdate', str(fryear)),
             ('todate', str(toyear)),
             ('Submit', 'Submit'),
        ]
        url = "http://lobis.nic.in/judname1.php"

        cookies = {
            'PHPSESSID': str(x),
        }

        params = (
            ('scode', '31'),
            ('fflag', '1'),
        )

        r2 = requests.post(url=url, params=params, cookies=cookies, data=data)

        htmlsource = r2.text
        tree = html.fromstring(htmlsource)
        judgement = {}

        if (len(tree.xpath('/html/body/div/table/tr[2]/td[1]/span/text()')) > 0):
            try:
                i = 2
                while (len(tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]) != 0):
                    judgement[tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]] = {
                        'Case Number judgment link': "http://lobis.nic.in" +
                                                     tree.xpath('/html/body/div/table/tr[{}]/td[2]/a/@href'.format(i))[
                                                         0],
                        'Date of Judgment/Order': tree.xpath('/html/body/div/table/tr[{}]/td[3]/span/text()'.format(i))[
                            0],
                        'Party': ' '.join(tree.xpath('/html/body/div/table/tr[{}]/td[4]/span//text()'.format(i))),
                        'Corrigendum': tree.xpath('/html/body/div/table/tr[{}]/td[5]/span//text()'.format(i))[0]

                    }
                    i += 1
            except:
                return json.dumps(judgement)
        else:
            judgement['status'] = "unsuccessfull"
            return json.dumps(judgement)

    # data = [
    #         ('juddt', str("18/12/2018")),
    #         ('Submit', 'Submit'),
    #     ]

    def getJudgement_judgementdate(self, judgementdate):

        r1 = requests.get("http://lobis.nic.in/dhcindex.php?cat=1&hc=31")

        x = str([i for i in r1.cookies.values()][0])

        # print x

        data = [
            ('juddt', str(judgementdate)),
            ('Submit', 'Submit'),
        ]
        url = "http://lobis.nic.in/juddt1.php"

        cookies = {
            'PHPSESSID': str(x),
        }

        params = (
            ('dc', '31'),
            ('fflag', '1'),
        )

        r2 = requests.post(url=url, params=params, cookies=cookies, data=data)

        htmlsource = r2.text
        tree = html.fromstring(htmlsource)
        judgement = {}
        if (len(tree.xpath('/html/body/div/table/tr[2]/td[1]/span/text()')) > 0):

            try:
                i = 2
                while (len(tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]) != 0):
                    judgement[tree.xpath('/html/body/div/table/tr[{}]/td[1]/span/text()'.format(i))[0]] = {
                        'Case Number judgment link': "http://lobis.nic.in" +
                                                     tree.xpath('/html/body/div/table/tr[{}]/td[2]/a/@href'.format(i))[
                                                         0],
                        'Date of Judgment/Order': tree.xpath('/html/body/div/table/tr[{}]/td[3]/span/text()'.format(i))[
                            0],
                        'Party': ' '.join(tree.xpath('/html/body/div/table/tr[{}]/td[4]/span//text()'.format(i))),
                        'Corrigendum': tree.xpath('/html/body/div/table/tr[{}]/td[5]/span//text()'.format(i))[0]

                    }
                    i += 1
            except:
                return json.dumps(judgement)
        else:
            judgement['status'] = "unsuccessfull"
            return json.dumps(judgement)


    # payload = {
    #             "plstation": "82",
    #             "FirNo": "157",
    #             "FirYr": "2014",
    #             "6_letters_code": s,
    #             "submit": "Submit" }

    def getCaseHistory_firno(self, policestation, number, year):

        data = {}
        error_found = True
        attempts = 0
        while (attempts < 100):
            session = requests.Session()
            response = session.get(url='http://164.100.68.118/case/guiFirNoWise.php')
            tree = html.fromstring(response.text)
            payload = {
                "plstation": str(policestation),
                "FirNo": str(number),
                "FirYr": str(year),
                "acode": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "6_letters_code": str(tree.xpath('/html/body/form/table/tr[6]/td[2]/font/text()')[0]),
                "submit": "Submit"}
            r = session.post(url="http://164.100.68.118/case/detailByFirNo.php", data=payload)
            htmlwa = (r.text)
            tree = html.fromstring(htmlwa)
            error_found = tree.xpath('//*/table[2]/tr[2]/td[1]/text()')
            attempts += 1
            if (len(error_found) > 0):
                data['Details'] = {}
                data['status'] = "successfull"
                try:
                    i = 2
                    while (len(tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]) != 0):
                        data['Details'][tree.xpath('//*/table[2]/tr[{}]/td[1]/text()'.format(i))[0]] = {
                            'status': "successfull",
                            'Case No': tree.xpath('//*/table[2]/tr[{}]/td[2]/a/text()'.format(i))[0],
                            'Case link': "http://164.100.68.118/case/" +
                                         tree.xpath('//*/table[2]/tr[{}]/td[2]/a/@href'.format(i))[0],
                            'Party': re.sub('[^a-zA-Z0-9-_*.]', ' ',
                                            ' '.join(tree.xpath('//*/table[2]/tr[{}]/td[3]//text()'.format(i)))),
                            'Advocate': tree.xpath('//*/table[2]/tr[{}]/td[4]/text()'.format(i))[0],
                            'Status': tree.xpath('//*/table[2]/tr[{}]/td[5]/text()'.format(i))[0]

                        }
                        i += 1
                except:
                    return json.dumps(data)
            else:
                data['status'] = "unsuccessfull"
                return json.dumps(data)

    '''CERTIFIED COPIES'''

    def getCertifiedCopiesSimple(self, caseno, cyear, ctype, deli):
        url = 'http://delhihighcourt.nic.in/dhccerlist.asp'
        if (deli == 'ON'):
            data = {
                "fil_adv": "",
                "Filing_date_from": "",
                "Filing_date_to": "",
                "side": "ALL",
                "diary_no": "",
                "diary_yr": "ALL",
                "ctype": ctype,
                "no": caseno,
                "cyear": cyear,
                "del": "ON",
                "B1": "Show+Details", }
        else:
            data = {
                "fil_adv": "",
                "Filing_date_from": "",
                "Filing_date_to": "",
                "side": "ALL",
                "diary_no": "",
                "diary_yr": "ALL",
                "ctype": ctype,
                "no": caseno,
                "cyear": cyear,
                "B1": "Show+Details", }

        r = requests.post(url, data)

        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)

        if (tree.xpath('//*[@id="InnerPageContent"]/ul//text()')[0].strip() != "No Match Found."):
            # DATA FETCHING STARTS FROM HERE

            result = []

            number_of_list_tags = tree.xpath('count(//*[@id="InnerPageContent"]/ul/li)')

            for i in range(1, int(number_of_list_tags) + 1):
                diaryno = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[2]/text()'.format(i))[0].strip()
                caseno = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[2]/span/text()'.format(i))[0]
                caseno = re.sub(r'[^\x00-\x7F]+', ':', caseno)
                applied_by = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[3]/text()'.format(i))[0]
                status = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[4]/span/text()'.format(i))[0]
                amt_bal = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[5]/text()'.format(i))[0].strip()
                filing_date = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[1]/text()'.format(i))[
                    0].strip().replace('Filing ', '')
                ready_date = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[2]/text()'.format(i))[
                    0].strip().replace('Ready:', '')
                delivery_date = tree.xpath('///*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[3]/text()'.format(i))[
                    0].strip().replace('Delivery : ', '')
                temp = {}
                temp['diaryno'] = diaryno
                temp['caseno'] = caseno
                temp['applied_by'] = applied_by
                temp['status'] = status
                temp['filing_date'] = filing_date
                temp['ready_date'] = ready_date
                temp['delivery_date'] = delivery_date
                temp['amt_bal'] = amt_bal
                result.append(temp)

            if len(result) == 0:
                raise Exception

            certCopies = json.dumps({"status": "successful", "checking": "orignal", "Certified Copies": result})
            return certCopies
        else:
            ret = json.dumps({"status": "unsuccessful"})
            return (ret)

    '''CERTIFIED COPIES (APPLIED BY)'''

    def getCertifiedAppliedby(self, applied_by, diary_yr, cyear):
        url = 'http://delhihighcourt.nic.in/dhccerlist.asp'

        data = {
            "fil_adv": applied_by,
            "Filing_date_from": "",
            "Filing_date_to": "",
            "side": "ALL",
            "diary_no": "",
            "diary_yr": diary_yr,
            "ctype": "ALL",
            "no": "",
            "cyear": cyear,
            "del": "ON",
            "B1": "Show+Details", }

        r = requests.post(url, data)

        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)

        # DATA FETCHING STARTS FROM HERE

        result = []

        number_of_list_tags = tree.xpath('count(//*[@id="InnerPageContent"]/ul/li)')

        for i in range(1, int(number_of_list_tags) + 1):
            diaryno = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[2]/text()'.format(i))[0].strip().encode(
                'utf-8')
            caseno = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[2]/span/text()'.format(i))[0].encode(
                'utf-8')
            caseno = re.sub(r'[^\x00-\x7F]+', ':', caseno)
            applied_by = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[3]/text()'.format(i))[0].encode(
                'utf-8')
            status = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[4]/span/text()'.format(i))[0].encode(
                'utf-8')
            amt_bal = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[5]/text()'.format(i))[0].strip().encode(
                'utf-8')
            filing_date = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[1]/text()'.format(i))[
                0].strip().encode('utf-8').replace('Filing ', '')
            ready_date = tree.xpath('//*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[2]/text()'.format(i))[
                0].strip().encode('utf-8').replace('Ready:', '')
            delivery_date = tree.xpath('///*[@id="InnerPageContent"]/ul/li[{0}]/span[6]/span[3]/text()'.format(i))[
                0].strip().encode('utf-8').replace('Delivery : ', '')
            temp = {}
            temp['diaryno'] = diaryno
            temp['caseno'] = caseno
            temp['applied_by'] = applied_by
            temp['status'] = status
            temp['filing_date'] = filing_date
            temp['ready_date'] = ready_date
            temp['delivery_date'] = delivery_date
            temp['amt_bal'] = amt_bal
            result.append(temp)
        if len(result) == 0:
            raise Exception
        certCopies = json.dumps({"status": "successful",  "checking": "orignal", "Certified Copies": result})
        return certCopies

    '''DISPLAY BOARD'''

    def displayBoard(self):
        allcourt = []
        for i in range(1, 39):
            url = "http://delhihighcourt.nic.in/his.asp?cno={}".format(i)
            base_url = "http://delhihighcourt.nic.in/"
            response = requests.get(url).text
            htmlwa = (response)
            tree = html.fromstring(htmlwa)
            output = []
            # table1
            itemno = tree.xpath('//ul[@class="grid single-line"]//span[@class="pull-left width-33 ac sr-no"]/text()')
            result = tree.xpath('//ul[@class="grid single-line"]//span[2]/text()')
            for i in range(len(itemno)):
                temp = {}
                temp['item no'] = itemno[i].replace('\t', '').replace('\r', '').replace('\n', '')
                temp['result'] = result[i].replace('\t', '').replace('\r', '').replace('\n', '')
                output.append(temp)
            # print output
            # table2
            itemno = tree.xpath('//ul[@class="grid"]//span[@class="pull-left width-33 ac sr-no"]/text()')
            result = tree.xpath('//ul[@class="grid"]//span[2]/text()')
            for i in range(len(itemno)):
                temp = {}
                temp['item no'] = itemno[i].replace('\t', '').replace('\r', '').replace('\n', '')
                temp['result'] = result[i].replace('\t', '').replace('\r', '').replace('\n', '')
                output.append(temp)
            # print output
            temp = {'courtno': i, 'displayboard': output}
            allcourt.append(temp)
        ret = json.dumps({"status": "successful", 'Display Board': allcourt})
        return ret

    '''JUDGES ROSTER'''

    def getJudgesRoster(self):
        url = "http://delhihighcourt.nic.in/roster_judges_current.asp"
        base_url = "http://delhihighcourt.nic.in/"
        response = requests.get(url).text
        htmlwa = (response)
        tree = html.fromstring(htmlwa)

        path = tree.xpath('//*[@id="InnerPageContent"]/ul/li/span[2]/a/@href')[0]
        full_path = base_url + path

        # judges_roster = json.dumps({"status":"successful","judges_roster": full_path})
        judges_roster = json.dumps({"judges_roster": full_path})
        return judges_roster

    '''FORMS(also see download_form.py for scrapers)'''

    def GetDforms(self):
        x = dict(
            forms=[{"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_C7AFAVYS.PDF",
                    "title": "Application for supply of Digital Copy."},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_I1S5XUIM.PDF",
                    "title": "Notice regarding online downloading facility of e-court fee."},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_GD1CE4H6.PDF",
                    "title": "Procedure for Online Gate Pass Registration"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_Q07RCVK6.PDF",
                    "title": "Template for uploading Memo of Parties in e-filing facility."},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_BF49033X.PDF",
                    "title": "FORM FOR URGENT (MENTIONING) CASES FOR LISTING / ACCOMMODATION"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_WMMEFA41.PDF",
                    "title": "Application for Certified Copy"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_HFP32GFB.PDF",
                    "title": "Form for Interlocutory Applications"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_1227ZY87.PDF",
                    "title": "Process Fee Form"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_45PPC98K.PDF",
                    "title": "Application for Adjournment"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_2PXD71RE.PDF",
                    "title": "Memorandum of Appearance of Advocate"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_KUD67PSJ.PDF",
                    "title": "Caveat"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_T3KJ5W6B.PDF",
                    "title": "Urgent Application"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_WE9XYP1U.PDF",
                    "title": "Index"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_44T6CX1T.PDF",
                    "title": "List of Documents"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_STNSYU8C.PDF",
                    "title": "Application for Uncertified Copy"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_CUAM42BV.PDF",
                    "title": "Opening Sheet for Criminal Revision"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_EA9SIGCT.PDF",
                    "title": "Inspection of File"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_6G9BF7PB.PDF",
                    "title": "Opening Sheet for Criminal Section 374 Criminal Procedure"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_ADUPYNC8.PDF",
                    "title": "Vakalatnama"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_2UYN5W9S.PDF",
                    "title": "Notice of Motion"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_77KUH3ST.PDF",
                    "title": "Listing Performa"},
                   {"link": "http://delhihighcourt.nic.in/writereaddata/upload/Downloads/DownloadFile_TYNGUEZV.PDF",
                    "title": "List Proforma II"}])
        return x

    '''GENERAL NOTICES'''

    def getGenNotices(self):
        print("hello")
        ret_this = []
        url = 'http://delhihighcourt.nic.in/generalnotices.asp'
        r = requests.get(url)
        tree = html.fromstring(r.text)

        number_of_list_tags = tree.xpath('count(/html/body/div[1]/div/article/div/div[2]/ul/li)')

        # print number_of_list_tags

        titles = tree.xpath('/html/body/div[1]/div/article/div/div[2]/ul/li/span[2]/text()')
        dates = tree.xpath('/html/body/div[1]/div/article/div/div[2]/ul/li/span[3]/text()')
        links = tree.xpath('/html/body/div[1]/div/article/div/div[2]/ul/li/span[4]/a/@href')

        baseurl = "http://delhihighcourt.nic.in/"

        for i in range(int(number_of_list_tags)):
            temp = {}
            temp['title'] = titles[i]
            temp['date'] = dates[i]
            temp['link'] = baseurl + links[i]
            ret_this.append(temp)

        # final_ret = json.dumps({"status":"successful","Notices": ret_this})
        final_ret = json.dumps({"Notices": ret_this})
        return final_ret

    '''CASE STATUS'''

    def get_data(self, case_no, case_type, case_year):
        url2 = "http://delhihighcourt.nic.in/case.asp"
        r2 = requests.get(url2)
        htmlwa = (r2.text)
        tree = html.fromstring(htmlwa)
        text = re.findall(r'\d+', tree.xpath('//div[1]/div/article/div/div[2]/form[1]/label[4]/text()')[0])[0]

        url = "http://delhihighcourt.nic.in/dhc_case_status_list_new.asp"
        payload = [
            ('cno', case_no),
            ('ctype_29', case_type),
            ('cyear', case_year),
            ('hiddeninputdigit', text),
            ('inputdigit', text),
            ('sno', 1)]
        r = requests.post(url, data=payload)
        htmlwa = (r.text)
        tree = html.fromstring(htmlwa)
        diary_caseno = []
        if (tree.xpath('//*[@id="InnerPageContent"]//text()')[0].strip() != "CASE NOT FOUND"):
            text = tree.xpath('//*[@id="InnerPageContent"]/ul/li/span[2]/text()')[0].strip()
            diary_caseno.append(re.sub(r'[^\x00-\x7F]+', ':', text))

            petVsRes = []
            for i in range(1, 4):
                y = tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[3]/text()[{0}]'.format(i))[0].strip()
                petVsRes.append((re.sub(r'[^\x00-\x7F]+', '', y)))

            ListingDate = []
            for i in range(1, 3):
                y = tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[4]/text()[{0}]'.format(i))[0].strip().replace(
                    '/t',
                    '').replace(
                    '/n', '').replace('/r', '')
                ListingDate.append(y)
            case_status = tree.xpath('//*[@id="InnerPageContent"]/ul/li[1]/span[2]/font//text()')[0].replace('[',
                                                                                                             '').replace(
                ']',
                '')

            link = "http://delhihighcourt.nic.in/" + tree.xpath('//*[@class="button pull-right"]/@onclick')[0].rstrip(
                "'").lstrip("location.href='")

            r = requests.get(link)
            htmlwa = (r.text)
            tree = html.fromstring(htmlwa)

            pdf_link = []

            li = tree.xpath('//ul[@class="clearfix grid last"]/li')

            # for i in range(1, len(li) + 1):

            dic = {}

            links_present = len(tree.xpath('//ul[@class="clearfix grid last"]/li[*]/span/button/@onclick'))
            for i in range(1, len(li) + 1):
                if (links_present) != 0:
                    test = tree.xpath('//ul[@class="clearfix grid last"]/li[{}]/span/button/@onclick'.format(i))[
                        0].strip(
                        "location.href=").strip("'")
                    link = test if len(test) > 1 else ""
                    test2 = tree.xpath('//ul[@class="clearfix grid last"]/li[{}]/span[3]/text()'.format(i))[0].strip()
                    date = test2 if len(test2) > 1 else ""
                    temp = {}
                    temp['link'] = link
                    temp['date'] = date
                    dic['status'] = 'successfull'
                    pdf_link.append(temp)
                else:
                    dic['status'] = 'unsuccessfull'

            dic['Case_type-no-year'] = diary_caseno[0]
            dic['PetitionerVsRespondent'] = petVsRes[0] + " " + petVsRes[1]

            try:
                dic['Advocate'] = str(petVsRes[2]).split(':')[1]
            except:
                try:
                    dic['Advocate'] = str(petVsRes[2])
                except:
                    dic['Advocate'] = ""

            try:
                dic['ListingDate-CourtNo'] = ' '.join(ListingDate).replace("\r", "").replace("\n", "").replace("\t",
                                                                                                             "")
            except:
                try:
                    dic['ListingDate-CourtNo'] = str(ListingDate[0]).replace("\r", "").replace("\n", "").replace("\t",
                                                                                                                 "")
                except:
                    dic['ListingDate-CourtNo'] = ""

            try:
                dic['next_date'] = str(ListingDate[1]).replace("\r", "").replace("\n", "").replace("\t", "").split(':')[
                    1]
            except:
                try:
                    dic['next_date'] = str(ListingDate[1]).replace("\r", "").replace("\n", "").replace("\t", "")
                except:
                    dic['next_date'] = ""

            dic['Status'] = case_status
            dic['Order PDF'] = pdf_link
            dic['status'] = "successful"

            ret = json.dumps(dic)

            return (ret)
        else:
            dic = {}
            dic['status'] = "unsuccessful"
            ret = json.dumps(dic)
            return (ret)

    '''JUDGEMENTS'''

    def getJudgement(self, ctype, cnum, cyear, cdesc='Array'):
        def party_all(tree):
            all_party = ''
            for i in range(1, 10):
                try:
                    party = str(tree.xpath("//table//tr[2]/td[4]/span[" + str(i) + "]/text()")[0])
                    all_party += party
                except:
                    pass
            return all_party

        r1 = requests.get("http://lobis.nic.in/dhcindex.php?cat=1&hc=31")

        x = str([i for i in r1.cookies.values()][0])

        # print x

        data = [
            ('ctype', str(ctype)),
            ('cnum', str(cnum)),
            ('cyear', str(cyear)),
            ('cdesc', str(cdesc)),
            ('Submit', 'Submit'),
        ]
        url = "http://lobis.nic.in/casetype1.php"

        cookies = {
            'PHPSESSID': str(x),
        }

        params = (
            ('scode', '31'),
            ('fflag', '1'),
        )

        r2 = requests.post(url=url, params=params, cookies=cookies, data=data)

        htmlsource = r2.text
        # print htmlsource
        tree = html.fromstring(htmlsource)
        judgement = {}
        judgement["status"] = "successful"
        if (tree.xpath("/html/body/p/span//text()")[0] != "INVALID INPUT!!! TRY AGAIN!!"):
            try:
                case_number = str(tree.xpath("//table//tr[2]/td[2]/a/text()")[0])
                case_number_pdf = str("http://lobis.nic.in" + str(tree.xpath("//table//tr[2]/td[2]/a/@href")[0]))
                date_of_judgement = str(tree.xpath("//table//tr[2]/td[3]/span/text()")[0])
                party = party_all(tree)
                try:
                    corrigendum = str(tree.xpath("//table//tr[2]/td[5]/span/text()")[0])
                except:
                    corrigendum = ''

                judgement["judgement"] = {"case_number": case_number, "case_number_pdf": case_number_pdf,
                                          "date_of_judgement": date_of_judgement, "party": party,
                                          "corrigendum": corrigendum}
                return (judgement)
            except Exception as e:
                print(e)
                return {"status": "unsuccessful"}
        else:
            dic = {}
            dic["status"] = "unsuccessful"
            return (dic)

    '''NOMINATED COUNSEL'''

    def getNominatedCounsel(self):
        url = "http://delhihighcourt.nic.in/nominatedcouncils.asp"
        base_url = "http://delhihighcourt.nic.in/"
        response = requests.get(url).text
        htmlwa = (response)
        tree = html.fromstring(htmlwa)

        path = tree.xpath('//*[@id="InnerPageContent"]/ul/li/span[2]/a/@href')[0]
        full_path = base_url + path

        # nominated_counsel = json.dumps({"status":"successful","nominated_counsel": full_path})
        nominated_counsel = json.dumps({"nominated_counsel": full_path})
        return nominated_counsel

    '''SITTING JUDGES'''

    def SittingJudges(self):
        data = []
        count = 1
        base_url = "http://delhihighcourt.nic.in/"

        urls = [
            "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=1",
            "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=2",
            "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=3",
            "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=4",
            "http://delhihighcourt.nic.in/cjsittingjudges.asp?currentPage=5"
        ]

        pool = ThreadPool(5)

        cleaned = pool.map(requests.get, urls)
        # cleaned = [x for x in results if not x is None]
        pool.close()
        pool.join()

        for item in cleaned:
            tree = html.fromstring(item.text)

            for i in range(0, 9):
                # print(tree)
                try:
                    image = str(base_url + str(tree.xpath('//*[@id="inline' + str(i) + '"]/img/@src')[0]))
                    name = str(tree.xpath('//*[@id="inline' + str(i) + '"]/following::h6/text()')[0])
                    info = (tree.xpath('//*[@id="data' + str(i) + '"]//div/text()'))
                    paragraph = ''
                    for para in info:
                        paragraph += fix_text(str(
                            para)) + "<br><br>"  # ascii(str(para).encode('ascii',errors='ignore')).replace("b'",'')#ascii(para.encode('ascii'))#str(codecs.decode((para),'ascii'))# + "<br><br>"
                    # print count

                    data.append({"name": name, "image": image, "info": (
                        (paragraph).replace("\n\t\t\t\t\t\t\t\t\t\t", "").replace("\t",
                                                                                  ""))})  # .replace('\t','').replace("\r","").replace("\n","")})
                    # count += 1
                except:
                    pass

        # return {"status": "successful", "data": data}
        return {"data": data}

