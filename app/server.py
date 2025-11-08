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

@app.get("/")
def root():
  return {"message": "running on port 8000"}

