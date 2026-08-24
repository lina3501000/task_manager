import network
import time
import urequests
import ubinascii
import ntptime
import gc

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    BASE_URL,
    USERNAME,
    PASSWORD,
    CALENDARS
)

min_free_memory = 999999

def check_memory():
    global min_free_memory

    gc.collect()
    free = gc.mem_free()

    if free < min_free_memory:
        min_free_memory = free

    print("RAM frei:", free, "Bytes")
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
    
    print("Hole aktuelle Zeit...")
    ntptime.settime()
    print("Zeit:", time.localtime())
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
    check_memory()
    gc.collect()
    try:
        response = urequests.request(
            "REPORT",
            url,
            headers=headers,
            data=body
        )
        check_memory()

        print("HTTP Status:", response.status_code)

        if response.status_code != 207:
            print("Nextcloud Fehler:", response.status_code)
            response.close()
            return []

        xml = response.text
        response.close()

        entries = parse_xml(xml, component, calendar)

        del xml

        return entries

    except Exception as e:
        print("CalDAV Fehler:", e)
        return []

def complete_task(task):

    href = task.get("href")
    etag = task.get("etag")

    if not href:
        print("Keine Href für Aufgabe vorhanden")
        return False

    url = BASE_URL + href
    auth = get_auth_header()

    print()
    print("Markiere Aufgabe als erledigt:")
    print(task.get("summary", ""))

    try:
        # Bestehende iCalendar-Datei holen
        response = urequests.get(
            url,
            headers={
                "Authorization": auth
            }
        )

        print("GET Status:", response.status_code)

        if response.status_code != 200:
            response.close()
            return False

        ical = response.text
        response.close()

        # STATUS ändern
        if "STATUS:" in ical:
            ical = ical.replace(
                "STATUS:NEEDS-ACTION",
                "STATUS:COMPLETED"
            )

        else:
            marker = "END:VTODO"
            ical = ical.replace(
                marker,
                "STATUS:COMPLETED\r\n"
                "END:VTODO"
            )

        # PERCENT-COMPLETE setzen
        if "PERCENT-COMPLETE:" in ical:
            lines = ical.split("\r\n")

            new_lines = []

            for line in lines:
                if line.startswith("PERCENT-COMPLETE:"):
                    new_lines.append(
                        "PERCENT-COMPLETE:100"
                    )
                else:
                    new_lines.append(line)

            ical = "\r\n".join(new_lines)

        else:
            ical = ical.replace(
                "END:VTODO",
                "PERCENT-COMPLETE:100\r\n"
                "END:VTODO"
            )

        check_memory()

        # Zurück zu Nextcloud
        headers = {
            "Content-Type": "text/calendar; charset=utf-8",
            "Authorization": auth,
            "If-Match": etag
        }

        response = urequests.put(
            url,
            headers=headers,
            data=ical
        )

        status = response.status_code
        response.close()

        del ical
        gc.collect()

        print("PUT Status:", status)

        if status in (200, 201, 204):
            print("Aufgabe erfolgreich abgeschlossen")
            return True

        print("Nextcloud Fehler:", status)
        return False

    except Exception as e:
        print("Fehler beim Abschließen:", e)
        gc.collect()
        return False
# --------------------------------------------------
# XML auswerten
# --------------------------------------------------

def extract_calendar_data(xml):

    entries = []

    start_tag = "<cal:calendar-data>"
    end_tag = "</cal:calendar-data>"

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
        elif key_name == "DUE":
            current["due"] = value

        elif key_name == "STATUS":
            current["status"] = value

        elif key_name == "UID":
            current["uid"] = value
        elif key_name == "RELATED-TO":
            current["related_to"] = value

        elif key_name == "RECURRENCE-ID":
            current["recurrence_id"] = value

        elif key_name == "RRULE":
            current["rrule"] = value

        elif key_name == "PERCENT-COMPLETE":
            current["percent_complete"] = value

    return entries


# --------------------------------------------------
# XML -> iCalendar
# --------------------------------------------------

