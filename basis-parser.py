import os
import re
import requests
import pandas as pd
from hashlib import md5
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

repeat_mapping = {
    "einzel": 0,
    "wöch": 1,
    "14-täglich": 2,
}

weekday_mapping = {
    "mo": 0,
    "di": 1,
    "mi": 2,
    "do": 3,
    "fr": 4,
    "sa": 5,
    "so": 6,
}


role_mapping = {
    "verantwortlich": 0,
    "durchführend": 1
}

def clean_text(text:str) -> str:
    text = ''.join((c if c.isprintable() else " " for c in text))
    text = re.sub(" +", " ", text.strip())
    return text

def parse(url:str) -> None:

    # create dataframes to hold gathered data
    df_info = pd.DataFrame(columns=["EventID", "Name", "Type", "Workload"])
    df_time = pd.DataFrame(columns=["EventID", "From", "To", "Weekday", "Start_Date", "End_Date", "Repeat"])
    df_lecs = pd.DataFrame(columns=["EventID", "Lecturer", "Role"])

    # get html
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response! (%s)" % resp.status_code)

    # cleanup and parse response
    soup = BeautifulSoup(resp.content, 'lxml')
    
    # find all tables holding information about an event
    tables = soup.select("#wrapper > div.divcontent > div.content_max_portal_qis > table > tr > td > table")

    k = 0
    tables_iter = iter(tables)
    while True:

        # get next table
        try:                    event = next(tables_iter)
        except StopIteration:   break

        event_info = event.select_one("tr > td > div.klein")
        # check if item defines a new module
        if event_info is None:
            continue

        # get event name
        event_name = event.select_one("tr > td > h2 > a.regular")
        event_name = clean_text(event_name.text)

        info, lecs = re.split(r"\s*:\s*", event_info.text.strip())
        #  gather some general information about the event
        info = re.split(r"[\t\r\n\xa0]+", info.strip())
        info = [txt for txt in map(clean_text, info) if len(txt) > 0]
        semester, event_id, event_type = info[:3]
        # make sure the event id is valid
        if not re.match(r"[0-9]+", event_id):
            # in case this is a tutorial just take the event id
            # of the corresponding module (should be right before this one)
            if event_type in ["Übung", "Tutorial"]:
                event_id = df_info.iloc[-1]["EventID"]
            else:
                # create new id by hashing name (hopefully unique)
                event_id = md5(event_name.encode('utf-8')).hexdigest()[:9]
                event_id = str(int(event_id, 16))[:9] # convert to decimal
        # workload
        workload = None
        if len(info) > 3:
            match = re.search("\d.\d(?=\s*SWS)", info[3])
            if match is not None:
                workload = match.group().strip()

        # add row to dataframe
        df_info = df_info.append({
            "EventID": event_id,
            "Name": event_name,
            "Type": event_type,
            "Workload": workload
        }, ignore_index=True)

        # parse lecturers
        lecs = re.split(r"\s*;\s*", clean_text(lecs))
        lecs = lecs[:-1] if len(lecs[-1]) == 0 else lecs
        # get role of each lecturer
        roles = [re.search(r"\(.*\)", l) for l in lecs]
        roles = [None if m is None else m.group()[1:-1].strip() for m in roles]
        roles = [None if r is None else role_mapping[r.lower()] for r in roles]
        # clean-up lecturers
        lecs = [re.sub(r"\(.*\)", "", l) for l in lecs]
        # add all to lecturers dataframe
        for lec, role in zip(lecs, roles):
            df_lecs = df_lecs.append({
                "EventID": event_id, 
                "Lecturer": lec, 
                "Role": role
            }, ignore_index=True)
        
        # the next table should be the time table
        # corresponding to the current event 
        table = next(tables_iter)
        # so lets parse it
        table = [row.find_all("td") for row in table.find_all("tr")]
        table = [
            [clean_text(el.get_text(separator=" ")) for el in row]
            for row in table if len(row) == 7
        ]
        
        for (_, weekday, time, _, _, _, period) in table:
            row = {"EventID": event_id}
            if len(weekday) > 1:
                row["Weekday"] = weekday_mapping[weekday.lower()]
            # parse period dates
            begin_end = re.findall(r"\d+\s*[.-/]\s*\d+\s*[.-/]\s*\d\d\d\d", period)
            if len(begin_end) >= 1:
                row["Start_Date"] = begin_end[0]
            if len(begin_end) == 2:
                row["End_Date"] = begin_end[1]

            # parse time and repeat
            time = time.lower()
            is_ct = ("s.t." not in time)    # by default assumes c.t.
            repeat = [v for k, v in repeat_mapping.items() if k in time]
            repeat = repeat[0] if len(repeat) > 0 else 1
            # find start and end time
            from_to = re.findall(r"\d{1,2}(?::\d\d)?", time)
            if len(from_to) >= 2:
                from_time, to_time = from_to[:2]
                # convert to time objects
                from_time = datetime.strptime(from_time, "%H:%M" if ":" in from_time else "%H")
                to_time = datetime.strptime(to_time, "%H:%M" if ":" in to_time else "%H")
                # adjust timing by st/ct
                from_time += timedelta(minutes=15 if is_ct else 0)
                to_time -= timedelta(minutes=15 if is_ct else 30)
                # write to row
                row.update({
                    "From":   from_time.strftime("%H:%M"),
                    "To":     to_time.strftime("%H:%M"),
                    "Repeat": repeat
                })
            # add row to dataframe
            if len(row) > 1:
                df_time = df_time.append(row, ignore_index=True)

    return df_info, df_time, df_lecs


if __name__ == '__main__':

    URL = "https://basis.uni-bonn.de/qisserver/rds?state=wtree&search=1&trex=step&root120212=235519%7C241835%7C241834%7C241849&P.vx=lang"
    df_info, df_time, df_lecs = parse(URL)

    print("General Information:")
    print(df_info)
    print("\nTimes:")
    print(df_time)
    print("\nLecturers:")
    print(df_lecs)
