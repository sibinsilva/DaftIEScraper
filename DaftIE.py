import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import os


def extract(page):
    Header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}
    URL = f'https://www.daft.ie/property-for-sale/ireland?pageSize=20&from={page}'
    r = requests.get(URL, Header)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def transform(soup):
    divs = soup.find_all(
        'div', class_='Cardstyled__TitleBlockWrapper-nngi4q-4 eMeJos')
    for item in divs:
        price = item.find(
            'span', class_='TitleBlock__StyledSpan-sc-1avkvav-5 fKAzIL').text.strip()
        address = item.find(
            'p', class_='TitleBlock__Address-sc-1avkvav-8 dzihyY').text.strip()
        detail = soup.find("div", {"class":"TitleBlock__CardInfo-sc-1avkvav-10 iCjViR"}).findAll('p')
        info =""
        for res in detail:
            info += '\n' + ''.join(res.findAll(text = True))
        home = {
            'Address': address,
            'Details': info,
            'Price': price
        }
        homelist.append(home)
    return


def find_duplications():
    entries = []
    duplicate_entries = []
    if os.path.isfile('./DaftIE.csv'):
        with open('DaftIE.csv', 'r') as my_file:
            for line in my_file:
                columns = line.strip().split(',')
                # address duplications are taken because they are unique
                if columns[2] not in entries:
                    entries.append(columns[2])
                else:
                    duplicate_entries.append(columns[2])

        if len(duplicate_entries) > 0:
            df = pd.DataFrame(list())
            df.to_csv('DaftIE_nodup.csv')
            with open('DaftIE_nodup.csv', 'w') as out_file:
                with open('DaftIE.csv', 'r') as my_file:
                    for line in my_file:
                        columns = line.strip().split(',')
                        if columns[2] in duplicate_entries:
                            out_file.write(line)
            os.remove('./DaftIE.csv')  # Lets remove the old File
            os.rename('./DaftIE_nodup.csv', './DaftIE.csv')  # Rename the file
        else:
            print("No repetitions")
    else:
        print("No File found")


while 1:
    print('Finding Homes To Buy')
    homelist = []
    myList = range(0, 101)  # Each page is in multiples of 20 so here I just extract data from 5 pages

    for e in myList[0::20]:
        print(f'Getting data from Page:{e}')
        c = extract(e)
        transform(c)
    df = pd.DataFrame(homelist)
    print(df.head())
    # if file does not exist write header
    if not os.path.isfile('D:\DaftIE.csv'):
        df.to_csv('D:\DaftIE.csv', header='column_names')
    else:  # else it exists so append without writing the header
        df.to_csv('D:\DaftIE.csv', mode='a', header=False)
    # if os.path.isfile('./DaftIE.csv'):
    #   find_duplications()   # Still to test this bit

    dt = datetime.now() + timedelta(hours=24)   # Scarpe data every 24 hours

    while datetime.now() < dt:
        time.sleep(1)
