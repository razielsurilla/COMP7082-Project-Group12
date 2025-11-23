# app/pages/home.py
from nicegui import app, ui
from datetime import date, timedelta, datetime
import calendar

from app.components import upcoming_events
from app.sharedVars import SharedVars


# TODO: this should be a component, then home.py should create a Calendar object
class Calendar:
    def __init__(self, calendar_data):
        self.today = date.today()
        self.state = {"year": self.today.year, "month": self.today.month}
        self.calendar_container = None
        self.calendar_label = None
        self.month_select = None
        self.year_select = None
        self.sharedData = SharedVars()
        self.month_event_data = None
        self.calendar_data = calendar_data

    def generate_month(self, year: int, month: int):
        first_day = date(year, month, 1)

        # find the sunday before the first day so grid is always 7x6
        start_day = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
        last_day = start_day + timedelta(days=41)

        start_day_unix = int(datetime.combine(start_day, datetime.min.time()).timestamp())
        last_day_unix = int(datetime.combine(last_day, datetime.max.time()).timestamp())

        self.month_event_data = self.calendar_data.findEventsInRangeMainCal(start_day_unix, last_day_unix)

        # 6 weeks displayed, so 42 days
        return [start_day + timedelta(days=i) for i in range(42)]

    def render_calendar(self):
        self.calendar_container.clear()  # clear old calendar or it stacks
        days = self.generate_month(self.state["year"], self.state["month"])

        with self.calendar_container:
            with ui.grid(columns=7).classes('gap-x-4 gap-y-2 justify-center'):
                for weekday in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                    ui.label(weekday).classes('text-md font-bold text-center')
                #TODO: Make Buttons
                for index, day in enumerate(days):
                    is_current = day.month == self.state["month"]
                    is_today = day == self.today
                    bg = 'bg-white' if is_current else 'bg-gray-200'
                    if is_today:
                        bg = 'bg-blue-100'  # highlight today

                    def show_day_modal(index=index, day=day):
                        with ui.dialog() as dialog, ui.card().classes(
                                'p-4 w-80 h-120 flex items-center rounded-3xl relative bg-[#d9d9d9]'):
                            with ui.row().classes():
                                app.storage.user.update({
                                                            self.sharedData.ADDEDIT_DATA_KEY: f"{calendar.month_name[day.month]} {day.day}, {day.year}"})
                                ui.icon('add').classes('text-black absolute top-4 right-4 text-2xl').on(
                                    'click', lambda: ui.navigate.to('/add-edit'))

                            ui.label(f"{calendar.month_name[day.month]} {day.day}, {day.year}").classes(
                                'text-xl font-bold text-center align-center'
                            )

                            with ui.column().classes('overflow-y-auto h-90 w-full my-2 gap-2'):
                                if day_events := self.month_event_data.get(index):
                                    for e in day_events:
                                        print(e)
                                        with ui.card().classes('w-60 h-20 p-2 flex justify-between min-w-0'):
                                            #LS
                                            with ui.element('div').classes('flex flex-col shrink overflow-hidden min-w-0'):
                                                ui.label(f"{e[0]}").classes('text-ellipsis whitespace-nowrap overflow-hidden min-w-0 max-w-40 mb-5')
                                                if e[4]:  #If is a recurring event
                                                    s = ""
                                                    match e[6]: #check type of recurrence
                                                        case 1:
                                                            s = f"Every {e[8]} Day(s)"
                                                        case 2:
                                                            s = "Weekly"
                                                        case 3:
                                                            s = "Monthly"
                                                        case 4:
                                                            s = "Yearly"
                                                    with ui.element('div').classes('flex'):
                                                        ui.icon('cached').classes('pt-1 pr-1')
                                                        ui.label(f"{s}")

                                            with ui.element('div').classes('h-full block ml-auto justify-right items-end text-right'):
                                                ui.label(f"{datetime.fromtimestamp(e[1]).strftime('%H:%M')}")
                                                if e[2] > 0:  #If event has end time
                                                    ui.label("to")
                                                    ui.label(f"{datetime.fromtimestamp(e[2]).strftime('%H:%M')}")

                        dialog.open()

                    # card is one day cell
                    #TODO: Make Clickable to pop up modal
                    with ui.card().classes(f'w-24 h-24 block p-2 {bg}').on('click', show_day_modal):
                        weekend = 'text-red' if (day.weekday() == 5 or day.weekday() == 6) else 'text-black'
                        ui.label(str(day.day)).classes(f'{weekend}')
                        if day_events := self.month_event_data.get(index):
                            with ui.element('div').classes('flex flex-nowrap items-center overflow-hidden'):
                                ui.icon('circle').classes('text-blue-500 text-xs pr-1')
                                ui.label(f"{day_events[0][0]}").classes("overflow-hidden whitespace-nowrap text-ellipsis min-w-0")
                            if len(day_events) > 1:
                                with ui.element('div').classes('flex flex-nowrap items-center overflow-hidden'):
                                    ui.icon('circle').classes('text-blue-500 text-xs pr-1')
                                    ui.label(f"{day_events[1][0]}").classes("overflow-hidden whitespace-nowrap text-ellipsis min-w-0")
                            if len(day_events) > 2:  #if more than two events
                                num_events = len(day_events) - 2
                                ui.label(f"+{num_events} More").classes('text-center')

    def prev_month(self):
        # wraparound jan -> dec
        if self.state["month"] == 1:
            self.state["month"] = 12
            self.state["year"] -= 1
        else:
            self.state["month"] -= 1
        # self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        # self.render_calendar()  # redraw for prev month
        self.update_state(self.state["month"], self.state["year"])

    def next_month(self):
        # wraparound dec -> jan
        if self.state["month"] == 12:
            self.state["month"] = 1
            self.state["year"] += 1
        else:
            self.state["month"] += 1
        # self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        # self.render_calendar()  # redraw for next month
        self.update_state(self.state["month"], self.state["year"])

    def update_state(self, month, year):
        self.state["month"] = month
        self.state["year"] = year

        if self.month_select:
            self.month_select.set_value(calendar.month_name[self.state["month"]])
        if self.year_select:
            self.year_select.set_value(str(self.state["year"]))

        self.render_calendar()

    def show(self):
        months = list(calendar.month_name)[1:]
        years = [str(y) for y in range(self.today.year - 1000, self.today.year + 1000)]

        # this is so everything is centered
        with ui.column().classes('justify-center items-center w-full'):
            # month label on top
            #self.calendar_label = ui.label(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}') \
            #					 .classes('text-3xl font-bold mb-4 justify-center text-center')
            # TODO: Make these dropdown menus with on_change events (set state, set text, render_calendar)
            with ui.row():
                def on_month_change(e):
                    month_index = months.index(e.value) + 1
                    self.update_state(month_index, self.state["year"])

                def on_year_change(e):
                    year_value = int(e.value)
                    self.update_state(self.state["month"], year_value)

                self.month_select = ui.select(
                    options=months,
                    value=calendar.month_name[self.state["month"]],
                    on_change=on_month_change
                )

                self.year_select = ui.select(
                    options=years,
                    value=str(self.state["year"]),
                    on_change=on_year_change
                )

            # Implement Later, not important for now
            # ui.button("Today", on_click=lambda: self.update_state(self.today.month, self.today.year))

            # row here, so the arrows are on the same row as the calendar
            with ui.row().classes('items-center justify-center gap-4'):
                ui.button('<', on_click=self.prev_month).classes('w-10 h-10 self-center')
                self.calendar_container = ui.column().classes('items-center mb-4')
                ui.button('>', on_click=self.next_month).classes('w-10 h-10 self-center')

            self.render_calendar()


