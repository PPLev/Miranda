import os

from textual import binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual import widgets, on
from core import Core


def get_plugins_manifests():
    return {
        plugin_name: Core.get_manifest(plugin_name)
        for plugin_name in os.listdir("plugins") if not plugin_name.startswith("_")
    }


class PluginList(widgets.Static):
    def compose(self) -> ComposeResult:
        self.table = widgets.DataTable()
        yield self.table

    def on_mount(self) -> None:
        plugin_rows = [
            (name, manifest["name"], manifest["version"])
            for name, manifest in get_plugins_manifests().items()
        ]
        rows = [("Name", "Description", "Ver", "Staut")]
        rows.extend(plugin_rows)
        self.table.add_columns(*rows[0])
        self.table.add_rows(rows[1:])


class Plugins(Screen):
    BINDINGS = [
        binding.Binding(key="escape", action="app.pop_screen", description="Back")
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield widgets.Footer()
        self.name_layout = PluginList("PluginList", classes="box")
        yield self.name_layout