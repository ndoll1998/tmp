import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def clean_text(text:str) -> str:
    text = ''.join((c if c.isprintable() else " " for c in text))
    text = re.sub(" +", " ", text.strip())
    return text

def parse(url:str) -> pd.DataFrame:

    # get html
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response! (%s)" % resp.status_code)

    # parse html 
    soup = BeautifulSoup(resp.content, 'lxml')

    selector = "#wrapper > div.divcontent > div.content_max_portal_qis > table > tr > td > table"

    next_is_time_table = False
    for item in soup.select(selector):
    
        item_info = item.select_one("tr > td")
        # check if item is valid
        if item_info is None:
            continue

        # check if item is a module, toturial, etc. or none
        item_type = item_info.select_one("div.klein > strong[style*='color: green']")
        # item does not initialize a new module
        if item_type is None:
            # but it could be a time table for the previous module
            if next_is_time_table:
                next_is_time_table = False
                # parse table
                table = [row.find_all("td") for row in item.find_all("tr")]
                table = [
                    [clean_text(el.get_text(separator=" ")) for el in row]
                    for row in table if len(row) == 7
                ]
                print(table)
                print("-" * 4)

            continue
        
        assert not next_is_time_table

        # find some more information
        item_type = item_type.text.strip()
        item_name = item_info.select_one("h2 > a.regular").text.strip()
        
        infos = item_info.select_one("div.klein").text.strip()
        infos = clean_text(infos)

        general, lecturers = re.split(r"[Dozent|Dozenten]\s*:", infos)
        item_workload = re.search(r"\b[0-9]+\.[0-9]\s*SWS\b", general)
        item_workload = item_workload.group()
        # clean up lecturers
        lecturers = [lec.strip() for lec in lecturers.split(';')]
        lecturers = [lec for lec in lecturers if len(lec) > 0]

        print("Name:     ", item_name)
        print("Type:     ", item_type)
        print("Workload: ", item_workload)
        print("Lecturers:", lecturers)
        print()

        # next table will be a time table
        next_is_time_table = True

    # print(soup.select("#wrapper > div.divcontent > div.content_max_portal_qis")[0].prettify())
    

if __name__ == '__main__':

    URL = "https://basis.uni-bonn.de/qisserver/rds?state=wtree&search=1&trex=step&root120212=235519%7C241835%7C241834%7C241849&P.vx=lang"
    parse(URL)