def parse_xml(xml, component, calendar):

    entries = []

    # Jede DAV response einzeln finden
    pos = 0

    while True:

        start = xml.find("<d:response>", pos)

        if start == -1:
            break

        end = xml.find("</d:response>", start)

        if end == -1:
            break

        block = xml[start:end]

        # href
        href_start = block.find("<d:href>")
        href_end = block.find("</d:href>")

        if href_start != -1 and href_end != -1:
            href = block[
                href_start + len("<d:href>"):
                href_end
            ]
        else:
            href = ""

        # ETag
        etag_start = block.find("<d:getetag>")
        etag_end = block.find("</d:getetag>")

        if etag_start != -1 and etag_end != -1:
            etag = block[
                etag_start + len("<d:getetag>"):
                etag_end
            ]
            etag = etag.replace("&quot;", '"')
        else:
            etag = ""

        # calendar-data
        data_start = block.find("<cal:calendar-data>")
        data_end = block.find("</cal:calendar-data>")

        if data_start != -1 and data_end != -1:

            data = block[
                data_start + len("<cal:calendar-data>"):
                data_end
            ]

            parsed = parse_icalendar(
                data,
                component,
                calendar
            )

            for entry in parsed:
                entry["href"] = href
                entry["etag"] = etag
                entry["ical_data"] = data

            entries.extend(parsed)

        pos = end + len("</d:response>")

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

            gc.collect()

    return entries
def get_task_date(task):
    """Gibt das relevante Datum der Aufgabe als YYYYMMDD zurück."""

    value = task.get("due", "")

    if not value:
        value = task.get("start", "")

    if not value:
        return 99999999

    # z.B. 20260823 oder 20260823T215900Z
    try:
        return int(value[:8])
    except:
        return 99999999


def is_completed(task):
    """Prüft, ob eine Aufgabe erledigt ist."""

    if task.get("status") == "COMPLETED":
        return True

    if task.get("percent_complete") == "100":
        return True

    return False


def filter_tasks(tasks):
    """
    Wählt pro UID nur die relevante offene Instanz aus.

    - vergangene offene Aufgabe -> behalten
    - nächste offene Aufgabe -> behalten
    - erledigte Instanzen -> entfernen
    - doppelte offene Instanzen -> nur eine behalten
    """

    now = time.localtime()
    today = (
        now[0] * 10000
        + now[1] * 100
        + now[2]
    )

    grouped = {}

    # Nach UID gruppieren
    for task in tasks:

        uid = task.get("uid")

        if not uid:
            continue

        if uid not in grouped:
            grouped[uid] = []

        grouped[uid].append(task)

    result = []

    for uid, instances in grouped.items():

        open_tasks = []

        for task in instances:

            if not is_completed(task):
                open_tasks.append(task)

        # Keine offene Instanz vorhanden
        if not open_tasks:
            continue

        # Nach Datum sortieren
        open_tasks.sort(key=get_task_date)

        overdue = []
        upcoming = []

        for task in open_tasks:

            date = get_task_date(task)

            if date < today:
                overdue.append(task)
            else:
                upcoming.append(task)

        # Falls eine offene Aufgabe überfällig ist:
        # älteste offene Instanz nehmen.
        if overdue:
            selected = overdue[0]

        # Sonst nächste zukünftige Aufgabe.
        else:
            selected = upcoming[0]

        result.append(selected)

    return result
def get_current_tasks(entries):

    tasks = []

    for entry in entries:
        if entry["type"] == "VTODO":
            tasks.append(entry)

    tasks = filter_tasks(tasks)

    return tasks
def filter_events(events):
    now = time.localtime()

    today = (
        now[0] * 10000
        + now[1] * 100
        + now[2]
    )

    filtered = []

    for event in events:

        start = event.get("start", "")
        end = event.get("end", "")

        if not start:
            continue

        # YYYYMMDD bzw. YYYYMMDDTHHMMSS...
        try:
            date_string = start[:8]

            year = int(date_string[0:4])
            month = int(date_string[4:6])
            day = int(date_string[6:8])

            event_date = (
                year * 10000
                + month * 100
                + day
            )

        except:
            continue

        # Event ist heute oder in der Zukunft
        if event_date >= today:
            filtered.append(event)
            continue

        # Falls es ein mehrtägiges Event ist:
        if end:

            try:
                end_date_string = end[:8]

                end_year = int(end_date_string[0:4])
                end_month = int(end_date_string[4:6])
                end_day = int(end_date_string[6:8])

                end_date = (
                    end_year * 10000
                    + end_month * 100
                    + end_day
                )

                if end_date >= today:
                    filtered.append(event)

            except:
                pass

    return filtered
