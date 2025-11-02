from nicegui import ui

class UploadSchedule:
    def __init__(self):
        self.upload_id = "upload_button"

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
            ).props(f'accept=".png,.jpg,.jpeg" id="{self.upload_id}"').style("opacity: 0; width: 0; height: 0; position: absolute;")


            ui.label("Upload Schedule").classes(
                "text-4xl font-bold text-gray-800 mb-4"
            )

           
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

            ui.button("Process Schedule").classes(
                "bg-gray-300 hover:bg-gray-400 text-black font-medium "
                "px-6 py-2 rounded"
            )
