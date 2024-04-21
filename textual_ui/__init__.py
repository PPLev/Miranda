from .main_page import UI

app = UI()

async def run_ui():
    await app.run_async()
