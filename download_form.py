from bs4 import BeautifulSoup
# import urllib2
import json


#
# def GetDforms():
#     try:
#         Return_forms = None
#
#         ret_forms = []
#
#         for i in range(1, 4):
#
#             url = 'http://delhihighcourt.nic.in/Downloads.asp?currentPage={}'.format(i)
#             base_url = 'http://delhihighcourt.nic.in/'
#
#             content = urllib2.urlopen(url).read()
#             soup = BeautifulSoup(content, 'lxml')
#
#             # DATA FETCHING STARTS FROM HERE
#
#             forms = []
#
#             links = soup.find_all('span', {'class': 'pdf-download width-20 last pull-right ac'})
#             for link in links:
#                 for i in link.find_all('a'):
#                     forms.append(base_url + i.get('href'))
#
#             titles = soup.find_all('span', {'class': 'pull-left title al width-73'})
#
#             all_titles = []
#
#             for i in range(1, len(titles)):
#                 temp = titles[i].text.strip().encode('utf-8')
#                 all_titles.append(temp)
#
#             for k in range(0, len(all_titles)):
#                 temp = {}
#                 temp['title'] = all_titles[k]
#                 temp['link'] = forms[k]
#                 ret_forms.append(temp)
#
#             Return_forms = json.dumps({"forms": ret_forms})
#             print Return_forms
#
#     except:
#         pass
#
#     return Return_forms
