from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from lxml import etree
from io import StringIO
import requests
from multiprocessing.pool import ThreadPool
import os

chrome_options = Options()
prefs = {'download.default_directory' : '/home/ubuntu/pdf', "download.prompt_for_download": False}
chrome_options.add_experimental_option('prefs', prefs)

chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': "/home/ubuntu/pdf"}}
command_result = driver.execute("send_command", params)


pool = ThreadPool(processes=2)

def delhiPoliceFirBefore2015(district, policestation, caseyear, firno):
    driver.get('http://59.180.234.21:85/index.aspx')


    district_name = Select(driver.find_element_by_id("ddlDistrict"))
    district_name.select_by_visible_text(district)
    sleep(2)

    policestn_name = Select(driver.find_element_by_id("ddlPS"))
    policestn_name.select_by_visible_text(policestation)

    year = Select(driver.find_element_by_id("ddlYear"))
    year.select_by_visible_text(caseyear)

    search_box1 = driver.find_element_by_id("txtRegNo")
    search_box1.send_keys(firno)

    driver.find_element_by_id("btnSearch").click()
    sleep(2)

    html_page=driver.page_source

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html_page), parser)

    firData = []
    trindex = 2
    try:
        while len(tree.xpath('//*[@id="DgRegist"]/tbody/tr[{}]//text()'.format(trindex))) > 3:
            trrow = tree.xpath('//*[@id="DgRegist"]/tbody/tr[{}]//text()'.format(trindex))
            trrow_striped = []
            for td in trrow:
                if(td.strip() != ''):
                    trrow_striped.append(td)
            try:
                link = driver.find_element_by_xpath('//*[@id="DgRegist_ctl0{}_imgDelete"]'.format(trindex + 1))
                link.click()
                sleep(2)
                trrow_striped.append(driver.find_element_by_id('divAutomobile').text)
            except Exception as e:
                print(e)
                trrow_striped.append("no content")


            firData.append({
                'firno': trrow_striped[0],
                'firyear': trrow_striped[1],
                'firdate': trrow_striped[2],
                'linkData': trrow_striped[3]
            })



            trindex += 1
    except:
        print("##############################################")




    return firData





def getDelhiPolicestationBefore2015(districtCodes):
    policestation = [{'162': [{'ANAND PARBAT': '01'}, {'CHANDANI MAHAL': '08'}, {'D.B.G. ROAD': '38'},
                              {'DARYA GANJ': '10'}, {'HAUZ QAZI': '15'}, {'I.P. ESTATE': '16'}, {'JAMA MASJID': '19'},
                              {'KAMLA MKT.': '23'}, {'KAROL BAGH': '26'}, {'NABI KARIM': '30'}, {'PAHAR GANJ': '41'},
                              {'PARSAD NAGAR': '40'}, {'PATEL NAGAR': '42'}, {'RAJINDER NAGAR': '45'},
                              {'RANJIT NAGAR': '56'}]}, {
                         '164': [{'ANAND VIHAR RLY STATION': '04'}, {'CRIME BRANCH': '02'},
                                 {'e-Police Station M.V. Theft': '46'}, {'E.O.W': '39'}, {'H.N.DIN STN.': '32'},
                                 {'IGI AIRPORT METRO': '08'}, {'KALKAJI METRO': '06'}, {'KASHMIRI GATE METRO': '38'},
                                 {'N.D.L.S.': '26'}, {'NARCOTIC CELL': '01'}, {'NARCOTICS': '27'},
                                 {'QUTUB MINAR': '07'}, {'R.M.D. MAIN': '25'}, {'RAJOURI GARDEN METRO STATION': '40'},
                                 {'RITHALA METRO STATION': '36'}, {'SARAI ROHILLA STN.': '34'},
                                 {'SHASTRI PARK METRO STATION': '37'}, {'YAMUNA DEPOT METRO': '05'}]},
                     {'168': [{'ANAND VIHAR': '01'}, {'FARSH BAZAR': '07'}, {'GANDHI NAGAR': '11'},
                              {'GEETA COLONY': '12'}, {'GHAZIPUR': '10'}, {'JAGAT PURI': '14'}, {'KALYAN PURI': '13'},
                              {'KIRSHNA NAGAR': '20'}, {'MADHU VIHAR': '23'}, {'MANDAWALI': '24'},
                              {'MAYUR VIHAR': '26'}, {'NEW ASHOK NAGAR': '28'}, {'PANDAV NAGAR': '50'},
                              {'PREET VIHAR': '30'}, {'SHAKAR PUR': '41'}, {'VIVEK VIHAR': '09'}]},
                     {'169': [{'DOMESTIC AIRPORT': '01'}, {'IGI AIRPORT': '02'}, {'MAHIPAL PUR': '03'}]},
                     {'165': [{'BARAKHAMBA ROAD': '02'}, {'CHANAKYA PURI': '07'}, {'CON. PLACE': '11'},
                              {'EXH. GROUN': '12'}, {'MANDIR MARG': '15'}, {'PT. STREET': '22'}, {'TILAK MARG': '35'},
                              {'TUGLAK ROAD': '36'}]},
                     {'166': [{'B.H.RAO': '04'}, {'BURARI': '52'}, {'CIVIL LINES': '07'}, {'GULABI BAGH': '24'},
                              {'K.GATE': '16'}, {'KOTWALI': '18'}, {'LAHORI GATE': '23'}, {'MOURICE NAGAR': '10'},
                              {'ROOP NAGAR': '31'}, {'SADAR BAZAR': '38'}, {'SARAI ROHILLA': '39'},
                              {'SUBZI MANDI': '41'}, {'TIMAR PUR': '51'}]},
                     {'173': [{'BHAJAN PURA': '05'}, {'DILSHAD GARDEN': '07'}, {'G.T.B. ENCLAVE': '20'},
                              {'GOKUL PURI': '54'}, {'HARSH VIHAR': '55'}, {'JYOTI  NAGAR': '56'},
                              {'KARAWAL NAGAR': '16'}, {'KHAJURI KHAS': '15'}, {'M.S. PARK': '21'},
                              {'NAND  NAGARI': '25'}, {'NEW USMAN PUR': '30'}, {'SEELAM PUR': '42'},
                              {'SEEMA PURI': '44'}, {'SHAHADRA': '40'}, {'SONIA VIHAR': '57'}, {'WELCOME': '45'},
                              {'ZAFRABAD': '58'}]},
                     {'172': [{'ADARSH NAGAR': '03'}, {'ASHOK VIHAR': '06'}, {'BHALSWA DAIRY': '08'},
                              {'BHARAT NAGAR': '07'}, {'JAHANGIR PURI': '14'}, {'KESHAV PURAM': '25'},
                              {'MAHENDRA PARK': '51'}, {'MAURYA ENCLAVE': '49'}, {'MODEL TOWN': '17'},
                              {'MUKHERJI NAGAR': '30'}, {'RANI BAGH': '50'}, {'SHALIMAR BAGH': '35'},
                              {'SUBHASH PLACE': '47'}, {'SWAROOP NAGAR': '36'}]},
                     {'174': [{'ALIPUR': '01'}, {'AMAN VIHAR': '08'}, {'BAWANA': '09'}, {'BEGUM PUR': '15'},
                              {'K.N.KATJU MARG': '16'}, {'KANJHAWLA': '10'}, {'MANGOL PURI': '05'}, {'NARELA': '02'},
                              {'NORTH ROHINI': '17'}, {'PRASHANT VIHAR': '14'}, {'SAMAI PUR BADLI': '03'},
                              {'SHAHBAD DAIRY': '13'}, {'SOUTH ROHINI': '07'}, {'SULTAN PURI': '11'},
                              {'VIJAY VIHAR': '12'}]},
                     {'167': [{'DEFENCE COLONY': '10'}, {'FATEHPUR BERI': '12'}, {'HAUZ KHAS': '17'}, {'K.M.PUR': '23'},
                              {'LODHI COLONY': '28'}, {'MALVIYA NAGAR': '33'}, {'MEHRAULI': '32'}, {'NEB SARAI': '57'},
                              {'R. K. PURAM': '41'}, {'S.N.PURI': '45'}, {'SAFDARJUNG ENCLAVE': '47'}, {'SAKET': '56'},
                              {'SAROJINI NAGAR': '46'}, {'SOUTH CAMPUS': '11'}, {'VASANT KUNJ NORTH': '58'},
                              {'VASANT KUNJ SOUTH': '60'}, {'VASANT VIHAR': '59'}]},
                     {'955': [{'AMAR COLONY': '07'}, {'AMB. NAGAR': '15'}, {'BADAR PUR': '12'}, {'C. R. PARK': '10'},
                              {'GOVIND PURI': '02'}, {'GREATER KAILASH': '08'}, {'H. N. DIN': '05'}, {'JAIT PUR': '01'},
                              {'JAMIA NAGAR': '04'}, {'KALKAJI': '09'}, {'LAJPAT NAGAR': '06'}, {'N. F. COLONY': '03'},
                              {'O. I. ESTATE': '13'}, {'PUR PRAHLAD PUR': '17'}, {'SANGAM VIHAR': '14'},
                              {'SARITA VIHAR': '11'}, {'SUNLIGHT COLONY': '16'}]},
                     {'171': [{'BABA HARIDAS NAGAR': '05'}, {'BINDA PUR': '04'}, {'CHHAWALA': '58'}, {'DABRI': '10'},
                              {'DELHI CANTT': '11'}, {'DWARKA NORTH': '15'}, {'DWARKA SECTOR 23': '16'},
                              {'DWARKA SOUTH': '14'}, {'INDER PURI': '17'}, {'J.P. KALAN': '20'}, {'KAPSHERA': '30'},
                              {'NAJAFGARH': '32'}, {'NARAINA': '35'}, {'PALAM VILLAGE': '57'}, {'SAGAR PUR': '54'}]},
                     {'954': [{'SPECIAL CELL': '01'}]},
                     {'953': [{'C.A.W NANAK PURA': '01'}]},
                     {'161': [{'VIGILANCE': '01'}]},
                     {'170': [{'HARI NAGAR': '15'}, {'JANAK PURI': '21'}, {'KHYALA': '62'}, {'KIRTI NAGAR': '25'},
                              {'MADI PUR': '26'}, {'MAYA PURI': '28'}, {'MIANWALI NAGAR': '30'}, {'MOTI NAGAR': '29'},
                              {'MUNDKA': '27'}, {'NANGLOI': '33'}, {'NIHAL VIHAR': '61'}, {'PASCHIM VIHAR': '44'},
                              {'PUNJABI BAGH': '43'}, {'RAJOURI GARDEN': '37'}, {'RANHOLA': '38'},
                              {'TILAK NAGAR': '51'}, {'UTTAM NAGAR': '55'}, {'VIKAS PURI': '60'}]}]


    for station in policestation:
        if(list(station.keys())[0] == districtCodes):
            return (station)


