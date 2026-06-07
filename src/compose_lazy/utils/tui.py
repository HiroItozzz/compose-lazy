"""
compose-lazy TUI prototype using Textual.

Replaces the number-input based interactive_select with a proper TUI.
Supports single select, multiple select, and allow_zero (new entry).

Usage:
    python proto_tui.py
"""
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Label,
    ListView,
    ListItem,
    Button,
    Static,
)
from textual.screen import Screen, ModalScreen
from textual import events
from typing import Callable


# ── Core TUI select widget ────────────────────────────────────────────────────

class SelectScreen(ModalScreen[list[str] | None]):
    """Modal selection screen — replaces interactive_select()."""

    BINDINGS = [
        Binding("q", "quit_cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
        Binding("space", "toggle", "Toggle", show=True),
    ]

    DEFAULT_CSS = """
    SelectScreen {
        align: center middle;
    }

    #dialog {
        width: 70;
        max-height: 30;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #hint {
        color: $text-muted;
        margin-bottom: 1;
        text-style: italic;
    }

    ListView {
        height: auto;
        max-height: 15;
        border: solid $panel;
        margin-bottom: 1;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:focus {
        background: $primary 30%;
    }

    ListItem.selected {
        background: $primary 50%;
        color: $text;
    }

    ListItem.selected Label {
        text-style: bold;
    }

    #new-entry-hint {
        color: $warning;
        margin-bottom: 1;
    }

    #buttons {
        height: 3;
        align: right middle;
        margin-top: 1;
    }

    Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        title: str,
        candidates: list[str],
        multiple: bool = False,
        allow_zero: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._candidates = candidates
        self._multiple = multiple
        self._allow_zero = allow_zero
        self._selected: set[int] = set()

    def compose(self) -> ComposeResult:
        count = len(self._candidates)
        plural = "s" if count != 1 else ""
        with Vertical(id="dialog"):
            yield Label(self._title, id="title")
            hint = "Space to toggle, Enter to confirm" if self._multiple else "Enter to select"
            yield Label(f"☑ Found {count} item{plural}  ·  {hint}", id="hint")
            with ListView(id="list"):
                for candidate in self._candidates:
                    yield ListItem(Label(f"  {candidate}"), name=candidate)
            if self._allow_zero:
                yield Label(" ── Or press 0 to create a new entry", id="new-entry-hint")
            with Horizontal(id="buttons"):
                yield Button("Confirm", variant="primary", id="confirm")
                yield Button("Cancel", variant="default", id="cancel")

    def on_key(self, event: events.Key) -> None:
        if event.key == "0" and self._allow_zero:
            self.dismiss(None)
            event.stop()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Single-select mode: immediately confirm on click/enter."""
        if not self._multiple:
            idx = self._candidates.index(event.item.name)  # type: ignore
            self.dismiss([self._candidates[idx]])

    def action_toggle(self) -> None:
        """Multiple-select mode: toggle highlight."""
        if not self._multiple:
            return
        lv = self.query_one(ListView)
        if lv.highlighted_child is None:
            return
        item = lv.highlighted_child
        idx = self._candidates.index(item.name)  # type: ignore
        if idx in self._selected:
            self._selected.discard(idx)
            item.remove_class("selected")
            item.query_one(Label).update(f"  {self._candidates[idx]}")
        else:
            self._selected.add(idx)
            item.add_class("selected")
            item.query_one(Label).update(f"✔ {self._candidates[idx]}")

    def action_confirm(self) -> None:
        if self._multiple:
            if not self._selected:
                return
            result = [self._candidates[i] for i in sorted(self._selected)]
            self.dismiss(result)
        else:
            lv = self.query_one(ListView)
            if lv.highlighted_child is None:
                return
            idx = self._candidates.index(lv.highlighted_child.name)  # type: ignore
            self.dismiss([self._candidates[idx]])

    def action_quit_cancel(self) -> None:
        self.dismiss([])  # empty list = cancelled

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.action_confirm()
        elif event.button.id == "cancel":
            self.action_quit_cancel()


# ── Demo App ──────────────────────────────────────────────────────────────────

class DemoApp(App):
    """Demo that simulates the ws exec flow."""

    CSS = """
    Screen {
        background: $background;
    }

    #log {
        height: 1fr;
        border: solid $panel;
        padding: 1 2;
        margin: 1 2;
        overflow-y: auto;
    }

    #actions {
        height: auto;
        padding: 1 2;
        align: left middle;
    }

    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    WORKSPACES = ["myproject", "infra", "staging"]
    REPOS = {
        "myproject": [
            "/home/hiro/dev/projects/fast-dcp",
            "/home/hiro/dev/projects/trail-condition-portal",
        ]
    }
    SERVICES = ["app", "db", "nginx"]

    def on_mount(self) -> None:
        self._log_lines: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="log")
        with Horizontal(id="actions"):
            yield Button("ws up (single select)", id="btn-single", variant="primary")
            yield Button("ws build (multi select)", id="btn-multi", variant="success")
            yield Button("ws register (allow_zero)", id="btn-zero", variant="warning")
            yield Button("ws exec (chained)", id="btn-exec", variant="error")
        yield Footer()

    def log_line(self, text: str) -> None:
        self._log_lines.append(text)
        log = self.query_one("#log", Static)
        log.update("\n".join(self._log_lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-single":
            self._demo_single()
        elif event.button.id == "btn-multi":
            self._demo_multi()
        elif event.button.id == "btn-zero":
            self._demo_zero()
        elif event.button.id == "btn-exec":
            self._demo_exec_chain()

    # ── single select: ws up ──
    def _demo_single(self) -> None:
        def on_result(result: list[str] | None) -> None:
            if not result:
                self.log_line("Cancelled.")
                return
            self.log_line(f"▷ Executing `docker compose up -d` in workspace: {result[0]}")

        self.push_screen(
            SelectScreen("Select workspace", self.WORKSPACES, multiple=False),
            on_result,
        )

    # ── multiple select: ws build ──
    def _demo_multi(self) -> None:
        files = ["docker-compose.yml", "docker-compose.prod.yml", "docker-compose.staging.yml"]

        def on_result(result: list[str] | None) -> None:
            if not result:
                self.log_line("Cancelled.")
                return
            self.log_line(f"▷ Selected compose files: {', '.join(result)}")

        self.push_screen(
            SelectScreen("Select compose files", files, multiple=True),
            on_result,
        )

    # ── allow_zero: ws register ──
    def _demo_zero(self) -> None:
        def on_result(result: list[str] | None) -> None:
            if result is None:
                ws_name = "new-workspace"  # in real: input()
                self.log_line(f"▷ Creating new workspace: {ws_name}")
            elif not result:
                self.log_line("Cancelled.")
            else:
                self.log_line(f"▷ Registering to workspace: {result[0]}")

        self.push_screen(
            SelectScreen("Select workspace", self.WORKSPACES, multiple=False, allow_zero=True),
            on_result,
        )

    # ── chained selects: ws exec ──
    def _demo_exec_chain(self) -> None:
        repos = self.REPOS["myproject"]

        def on_repo_selected(result: list[str] | None) -> None:
            if not result:
                self.log_line("Cancelled.")
                return
            repo = result[0]
            self.log_line(f"  repo: {repo}")

            def on_service_selected(svc_result: list[str] | None) -> None:
                if not svc_result:
                    self.log_line("Cancelled.")
                    return
                svc = svc_result[0]
                self.log_line(f"▷ docker compose exec {svc} bash  (in {repo.split('/')[-1]})")

            self.push_screen(
                SelectScreen(f"Select service in {repo.split('/')[-1]}", self.SERVICES, multiple=False),
                on_service_selected,
            )

        self.push_screen(
            SelectScreen("Select repository", repos, multiple=False),
            on_repo_selected,
        )


if __name__ == "__main__":
    DemoApp().run()