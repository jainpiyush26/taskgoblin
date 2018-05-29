from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import re
import sys
from resources import resources
from authentication import authentication_module
from collections import defaultdict

class CustomListWidget(QWidget):
    def __init__(self, task_title, task_uid, task_list_uid, task_status, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.task_title = task_title
        self._tasklist_uid = task_list_uid
        self.parent = parent
        self.widget_layout = QFormLayout()
        self._status = task_status
        self._uid = task_uid
        self.setObjectName(str(self._uid)

        self.checkbox_completion = QCheckBox()
        self.checkbox_completion.clicked.connect(lambda: self.toggle_status_change(self.checkbox_completion.isChecked()))
        self.checkbox_completion.setToolTip("click this to complete task!")

        self.task_title_textedit = QTextEdit()
        self.task_title_textedit.textChanged.connect(self.update_task_button)
        self.task_title_textedit.setMaximumHeight(50)

        self.update_task_text_button = QPushButton()
        self.update_task_text_button.setText("Update")
        self.update_task_text_button.setIcon(QIcon(":/Images/assets/images/update.png"))
        self.update_task_text_button.setFixedHeight(24)
        self.update_task_text_button.setEnabled(False)
        self.update_task_text_button.clicked.connect(self.update_tasks_gtasks)

        self.spacer_item = QSpacerItem(100, 10, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Fixed)

        self.button_layout = QHBoxLayout()
        self.button_layout.addItem(self.spacer_item)
        self.button_layout.addWidget(self.update_task_text_button)
        self.widget_layout.addRow(self.checkbox_completion, self.task_title_textedit)
        self.widget_layout.addRow(self.button_layout)

        self.setLayout(self.widget_layout)
        self.init_task()

    def update_task_button(self):
        if str(self.task_title_textedit.toPlainText()) != self.task_title:
            self.update_task_text_button.setEnabled(True)
        else:
            self.update_task_text_button.setEnabled(False)

    def init_task(self):
        self.task_title_textedit.setText(self.task_title)
        if self._status == "completed":
            self.checkbox_completion.setChecked(True)
            self.change_status_appearance()
        else:
            self.checkbox_completion.setChecked(False)
            self.change_status_appearance()

    def change_status_appearance(self):
        if self._status == "completed":
            self.task_title_textedit.setStyleSheet("""text-decoration: line-through;
            font-style: italic;
            color: gray""")
        else:
            self.task_title_textedit.setStyleSheet("""text-decoration:;
            font-style: normal;
            color: white""")

    @property
    def status(self):
        return self._status

    @property
    def uid(self):
        return self._uid

    @property
    def tasklist_uid(self):
        return self._tasklist_uid

    def update_tasks_gtasks(self):
        task_body = {"title": str(self.task_title_textedit.toPlainText()),
                     "status": self.status,
                     "id": self._uid}
        service_obj = authentication_module.setup_authentication()
        service_obj.tasks().update(tasklist=self._tasklist_uid, task=self._uid, body=task_body).execute()
        self.update_task_text_button.setEnabled(False)

    def toggle_status_change(self, check_status):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if not check_status:
                self._status = "needsAction"
                self.change_status_appearance()
            else:
                self._status = "completed"
                self.change_status_appearance()
            self.update_tasks_gtasks()
        except:
            print("You got errors!")
        QApplication.restoreOverrideCursor()

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Return:
            if self.update_task_text_button.isEnabled():
                self.update_tasks_gtasks()


class ListWidgetObject(QListWidget):
    def __init__(self, task_list_collection, tasklist_id,  parent=None):
        super(ListWidgetObject, self).__init__(parent)
        self.tasklist_id = tasklist_id
        self.task_list_collection = task_list_collection
        self.init_listwidget_items()
        self.parent = parent
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def sorted_task_list_items(self):
        position_aware_items = {}
        for task_item_key, task_item_values in self.task_list_collection["task_items"].items():
            position_aware_items[task_item_values['position']] = {"task_item_key": task_item_key,
                                                                  "task_item_value": task_item_values}
        return position_aware_items

    def init_listwidget_items(self):
        position_aware_dict = self.sorted_task_list_items(self.task_list_collection["task_items"])
        for position, position_values in sorted(position_aware_dict.items()):
            list_item_object = CustomListWidget(task_title=position_values.get("task_item_value")['title'],
                                                task_uid=position_values.get("task_item_key"),
                                                task_list_uid=self.tasklist_id,
                                                task_status=position_values.get("task_item_value")['status'])

            insert_widget_item = QListWidgetItem(self)
            insert_widget_item.setSizeHint(list_item_object.sizeHint())
            self.addItem(insert_widget_item)
            self.setItemWidget(insert_widget_item, list_item_object)
            self.parent.tasks_collection[list_item_object.objectName()] =

class TaskGoblin(QWidget):
    def __init__(self, parent=None):
        super(TaskGoblin, self).__init__(parent)
        # App basics
        self.setWindowTitle("TaskGoblin")
        self.goblin_icon = QIcon(":/Images/assets/images/icon.png")
        self.setWindowIcon(self.goblin_icon)
        self.setWhatsThis("""This links to your google tasks and uses the google 
        API to give you and easy windows desktop!""")

        self.task_list_items = defaultdict(dict)
        self.task_list_objects = {}
        self.service_object = None
        # Create the authentication module..
        self.setup_authentication()

        self.available_window_size = QDesktopWidget().availableGeometry()
        self.screen_window_size = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, 450, 550)
        widget = self.geometry()
        x = self.available_window_size.width() - widget.width() - 15
        y = 2 * self.available_window_size.height() - self.screen_window_size.height() - widget.height()
        self.move(x, y)

        self.main_layout = QVBoxLayout()

        self.add_pushbutton = QPushButton(self)
        self.add_pushbutton.setIcon(QIcon(":/Images/assets/images/plus.png"))
        self.add_pushbutton.setStyleSheet("border:None")
        self.add_pushbutton.setMaximumSize(30, 30)
        self.add_pushbutton.clicked.connect(self.insert_tasks)

        self.clear_completed_pushbutton = QPushButton(self)
        self.clear_completed_pushbutton.setIcon(QIcon(":/Images/assets/images/completed.png"))
        self.clear_completed_pushbutton.setMaximumSize(30, 30)
        self.clear_completed_pushbutton.setStyleSheet("border:None")

        self.button_spacer = QSpacerItem(100, 30, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Fixed)
        self.pushbutton_layout = QHBoxLayout()
        self.pushbutton_layout.addWidget(self.add_pushbutton)
        self.pushbutton_layout.addWidget(self.clear_completed_pushbutton)
        self.pushbutton_layout.addItem(self.button_spacer)

        self.tasks_tab_widget = QTabWidget(self)
        self.tasks_tab_widget.setMovable(True)

        self.main_layout.addWidget(self.tasks_tab_widget)
        self.main_layout.addLayout(self.pushbutton_layout)

        self.setLayout(self.main_layout)

        # Populating the task lists
        self.populate_task_list()

        # Setting up the systemtrayicon
        self.tray_menu = QMenu()
        restore_action = self.tray_menu.addAction("Restore")
        restore_action.triggered.connect(self.restore_task_goblin)
        close_action = self.tray_menu.addAction("Exit")
        close_action.triggered.connect(sys.exit)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.goblin_icon)
        self.tray.setContextMenu(self.tray_menu)

        self.window_state = QSettings("PJ", "TaskGoblin")

    def restore_task_goblin(self):
        self.showNormal()
        self.tray.hide()

    def insert_tasks(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        current_tab = self.tasks_tab_widget.currentWidget()
        service = authentication_module.setup_authentication()
        new_task_object = {"title": ""}
        new_task_item = service.tasks().insert(tasklist=current_tab.tasklist_id, body=new_task_object).execute()
        new_listwidget_item = QListWidgetItem()
        list_item_object = CustomListWidget(task_title=new_task_item.get('title'), task_uid=new_task_item.get('id'),
                                            task_list_uid=current_tab.tasklist_id, task_status="needsAction")
        new_listwidget_item.setSizeHint(list_item_object.sizeHint())
        current_tab.insertItem(0, new_listwidget_item)
        current_tab.setItemWidget(new_listwidget_item, list_item_object)

        QApplication.restoreOverrideCursor()

    def setup_authentication(self):
        self.service = authentication_module.setup_authentication()
        if not self.service:
            return None
        self.task_list_items = authentication_module.get_lists_task(self.service)

    def populate_task_list(self):
        for task_list_item_key, task_list_item_values in self.task_list_items.items():
            if task_list_item_values["task_items"]:
                listwidget_item = ListWidgetObject(tasklist_id=task_list_item_key,
                                                   task_list_collection=task_list_item_values,
                                                   parent=self)
                self.tasks_tab_widget.addTab(listwidget_item, QIcon(":/Images/assets/images/list.png"),
                                             task_list_item_values["title"])

        for items in self.tasks_tab_widget.children():
            if isinstance(items, QStackedWidget):
                print (items.children())

    def closeEvent(self, event):
        self.setWindowState(Qt.WindowMinimized)
        self.tray.show()
        self.setVisible(False)
        event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.window_state.setValue("geometry", self.saveGeometry())
                self.tray.show()
                self.setVisible(False)


def main():
    app = QApplication(sys.argv)
    task_goblin_window = TaskGoblin()
    task_goblin_window.show()
    app.exec_()

if __name__ == "__main__":
    main()