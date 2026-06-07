from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Input, Button, DataTable, Label
from textual.binding import Binding

class Task:
    def __init__(self, title: str):
        self.title = title
        self.created_at = datetime.now()
        self.completed = False

    def toggle_complete(self):
        self.completed = not self.completed

class TaskManagerApp(App):
    """シンプルなタスク管理アプリ"""
    
    BINDINGS = [
        Binding("q", "quit", "終了"),
        Binding("a", "add_task", "タスク追加"), 
        Binding("d", "delete_task", "タスク削除"),
        Binding("space", "toggle_task", "完了切替"),
    ]
    
    def __init__(self):
        super().__init__()
        self.tasks = []
    
    def compose(self) -> ComposeResult:
        """UIの構成"""
        yield Header()
        
        # 入力部分
        yield Label("新しいタスクを追加")
        yield Input(placeholder="タスクのタイトルを入力...", id="task-input")
        with Horizontal():
            yield Button("追加", id="add-btn", variant="primary")
            yield Button("削除", id="delete-btn", variant="error")
            yield Button("完了切替", id="toggle-btn", variant="success")
        
        # タスク一覧
        yield Label("タスク一覧")
        yield DataTable(id="task-table")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """アプリ起動時の初期化"""
        table = self.query_one("#task-table", DataTable)
        table.add_columns("ID", "タイトル", "作成日時", "状態")
        table.cursor_type = "row"
        
        # サンプルタスクを追加
        self.add_sample_tasks()
    
    def add_sample_tasks(self):
        """サンプルタスクの追加"""
        sample_tasks = ["Textualの勉強", "Qiita記事を書く", "コードのリファクタリング"]
        
        for task_title in sample_tasks:
            task = Task(task_title)
            self.tasks.append(task)
        
        self.refresh_task_table()
    
    def refresh_task_table(self):
        """タスクテーブルの更新"""
        table = self.query_one("#task-table", DataTable)
        table.clear()
        
        for i, task in enumerate(self.tasks):
            status = "✅ 完了" if task.completed else "⏳ 未完了"
            created_time = task.created_at.strftime("%m/%d %H:%M")
            
            table.add_row(
                str(i + 1),
                task.title, 
                created_time,
                status,
                key=str(i)
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ボタンクリック時の処理"""
        if event.button.id == "add-btn":
            self.action_add_task()
        elif event.button.id == "delete-btn":
            self.action_delete_task()
        elif event.button.id == "toggle-btn":
            self.action_toggle_task()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """入力フィールドでEnterが押された時"""
        if event.input.id == "task-input":
            self.action_add_task()
    
    def action_add_task(self) -> None:
        """タスクの追加"""
        task_input = self.query_one("#task-input", Input)
        title = task_input.value.strip()
        
        if title:
            task = Task(title)
            self.tasks.append(task)
            task_input.value = ""
            self.refresh_task_table()
            self.notify(f"タスク '{title}' を追加しました")
    
    def action_delete_task(self) -> None:
        """選択されたタスクの削除"""
        table = self.query_one("#task-table", DataTable)
        
        if table.cursor_row is not None and self.tasks:
            task_index = table.cursor_row
            if 0 <= task_index < len(self.tasks):
                deleted_task = self.tasks.pop(task_index)
                self.refresh_task_table()
                self.notify(f"タスク '{deleted_task.title}' を削除しました")
    
    def action_toggle_task(self) -> None:
        """選択されたタスクの完了状態を切り替え"""
        table = self.query_one("#task-table", DataTable)
        
        if table.cursor_row is not None and self.tasks:
            task_index = table.cursor_row
            if 0 <= task_index < len(self.tasks):
                task = self.tasks[task_index]
                task.toggle_complete()
                self.refresh_task_table()
                status = "完了" if task.completed else "未完了"
                self.notify(f"タスク '{task.title}' を{status}にしました")

if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()
