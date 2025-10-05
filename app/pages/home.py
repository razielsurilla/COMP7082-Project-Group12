from nicegui import ui
from datetime import date, timedelta
import calendar

def show():
    today = date.today()
    year, month = today.year, today.month
    month_name = calendar.month_name[month]

    def generate_month(year, month):
        first_day = date(year, month, 1)
        start_day = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
        return [start_day + timedelta(days=i) for i in range(42)]

    ui.label(f'{month_name} {year}').classes('text-3xl font-bold mb-4')
    days = generate_month(year, month)

    with ui.grid(columns=7).classes('gap-2 justify-center'):
        for weekday in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            ui.label(weekday).classes('text-md font-bold text-center')

        for day in days:
            is_current = day.month == month
            is_today = day == today
            bg = 'bg-white' if is_current else 'bg-gray-100'
            if is_today:
                bg = 'bg-blue-200'
            with ui.card().classes(f'w-20 h-20 flex items-center justify-center {bg}'):
                ui.label(str(day.day))
