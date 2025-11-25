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
		
		#elements
		self.eventName = None
		self.eventDesc = None
		self.eventStartDate = None
		self.eventEndDate = None
		self.eventStartTime = None
		self.eventEndTime = None
		
		self.recurringToggle = None
		self.recurringInterval = None
		self.recurringCountToggle = None
		self.recurringEndDate = None
		self.recurringEndTime = None
		self.recurringCount = None
		
		self.alertsToggle = None
		
		return None

	def showPage(self):
		def onDescriptionChange(event):
			self.pageData.eventDescription = event.value
		
		def onSaveEvent(event):
			if self.eventStartDate.validation == None:
				self.eventStartDate.without_auto_validation()
				self.eventStartDate.validation = self.validateDate
			
			if self.eventStartTime.validation == None:
				self.eventStartTime.without_auto_validation()
				self.eventStartTime.validation = self.validateTime
				
			if self.eventEndDate.validation == None:
				self.eventEndDate.without_auto_validation()
				self.eventEndDate.validation = self.validateDate
			
			if self.eventEndTime.validation == None:
				self.eventEndTime.without_auto_validation()
				self.eventEndTime.validation = self.validateTime
				
			if self.recurringEndDate.validation == None:
				self.recurringEndDate.without_auto_validation()
				self.recurringEndDate.validation = self.validateDate
			
			if self.recurringEndTime.validation == None:
				self.recurringEndTime.without_auto_validation()
				self.recurringEndTime.validation = self.validateTime
			
			validationPassMain = False;
			validationPassRecurring1 = False;
			validationPassRecurring2 = False;
			
			# to prevent short-circuit-eval
			if all([self.eventName.validate(), self.eventStartDate.validate(),  self.eventEndDate.validate()]):
				validationPassMain = True
			
			if self.recurringToggle.value:
				validationPassRecurring1 = self.recurringInterval.validate()
				
				if self.recurringCountToggle.value == 1:
					if all([self.recurringEndDate.validate(), self.recurringEndTime.validate()]):
						validationPassRecurring2 = True;
				elif self.recurringCountToggle.value == 2:
					validationPassRecurring2 = self.recurringCount.validate()
				
			if not all([validationPassMain, validationPassRecurring1, validationPassRecurring2]):
				ui.notify('Event data incorrect!')
			else:
				ui.notify('Event data saved!')
				self.pageData.eventStartDate = self.eventStartData.getDateTimestamp()
				self.pageData.eventEndDate = self.eventEndData.getDateTimestamp()
				if self.isCountSelected == True:
					self.pageData.recurringEndDate = None
				else:
					self.pageData.recurringEndDate = self.recurringEndData.getDateTimestamp()
				print(self.pageData)
				self.calendarData.addData(self.pageData)
		
		with ui.column().classes("justify-center items-center h-screen w-full pl-[8rem] gap-8"):
			ui.label(self.currentDate)
			with ui.row():
				with ui.column():
					self.eventEntryPanel()
					self.alertsPanel()
				with ui.column():
					self.eventDesc = ui.textarea(label='Event Description', on_change=onDescriptionChange).props('clearable')
					resultDescription = ui.label()
					self.recurringEventPanel()
			ui.button('Save Event', on_click=onSaveEvent)
		return None
	
	def alertsPanel(self):
		def onRecurringToggleChange(event):
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
		self.alertsToggle = ui.switch('Set Alerts', on_change=onRecurringToggleChange)
		ui.label('Remind me:').bind_visibility_from(self.alertsToggle, 'value')
		checkbox1 = ui.checkbox(listCheckboxes[0], on_change=onCheck0).bind_visibility_from(self.alertsToggle, 'value')
		checkbox2 = ui.checkbox(listCheckboxes[1], on_change=onCheck1).bind_visibility_from(self.alertsToggle, 'value')
		checkbox3 = ui.checkbox(listCheckboxes[2], on_change=onCheck2).bind_visibility_from(self.alertsToggle, 'value')
		checkbox4 = ui.checkbox(listCheckboxes[3], on_change=onCheck3).bind_visibility_from(self.alertsToggle, 'value')
		return None

	def recurringEventPanel(self):
		radio_list = {1:'Days', 2:'Week', 3:'Month', 4:'Year'}
		defaultIndex = 2
		defaultDays = 1
		self.pageData.recurringEventOptionIndex = defaultIndex
		
		def onRecurringToggleChange(event):
			self.pageData.isRecurringEvent = event.value
			if event.value == False:
				self.pageData.recurringEventOptionIndex = 0
		
		def onRadioChange(event):
			self.pageData.recurringEventOptionIndex = event.value
		
		def onRecurringIntervalChange(event):
			self.recurringInterval.error = None
			self.pageData.recurringInterval = event.value
		
		def onEndDateSelect(event):
			self.recurringEndDate.error = None
			self.recurringEndData.dateStr = event.value
			
		def onEndTimeSelect(event):
			self.recurringEndTime.error = None
			self.recurringEndData.timeStr = event.value
		
		def onRecurringCountToggleChange(event):
			self.recurringCountToggle.error = None
			toggleEndDateCount(event.value)
		
		def toggleEndDateCount(val):
			if val == 1:
				self.recurringEndTime.enable()
				self.recurringEndDate.enable()
				self.recurringCount.disable()
				self.isCountSelected = False
				self.pageData.recurringEndCount = None
			else:
				self.recurringCount.enable()
				self.recurringEndTime.disable()
				self.recurringEndDate.disable()
				self.isCountSelected = True
				self.pageData.recurringEndDate = None
		
		def onRecurringCountChange(event):
			self.pageData.recurringEndCount = event.value
		
		#toggle
		self.recurringToggle = ui.switch('Set Recurring Event', on_change=onRecurringToggleChange)
		with ui.row():
			with ui.column():
				with ui.row():
					ui.label('I want this event to happen every:').bind_visibility_from(self.recurringToggle, 'value')
					self.recurringInterval = ui.number(label="Number", on_change=onRecurringIntervalChange, validation=self.validateRecurringInterval, min=0, step=1, precision=0).bind_visibility_from(self.recurringToggle, 'value').style('margin-top: -35px;').without_auto_validation()
					recurringOptions = ui.radio(radio_list, value=defaultIndex, on_change=onRadioChange).bind_visibility_from(self.recurringToggle, 'value').style('margin-top: -10px;')
		self.recurringCountToggle = ui.toggle({1: 'End At Time', 2: 'End At Count'}, value=1, on_change=onRecurringCountToggleChange).bind_visibility_from(self.recurringToggle, 'value')
		self.recurringEndDate = datePickerLabel("Recurring End Date", onEndDateSelect)
		self.recurringEndDate.bind_visibility_from(self.recurringToggle, 'value')
		self.recurringEndTime = timePickerLabel("Recurring End Time", onEndTimeSelect)
		self.recurringEndTime.bind_visibility_from(self.recurringToggle, 'value')
		with ui.row().style('margin-top: 20px;'):
			repeatLabel = ui.label('I want this event to repeat every:').bind_visibility_from(self.recurringToggle, 'value')
			self.recurringCount = ui.number(label="Number", on_change=onRecurringCountChange, validation=self.validateRecurringInterval, min=0, step=1, precision=0).bind_visibility_from(self.recurringToggle, 'value').style('margin-top: -35px;').without_auto_validation()
		toggleEndDateCount(1)
		
		return None

	def eventEntryPanel(self):
		def onStartDateSelect(event):
			self.eventStartDate.error = None
			self.eventStartData.dateStr = event.value
		
		def onStartTimeSelect(event):
			self.eventStartTime.error = None
			self.eventStartData.timeStr = event.value
			
		def onEndDateSelect(event):
			self.eventEndDate.error = None
			self.eventEndData.dateStr = event.value
			
		def onEndTimeSelect(event):
			self.eventEndTime.error = None
			self.eventEndData.timeStr = event.value
			
		def onEventNameChange(event):
			self.eventName.error = None
			self.pageData.eventName = event.value
		
		self.eventName = ui.input(label='Event Name', on_change=onEventNameChange, validation=self.validateName).without_auto_validation()
		with ui.row():
			self.eventStartDate = datePickerLabel("Start Date", onStartDateSelect)
			self.eventStartTime = timePickerLabel("Start Time", onStartTimeSelect)
			
		with ui.row():
			self.eventEndDate = datePickerLabel("End Date", onEndDateSelect)
			self.eventEndTime = timePickerLabel("End Time", onEndTimeSelect)
		return None
	
	def validateName(self, value):
		if len(value) < 1:
			return "Please add a meaningful name."
		return None
		
	def validateDate(self, value):
		if len(value) < 1:
			return "Please add valid date."
		return None
	
	def validateTime(self, value):
		if len(value) < 1:
			return "Please add valid time."
		return None
	
	def validateRecurringInterval(self, value):
		if value == None or value < 1:
			return "Please add interval value."
		return None