def getPoliceDistrictBefore2015():
    return [{'CENTRAL DISTT': '162'}, {'CRIME AND RAILWAYS': '164'}, {'EAST DELHI DISTT': '168'}, {'IGI DISTT': '169'}, {'NEW DELHI DISTT': '165'}, {'NORTH DISTT': '166'}, {'NORTH EAST DISTT': '173'}, {'NORTH WEST DISTT': '172'}, {'OUTER DISTT': '174'}, {'SOUTH DISTT': '167'}, {'SOUTH EAST DISTT': '955'}, {'SOUTH WEST DISTT': '171'}, {'SPECIAL CELL DISTT': '954'}, {'SPUW & C DISTT': '953'}, {'VIGILANCE': '161'}, {'WEST DISTT': '170'}]




def getDelhiPolicestationAfter2015(districtCodes):
    policestation = [{ '8162': [{'ANAND PARBAT': '8162001'}, {'CHANDNI MAHAL': '8162008'}, {'D.B.G. ROAD': '8162038'}, {'DARYA GANJ': '8162010'}, {'HAUZ QAZI': '8162015'}, {'I.P.ESTATE': '8162016'}, {'JAMA MASJID': '8162019'}, {'KAMLA MARKET': '8162023'}, {'KAROL BAGH': '8162026'}, {'NABI KARIM': '8162030'}, {'PAHAR GANJ': '8162041'}, {'PATEL NAGAR': '8162042'}, {'PRASAD NAGAR': '8162040'}, {'RAJINDER NAGAR': '8162045'}, {'RANJIT NAGAR': '8162056'}] },
                 {'8175': [{'CRIME BRANCH': '8175001'}]},
                 {'8176': [{'BABA HARIDAS NAGAR': '8176009'}, {'BINDA PUR': '8176001'}, {'CHHAWALA': '8176007'}, {'DABRI': '8176002'}, {'DWARKA NORTH': '8176004'}, {'DWARKA SOUTH': '8176003'}, {'JAFFARPUR KALAN': '8176006'}, {'MOHAN GARDEN': '8176012'}, {'NAJAF GARH': '8176010'}, {'SECTOR 23 DWARKA': '8176005'}, {'UTTAM NAGAR': '8176008'}]},
                 {'8168': [{'ANAND VIHAR(EAST)': '8168001'}, {'FARSH BAZAR(EAST)': '8168007'}, {'GANDHI NAGAR(EAST)': '8168011'}, {'GEETA COLONY(EAST)': '8168012'}, {'GHAZIPUR': '8168010'}, {'JAGAT PURI(EAST)': '8168014'}, {'KALYANPURI': '8168013'}, {'KRISHNA NAGAR(EAST)': '8168020'}, {'LAXMI NAGAR': '8168054'}, {'MADHU VIHAR': '8168023'}, {'MANDAWLI FAZAL PUR': '8168024'}, {'MAYUR VIHAR PH-I': '8168026'}, {'NEW ASHOK NAGAR': '8168028'}, {'PANDAV NAGAR': '8168050'}, {'PATPARGANJ INDUSTRIAL AREA': '8168053'}, {'PREET VIHAR': '8168030'}, {'SHAKARPUR': '8168052'}, {'SHAKARPUR(EAST)': '8168041'}, {'VIVEK VIHAR(EAST)': '8168009'}]},
                 {'8956': [{'ECONOMIC OFFENCES WING': '8956001'}]},
                 {'8169': [{'DOMESTIC AIRPORT': '8169001'}, {'I.G.I.AIRPORT': '8169002'}]},
                 {'8160': [{'IGI AIRPORT METRO': '8160004'}, {'INA METRO': '8160011'}, {'JANAK PURI METRO': '8160010'}, {'KASHMIRI GATE METRO': '8160007'}, {'Metro Police Station Azadpur': '8160015'}, {'Metro Police Station Ghitorni': '8160003'}, {'Metro Police Station Nangloi': '8160009'}, {'Metro Police Station Netaji Subhash Place': '8160016'}, {'Metro Police Station Okhla Vihar': '8160002'}, {'Metro Police Station Pragati Maidan': '8160014'}, {'Metro Police Station Rajiv Chowk': '8160012'}, {'Nehru Place Metro': '8160013'}, {'RAJA GARDEN METRO': '8160008'}, {'RITHALA METRO': '8160005'}, {'SHASHTRI PARK METRO': '8160006'}, {'YAMUNA DEPOT METRO': '8160001'}]},
                 {'8165': [{'BARAKHAMBA ROAD': '8165002'}, {'CHANKYA PURI': '8165007'}, {'CONNAUGHT PLACE': '8165011'}, {'IITF,Pragati Maidan': '8165012'}, {'MANDIR MARG': '8165015'}, {'NORTH AVENUE': '8165038'}, {'PARLIAMENT STREET': '8165022'}, {'SOUTH AVENUE': '8165037'}, {'TILAK MARG': '8165035'}, {'TUGHLAK ROAD': '8165036'}]},
                 {'8166': [{'BARA HINDU RAO': '8166004'}, {'BURARI': '8166052'}, {'CIVIL LINES': '8166007'}, {'GULABI BAGH': '8166024'}, {'KASHMERI GATE': '8166016'}, {'KOTWALI': '8166018'}, {'LAHORI GATE': '8166023'}, {'MAURICE NAGAR': '8166010'}, {'ROOP NAGAR': '8166031'}, {'SADAR BAZAR': '8166038'}, {'SARAI ROHILLA': '8166039'}, {'SUBZI MANDI': '8166041'}, {'TIMARPUR': '8166051'}, {'WAZIRABAD': '8166054'}]},
                 {'8173': [{'BHAJAN PURA': '8173005'}, {'DAYAL PUR': '8173061'}, {'G.T.B. ENCLAVE(NORTH EAST)': '8173020'}, {'GOKUL PURI': '8173054'}, {'HARSH VIHAR': '8173055'}, {'JAFRABAD': '8173058'}, {'JYOTI NAGAR': '8173056'}, {'KARAWAL NAGAR': '8173016'}, {'KHAJURI KHAS': '8173015'}, {'MANSAROVAR PARK(NORTH EAST)': '8173021'}, {'NAND NAGRI': '8173025'}, {'NEW USMANPUR': '8173030'}, {'SEELAMPUR': '8173042'}, {'SEEMAPURI(NORTH EAST)': '8173044'}, {'SHAHDARA(NORTH EAST)': '8173040'}, {'SHASTRI PARK': '8173060'}, {'SONIA VIHAR': '8173057'}, {'WELCOME': '8173045'}]},
                 {'8172': [{'ADARSH NAGAR': '8172003'}, {'ASHOK VIHAR': '8172006'}, {'BHALSWA DAIRY(NORTH WEST)': '8172008'}, {'BHARAT NAGAR': '8172007'}, {'JAHANGIR PURI': '8172014'}, {'KESHAV PURAM': '8172025'}, {'MAHENDRA PARK': '8172051'}, {'MAURYA ENCLAVE': '8172049'}, {'MODEL TOWN': '8172017'}, {'MUKHERJEE NAGAR': '8172030'}, {'RANI BAGH(NORTH WEST)': '8172050'}, {'SHALIMAR BAGH': '8172035'}, {'SUBHASH PLACE': '8172047'}, {'SWAROOP NAGAR(NORTH WEST)': '8172036'}]},
                 {'8174': [{'ALIPUR(OUTER)': '8174001'}, {'AMAN VIHAR(OUTER)': '8174008'}, {'BABA HARIDAS NAGAR(OUTER)': '8174018'}, {'BAWANA(OUTER)': '8174009'}, {'BEGUM PUR(OUTER)': '8174015'}, {'K.N. KATJU MARG(OUTER)': '8174016'}, {'KANJHAWALA(OUTER)': '8174010'}, {'MANGOL PURI': '8174005'}, {'MIANWALI NAGAR(OUTER)': '8174023'}, {'MUNDKA': '8174025'}, {'NAJAF GARH(OUTER)': '8174019'}, {'NANGLOI': '8174021'}, {'NIHAL VIHAR': '8174022'}, {'NORTH ROHINI(OUTER)': '8174017'}, {'PASCHIM VIHAR EAST': '8174026'}, {'PASCHIM VIHAR WEST': '8174027'}, {'PASCHIM VIHAR(OUTER)': '8174024'}, {'PRASHANT VIHAR(OUTER)': '8174014'}, {'RAJ PARK': '8174029'}, {'RANHOLA': '8174020'}, {'RANI BAGH': '8174028'}, {'SAMAIPUR BADLI(OUTER)': '8174003'}, {'SHAHBAD DAIRY(OUTER)': '8174013'}, {'SOUTH ROHINI(OUTER)': '8174007'}, {'SULTANPURI': '8174011'}, {'VIJAY VIHAR(OUTER)': '8174012'}]},
                 {'8991': [{'ALIPUR': '8991006'}, {'BAWANA': '8991004'}, {'BHALSWA DAIRY': '8991003'}, {'NARELA': '8991007'}, {'NARELA INDUSTRIAL AREA': '8991001'}, {'SAMAIPUR BADLI': '8991008'}, {'SHAHBAD DAIRY': '8991005'}, {'SWAROOP NAGAR': '8991002'}]},
                 {'8164': [{'ANAND VIHAR RLY STN': '8164004'}, {'DELHI CANTT. RAILWAY STATION': '8164041'}, {'HAZRAT NIZAMUDDIN RLY STN': '8164032'}, {'NEW DELHI RLY. STN.': '8164026'}, {'OLD DELHI (DELHI MAIN) RLY. STN.': '8164025'}, {'SARAI ROHILLA STATION': '8164034'}, {'SUBZI MANDI RAILWAY STATION': '8164042'}]},
                 {'8959': [{'ALIPUR(ROHINI)': '8959004'}, {'AMAN VIHAR': '8959016'}, {'BAWANA(ROHINI)': '8959001'}, {'BEGUM PUR': '8959003'}, {'BUDH VIHAR': '8959014'}, {'K.N. KATJU MARG': '8959007'}, {'KANJHAWALA': '8959015'}, {'NARELA(ROHINI)': '8959005'}, {'NORTH ROHINI': '8959011'}, {'PRASHANT VIHAR': '8959008'}, {'PREM NAGAR': '8959013'}, {'SAMAIPUR BADLI(ROHINI)': '8959006'}, {'SHAHBAD DAIRY(ROHINI)': '8959002'}, {'SOUTH ROHINI': '8959010'}, {'VIJAY VIHAR': '8959009'}]},
                 {'8957': [{'ANAND VIHAR': '8957002'}, {'FARSH BAZAR': '8957006'}, {'G.T.B. ENCLAVE': '8957009'}, {'GANDHI NAGAR': '8957004'}, {'GEETA COLONY': '8957005'}, {'JAGAT PURI': '8957011'}, {'KRISHNA NAGAR': '8957003'}, {'MANSAROVAR PARK': '8957008'}, {'SEEMAPURI': '8957010'}, {'SHAHDARA': '8957007'}, {'VIVEK VIHAR': '8957001'}]},
                 {'8167': [{'AMBEDKAR NAGAR': '8167064'}, {'CHITRANJAN PARK': '8167062'}, {'DEFENCE COLONY': '8167010'}, {'FATEHPUR BERI': '8167012'}, {'GREATER KAILASH': '8167061'}, {'HAUZ KHAS': '8167017'}, {'K.M. PUR': '8167023'}, {'LODI COLONY': '8167028'}, {'MAIDAN GARHI': '8167066'}, {'MALVIYA NAGAR': '8167033'}, {'MEHRAULI': '8167032'}, {'NEB SARAI': '8167057'}, {'R. K. PURAM(SOUTH)': '8167041'}, {'SAFDARJUNG ENCLAVE(SOUTH)': '8167047'}, {'SAKET': '8167056'}, {'SANGAM VIHAR': '8167063'}, {'SAROJINI NAGAR(SOUTH)': '8167046'}, {'SOUTH CAMPUS(SOUTH)': '8167011'}, {'TIGRI': '8167067'}, {'VASANT KUNJ NORTH(SOUTH)': '8167058'}, {'VASANT KUNJ SOUTH(SOUTH)': '8167060'}, {'VASANT VIHAR(SOUTH)': '8167059'}]},
                 {'8171': [{'BABA HARIDAS NAGAR(SOUTH WEST)': '8171005'}, {'BINDA PUR(SOUTH WEST)': '8171004'}, {'CHHAWALA(SOUTH WEST)': '8171058'}, {'DABRI(SOUTH WEST)': '8171010'}, {'DELHI CANTT': '8171011'}, {'DWARKA NORTH(SOUTH WEST)': '8171015'}, {'DWARKA SOUTH(SOUTH WEST)': '8171014'}, {'INDER PURI(SOUTH WEST)': '8171017'}, {'JAFFARPUR KALAN(SOUTH WEST)': '8171020'}, {'KAPASHERA': '8171030'}, {'KISHAN GARH': '8171066'}, {'NAGAF GARH(SOUTH WEST)': '8171032'}, {'NARAINA(SOUTH WEST)': '8171035'}, {'PALAM VILLAGE': '8171057'}, {'R. K. PURAM': '8171060'}, {'SAFDARJUNG ENCLAVE': '8171067'}, {'SAGAR PUR': '8171054'}, {'SAROJINI NAGAR': '8171068'}, {'SECTOR 23 DWARKA(SOUTH WEST)': '8171016'}, {'SOUTH CAMPUS': '8171061'}, {'UTTAM NAGAR(SOUTH WEST)': '8171059'}, {'VASANT KUNJ NORTH': '8171062'}, {'VASANT KUNJ SOUTH': '8171063'}, {'VASANT VIHAR': '8171064'}]},
                 {'8955': [{'AMAR COLONY': '8955007'}, {'AMBEDKAR NAGAR(SOUTH EAST)': '8955015'}, {'BADARPUR': '8955012'}, {'CHITRANJAN PARK(SOUTH EAST)': '8955010'}, {'GOVIND PURI': '8955002'}, {'GREATER KAILASH(SOUTH EAST)': '8955008'}, {'HAZARAT NIZAMUDDIN': '8955005'}, {'JAIT PUR': '8955001'}, {'JAMIA NAGAR': '8955004'}, {'KALANDI KUNJ': '8955019'}, {'KALKAJI': '8955009'}, {'LAJPAT NAGAR': '8955006'}, {'NEW FRIENDS COLONY': '8955003'}, {'OKHLA INDUSTRIAL AREA': '8955013'}, {'PUL PRAHLAD PUR': '8955017'}, {'SANGAM VIHAR(SOUTH EAST)': '8955014'}, {'SARITA VIHAR': '8955011'}, {'SHAHEEN BAGH': '8955020'}, {'SUNLIGHT COLONY': '8955016'}]},
                 {'8954': [{'SPECIAL CELL (SB)': '8954001'}]},
                 {'8953': [{'CRIME (WOMEN) CELL NANAK PURA': '8953001'}]},
                 {'8161': [{'VIGILANCE PS': '8161001'}]},
                 {'8170': [{'HARI NAGAR': '8170015'}, {'INDER PURI': '8170064'}, {'JANAK PURI': '8170021'}, {'KHYALA': '8170062'}, {'KIRTI NAGAR': '8170025'}, {'MAYAPURI': '8170028'}, {'MIANWALI NAGAR(WEST)': '8170030'}, {'MOTI NAGAR': '8170029'}, {'MUNDKA(WEST)': '8170027'}, {'NANGLOI(WEST)': '8170033'}, {'NARAINA': '8170063'}, {'NIHAL VIHAR(WEST)': '8170061'}, {'PASCHIM VIHAR(WEST)': '8170044'}, {'PUNJABI BAGH': '8170043'}, {'RAJOURI GARDEN': '8170037'}, {'RANHOLA(WEST)': '8170038'}, {'TILAK NAGAR': '8170051'}, {'UTTAM NAGAR(WEST)': '8170055'}, {'VIKASPURI': '8170060'}]}]

    for station in policestation:
        if(list(station.keys())[0] == districtCodes):
            return (station)


