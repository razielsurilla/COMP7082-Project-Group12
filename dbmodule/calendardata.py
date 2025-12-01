from enum import Enum
import json
from datetime import datetime
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
    def __init__(self, sql_instance):
        self.sql = sql_instance

    def build_data(self):
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
    def delete_data(self):
        query = f"DROP TABLE IF EXISTS {Event.TABLE_NAME.value};"
        self.sql.execute(query)

    def verify_data(self):
        query = f"PRAGMA table_info({Event.TABLE_NAME.value});"
        self.sql.execute(query)
        self.print_query_data()

    def print_query_data(self):
        rows = self.sql.fetchall()
        print("number of rows fetched: ", len(rows))
        for row in rows:
            print(row)

    def get_all_data(self):
        query = f"SELECT * FROM {Event.TABLE_NAME.value};"
        self.sql.execute(query)

        rows = self.sql.fetchall()
        row_count = len(rows)
        data_list = []

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

        if row_count > 0:
            for i in range(row_count):
                row = rows[i]
                data_frame = AddEditEventData()

                data_frame.eventName = row[0]
                data_frame.eventStartDate = row[1]
                data_frame.eventEndDate = row[2]
                data_frame.eventDescription = row[3]
                data_frame.isRecurringEvent = row[4]
                data_frame.isAlerting = row[5]
                data_frame.recurringEventOptionIndex = row[6]

                # alert options as JSON list, if present
                try:
                    data_frame.selectedAlertCheckboxes = (
                        json.loads(row[7]) if row[7] else []
                    )
                except Exception:
                    data_frame.selectedAlertCheckboxes = []

                data_frame.recurringInterval = row[8]
                data_frame.recurringEndOptionIndex = row[9]      # NEW: 0/1/2
                data_frame.recurringEndDate = row[10]            # timestamp or None
                data_frame.recurringEndCount = row[11]           # int or None

                data_list.append(data_frame)

        return data_list

    def add_data(self, data_frame):
        # Convert Python None → SQL NULL for nullable fields
        end_opt = int(getattr(data_frame, "recurringEndOptionIndex", 0) or 0)

        # timestamps or None
        end_date = getattr(data_frame, "recurringEndDate", None)
        end_date_sql = "NULL" if end_date is None else str(end_date)

        end_count = getattr(data_frame, "recurringEndCount", None)
        end_count_sql = "NULL" if end_count is None else str(int(end_count))

        alert_json = json.dumps(getattr(data_frame, "selectedAlertCheckboxes", []))

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
            f"'{data_frame.eventName}', "
            f"{data_frame.eventStartDate}, "
            f"{data_frame.eventEndDate}, "
            f"'{data_frame.eventDescription}', "
            f"{int(bool(data_frame.isRecurringEvent))}, "
            f"{int(bool(data_frame.isAlerting))}, "
            f"{int(data_frame.recurringEventOptionIndex)}, "
            f"'{alert_json}', "
            f"{data_frame.recurringEventInterval}, "
            f"{end_opt}, "
            f"{end_date_sql}, "
            f"{end_count_sql}"
            f");"
        )

        self.sql.execute(query)
        self.sql.commit()

    def print_all_data(self):
        query = f"SELECT * FROM {Event.TABLE_NAME.value};"
        self.sql.execute(query)
        self.print_query_data()

    def get_date_from_timestamp(self, timestamp):
        date_obj = datetime.fromtimestamp(timestamp)
        return date_obj

    def get_all_recurring_events_within_range(self, start_date, end_date):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.RECURRING.value} = 1 "
            f"AND {Event.START_DATE.value} <= '{end_date}'"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()
        fetched_data = [list(row) for row in fetched_data] #make list so mutable

        repeated_events = []
        for item in fetched_data:
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
                    while inc <= end_date:
                        if inc >= start_date:
                            temp = item.copy()
                            temp[1] = inc
                            repeated_events.append(temp)
                        inc += increment

                case 1: #End Date
                    inc = item[1]
                    while inc < item[10]:
                        inc += increment
                        temp = item.copy()
                        temp[1] = inc
                        if temp[1] > start_date:
                            repeated_events.append(temp)

                case 2: #Num Times
                    counter = 0
                    while counter < item[11]:
                        temp = item.copy()
                        temp[1] += (increment * (counter + 1))
                        if temp[1] > start_date:
                            repeated_events.append(temp)
                        counter += 1

        repeated_events = [tuple(e) for e in repeated_events] #back to tuples
        return repeated_events


    def find_events_in_range_main_cal(self, range_min, range_max):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} BETWEEN {range_min} AND {range_max};"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()

        recurring_data = self.get_all_recurring_events_within_range(range_min, range_max)

        for event in recurring_data:
            fetched_data.append(event)

        event_dict = {}
        start = range_min
        end = range_min + DAY_IN_SECONDS

        for i in range(42):
            day_list = []
            for row in fetched_data:
                day_list.append(row) if start <= row[1] < end else None
            if len(day_list) > 0:
                event_dict[i] = day_list
            start += DAY_IN_SECONDS
            end += DAY_IN_SECONDS

        return event_dict

    def find_events_in_range_imp_date(self, old_date, new_date, days_in_month):
        query = (
            f"SELECT * FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} BETWEEN {old_date} AND {new_date};"
        )
        self.sql.execute(query)
        fetched_data = self.sql.fetchall()

        recurring_data = self.get_all_recurring_events_within_range(old_date, new_date)

        for event in recurring_data:
            fetched_data.append(event)

        event_dict = {}
        start = old_date
        end = old_date + DAY_IN_SECONDS

        for i in range(days_in_month):
            day_list = []
            for row in fetched_data:
                day_list.append(row) if start <= row[1] <= end else None
            if len(day_list) > 0:
                event_dict[i] = day_list
            start += DAY_IN_SECONDS
            end += DAY_IN_SECONDS

        return event_dict

    def update_event(self, old_start_ts, old_end_ts, data_frame):
        """Update a single event identified by its original start/end timestamps."""
        end_opt = int(getattr(data_frame, "recurringEndOptionIndex", 0) or 0)

        end_date = getattr(data_frame, "recurringEndDate", None)
        end_date_sql = "NULL" if end_date is None else str(end_date)

        end_count = getattr(data_frame, "recurringEndCount", None)
        end_count_sql = "NULL" if end_count is None else str(int(end_count))

        alert_json = json.dumps(getattr(data_frame, "selectedAlertCheckboxes", []))

        query = (
            f"UPDATE {Event.TABLE_NAME.value} SET "
            f"{Event.EVENT_NAME.value} = '{data_frame.eventName}', "
            f"{Event.START_DATE.value} = {data_frame.eventStartDate}, "
            f"{Event.END_DATE.value} = {data_frame.eventEndDate}, "
            f"{Event.DESC.value} = '{data_frame.eventDescription}', "
            f"{Event.RECURRING.value} = {int(bool(data_frame.isRecurringEvent))}, "
            f"{Event.ALERTING.value} = {int(bool(data_frame.isAlerting))}, "
            f"{Event.R_OPTION.value} = {int(data_frame.recurringEventOptionIndex)}, "
            f"{Event.A_OPTIONS.value} = '{alert_json}', "
            f"{Event.R_INTERVAL.value} = {data_frame.recurringInterval}, "
            f"{Event.R_END_OPTIONS.value} = {end_opt}, "
            f"{Event.R_END_DATE.value} = {end_date_sql}, "
            f"{Event.R_END_COUNT.value} = {end_count_sql} "
            f"WHERE {Event.START_DATE.value} = {old_start_ts} "
            f"AND {Event.END_DATE.value} = {old_end_ts};"
        )

        self.sql.execute(query)
        self.sql.commit()

    def delete_event(self, start_ts, end_ts):
        """Delete a single event identified by its start/end timestamps."""
        query = (
            f"DELETE FROM {Event.TABLE_NAME.value} "
            f"WHERE {Event.START_DATE.value} = {start_ts} "
            f"AND {Event.END_DATE.value} = {end_ts};"
        )
        self.sql.execute(query)
        self.sql.commit()
