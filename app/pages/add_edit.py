from nicegui import ui
from app.components.addedit import datePickerLabel, timePickerLabel
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import ClassVar, List

@dataclass
class AddEditEventData:
	eventName: str = ""
	eventDescription: str = ""
	eventStartDate: date = field(default_factory=datetime.now)
	eventEndDate: date = field(default_factory=datetime.now)
	isRecurringEvent: bool = False
	isAlerting: bool = False
	recurringEventOptionIndex: int = 0
	selectedAlertCheckboxes: List[int] = field(default_factory=list)
			
@dataclass
class EventDateTime:
	DATE_FORMAT: ClassVar[str] = "%Y-%m-%d/%H:%M"
	dateStr: str = ""
	timeStr: str = ""
	
	def getDate(self):
		try:
			self.eventStartDate = date.strptime(f"{self.dateStr}/{self.timeStr}", self.DATE_FORMAT)
		except ValueError:
			print("event date incorrect format!")
		
		return date
	

# TODO: this should be a component, then home.py should create a Calendar object
class AddEditEvent:
	def __init__(self, date, calendarData):
		self.currentDate = date
		self.pageData = AddEditEventData()
		self.eventStartData = EventDateTime()
		self.eventEndData = EventDateTime()
		self.calendarData = calendarData
		return None

	def showPage(self):
		def onDescriptionChange(event):
			self.pageData.eventDescription = event.value
		
		def onSaveEvent(event):
			print(self.pageData);
			self.calendarData.addData(None, None, None)
			self.calendarData.updateDescription(None, None)
			self.calendarData.updateDetail(None, None)
			self.calendarData.updateDate(None, None)
		
		with ui.column().classes("justify-center items-center h-screen w-full pl-[8rem] gap-8"):
			ui.label(self.currentDate)
			with ui.row():
				with ui.column():
					self.eventEntryPanel()
					self.alertsPanel()
				with ui.column():
					ui.textarea(label='Event Description', on_change=onDescriptionChange).props('clearable')
					resultDescription = ui.label()
					self.recurringEventPanel()
			ui.button('Save Event', on_click=onSaveEvent)
		return None
	
	def alertsPanel(self):
		def onToggleChange(event):
			self.pageData.isAlerting = event.value
			if event.value == False:
				self.pageData.selectedAlertCheckboxes.clear()
		
		def onCheck0(event):
			if event.value == True:
				self.pageData.selectedAlertCheckboxes.append(0)
			else:
				self.pageData.selectedAlertCheckboxes.remove(0)
		
		def onCheck1(event):
			if event.value == True:
				self.pageData.selectedAlertCheckboxes.append(1)
			else:
				self.pageData.selectedAlertCheckboxes.remove(1)
		
		def onCheck2(event):
			if event.value == True:
				self.pageData.selectedAlertCheckboxes.append(2)
			else:
				self.pageData.selectedAlertCheckboxes.remove(2)
		
		def onCheck3(event):
			if event.value == True:
				self.pageData.selectedAlertCheckboxes.append(3)
			else:
				self.pageData.selectedAlertCheckboxes.remove(3)
		
		listCheckboxes = ['When it happens', '15 minutes before', '1 hour before', '1 day before']
		
		#toggle
		switch = ui.switch('Set Alerts', on_change=onToggleChange)
		ui.label('Remind me:').bind_visibility_from(switch, 'value')
		checkbox1 = ui.checkbox(listCheckboxes[0], on_change=onCheck0).bind_visibility_from(switch, 'value')
		checkbox2 = ui.checkbox(listCheckboxes[1], on_change=onCheck1).bind_visibility_from(switch, 'value')
		checkbox3 = ui.checkbox(listCheckboxes[2], on_change=onCheck2).bind_visibility_from(switch, 'value')
		checkbox4 = ui.checkbox(listCheckboxes[3], on_change=onCheck3).bind_visibility_from(switch, 'value')
		return None

	def recurringEventPanel(self):
		radio_list = {1:'Every label days', 2:'Every Week', 3:'Every Month', 4:'Every Year'}
		defaultIndex = 2
		
		def onToggleChange(event):
			self.pageData.isRecurringEvent = event.value
			if event.value == False:
				self.pageData.recurringEventOptionIndex = 0
		
		def onRadioChange(event):
			self.pageData.recurringEventOptionIndex = event.value
		
		#toggle
		switch = ui.switch('Set Recurring Event', on_change=onToggleChange)
		ui.label('I want this event to happen:').bind_visibility_from(switch, 'value')
		recurringOptions = ui.radio(radio_list, value=defaultIndex, on_change=onRadioChange).bind_visibility_from(switch, 'value')
		return None

	def eventEntryPanel(self):
		def onStartDateSelect(event):
			self.eventStartData.dateStr = event.value
		
		def onStartTimeSelect(event):
			self.eventStartData.timeStr = event.value
			
		def onEndDateSelect(event):
			self.eventEndData.dateStr = event.value
			
		def onEndTimeSelect(event):
			self.eventEndData.timeStr = event.value
			
		def onEventNameChange(event):
			self.pageData.eventName = event.value
		
		eventName = ui.input(label='Event Name', placeholder='start typing',
		on_change=onEventNameChange,
		validation={'Input too long': lambda value: len(value) < 20})
		with ui.row():
			datePickerLabel("Start Date", onStartDateSelect)
			timePickerLabel("Start Time", onStartTimeSelect)
		with ui.row():
			datePickerLabel("End Date", onEndDateSelect)
			timePickerLabel("End Time", onEndTimeSelect)
		return None

