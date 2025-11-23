from nicegui import ui
from app.components.addedit import datePickerLabel, timePickerLabel
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import ClassVar, List
from app.sharedVars import AddEditEventData, EventDateTime

# TODO: this should be a component, then home.py should create a Calendar object
class AddEditEvent:
	def __init__(self, date, calendarData):
		self.currentDate = date
		self.pageData = AddEditEventData()
		self.eventStartData = EventDateTime()
		self.eventEndData = EventDateTime()
		self.calendarData = calendarData
		self.recurringEndData = EventDateTime()
		self.isCountSelected = False
		return None

	def showPage(self):
		def onDescriptionChange(event):
			self.pageData.eventDescription = event.value
		
		def onSaveEvent(event):
			self.pageData.eventStartDate = self.eventStartData.getDateTimestamp()
			self.pageData.eventEndDate = self.eventEndData.getDateTimestamp()
			if self.isCountSelected == True:
				self.pageData.recurringEndDate = None
			else:
				self.pageData.recurringEndDate = self.recurringEndData.getDateTimestamp()
			print(self.pageData)
			self.calendarData.addData(self.pageData)
			ui.notify('Event data saved!')
		
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
		radio_list = {1:'Days', 2:'Week', 3:'Month', 4:'Year'}
		defaultIndex = 2
		defaultDays = 1
		customDaysInput = None
		self.pageData.recurringEventOptionIndex = defaultIndex
		
		def onToggleChange(event):
			self.pageData.isRecurringEvent = event.value
			if event.value == False:
				self.pageData.recurringEventOptionIndex = 0
		
		def onRadioChange(event):
			self.pageData.recurringEventOptionIndex = event.value
		
		def onCustomDaysChange(event):
			self.pageData.recurringInterval = event.value
		
		def onEndDateSelect(event):
			self.recurringEndData.dateStr = event.value
			
		def onEndTimeSelect(event):
			self.recurringEndData.timeStr = event.value
		
		def onSecondToggleChange(event):
			toggleEndDateCount(event.value)
		
		def toggleEndDateCount(val):
			if val == 1:
				timeLabel.enable()
				dateLabel.enable()
				countInput.disable()
				self.isCountSelected = False
				self.pageData.recurringEndCount = None
			else:
				countInput.enable()
				timeLabel.disable()
				dateLabel.disable()
				self.isCountSelected = True
				self.pageData.recurringEndDate = None
		
		def onCountChange(event):
			self.pageData.recurringEndCount = event.value
		
		#toggle
		switch = ui.switch('Set Recurring Event', on_change=onToggleChange)
		with ui.row():
			with ui.column():
				with ui.row():
					ui.label('I want this event to happen every:').bind_visibility_from(switch, 'value')
					customDaysInput = ui.number(label="Number", on_change=onCustomDaysChange, min=0, step=1, precision=0).bind_visibility_from(switch, 'value').style('margin-top: -35px;')
					recurringOptions = ui.radio(radio_list, value=defaultIndex, on_change=onRadioChange).bind_visibility_from(switch, 'value').style('margin-top: -10px;')
		toggle = ui.toggle({1: 'End At Time', 2: 'End At Count'}, value=1, on_change=onSecondToggleChange).bind_visibility_from(switch, 'value')
		dateLabel = datePickerLabel("Recurring End Date", onEndDateSelect)
		dateLabel.bind_visibility_from(switch, 'value')
		timeLabel = timePickerLabel("Recurring End Time", onEndTimeSelect)
		timeLabel.bind_visibility_from(switch, 'value')
		with ui.row().style('margin-top: 20px;'):
			repeatLabel = ui.label('I want this event to repeat every:').bind_visibility_from(switch, 'value')
			countInput = ui.number(label="Number", on_change=onCountChange, min=0, step=1, precision=0).bind_visibility_from(switch, 'value').style('margin-top: -35px;')
		toggleEndDateCount(1)
		
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

	def validateData(self):
		
		return None