def getPoliceDistrictAfter2015():
    return [{'CENTRAL': '8162'}, {'CRIME BRANCH': '8175'}, {'DWARKA': '8176'}, {'EAST': '8168'}, {'EOW': '8956'}, {'IGI AIRPORT': '8169'}, {'METRO': '8160'}, {'NEW DELHI': '8165'}, {'NORTH': '8166'}, {'NORTH EAST': '8173'}, {'NORTH WEST': '8172'}, {'OUTER DISTRICT': '8174'}, {'OUTER NORTH': '8991'}, {'RAILWAYS': '8164'}, {'ROHINI': '8959'}, {'SHAHDARA': '8957'}, {'SOUTH': '8167'}, {'SOUTH WEST': '8171'}, {'SOUTH-EAST': '8955'}, {'SPECIAL CELL(SB)': '8954'}, {'SPECIAL POLICE UNIT FOR WOMEN & CHILDREN': '8953'}, {'VIGILANCE': '8161'}, {'WEST': '8170'}]



def getstov():
    driver.get('http://59.180.234.21:8080/citizen/firSearch.htm')
    return str(driver.find_element_by_id('formfirsearch').get_attribute('action')).split('stov=')[1]


def getFir_after2015(sdis_no,sps_no, year, firno):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
               'Host': '59.180.234.21:8080', 'Content-Length': '125'}
    url = "http://59.180.234.21:8080/citizen/regfirsearchpage.htm"
    payload = 'sdistrict=' + str(sdis_no) + '&spolicestation=' + str(
        sps_no) + '&firFromDateStr=&firToDateStr=&regFirNo=' + firno + '&radioValue=undefined&searchName=&firYear=' + year

    r = requests.post(url, headers=headers, params=payload)

    # r = requests.post(url, headers=headers, params=payload)
    p = r.json()

    data = []

    for i in p['list']:
        data.append({
            'firRegDate': i['firRegDate'],
            'recordCreatedOn': i["recordCreatedOn"],
            'firNumDisplay': i["firNumDisplay"],
            'link': 'http://59.180.234.21:8080/citizen/gefirprint.htm?firRegNo=' + i[
                "firRegNum"] + '&stov='
        })

    if (data == []):
        return {"success": False}
    else:
        return {"success": True, 'data': data}




