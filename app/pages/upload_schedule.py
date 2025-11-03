from nicegui import events,  ui
import asyncio
import os

UPLOAD_DIRECTORY =  "uploaded_schedule_files"

class UploadSchedule:
    def __init__(self):
        self.upload_id = "upload_button"
        self.uploaded_file = None
        self.uploaded_file_name = None
        self.upload_component = None
        self.card_container = None

    async def process_file(self):
        self.card_container.clear()
        with self.card_container:
            with ui.row().classes(
                "items-center justify-center w-80 h-32 border rounded-lg border-gray-300 bg-gray-50"
            ):
                ui.spinner(size="lg", color="primary")
                ui.label("Processing file...").classes("text-lg font-semibold text-gray-700 ml-2")        

        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)       

        await asyncio.sleep(0.5)
        
        filename = self.uploaded_file.name
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(file_path, "wb") as file:
            file.write(await self.uploaded_file.read())

        print(filename)

        # replace this. should move to new page with the new events
        self.update_display()

    # this should be done one process button click
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
                    ui.icon("close").classes("cursor-pointer text-gray-800 text-2xl flex-shrink-0").on("click", self.remove_file)
            else:
                with ui.card().classes(
                    "w-96 h-48 flex flex-col items-center justify-center border-2 "
                    "border-dashed border-gray-400 bg-gray-50 hover:bg-gray-100 "
                    "transition-all cursor-pointer text-center"
                ).on(
                     "click",
    
                     # workaround cause there is no function in nicegui (that i could i find) for local file uploads.
                     # file uploads must be implemented for each operating system:
                     #     https://github.com/zauberzeug/nicegui/blob/main/examples/local_file_picker/local_file_picker.py
                     #
                     # we query the html for the nested <input> element of the nicegui upload component
                     # we then call the click() function on it, to simulate the user clicking on it to upload their file
                         # and from there, the user can upload their file as if they had clicked on the invisible nicegui upload component
                     #
                     # TL;DR this is workaround, don't touch this please
                    lambda: ui.run_javascript(f'document.querySelector("#{self.upload_id} input[type=file]").click()')
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
            # we make this invisible on the html, since we only need it for the upload functionality
            # the user will never directly use it (interact with it) to upload their file
            # the user should never see this
            ui.upload(
                label="",
                auto_upload=True,
                on_upload=self.handle_upload,
            ).props(f'accept=".png,.jpg,.jpeg" id="{self.upload_id}"').style("opacity: 0; width: 0; height: 0; position: absolute;")


            ui.label("Upload Schedule").classes(
                "text-4xl font-bold text-gray-800 mb-4"
            )

            self.card_container = ui.column()
            self.update_display()           

            ui.button("Process Schedule").classes(
                "bg-gray-300 hover:bg-gray-400 text-black font-medium "
                "px-6 py-2 rounded"
            ).on("click", self.process_file)
