from datetime import datetime
from urllib2 import urlopen as uReq
from bs4 import  BeautifulSoup as soup
from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def main():
    time = str(datetime.now().time().hour)
    day = datetime.today().weekday()

    dining_url = 'http://housing.utexas.edu/dining/hours'
    uClient = uReq(dining_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("table",{"class": "tablesaw tablesaw-stack"})
    openPlaces = []
    times = []
    places = []
    data = []

    for container in containers:
        day_values = container.tbody.findAll("tr")
        place = ""
        for val in day_values:
            if val.th is not None: # Ex. J2 Dining
                place = val.th
                places.append(place.text.strip())
            day_info = val.findAll("td")
            days = []
            isTime = 0
            timeLeft = 0
            timesRange = ""
            dayRange = ""
            for temp in day_info:
                text = temp.text.strip()
                if (len(text) != 0): # avoid spaces under days
                    if (text[0].isdigit() or text == "Closed" or text[0] == "N"): # time ranges
                        timesRange = text
                        isTime = checkTime(text, time)
                    else:
                        dayRange = text
                        days = checkDay(text)
            if (len(days) > 0 and -1 not in days):
                if (day in days and isTime == 1):
                    data.append({"name": place.text.strip()})
    sac(time, data)
    union(time, data)
    print data
    return render_template('index.html', data=data)

def sac(currTime, data):
    sacRestaurants = ["Chick-fil-A", "P.O.D.", "Starbucks", "Taco Cabana", "Zen"]
    dayIndex = datetime.today().weekday()
    # dayIndex = getDayIndex(day)
    dining_url = 'https://universityunions.utexas.edu/sac-hours/fall-2019'
    uClient = uReq(dining_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("table",{"class": "tablesaw tablesaw-stack"})
    locations = containers[2].tbody.findAll("tr")
    for location in locations:
        times = location.findAll("td")
        name = times[0].text.strip()
        if (name[:6] == "P.O.D."):
            name = "P.O.D."
        if (name in sacRestaurants):
            if (checkSacTime(times[dayIndex].text.strip(), currTime) == 1):
                data.append({"name": name})
    # print data

def union(currTime, data):
    unionRestaurants = ["Starbucks", "Chick-Fil-A", "P.O.D.", "Quiznos", "MoZZo", "Panda Express", "Field of Greens Market Place", "Wendy's @ Jester", "Java City @ PCL"]
    dayIndex = datetime.today().weekday()
    # print day
    # dayIndex = getDayIndex(day)
    dining_url = 'https://universityunions.utexas.edu/union-hours/fall-2019'
    uClient = uReq(dining_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("table",{"class": "tablesaw tablesaw-stack"})
    locations = containers[0].tbody.findAll("tr")
    # print dayIndex
    for location in locations:
        times = location.findAll("td")
        name = times[0].text.strip()
        if (name[:3] == "Prov"):
            name = "P.O.D."
        if (name in unionRestaurants):
            # print name
            if (checkUnionTime(times[dayIndex].text.strip(), currTime) == 0):
                data.append({"name": name})

def checkUnionTime(text, currTime):
    if (text == "Closed"):
        return 0
    split = text.split(" ")
    startTime = split[0]
    endTime = split[2]
    start = -1
    if (startTime[1] == "0"):
        start = 10
    elif (startTime[1] == "1"):
        start = 11
    elif (startTime[0] == "N"):
        start = 12
    else:
        if (startTime[-2] == "a"):
            start = int(startTime[0])
        else:
            start = int(startTime[0]) + 12
    end = -1
    if (endTime[1] == "0"):
        end = 22
    elif (endTime[1] == "1"):
        end = 23
    else:
        if (endTime[-2] == "a"):
            end = int(endTime[0])
        else:
            end = int(endTime[0]) + 12
    if (int(currTime) > int(start) and int(currTime) < int(end)):
        return 1
    return 0

def checkSacTime(text, currTime):
    if (text == "Closed"):
        return 0
    split = text.split(" ")
    startTime = split[0]
    endTime = split[2]
    start = 10 if startTime[1] != ":" else int(startTime[0]) if startTime[-2] == "a" else int(startTime[0]) + 12
    end = int(endTime[0]) if endTime[-2] == "a" else int(endTime[0]) + 12 if endTime[1] == ":" else int(endTime[:2]) + 12
    if (currTime > start and currTime < end):
        return 1
    return 0

# Compares current time to open times and returns 0
# if closed, 1 if open
def checkTime(text, currTime):
    if (text == "Closed"):
        return 0
    split = text.split(" ")
    begin = split[0]
    if (begin == "Noon"):
        begin = 12
    if (split[1] == "p.m."): # convert to 24 hour time
        begin = int(begin) + 12
    end = split[-2] if split[-1] != "p.m." else int(split[-2]) + 12
    if (int(currTime) < int(end) and int(currTime) >= int(begin)):
        return 1
    return 0

# Takes range of dates and returns array holding indices of
# the days
def checkDay(text):
    days = []
    split = text.split(" ")
    if len(split) == 1:
        days.append(getDayIndex(split[0]))
    elif ("-" in split):
        start = getDayIndex(split[0])
        end = getDayIndex(split[2])
        for i in range(start, end + 1):
            days.append(i)
    elif ("and" in split or "&" in split):
        days.append(getDayIndex(split[0]))
        days.append(getDayIndex(split[2]))
    return days

# Changes day to index
def getDayIndex(text):
    if text == "Monday":
        return 0
    if text == "Tuesday":
        return 1
    if text == "Wednesday":
        return 2
    if text == "Thursday":
        return 3
    if text == "Friday":
        return 4
    if text == "Saturday":
        return 5
    if text == "Sunday":
        return 6
    return -1

time = str(datetime.now().time().hour)
# union(time, [])
# sac(time, [])
# main()
if __name__ == '__main__':
    app.run(debug=True)