def delhiPoliceFirAfter2015(sdis_no,sps_no, year, firno):
    stov = pool.apply_async(getstov)
    fir = pool.apply_async(getFir_after2015, args=(sdis_no,sps_no, year, firno))

    stovToken = stov.get()
    firData = fir.get()

    data = []
    for i in firData['data']:
        i['link']  = i['link'] + stovToken
        data.append(i)
    firData['data'] = data


    return firData


def Mvtheft(textfirno, textfiryear, textdistrict, textpolicestation):

    try:
        driver.get('http://59.180.234.21:8070/publicviewfir.aspx')

        firno = driver.find_element_by_id("txtFIRNO")
        firno.send_keys((textfirno))

        if(textfiryear != ""):
            firyear = Select(driver.find_element_by_id("ddlYear"))
            firyear.select_by_visible_text(textfiryear)


        if(textdistrict != "" and textpolicestation != ""):
            firdistrict = Select(driver.find_element_by_id("ddlDistrict"))
            firdistrict.select_by_visible_text(textdistrict)
            sleep(1)

            firpolicestation = Select(driver.find_element_by_id("ddlPoliceStation"))
            firpolicestation.select_by_visible_text(textpolicestation)

        driver.find_element_by_id("btnSubmit").click()
        sleep(2)

        html_page= driver.page_source

        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html_page), parser)

        mvtheft_details = []
        mvtheft_index = 2
        while len(list(filter(lambda x: x.strip() != "",tree.xpath('//*[@id="GridViewFIRList"]/tbody/tr[{}]//text()'.format(mvtheft_index))))) > 3:
            details = list(filter(lambda x: x.strip() != "",tree.xpath('//*[@id="GridViewFIRList"]/tbody/tr[{}]//text()'.format(mvtheft_index))))


            mvtheft_details.append({
                'firno': details[0],
                'Name': details[1],
                'Mobile': details[2],
                'Address': details[3],
                'firno_name': details[0].split('/')[0]
            })

            mvtheft_index += 1
        return { 'success': 'successfull', 'details': mvtheft_details  }

    except:
        return { 'status' : 'unsuccessfull' }


