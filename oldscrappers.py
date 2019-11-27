# -*- coding: utf-8 -*-

import requests
from lxml import html, etree
from collections import OrderedDict
import json
import re
from multiprocessing.dummy import Pool as ThreadPool
from ftfy import fix_text


class Scrapers:
    def __init__(self):
        pass

    '''CAUSE LIST'''

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

    '''CERTIFIED COPIES'''

    def getCertifiedCopies(self, caseno, cyear, ctype, deli):
        url = 'http://delhihighcourt.nic.in/dhccerlist.asp'
        if (deli == 'ON'):
            data = {
                "fil_adv": "",
                "Filing_date_from": "",
                "Filing_date_to": "",
                "side": "ALL",
                "diary_no": "",
                "diary_yr": "2017",
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
                "diary_yr": "2017",
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

            certCopies = json.dumps({"status": "successful", "Certified Copies": result})
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
        certCopies = json.dumps({"status": "successful", "Certified Copies": result})
        return certCopies

    '''DISPLAY BOARD'''

    def displayBoard(self):
        allcourt = []
        for i in range(1, 39):
            url = "http://delhihighcourt.nic.in/his.asp?cno={}".format(i)
            base_url = "http://delhihighcourt.nic.in/"
            response = requests.get(url)
            htmlparser = etree.HTMLParser()
            tree = etree.parse(response, htmlparser)
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
                    dic['OrderFound'] = 'Orders found'
                    pdf_link.append(temp)
                else:
                    dic['OrderFound'] = 'Orders not found'

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
                dic['ListingDate-CourtNo'] = \
                    str(ListingDate[0]).replace("\r", "").replace("\n", "").replace("\t", "").split(':')[1]
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

