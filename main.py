import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("base_url")
username = os.getenv("username")
password = os.getenv("password")
print("URL:", base_url)
print("Username:", username)
print("Passwort geladen:", password is not None)
calendars = [
    "home-2",
    "generell-2",
    "school",
    "code-1",
    "privat"
]

headers = {
    "Depth": "1",
    "Content-Type": "application/xml; charset=utf-8",
}

NS = {
    "d": "DAV:",
    "c": "urn:ietf:params:xml:ns:caldav",
}


def get_entries(calendar, component):
    url = (
        f"{base_url}/remote.php/dav/calendars/"
        f"{username}/{calendar}/"
    )

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<c:calendar-query xmlns:d="DAV:"
                  xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop>
        <d:getetag/>
        <c:calendar-data/>
    </d:prop>

    <c:filter>
        <c:comp-filter name="VCALENDAR">
            <c:comp-filter name="{component}"/>
        </c:comp-filter>
    </c:filter>
</c:calendar-query>
"""

    return requests.request(
        "REPORT",
        url,
        headers=headers,
        data=body,
        auth=(username, password),
    )

def parse_events(xml):
    root = ET.fromstring(xml)

    entries = []

    for response in root.findall("d:response", NS):
        calendar_data = response.find(
            ".//c:calendar-data",
            NS
        )

        if calendar_data is None:
            continue

        data = calendar_data.text or ""

        entry = {}

        for line in data.splitlines():
            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            if key.startswith("SUMMARY"):
                entry["summary"] = value

            elif key.startswith("DTSTART"):
                entry["start"] = value

            elif key.startswith("DTEND"):
                entry["end"] = value

            elif key == "STATUS":
                entry["status"] = value

            elif key == "UID":
                entry["uid"] = value

        if entry:
            entries.append(entry)

    return entries


for calendar in calendars:

    print(f"\n{'=' * 40}")
    print(f"KALENDER: {calendar.upper()}")
    print("=" * 40)

    for component in ["VEVENT", "VTODO"]:

        print(f"\n--- {component} ---")

        response = get_entries(calendar, component)

        print("Status:", response.status_code)

        if response.status_code != 207:
            print(response.text)
            continue

        entries = parse_events(response.text)

        for entry in entries:
            print()
            print("Titel:", entry.get("summary", ""))
            print("Start:", entry.get("start", ""))
            print("Ende: ", entry.get("end", ""))
            print("Status:", entry.get("status", ""))
            print("UID:", entry.get("uid", ""))