def getMvtheftFir(FIRNO, textfirno, textfiryear, textdistrict, textpolicestation):
    try:
        driver.get('http://59.180.234.21:8070/publicviewfir.aspx')

        firno = driver.find_element_by_id("txtFIRNO")
        firno.send_keys((textfirno))

        if(textfiryear != ""):
            firyear = Select(driver.find_element_by_id("ddlYear"))
            firyear.select_by_visible_text(textfiryear)


        if(textdistrict != "" and textpolicestation != ""):
            firdistrict = Select(driver.find_element_by_id("ddlDistrict"))
            firdistrict.select_by_visible_text(textdistrict)
            sleep(1)

            firpolicestation = Select(driver.find_element_by_id("ddlPoliceStation"))
            firpolicestation.select_by_visible_text(textpolicestation)

        driver.find_element_by_id("btnSubmit").click()
        sleep(3)

        htmlpage = driver.page_source
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(htmlpage), parser)

        mv_theftindex = 0
        while len(tree.xpath('// *[ @ id = "GridViewFIRList_Label1_{}"]//text()'.format(mv_theftindex))) > 0:
            text = tree.xpath('// *[ @ id = "GridViewFIRList_Label1_{}"]//text()'.format(mv_theftindex))[0].split('/')[0]


            if(text == FIRNO):
                driver.find_element_by_id('GridViewFIRList_downloadPdf_{}'.format(mv_theftindex)).click()
                sleep(2)
                while True:
                    if any(fname.endswith('.part') for fname in os.listdir('/home/ubuntu/pdf')):
                        sleep(1)
                    elif not any(fname.endswith('.part') for fname in os.listdir('/home/ubuntu/pdf')):
                        break
                    else:
                        sleep(1)
                return {'success': 'successfull',
                        'link': 'https://www.indianlawportal.com/pdf/' + list(filter(lambda x: str(x).__contains__(text),
                                                                           os.listdir(
                                                                               '/home/ubuntu/pdf')))[0]}
            mv_theftindex += 1
    except Exception as e:
        print(e)
        return { 'success': 'unsuccessfull' }


