from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDateEdit, QDialogButtonBox
from datetime import datetime

class DateInputDialog(QDialog):
    def __init__(self, parent=None):
        super(DateInputDialog, self).__init__(parent)

        self.setWindowTitle("Ввод даты")

        layout = QVBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(datetime.now().date())

        layout.addWidget(QLabel("Введите дату:"))
        layout.addWidget(self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")