def get_upcoming_events(entries):

    events = []

    for entry in entries:
        if entry["type"] == "VEVENT":
            events.append(entry)

    events = filter_events(events)
    # Nach Startdatum sortieren
    events.sort(key=lambda event: event.get("start", "99999999"))
    return events
def build_task_hierarchy(tasks):

    task_by_uid = {}

    # Alle Aufgaben nach UID speichern
    for task in tasks:
        task_by_uid[task["uid"]] = task

        # Unteraufgaben-Liste vorbereiten
        task["children"] = []

    roots = []

    # Hauptaufgaben und Unteraufgaben verbinden
    for task in tasks:

        parent_uid = task.get("related_to", "")

        if parent_uid and parent_uid in task_by_uid:

            parent = task_by_uid[parent_uid]
            parent["children"].append(task)

        else:

            roots.append(task)

    return roots

def print_task_tree(tasks, level=0):

    for task in tasks:

        indent = "    " * level

        print(
            indent
            + "[ ] "
            + task.get("summary", "")
        )

        due = task.get("due", "")

        if due:
            print(
                indent
                + "    Fällig: "
                + due
            )

        children = task.get("children", [])

        if children:
            print_task_tree(
                children,
                level + 1
            )
def add_task(task, calendar):

    uid = task.get("uid")

    if not uid:
        print("Keine UID vorhanden")
        return False

    url = (
        BASE_URL
        + "/remote.php/dav/calendars/"
        + USERNAME
        + "/"
        + calendar
        + "/"
        + uid
        + ".ics"
    )

    now = time.gmtime()

    dtstamp = (
        "{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}Z"
        .format(
            now[0],
            now[1],
            now[2],
            now[3],
            now[4],
            now[5]
        )
    )

    ical = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Pico W//CalDAV//EN\r\n"
        "BEGIN:VTODO\r\n"
        "UID:" + uid + "\r\n"
        "DTSTAMP:" + dtstamp + "\r\n"
        "SUMMARY:" + task.get("summary", "") + "\r\n"
    )

    if task.get("start"):
        ical += "DTSTART;VALUE=DATE:" + task["start"] + "\r\n"

    if task.get("due"):
        ical += "DUE;VALUE=DATE:" + task["due"] + "\r\n"

    if task.get("description"):
        ical += "DESCRIPTION:" + task["description"] + "\r\n"

    if task.get("related_to"):
        ical += "RELATED-TO:" + task["related_to"] + "\r\n"

    ical += (
        "STATUS:NEEDS-ACTION\r\n"
        "PERCENT-COMPLETE:0\r\n"
        "END:VTODO\r\n"
        "END:VCALENDAR\r\n"
    )

    print("===== PUT ICAL =====")
    print(ical)
    print("====================")

    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": "text/calendar"
    }

    try:

        response = urequests.put(
            url,
            headers=headers,
            data=ical
        )
        print("PUT URL:", url)
        print("Content-Type:", headers["Content-Type"])

        status = response.status_code

        print("PUT Status:", status)

        response.close()

        if status in (200, 201, 204):
            print("Aufgabe erfolgreich erstellt")
            return True

        print("Nextcloud Fehler:", status)
        return False

    except Exception as e:

        print("Fehler beim Erstellen:", e)
        gc.collect()

        return False
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
        print("Fällig:", entry.get("due", ""))
        print("Status:", entry.get("status", ""))
        print("Erledigt:", entry.get("percent_complete", ""))
        print("Übergeordnet:", entry.get("related_to", ""))
        print("Wiederholung:", entry.get("rrule", ""))
        print("UID:", entry.get("uid", ""))
        print("Href:", entry.get("href", ""))
        print("ETag:", entry.get("etag", ""))