def Propertytheft(textfirno, textfiryear, textdistrict, textpolicestation):

    try:
        driver.get('http://59.180.234.21:8060/publicviewfir.aspx')

        firno = driver.find_element_by_id("txtFIRNO")
        firno.send_keys((textfirno))

        if(textfiryear != ""):
            firyear = Select(driver.find_element_by_id("ddlYear"))
            firyear.select_by_visible_text(textfiryear)


        if(textdistrict != "" and textpolicestation != ""):
            firdistrict = Select(driver.find_element_by_id("ddlDistrict"))
            firdistrict.select_by_visible_text(textdistrict)
            sleep(1)

            firpolicestation = Select(driver.find_element_by_id("ddlPoliceStation"))
            firpolicestation.select_by_visible_text(textpolicestation)

        driver.find_element_by_id("btnSubmit").click()
        sleep(3)

        html_page= driver.page_source

        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html_page), parser)

        mvtheft_details = []
        mvtheft_index = 2


        while len(list(filter(lambda x: x.strip() != "",tree.xpath('//*[@id="GridViewFIRList"]/tbody/tr[{}]//text()'.format(mvtheft_index))))) > 3:
            details = list(filter(lambda x: x.strip() != "",tree.xpath('//*[@id="GridViewFIRList"]/tbody/tr[{}]//text()'.format(mvtheft_index))))

            mvtheft_details.append({
                'firno': details[0],
                'Name': details[1],
                'Mobile': details[2],
                'Address': details[3],
                'firno_name': details[0].split('/')[0]
                
            })

            mvtheft_index += 1
        return { 'success': 'successfull', 'details': mvtheft_details  }

    except Exception as e:
        print(e)
        return { 'status' : 'unsuccessfull' }


def getPropertyFir(FIRNO, textfirno, textfiryear, textdistrict, textpolicestation):
    try:
        driver.get('http://59.180.234.21:8060/publicviewfir.aspx')

        firno = driver.find_element_by_id("txtFIRNO")
        firno.send_keys((textfirno))

        if(textfiryear != ""):
            firyear = Select(driver.find_element_by_id("ddlYear"))
            firyear.select_by_visible_text(textfiryear)


        if(textdistrict != "" and textpolicestation != ""):
            firdistrict = Select(driver.find_element_by_id("ddlDistrict"))
            firdistrict.select_by_visible_text(textdistrict)
            sleep(1)

            firpolicestation = Select(driver.find_element_by_id("ddlPoliceStation"))
            firpolicestation.select_by_visible_text(textpolicestation)

        driver.find_element_by_id("btnSubmit").click()
        sleep(3)

        htmlpage = driver.page_source
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(htmlpage), parser)

        mv_theftindex = 0
        while len(tree.xpath('// *[ @ id = "GridViewFIRList_Label1_{}"]//text()'.format(mv_theftindex))) > 0:
            text = tree.xpath('// *[ @ id = "GridViewFIRList_Label1_{}"]//text()'.format(mv_theftindex))[0].split('/')[0]


            if(text == FIRNO):
                driver.find_element_by_id('GridViewFIRList_downloadPdf_{}'.format(mv_theftindex)).click()
                sleep(2)
                while True:
                    if any(fname.endswith('.part') for fname in os.listdir('/home/ubuntu/pdf')):
                        sleep(1)
                    elif not any(fname.endswith('.part') for fname in os.listdir('/home/ubuntu/pdf')):
                        break
                    else:
                        sleep(1)
                return {'success': 'successfull',
                        'link': 'https://www.indianlawportal.com/pdf/' + list(filter(lambda x: str(x).__contains__(text),
                                                                           os.listdir(
                                                                               '/home/ubuntu/pdf')))[0]}
            mv_theftindex += 1
    except Exception as e:
        print(e)
        return { 'success': 'unsuccessfull' }



def getMvtheftdistrict():
    return [{'text': 'Select District', 'value': ''}, {'text': 'CENTRAL DISTRICT', 'value': '162-008'}, {'text': 'DELHI', 'value': '000-008'}, {'text': 'DIRECTORATE OF ENFORMENT', 'value': '998-008'}, {'text': 'DWARKA', 'value': '176-008'}, {'text': 'EAST DISTRICT', 'value': '168-008'}, {'text': 'IGI UNIT', 'value': '169-008'}, {'text': 'METRO', 'value': '160-008'}, {'text': 'NEW DELHI', 'value': '165-008'}, {'text': 'NORTH DISTRICT', 'value': '166-008'}, {'text': 'NORTH EAST', 'value': '173-008'}, {'text': 'NORTH WEST', 'value': '172-008'}, {'text': 'OUTER DISTRICT', 'value': '174-008'}, {'text': 'OUTER NORTH', 'value': '991-008'}, {'text': 'RAILWAYS', 'value': '164-008'}, {'text': 'ROHINI', 'value': '959-008'}, {'text': 'Shahdara', 'value': '957-008'}, {'text': 'SOUTH DISTRICT', 'value': '167-008'}, {'text': 'SOUTH EAST', 'value': '955-008'}, {'text': 'SOUTH WEST', 'value': '171-008'}, {'text': 'SPECIAL BRANCH', 'value': '163-008'}, {'text': 'WEST DISTRICT', 'value': '170-008'}]


