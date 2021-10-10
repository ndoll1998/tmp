import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime


repeat_mapping = {
    "einzel": 0,
    "wöch": 1,
    "14-täglich": 2
}

weekday_mapping = {
    "Mo": 0,
    "Di": 1,
    "Mi": 2,
    "Do": 3,
    "Fr": 4,
    "Sa": 5,
    "So": 6,
}


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

    df_11 = pd.DataFrame(columns=["ID", "Name", "Type", "Workload", "Lecturers"])
    df_time_1n = pd.DataFrame(columns=["ID", "From", "To", "Weekday", "Start_Date", "End_Date", "Repeat"])

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
                
                for row in table:
                    time_item = {}
                    time_item["ID"] = item_id
                    time_item["Weekday"] = weekday_mapping[row[1]] if len(row[1]) > 1 else None
                    # check if from - to - repeat string is valid
                    if " - " in row[2]:
                        from_st_ct, to_repeat = row[2].split(" - ")
                        from_time, st_ct = from_st_ct.split(" ") if " " in from_st_ct else (from_st_ct, "(c.t.)")
                        to_time, repeat = to_repeat.split(" ") if " " in to_repeat else (to_repeat, None)
                        # convert to datetime.time
                        from_time = datetime.datetime.strptime(from_time, "%H:%M" if ":" in from_time else "%H")
                        to_time = datetime.datetime.strptime(to_time, "%H:%M" if ":" in to_time else "%H")
                        # adjust timing by st_ct
                        from_time += datetime.timedelta(minutes=0 if st_ct == "(s.t.)" else 15)
                        to_time -= datetime.timedelta(minutes=30 if st_ct == "(s.t.)" else 15)
                        # convert repeat to integer codes
                        repeat = repeat_mapping[repeat.lower()]
                        # add time data item
                        time_item.update({
                            "From": from_time.strftime("%H:%M"),
                            "To": to_time.strftime("%H:%M"),
                            "Repeat": repeat,
                        })
                    if " bis " in row[-1]:
                        time_item["Start_Date"], time_item["End_Date"] = row[-1].split(" bis ")
                    df_time_1n = df_time_1n.append(time_item, ignore_index=True)

            continue
    
        assert not next_is_time_table

        # find some more information
        item_type = item_type.text.strip()
        item_name = item_info.select_one("h2 > a.regular").text.strip()
       
        item_id, item_name = item_name.split(" - ", maxsplit=1) 

        infos = item_info.select_one("div.klein").text.strip()
        infos = clean_text(infos)

        general, lecturers = re.split(r"[Dozent|Dozenten]\s*:", infos)
        item_workload = re.search(r"\b[0-9]+\.[0-9]\s*SWS\b", general)
        item_workload = item_workload.group()[:-3]
        # clean up lecturers
        lecturers = [lec.strip() for lec in lecturers.split(';')]
        lecturers = [lec for lec in lecturers if len(lec) > 0]

        df_11 = df_11.append({
            "ID": item_id,
            "Name": item_name,
            "Type": item_type,
            "Workload": float(item_workload),
            "Lecturers": "; ".join(lecturers),
        }, ignore_index=True)

        # next table will be a time table
        next_is_time_table = True

    # print(soup.select("#wrapper > div.divcontent > div.content_max_portal_qis")[0].prettify())
    df_11.set_index("ID", inplace=True)

    return df_11, df_time_1n


if __name__ == '__main__':

    URL = "https://basis.uni-bonn.de/qisserver/rds?state=wtree&search=1&trex=step&root120212=235519%7C241835%7C241834%7C241849&P.vx=lang"
    df_11, df_time_1n = parse(URL)

    print(df_11.head())
    print(df_time_1n.head())

    df_11.to_csv("df_11.csv")
    df_time_1n.to_csv("df_time_1n.csv")
