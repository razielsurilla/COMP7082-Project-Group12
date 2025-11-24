from enum import Enum
import json
from datetime import datetime, date, timedelta
from app.sharedVars import AddEditEventData

DAY_IN_SECONDS = 86400
WEEK_IN_SECONDS = 604800
YEAR_IN_SECONDS = 31536000

# data tables
class Event(Enum):
    TABLE_NAME = "events"

    EVENT_NAME = "name"
    START_DATE = "start_date"
    END_DATE = "end_date"
    DESC = "description"

    RECURRING = "is_recurring"
    ALERTING = "is_alerting"

    R_OPTION = "recurring_option"          # daily / weekly / monthly index
    A_OPTIONS = "alerting_options"         # JSON text of alert checkboxes
    R_INTERVAL = "recurring_interval"              # e.g. every N days / week pattern

    # End options:
    # 0 = never ends
    # 1 = ends on specific date (see R_END_DATE)
    # 2 = ends after X occurrences (see R_END_COUNT)
    R_END_OPTIONS = "recurring_end_options"
    R_END_DATE = "recurring_end_date"      # REAL (timestamp) or NULL
    R_END_COUNT = "recurring_end_count"    # INTEGER or NULL

class CalendarData:
    def __init__(self, sqlInstance):
        self.sql = sqlInstance

    def buildData(self):
        # NOTE: if the table already exists, you'll need ALTER TABLE commands instead.
        query = (
            f"CREATE TABLE IF NOT EXISTS {Event.TABLE_NAME.value} ("
            f"{Event.EVENT_NAME.value} TEXT,"
            f"{Event.START_DATE.value} REAL NOT NULL,"
            f"{Event.END_DATE.value} REAL NOT NULL,"
            f"{Event.DESC.value} TEXT,"
            f"{Event.RECURRING.value} BOOLEAN,"
            f"{Event.ALERTING.value} BOOLEAN,"
            f"{Event.R_OPTION.value} INT,"
            f"{Event.A_OPTIONS.value} TEXT,"
            f"{Event.R_INTERVAL.value} INT,"
            f"{Event.R_END_OPTIONS.value} INT DEFAULT 0,"       # 0 = never
            f"{Event.R_END_DATE.value} REAL,"                   # nullable
            f"{Event.R_END_COUNT.value} INT,"                   # nullable
            f"PRIMARY KEY ({Event.START_DATE.value}, {Event.END_DATE.value})"
            f");"
        )
        self.sql.execute(query)

    # don't execute this unless needed
    def deleteData(self):
        query = f"DROP TABLE IF EXISTS {Event.TABLE_NAME.value};"
        self.sql.execute(query)

    def verifyData(self):
        query = f"PRAGMA table_info({Event.TABLE_NAME.value});"
        self.sql.execute(query)
        self.printQueryData()

    def printQueryData(self):
        rows = self.sql.fetchall()
        print("number of rows fetched: ", len(rows))
        for row in rows:
            print(row)

    def getAllData(self):
        query = f"SELECT * FROM {Event.TABLE_NAME.value};"
        self.sql.execute(query)

        rows = self.sql.fetchall()
        rowCount = len(rows)
        dataList = []

        # Expected column order (matching buildData):
        # 0  name
        # 1  start_date
        # 2  end_date
        # 3  description
        # 4  is_recurring
        # 5  is_alerting
        # 6  recurring_option
        # 7  alerting_options (JSON text)
        # 8  recurring_interval
        # 9  recurring_end_options
        # 10 recurring_end_date
        # 11 recurring_end_count

        if rowCount > 0:
            for i in range(rowCount):
                row = rows[i]
                dataFrame = AddEditEventData()

                dataFrame.eventName = row[0]
                dataFrame.eventStartDate = row[1]
                dataFrame.eventEndDate = row[2]
                dataFrame.eventDescription = row[3]
                dataFrame.isRecurringEvent = row[4]
                dataFrame.isAlerting = row[5]
                dataFrame.recurringEventOptionIndex = row[6]

                # alert options as JSON list, if present
                try:
                    dataFrame.selectedAlertCheckboxes = (
                        json.loads(row[7]) if row[7] else []
                    )
                except Exception:
                    dataFrame.selectedAlertCheckboxes = []

                dataFrame.recurringInterval = row[8]
                dataFrame.recurringEndOptionIndex = row[9]      # NEW: 0/1/2
                dataFrame.recurringEndDate = row[10]            # timestamp or None
                dataFrame.recurringEndCount = row[11]           # int or None

                dataList.append(dataFrame)

        return dataList

    def addData(self, dataFrame):
        # Convert Python None → SQL NULL for nullable fields
        end_opt = int(getattr(dataFrame, "recurringEndOptionIndex", 0) or 0)

        # timestamps or None
        end_date = getattr(dataFrame, "recurringEndDate", None)
        end_date_sql = "NULL" if end_date is None else str(end_date)

        end_count = getattr(dataFrame, "recurringEndCount", None)
        end_count_sql = "NULL" if end_count is None else str(int(end_count))

        alert_json = json.dumps(getattr(dataFrame, "selectedAlertCheckboxes", []))

        query = (
            f"INSERT INTO {Event.TABLE_NAME.value} ("
            f"{Event.EVENT_NAME.value}, "
            f"{Event.START_DATE.value}, "
            f"{Event.END_DATE.value}, "
            f"{Event.DESC.value}, "
            f"{Event.RECURRING.value}, "
            f"{Event.ALERTING.value}, "
            f"{Event.R_OPTION.value}, "
            f"{Event.A_OPTIONS.value}, "
            f"{Event.R_INTERVAL.value}, "
            f"{Event.R_END_OPTIONS.value}, "
            f"{Event.R_END_DATE.value}, "
            f"{Event.R_END_COUNT.value}"
            f") VALUES ("
            f"'{dataFrame.eventName}', "
            f"{dataFrame.eventStartDate}, "
            f"{dataFrame.eventEndDate}, "
            f"'{dataFrame.eventDescription}', "
            f"{int(bool(dataFrame.isRecurringEvent))}, "
            f"{int(bool(dataFrame.isAlerting))}, "
            f"{int(dataFrame.recurringEventOptionIndex)}, "
            f"'{alert_json}', "
            f"{dataFrame.recurringInterval}, "
            f"{end_opt}, "
            f"{end_date_sql}, "
            f"{end_count_sql}"
            f");"
        )

        self.sql.execute(query)
        self.sql.commit()

    def printAllData(self):
        query = f"SELECT * FROM {Event.TABLE_NAME.value};"
        self.sql.execute(query)
        self.printQueryData()

    def getDateFromTimestamp(self, timestamp):
        dateObj = datetime.fromtimestamp(timestamp)
        return dateObj

    def getAllRecurringEventsWithinRange(self, startDate, endDate):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.RECURRING.value} = 1 "
            f"AND {Event.START_DATE.value} <= '{endDate}'"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()
        fetched_data = [list(row) for row in fetched_data] #make list so mutable

        repeated_events = []
        for item in fetched_data:
            copy = item[:]
            increment = 99999999

            match item[6]: #Find how much we increment by
                case 1: #Daily
                    increment = DAY_IN_SECONDS * item[8]
                case 2: #Weekly
                    increment = WEEK_IN_SECONDS * item[8]
                case 3: #Monthly, Simple logic due to time constraint
                    increment = DAY_IN_SECONDS * 30 * item[8]
                case 4: #Yearly
                    increment = YEAR_IN_SECONDS * item[8]

            match item[9]: #Handle end point logic
                case 0: #None
                    inc = item[1] + increment
                    while inc <= endDate:
                        if inc >= startDate:
                            temp = item.copy()
                            temp[1] = inc
                            repeated_events.append(temp)
                        print(inc)
                        inc += increment

                case 1: #End Date
                    inc = item[1]
                    while inc < item[10]:
                        inc += increment
                        temp = item.copy()
                        temp[1] = inc
                        if temp[1] > startDate:
                            repeated_events.append(temp)


                case 2: #Num Times
                    counter = 0
                    while counter < item[11]:
                        temp = item.copy()
                        temp[1] += (increment * (counter + 1))
                        if temp[1] > startDate:
                            repeated_events.append(temp)
                        counter += 1


        repeated_events = [tuple(e) for e in repeated_events] #back to tuples
        return repeated_events





    def findEventsInRangeMainCal(self, rangeMin, rangeMax):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} BETWEEN {rangeMin} AND {rangeMax};"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()

        recurring_data = self.getAllRecurringEventsWithinRange(rangeMin, rangeMax)

        for r in recurring_data:
            fetched_data.append(r)

        event_dict = {}
        start = rangeMin
        end = rangeMin + DAY_IN_SECONDS

        for i in range(42):
            day_list = []
            for row in fetched_data:
                day_list.append(row) if start <= row[1] < end else None
            if len(day_list) > 0:
                event_dict[i] = day_list
            start += DAY_IN_SECONDS
            end += DAY_IN_SECONDS

        return event_dict

    def findEventsInRangeImpDate(self, oldDate, newDate, daysInMonth):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} BETWEEN {oldDate} AND {newDate};"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()

        event_dict = {}
        start = oldDate
        end = oldDate + DAY_IN_SECONDS

        for i in range(daysInMonth):
            day_list = []
            for row in fetched_data:
                day_list.append(row) if start <= row[1] <= end else None
            if len(day_list) > 0:
                event_dict[i] = day_list
            start += DAY_IN_SECONDS
            end += DAY_IN_SECONDS

        return event_dict

    def updateEvent(self, old_start_ts, old_end_ts, dataFrame):
        """Update a single event identified by its original start/end timestamps."""
        end_opt = int(getattr(dataFrame, "recurringEndOptionIndex", 0) or 0)

        end_date = getattr(dataFrame, "recurringEndDate", None)
        end_date_sql = "NULL" if end_date is None else str(end_date)

        end_count = getattr(dataFrame, "recurringEndCount", None)
        end_count_sql = "NULL" if end_count is None else str(int(end_count))

        alert_json = json.dumps(getattr(dataFrame, "selectedAlertCheckboxes", []))

        query = (
            f"UPDATE {Event.TABLE_NAME.value} SET "
            f"{Event.EVENT_NAME.value} = '{dataFrame.eventName}', "
            f"{Event.START_DATE.value} = {dataFrame.eventStartDate}, "
            f"{Event.END_DATE.value} = {dataFrame.eventEndDate}, "
            f"{Event.DESC.value} = '{dataFrame.eventDescription}', "
            f"{Event.RECURRING.value} = {int(bool(dataFrame.isRecurringEvent))}, "
            f"{Event.ALERTING.value} = {int(bool(dataFrame.isAlerting))}, "
            f"{Event.R_OPTION.value} = {int(dataFrame.recurringEventOptionIndex)}, "
            f"{Event.A_OPTIONS.value} = '{alert_json}', "
            f"{Event.R_INTERVAL.value} = {dataFrame.recurringInterval}, "
            f"{Event.R_END_OPTIONS.value} = {end_opt}, "
            f"{Event.R_END_DATE.value} = {end_date_sql}, "
            f"{Event.R_END_COUNT.value} = {end_count_sql} "
            f"WHERE {Event.START_DATE.value} = {old_start_ts} "
            f"AND {Event.END_DATE.value} = {old_end_ts};"
        )

        self.sql.execute(query)
        self.sql.commit()

    def deleteEvent(self, start_ts, end_ts):
        """Delete a single event identified by its start/end timestamps."""
        query = (
            f"DELETE FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} = {start_ts} "
            f"AND {Event.END_DATE.value} = {end_ts};"
        )
        self.sql.execute(query)
        self.sql.commit()