def getMvtheftpolicestation(districtcode):
    policestation = [{ '162-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'ANAND PARBAT', 'value': '162-01'}, {'text': 'CHANDANI MAHAL', 'value': '162-08'}, {'text': 'D.B.G. ROAD', 'value': '162-38'}, {'text': 'DARYA GANJ', 'value': '162-10'}, {'text': 'HAUZ QAZI', 'value': '162-15'}, {'text': 'I.P. ESTATE', 'value': '162-16'}, {'text': 'JAMA MASJID', 'value': '162-19'}, {'text': 'KAMLA MKT.', 'value': '162-23'}, {'text': 'KAROL BAGH', 'value': '162-26'}, {'text': 'NABI KARIM', 'value': '162-30'}, {'text': 'PAHAR GANJ', 'value': '162-41'}, {'text': 'PARSAD NAGAR', 'value': '162-40'}, {'text': 'PATEL NAGAR', 'value': '162-42'}, {'text': 'RAJINDER NAGAR', 'value': '162-45'}, {'text': 'RANJIT NAGAR', 'value': '162-46'}]},
            {'000-008': [{'text': 'Select Police Station', 'value': ''}]},
            {'998-008': [{'text': 'Select Police Station', 'value': ''}]},
            {'176-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'BABA HARI DASS NAGAR', 'value': '176-009'}, {'text': 'BINDA PUR', 'value': '176-001'}, {'text': 'CHHAWALA', 'value': '176-007'}, {'text': 'DABRI', 'value': '176-002'}, {'text': 'DWARKA NORTH', 'value': '176-004'}, {'text': 'DWARKA SECTOR 23', 'value': '176-005'}, {'text': 'DWARKA SOUTH', 'value': '176-003'}, {'text': 'JAFFAR PUR KALAN\n', 'value': '176-006'}, {'text': 'MOHAN GARDEN', 'value': '176-012'}, {'text': 'NAJAFGARH', 'value': '176-010'}, {'text': 'UTTAM NAGAR', 'value': '176-008'}]},
            { '168-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'GHAZIPUR', 'value': '168-010'}, {'text': 'KALYAN PURI', 'value': '168-13'}, {'text': 'LAXMI NAGAR', 'value': '168-054'}, {'text': 'MADHU VIHAR', 'value': '168-23'}, {'text': 'MANDAWALI', 'value': '168-24'}, {'text': 'MAYUR VIHAR PH-1', 'value': '168-26'}, {'text': 'NEW ASHOK NAGAR', 'value': '168-28'}, {'text': 'PANDAV NAGAR', 'value': '168-50'}, {'text': 'PATPARGANJ INDUSTRIAL AREA', 'value': '168-053'}, {'text': 'PREET VIHAR', 'value': '168-30'}, {'text': 'SHAKAR PUR', 'value': '168-41'}]},
            { '169-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'IGI AIRPORT', 'value': '169-02'}, {'text': 'PALAM DOMESTIC AIRPORT', 'value': '169-01'}] },
            { '160-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'Azadpur Metro', 'value': '160-15'}, {'text': 'Central Secretariat Metro', 'value': '160-12'}, {'text': 'Ghitorni Metro', 'value': '160-03'}, {'text': 'IGI AIRPORT METRO', 'value': '160-04'}, {'text': 'INA Metro', 'value': '160-11'}, {'text': 'Janak Puri Metro', 'value': '160-10'}, {'text': 'KASHMIRI GATE METRO', 'value': '160-07'}, {'text': 'Lajpat Nagar Metro', 'value': '160-13'}, {'text': 'Mandi House Metro', 'value': '160-14'}, {'text': 'NETAJI SUBHASH PLACE METRO', 'value': '160-016'}, {'text': 'OKHLA VIHAR METRO', 'value': '160-002'}, {'text': 'RAJA GARDEN METRO STATION', 'value': '160-08'}, {'text': 'RITHALA METRO STATION', 'value': '160-05'}, {'text': 'SHASTRI PARK METRO STATION', 'value': '160-06'}, {'text': 'Udhyog Nagar Metro', 'value': '160-09'}, {'text': 'YAMUNA DEPOT', 'value': '160-01'}]}, { '165-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'BARAKHAMBA ROAD', 'value': '165-02'}, {'text': 'CHANAKYA PURI', 'value': '165-07'}, {'text': 'CONNAUGHT PLACE', 'value': '165-11'}, {'text': 'MANDIR MARG', 'value': '165-15'}, {'text': 'North Avenue', 'value': '165-38'}, {'text': 'PARLIAMENT STREET\n', 'value': '165-22'}, {'text': 'SOUTH AVENUE', 'value': '165-37'}, {'text': 'TILAK MARG', 'value': '165-35'}, {'text': 'TUGLAK ROAD', 'value': '165-36'}]}, { '173-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'BHAJAN PURA', 'value': '173-05'}, {'text': 'DAYAL PUR', 'value': '173-061'}, {'text': 'GOKUL PURI', 'value': '173-54'}, {'text': 'HARSH VIHAR', 'value': '173-055'}, {'text': 'JAFRABAD', 'value': '173-58'}, {'text': 'JYOTI  NAGAR', 'value': '173-56'}, {'text': 'KARAWAL NAGAR', 'value': '173-016'}, {'text': 'KHAJURI KHAS', 'value': '173-15'}, {'text': 'NAND  NAGARI', 'value': '173-25'}, {'text': 'NEW USMAN PUR', 'value': '173-30'}, {'text': 'SEELAM PUR', 'value': '173-42'}, {'text': 'SHASTRI PARK', 'value': '173-060'}, {'text': 'SONIA VIHAR', 'value': '173-57'}, {'text': 'WELCOME', 'value': '173-45'}] }, { '172-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'ADARSH NAGAR', 'value': '172-03'}, {'text': 'ASHOK VIHAR', 'value': '172-06'}, {'text': 'BHARAT NAGAR', 'value': '172-07'}, {'text': 'JAHANGIR PURI', 'value': '172-14'}, {'text': 'KESHAV PURAM', 'value': '172-25'}, {'text': 'MAHENDRA PARK', 'value': '172-51'}, {'text': 'MAURYA ENCLAVE', 'value': '172-49'}, {'text': 'MODEL TOWN', 'value': '172-17'}, {'text': 'MUKHERJI NAGAR', 'value': '172-30'}, {'text': 'SHALIMAR BAGH', 'value': '172-35'}, {'text': 'SUBHASH PLACE\n', 'value': '172-47'}] },
            { '174-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'MANGOL PURI', 'value': '174-05'}, {'text': 'MUNDKA', 'value': '174-25'}, {'text': 'NANGLOI', 'value': '174-21'}, {'text': 'NIHAL VIHAR', 'value': '174-22'}, {'text': 'PASCHIM VIHAR EAST', 'value': '174-24'}, {'text': 'PASCHIM VIHAR WEST', 'value': '174-23'}, {'text': 'RAJ PARK', 'value': '174-029'}, {'text': 'RANHOLA', 'value': '174-20'}, {'text': 'RANI BAGH', 'value': '174-50'}, {'text': 'SULTAN PURI', 'value': '174-11'}] },
            { '991-008': [{'text': 'Select Police Station', 'value': ''}, {'text': 'ALIPUR', 'value': '991-06'}, {'text': 'BAWANA', 'value': '991-04'}, {'text': 'BHALSWA DAIRY', 'value': '991-03'}, {'text': 'NARELA', 'value': '991-07'}, {'text': 'NARELA INDUSTRIAL AREA', 'value': '991-01'}, {'text': 'SAMAI PUR BADLI', 'value': '991-08'}, {'text': 'SHAHBAD DAIRY', 'value': '991-05'}, {'text': 'SWAROOP NAGAR', 'value': '991-02'}] },
            { '164-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'ANAND VIHAR RLY STN', 'value': '164-04'}, {'text': 'DELHI CANTT RLY STN', 'value': '164-41'}, {'text': 'H.N.DIN RAILWAY STATION', 'value': '164-32'}, {'text': 'NEW DELHI RAILWAY STATION\n\n', 'value': '164-26'}, {'text': 'OLD DELHI RAILWAY STATION', 'value': '164-25'}, {'text': 'SARAI ROHILLA RAILWAY STATION', 'value': '164-34'}, {'text': 'SUBZI MANDI RLY STN', 'value': '164-42'}] },
            { '959-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'AMAN VIHAR', 'value': '959-016'}, {'text': 'BEGUM PUR', 'value': '959-03'}, {'text': 'BUDH VIHAR', 'value': '959-014'}, {'text': 'K.N.KATJU MARG', 'value': '959-07'}, {'text': 'KANJHAWLA', 'value': '959-12'}, {'text': 'NORTH ROHINI', 'value': '959-11'}, {'text': 'PRASHANT VIHAR', 'value': '959-08'}, {'text': 'PREM NAGAR', 'value': '959-013'}, {'text': 'SOUTH ROHINI', 'value': '959-10'}, {'text': 'VIJAY VIHAR', 'value': '959-09'}] },
            { '957-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'ANAND VIHAR', 'value': '957-02'}, {'text': 'FARSH BAZAR', 'value': '957-06'}, {'text': 'GANDHI NAGAR', 'value': '957-04'}, {'text': 'GEETA COLONY', 'value': '957-05'}, {'text': 'GTB ENCLAVE', 'value': '957-09'}, {'text': 'JAGAT PURI', 'value': '957-14'}, {'text': 'KIRSHNA NAGAR', 'value': '957-03'}, {'text': 'MANSAROVER PARK', 'value': '957-08'}, {'text': 'SEEMA PURI', 'value': '957-10'}, {'text': 'SHAHADRA', 'value': '957-07'}, {'text': 'VIVEK VIHAR', 'value': '957-01'}] },
            { '167-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'AMBEDKAR NAGAR\n', 'value': '167-064'}, {'text': 'CHITRANJAN PARK\n', 'value': '167-062'}, {'text': 'DEFENCE COLONY', 'value': '167-10'}, {'text': 'FATEHPUR BERI', 'value': '167-12'}, {'text': 'GREATER KAILASH', 'value': '167-061'}, {'text': 'HAUZ KHAS', 'value': '167-17'}, {'text': 'K.M. PUR', 'value': '167-23'}, {'text': 'LODHI COLONY', 'value': '167-28'}, {'text': 'MAIDAN GARHI', 'value': '167-066'}, {'text': 'MALVIYA NAGAR', 'value': '167-33'}, {'text': 'MEHRAULI', 'value': '167-32'}, {'text': 'NEB SARAI', 'value': '167-57'}, {'text': 'SAKET', 'value': '167-56'}, {'text': 'SANGAM VIHAR', 'value': '167-063'}, {'text': 'TIGRI', 'value': '167-067'}] },
            { '955-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'AMAR COLONY', 'value': '955-07'}, {'text': 'BADAR PUR', 'value': '955-12'}, {'text': 'GOVIND PURI', 'value': '955-02'}, {'text': 'H. N. DIN', 'value': '955-05'}, {'text': 'JAIT PUR', 'value': '955-01'}, {'text': 'JAMIA NAGAR', 'value': '955-04'}, {'text': 'KALANDI KUNJ', 'value': '955-019'}, {'text': 'KALKAJI', 'value': '955-09'}, {'text': 'LAJPAT NAGAR', 'value': '955-06'}, {'text': 'NEW FRIENDS COLONY', 'value': '955-03'}, {'text': 'OKHLA INDUSTRIAL AREA', 'value': '955-13'}, {'text': 'PUL PRAHLAD PUR', 'value': '955-17'}, {'text': 'SARITA VIHAR', 'value': '955-11'}, {'text': 'SHAHEEN BAGH', 'value': '955-020'}, {'text': 'SUNLIGHT COLONY', 'value': '955-16'}] },
            { '171-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'DELHI CANTT', 'value': '171-11'}, {'text': 'KAPSHERA', 'value': '171-30'}, {'text': 'KISHAN GARH', 'value': '171-066'}, {'text': 'PALAM VILLAGE', 'value': '171-57'}, {'text': 'R. K. PURAM', 'value': '171-060'}, {'text': 'SAFDARJUNG ENCLAVE', 'value': '171-47'}, {'text': 'SAGAR PUR', 'value': '171-54'}, {'text': 'SAROJINI NAGAR', 'value': '171-46'}, {'text': 'SOUTH CAMPUS', 'value': '171-061'}, {'text': 'VASANT KUNJ NORTH', 'value': '171-062'}, {'text': 'VASANT KUNJ SOUTH', 'value': '171-063'}, {'text': 'VASANT VIHAR', 'value': '171-064'}] },
            { '163-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'SPECIAL CELL', 'value': '163-05'}] },
            { '170-008' : [{'text': 'Select Police Station', 'value': ''}, {'text': 'HARI NAGAR', 'value': '170-15'}, {'text': 'INDER PURI', 'value': '170-64'}, {'text': 'JANAK PURI', 'value': '170-21'}, {'text': 'KHYALA', 'value': '170-62'}, {'text': 'KIRTI NAGAR', 'value': '170-25'}, {'text': 'MAYAPURI', 'value': '170-028'}, {'text': 'MOTI NAGAR', 'value': '170-29'}, {'text': 'NARAINA', 'value': '170-63'}, {'text': 'PUNJABI BAGH', 'value': '170-43'}, {'text': 'RAJOURI GARDEN', 'value': '170-037'}, {'text': 'TILAK NAGAR', 'value': '170-51'}, {'text': 'VIKAS PURI', 'value': '170-60'}] }]


    for station in policestation:
        if(list(station.keys())[0] == districtcode):
            return (station)




