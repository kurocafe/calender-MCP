# FastAPIベースのMCPサーバー本体

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import datetime
import os
import pathlib

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from calendar_service import get_calendar_service

from requestType.eventRequest import CreateEventRequest

app = FastAPI()

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

TOKEN_FILE = pathlib.Path("token.json")
CREDS_FILE = pathlib.Path("credentials.json")

@app.get("/list-events")
def list_events():
  """ Return next 10 events from primary calendar """
  
  try: 
    service = get_calendar_service(SCOPES)
    
    now = datetime.datetime.now().isoformat() + "Z"
    events_result = service.events().list(
      calendarId='primary',
      timeMin=now,
      maxResults=10,
      singleEvents=True,
      orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return JSONResponse({"result": events})
  except Exception as e:
    return JSONResponse({"error": f"fail to get 10 events. Error: {e}"})

@app.post("/create-event")
def create_event(body: CreateEventRequest):
  """ Create new Event with an input of summary, start, end, description (Optional), location (Optional) """
  
  event = {
            'summary': body.summary,
            'description': body.description,
            'location': body.location,
            'start': {
                'dateTime': body.start,
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': body.end,
                'timeZone': 'Asia/Tokyo'
            }
        }
  
  try:
    service = get_calendar_service(SCOPES)
    
    is_available = check_available(service, body.start, body.end)
    if is_available:
      created = service.events().insert(calendarId='primary', body=event).execute()
      return {"message": "new event created!!", "id": created.get('id'), "link": created.get('htmlLink')}
    else:
      return {"message": "already occupied!!"}
    
  except Exception as e:
    return JSONResponse({"error": f"fail to create new Event. error = {e}"})
  

@app.get("/")
def root():
  return {"message": "running on port 8000"}


# 共通関数（空いているところを取得する）
def check_available(service, start: str, end: str):
  
  freebusy_query = {
    "timeMin": start,
    "timeMax": end,
    "items": [{"id": "primary"}]  
  }
  
  try:
    resp = service.freebusy().query(body=freebusy_query).execute()
    busy_slots = resp['calendar']['primary']['busy']
    print(resp)
    print(busy_slots)
    
    result = True
    if busy_slots:
      result = False
    
    return result
  
  except Exception as e:
    return JSONResponse({"error": f"fail to check free time slots. Error: {e}"})
  
  

