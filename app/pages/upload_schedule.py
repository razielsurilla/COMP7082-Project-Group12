from nicegui import events, ui, app
import asyncio
import os
from llmmodule import pipeline
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
from app.components.schedule_event import ScheduleEvent, UploadedEventDataFrame

UPLOAD_DIRECTORY = "uploaded_schedule_files"

class UploadSchedule:
    def __init__(self):
        self.upload_id = "upload_button"
        self.uploaded_file = None
        self.uploaded_file_name = None
        self.upload_component = None
        self.card_container = None
        self.results_container = None
        self.title_label = None
        self.process_button = None
        self.event_components = []

    async def on_save_clicked(self, e=None):
        all_data = [comp.get_data() for comp in self.event_components]
        print("Collected:", all_data)
        
        sql_db = Sql()
        calendar_data = CalendarData(sql_db)

        calendar_data.buildData()

        for item in all_data:
            df = UploadedEventDataFrame(
                name=item["event_name"],
                day=item["day_of_the_week"],
                desc=item["desc"],
            )
            calendar_data.addData(df)

        sql_db.conn.commit()
        sql_db.terminate()
        
        ui.notify("Saved schedule to database!", color="green", position="bottom-right")

        await asyncio.sleep(1.0)

        ui.navigate.to("/")        

    async def process_file(self):
        self.card_container.clear()
        with self.card_container:
            with ui.row().classes(
                "items-center justify-center w-80 h-32 border rounded-lg border-gray-300 bg-gray-50"
            ):
                ui.spinner(size="lg", color="primary")
                ui.label("Processing file...").classes("text-lg font-semibold text-gray-700 ml-2")

        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        await asyncio.sleep(0.1)

        filename = self.uploaded_file.name
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(file_path, "wb") as file:
            file.write(await self.uploaded_file.read())

        name, extension = os.path.splitext(filename)
        extension = extension.replace(".", "")

        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(
                None, pipeline.process_image_to_json, file_path, extension
            )
            self.render_results(results)

        except Exception as e:
            print(f"processing error: {e}")
            self.card_container.clear()
            with self.card_container:
                ui.label("Processing failed.").classes("text-red-600 text-md font-medium")

    def render_results(self, events):
        self.title_label.visible = False
        self.card_container.visible = False
        if self.process_button:
            self.process_button.visible = False

        self.results_container.clear()
        if not events:
            with self.results_container:
                ui.label("No schedule events found. Please upload a file first.").classes(
                    "text-gray-600 text-lg"
                )
            return

        with self.results_container:
            ui.label("Detected Schedule Events").classes(
                "text-3xl font-bold text-gray-800 mb-6"
            )

            with ui.scroll_area().classes("w-full h-[70vh]"):
                self.event_components = []
                with ui.grid().classes(
                    "gap-6 grid-cols-1 md:grid-cols-2 w-full max-w-5xl mx-auto"
                ):
                    for ev in events:
                        comp = ScheduleEvent(ev)
                        self.event_components.append(comp)
                        comp.render()

            with ui.row().classes(
                "bg-green-500 text-white rounded-full w-10 h-10 mt-4 flex items-center justify-center cursor-pointer"
            ).on("click", self.on_save_clicked):
                ui.icon("check").classes("text-xl")

    def handle_upload(self, e: events.UploadEventArguments):
        file = e.file
        self.uploaded_file = file
        self.uploaded_file_name = file.name

        ui.run_javascript(
            f'document.querySelector("#{self.upload_id} input[type=file]").value = ""'
        )
        self.update_display()

    def remove_file(self):
        self.uploaded_file = None
        self.uploaded_file_name = None
        self.update_display()

    def update_display(self):
        self.card_container.clear()
        with self.card_container:
            if self.uploaded_file_name:
                with ui.row().classes(
                    "flex items-center justify-between w-80 p-3 gap-3 border rounded-lg border-gray-400 bg-gray-50"
                ):
                    ui.icon("image").classes("text-gray-700 text-2xl flex-shrink-0")
                    ui.label(self.uploaded_file_name).classes(
                        "truncate text-base font-medium flex-1 overflow-hidden text-ellipsis whitespace-nowrap"
                    )
                    ui.icon("close").classes(
                        "cursor-pointer text-gray-800 text-2xl flex-shrink-0"
                    ).on("click", self.remove_file)
            else:
                with ui.card().classes(
                    "w-96 h-48 flex flex-col items-center justify-center border-2 "
                    "border-dashed border-gray-400 bg-gray-50 hover:bg-gray-100 "
                    "transition-all cursor-pointer text-center"
                ).on(
                    "click",
                    lambda: ui.run_javascript(
                        f'document.querySelector("#{self.upload_id} input[type=file]").click()'
                    ),
                ):
                    ui.icon("cloud_upload").classes("text-5xl text-gray-500 mb-2")
                    ui.label("Click to upload photo").classes(
                        "text-md font-semibold text-gray-700"
                    )
                    ui.label("(Max 128 MB, .PNG, .JPG, .JPEG)").classes(
                        "text-sm text-gray-500"
                    )

    def show(self):
        with ui.column().classes(
            "justify-center items-center h-screen w-full pl-[8rem] gap-8"
        ):
            ui.upload(
                label="",
                auto_upload=True,
                on_upload=self.handle_upload,
            ).props(
                f'accept=".png,.jpg,.jpeg" id="{self.upload_id}"'
            ).style(
                "opacity: 0; width: 0; height: 0; position: absolute;"
            )

            self.title_label = ui.label("Upload Schedule").classes(
                "text-4xl font-bold text-gray-800 mb-4"
            )

            self.card_container = ui.column()
            self.results_container = ui.column().classes("w-full mt-8")

            self.update_display()

            self.process_button = ui.button("Process Schedule").classes(
                "bg-gray-300 hover:bg-gray-400 text-black font-medium px-6 py-2 rounded"
            ).on("click", self.process_file)