class Dates:
    def __init__(self, calendar_data):
        self.today = date.today()
        self.state = {"year": self.today.year, "month": self.today.month}
        self.month_abr = calendar.month_abbr[self.today.month]
        self.calendar_data = calendar_data
        self.num_of_days = calendar.monthrange(self.state["year"], self.state["month"])[1]
        self.dict = self.populate()


    def populate(self):
        first_day = date(self.state["year"], self.state["month"], 1)
        #always get last day of any month
        last_day = date(self.state["year"], self.state["month"], self.num_of_days)

        start_day_unix = int(datetime.combine(first_day, datetime.min.time()).timestamp())
        last_day_unix = int(datetime.combine(last_day, datetime.max.time()).timestamp())

        return self.calendar_data.findEventsInRangeImpDate(start_day_unix, last_day_unix, self.num_of_days)

    def show(self):
        ui.label("Important Dates").classes('w-full text-center text-2xl mt-4 font-bold')
        ui.label(f"{calendar.month_name[self.state['month']]} {self.state['year']}").classes('w-full text-center text-xl font-bold')
        with ui.element().classes('flex flex-col w-full grow overflow-hidden').style("height: calc(100vh - 250px);"):
            with ui.element().classes("w-full overflow-x-auto overflow-y-hidden whitespace-nowrap p-4").style("flex: none"):
                with ui.row().classes('flex-nowrap gap-4 p-4'):
                    for item in self.dict:
                        with ui.card().classes('shrink-0 p-4 shadow-md inline-block bg-gray-300').style("width: calc(100vw / 4.5); height: 600px;"):
                            ui.label(f"{self.month_abr} {int(item) + 1}").classes('w-full text-center font-bold text-xl mb-4')
                            max = 5
                            counter = 0
                            for e in self.dict[item]:
                                if counter < max:
                                    with ui.card().classes('w-full h-20 p-2 flex justify-between mb-2'):
                                        # LS
                                        with ui.element('div').classes('flex flex-col shrink overflow-hidden min-w-0'):
                                            ui.label(f"{e[0]}").classes(
                                                'text-ellipsis whitespace-nowrap overflow-hidden min-w-0 max-w-40 mb-5')
                                            if e[4]:  # If is a recurring event
                                                s = ""
                                                match e[6]:  # check type of recurrence
                                                    case 1:
                                                        s = f"Every {e[8]} Day(s)"
                                                    case 2:
                                                        s = "Weekly"
                                                    case 3:
                                                        s = "Monthly"
                                                    case 4:
                                                        s = "Yearly"
                                                with ui.element('div').classes('flex'):
                                                    ui.icon('cached').classes('pt-1 pr-1')
                                                    ui.label(f"{s}")

                                        with ui.element('div').classes(
                                                'h-full block ml-auto justify-right items-end text-right'):
                                            ui.label(f"{datetime.fromtimestamp(e[1]).strftime('%H:%M')}")
                                            if e[2] > 0:  # If event has end time
                                                ui.label("to")
                                                ui.label(f"{datetime.fromtimestamp(e[2]).strftime('%H:%M')}")
                                    counter += 1
                            if len(self.dict[item]) > max:
                                ui.label(f"+{len(self.dict[item]) - max} More").classes(
                                    'w-full text-center text-xl mb-4')


                                # for event in self.dict[item]:
                            #     with ui.card().classes('w-full h-20 p-2 mb-2 flex justify-between'):
                            #         # LS
                            #         with ui.element('div').classes('block mr-auto'):
                            #             ui.label("Event Name").classes('mb-5')
                            #             if True:  # If is a recurring event
                            #                 with ui.element('div').classes('flex'):
                            #                     ui.icon('cached').classes('pt-1 pr-1')
                            #                     ui.label("Every 2 Days")
                            #
                            #         with ui.element('div').classes('block ml-auto justify-right items-end text-right'):
                            #             ui.label(f"12:00")
                            #             if True:  # If event has end time
                            #                 ui.label("to")
                            #                 ui.label(f"1:00")


class HomeTabs:
    def __init__(self, calendar_data):
        self.calendar_data = calendar_data

    def show(self):
        calendar_ui = Calendar(calendar_data=self.calendar_data)
        important_dates_ui = Dates(calendar_data=self.calendar_data)

        with ui.tabs().classes('w-full fixed bottom-0 left-0 h-10') as tabs:
            calendar_tab = ui.tab("Main Calendar")
            important_dates_tab = ui.tab('Important Dates')
            upcoming_tab = ui.tab('Upcoming Events')

        with ui.tab_panels(tabs, value=calendar_tab).classes('w-full p-0').props('animated=False'):
            with ui.tab_panel(calendar_tab).classes('p-0 overflow-hidden'):
                calendar_ui.show()

            with ui.tab_panel(important_dates_tab).classes('pl-20'):
                important_dates_ui.show()

            with ui.tab_panel(upcoming_tab).classes('pl-20'):
                # 🔹 embed upcoming events component, backed by DB
                upcoming_events.build_upcoming_events(calendar_data=self.calendar_data)
