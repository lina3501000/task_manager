import network
import time
import urequests
import ubinascii

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    BASE_URL,
    USERNAME,
    PASSWORD,
    CALENDARS
)


# --------------------------------------------------
# WLAN
# --------------------------------------------------

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("WLAN bereits verbunden")
        print(wlan.ifconfig())
        return wlan

    print("Verbinde mit WLAN...")

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 15
    start = time.time()

    while not wlan.isconnected():
        if time.time() - start > timeout:
            raise RuntimeError("WLAN-Verbindung fehlgeschlagen")

        time.sleep(0.5)

    print("WLAN verbunden")
    print("IP:", wlan.ifconfig()[0])

    return wlan


# --------------------------------------------------
# Basic Auth
# --------------------------------------------------

def get_auth_header():
    credentials = USERNAME + ":" + PASSWORD
    encoded = ubinascii.b2a_base64(
        credentials.encode()
    ).decode().strip()

    return "Basic " + encoded


# --------------------------------------------------
# CalDAV REPORT
# --------------------------------------------------

def get_entries(calendar, component):

    url = (
        BASE_URL
        + "/remote.php/dav/calendars/"
        + USERNAME
        + "/"
        + calendar
        + "/"
    )

    headers = {
        "Depth": "1",
        "Content-Type": "application/xml; charset=utf-8",
        "Authorization": get_auth_header()
    }

    body = """<?xml version="1.0" encoding="UTF-8"?>
<c:calendar-query
    xmlns:d="DAV:"
    xmlns:c="urn:ietf:params:xml:ns:caldav">

    <d:prop>
        <d:getetag/>
        <c:calendar-data/>
    </d:prop>

    <c:filter>
        <c:comp-filter name="VCALENDAR">
            <c:comp-filter name="%s"/>
        </c:comp-filter>
    </c:filter>

</c:calendar-query>
""" % component

    print()
    print("Hole", component, "aus", calendar)

    try:
        response = urequests.request(
            "REPORT",
            url,
            headers=headers,
            data=body
        )

        print("HTTP Status:", response.status_code)

        if response.status_code != 207:
            print("Nextcloud Fehler:", response.status_code)
            response.close()
            return []

        xml = response.text
        response.close()

        return parse_xml(xml, component, calendar)

    except Exception as e:
        print("CalDAV Fehler:", e)
        return []


# --------------------------------------------------
# XML auswerten
# --------------------------------------------------

def extract_calendar_data(xml):

    entries = []

    start_tag = "<c:calendar-data>"
    end_tag = "</c:calendar-data>"

    start = 0

    while True:

        start = xml.find(start_tag, start)

        if start == -1:
            break

        start += len(start_tag)

        end = xml.find(end_tag, start)

        if end == -1:
            break

        data = xml[start:end]

        entries.append(data)

        start = end + len(end_tag)

    return entries


# --------------------------------------------------
# iCalendar-Daten parsen
# --------------------------------------------------

def parse_icalendar(data, component, calendar):

    entries = []

    current = None

    lines = data.replace("\r\n", "\n").split("\n")

    for line in lines:

        line = line.strip()

        if line == "BEGIN:" + component:

            current = {
                "calendar": calendar,
                "type": component
            }

            continue

        if line == "END:" + component:

            if current is not None and "uid" in current:
                entries.append(current)

            current = None

            continue

        if current is None:
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        # Parameter entfernen
        # z.B. DTSTART;TZID=Europe/Berlin
        key_name = key.split(";", 1)[0]

        if key_name == "SUMMARY":
            current["summary"] = value

        elif key_name == "DTSTART":
            current["start"] = value

        elif key_name == "DTEND":
            current["end"] = value

        elif key_name == "STATUS":
            current["status"] = value

        elif key_name == "UID":
            current["uid"] = value

    return entries


# --------------------------------------------------
# XML -> iCalendar
# --------------------------------------------------

def parse_xml(xml, component, calendar):

    entries = []

    calendar_data_entries = extract_calendar_data(xml)

    for data in calendar_data_entries:

        parsed = parse_icalendar(
            data,
            component,
            calendar
        )

        entries.extend(parsed)

    return entries


# --------------------------------------------------
# Alles abrufen
# --------------------------------------------------

def get_all_entries():

    entries = []

    for calendar in CALENDARS:

        for component in ("VEVENT", "VTODO"):

            calendar_entries = get_entries(
                calendar,
                component
            )

            entries.extend(calendar_entries)

    return entries


# --------------------------------------------------
# Ausgabe
# --------------------------------------------------

def print_entries(entries):

    for entry in entries:

        print()
        print("Typ:", entry.get("type", ""))
        print("Kalender:", entry.get("calendar", ""))
        print("Titel:", entry.get("summary", ""))
        print("Start:", entry.get("start", ""))
        print("Ende:", entry.get("end", ""))
        print("Status:", entry.get("status", ""))
        print("UID:", entry.get("uid", ""))


# --------------------------------------------------
# Hauptprogramm
# --------------------------------------------------

def main():

    print("=== Pico W CalDAV ===")

    connect_wifi()

    print("URL:", BASE_URL)
    print("Username:", USERNAME)

    entries = get_all_entries()

    print()
    print("=====================")
    print("Einträge:", len(entries))
    print("=====================")

    print_entries(entries)

    events = []
    tasks = []

    for entry in entries:

        if entry["type"] == "VEVENT":
            events.append(entry)

        elif entry["type"] == "VTODO":
            tasks.append(entry)

    print()
    print("Events:", len(events))
    print("Tasks:", len(tasks))

    return entries, events, tasks


main()