from textual.app import App, ComposeResult
from textual import widgets, binding
from .options_screen import Options
from .plugins_screen import Plugins


class UI(App):
    SCREENS = {
        "options": Options(),
        "plugins": Plugins(),
    }
    BINDINGS = [binding.Binding(key="ctrl+q", action="quit", description="Exit")]

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield widgets.Footer()
        yield widgets.Button("Опции", id="options")
        yield widgets.Button("Плагины", id="plugins")

    def on_mount(self) -> None:
        self.title = "Настройки Лизы"

    def on_button_pressed(self, event: widgets.Button.Pressed) -> None:
        self.push_screen(event.button.id)
