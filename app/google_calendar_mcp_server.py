"""
Google Calendar MCP Server - Direct integration with Google Calendar API
"""
import os
import sys
import logging
import pathlib
import datetime
from mcp.server.fastmcp import FastMCP

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calendar_service import get_calendar_service

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("google-calendar-server")

# Initialize MCP server
mcp = FastMCP("google-calendar")

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_FILE = pathlib.Path("token.json")
CREDS_FILE = pathlib.Path("credentials.json")

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display."""
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str

def check_availability(service, start_time: str, end_time: str) -> bool:
    """Check if time slot is available."""
    freebusy_query = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": "primary"}]  
    }
  
    try:
        resp = service.freebusy().query(body=freebusy_query).execute()
        busy_slots = resp['calendar']['primary']['busy']
        
        result = True
        if busy_slots:
            result = False
        
        return result
    
    except Exception as e:
        return f"fail to check free time slots. Error: {e}"
    

@mcp.tool()
async def list_events(max_results: str = "10") -> str:
    """List upcoming Google Calendar events with optional limit."""
    logger.info(f"Listing up to {max_results} events")
    
    try:
        limit = int(max_results) if max_results.strip() else 10
        if limit < 1 or limit > 50:
            return "❌ Error: max_results must be between 1 and 50"
        
        service = get_calendar_service(SCOPES)
        
        now = datetime.datetime.now().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=limit,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📭 No upcoming events found."
        
        formatted_events = []
        for event in events:
            summary = event.get('summary', '(No title)')
            start = event['start'].get('dateTime', event['start'].get('date'))
            location = event.get('location', '')
            event_id = event.get('id', '')
            
            event_str = f"• **{summary}**\n  📅 {format_datetime(start)}"
            if location:
                event_str += f"\n  📍 {location}"
            event_str += f"\n  🆔 {event_id}"
            
            formatted_events.append(event_str)
        
        return f"📅 **Upcoming Events ({len(events)}):**\n\n" + "\n\n".join(formatted_events)
    
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return f"❌ Failed to list events: {str(e)}"
    

@mcp.tool()
async def create_event(
    summary: str = "",
    start_time: str = "",
    end_time: str = "",
    description: str = "",
    location: str = ""
) -> str:
    """Create a new Google Calendar event with title, start time, end time, and optional description and location."""
    logger.info(f"Creating event: {summary}")
    
    # Validate required fields
    if not summary.strip():
        return "❌ Error: Event summary (title) is required"
    if not start_time.strip():
        return "❌ Error: Start time is required (format: 2025-01-15T14:00:00)"
    if not end_time.strip():
        return "❌ Error: End time is required (format: 2025-01-15T15:00:00)"
    
    try:
        service = get_calendar_service(SCOPES)
        
        # Check if time slot is available
        is_available = check_availability(service, start_time, end_time)
        if not is_available:
            return f"⚠️ Time slot is already occupied!\n\nPlease choose a different time or check your calendar."
        
        # Create event object
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Tokyo'
            }
        }
        
        if description.strip():
            event['description'] = description
        if location.strip():
            event['location'] = location
        
        # Insert event
        created = service.events().insert(calendarId='primary', body=event).execute()
        
        event_id = created.get('id')
        link = created.get('htmlLink')
        
        result = f"✅ **Event Created Successfully!**\n\n"
        result += f"📋 **Title:** {summary}\n"
        result += f"📅 **Start:** {format_datetime(start_time)}\n"
        result += f"📅 **End:** {format_datetime(end_time)}\n"
        if location.strip():
            result += f"📍 **Location:** {location}\n"
        result += f"🆔 **ID:** {event_id}\n"
        result += f"🔗 **Link:** {link}"
        
        return result
    
    except HttpError as e:
        logger.error(f"Google API error: {e}")
        return f"❌ Google Calendar API error: {str(e)}"
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return f"❌ Failed to create event: {str(e)}"


@mcp.tool()
async def delete_event(event_id: str = "") -> str:
    """Delete a Google Calendar event by its ID."""
    logger.info(f"Deleting event: {event_id}")
    
    if not event_id.strip():
        return "❌ Error: Event ID is required"
    
    try:
        service = get_calendar_service(SCOPES)
        
        # Try to get event first to confirm it exists
        try:
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            event_title = event.get('summary', 'Untitled Event')
        except HttpError:
            return f"❌ Event not found with ID: {event_id}"
        
        # Delete the event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return f"✅ **Event Deleted Successfully!**\n\n📋 Deleted: {event_title}\n🆔 ID: {event_id}"
    
    except HttpError as e:
        logger.error(f"Google API error: {e}")
        return f"❌ Google Calendar API error: {str(e)}"
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return f"❌ Failed to delete event: {str(e)}"

@mcp.tool()
async def search_events(query: str = "", max_results: str = "10") -> str:
    """Search for events by keyword in title, description, or location."""
    logger.info(f"Searching events: {query}")
    
    if not query.strip():
        return "❌ Error: Search query is required"
    
    try:
        limit = int(max_results) if max_results.strip() else 10
        if limit < 1 or limit > 50:
            return "❌ Error: max_results must be between 1 and 50"
        
        service = get_calendar_service(SCOPES)
        
        events_result = service.events().list(
            calendarId='primary',
            q=query,
            maxResults=limit,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"🔍 No events found matching: '{query}'"
        
        formatted_events = []
        for event in events:
            summary = event.get('summary', '(No title)')
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_id = event.get('id', '')
            
            event_str = f"• **{summary}**\n  📅 {format_datetime(start)}\n  🆔 {event_id}"
            formatted_events.append(event_str)
        
        return f"🔍 **Search Results for '{query}' ({len(events)}):**\n\n" + "\n\n".join(formatted_events)
    
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        return f"❌ Failed to search events: {str(e)}"

@mcp.tool()
async def check_free_time(start_time: str = "", end_time: str = "") -> str:
    """Check if a time slot is available in your calendar."""
    logger.info(f"Checking availability: {start_time} to {end_time}")
    
    if not start_time.strip() or not end_time.strip():
        return "❌ Error: Both start_time and end_time are required"
    
    try:
        service = get_calendar_service(SCOPES)
        
        is_available = check_availability(service, start_time, end_time)
        
        if is_available:
            return f"✅ **Time Slot Available!**\n\n📅 {format_datetime(start_time)} to {format_datetime(end_time)}\n\nYou can schedule an event during this time."
        else:
            return f"⚠️ **Time Slot Occupied**\n\n📅 {format_datetime(start_time)} to {format_datetime(end_time)}\n\nYou already have an event during this time."
    
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return f"❌ Failed to check availability: {str(e)}"

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Google Calendar MCP server...")
    
    # Check for credentials file
    if not CREDS_FILE.exists():
        logger.warning(f"credentials.json not found at {CREDS_FILE}")
        logger.warning("OAuth authentication will fail until credentials are provided")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)