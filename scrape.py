from selenium import webdriver 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from selenium.webdriver.firefox.options import Options
from certificate import certificate

class Event:
    def __init__(self, performer, month, day, time, location, instrumentation, link):
        self.performer = performer
        self.month = month
        self.day = day
        self.time = time 
        self.location = location
        self.instrumentation = instrumentation
        self.link = link

options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)
driver.get("https://www.juilliard.edu/stage-beyond/performance/calendar")

# get to the end of the calendar first
while True:
    try:
        driver.implicitly_wait(10)
        button = driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/div[2]/article/div[2]/div/div/div[3]/div/ul/li/a')
        driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()
        sleep(1)
    except: 
        break

# extract the data
data = driver.find_element_by_xpath('//*[@id="event-listing"]/div[2]/div') 

eventGroupsULs = data.find_elements_by_class_name("event-groups")

eventsData = [] # our event objects

for eventGroupUL in eventGroupsULs:
        eventGroups = eventGroupUL.find_elements_by_class_name("event-group")
        
        for eventGroup in eventGroups:

                month = eventGroup.find_element_by_class_name("month").text
                day = eventGroup.find_element_by_class_name("day").text
                
                event_group_events = eventGroup.find_element_by_class_name("event-group-events")
                events = event_group_events.find_elements_by_class_name("event")

                for event in events:
                    event_class = event.get_attribute("class").split()
                    if "event-cta" in event_class:
                            continue
                    article = event.find_element_by_xpath('./article[contains(@class, "event-performance-calendar")]')

                    title = article.find_element_by_tag_name("h3").text

                    if ',' in title:
                            performer = title.split(",")[0]
                            instrumentation = title.split(",")[1]
                    else:
                            performer = title
                            instrumentation = None 
                    link = article.find_element_by_tag_name("a").get_attribute("href")
                    
                    location = article.find_element_by_class_name("field--name-field-venue").text
                    time = article.find_element_by_tag_name("time").text
                    
                    new_event = Event(performer, month, day, time, location, instrumentation, link)
                    eventsData.append(new_event)

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
from datetime import datetime
import pytz

tz = pytz.timezone('America/New_York')
time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

cred = credentials.Certificate(certificate)
firebase_admin.initialize_app(cred)

db = firestore.client()

eventsJSON = {}
#convert to JSON
for event in eventsData:
        eventsJSON[event.performer] = {}
        eventsJSON[event.performer]['instrumentation'] = event.instrumentation
        eventsJSON[event.performer]['location'] = event.location
        eventsJSON[event.performer]['month'] = event.month
        eventsJSON[event.performer]['day'] = event.day
        eventsJSON[event.performer]['time'] = event.time
        eventsJSON[event.performer]['link'] = event.link

def save(collection_id, document_id, data):
    db.collection(collection_id).document(document_id).set(data)

save(collection_id = "Events", document_id = f"{time}", data=eventsJSON)



                    










