# Imports
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import os
from resources import resources
from authentication import authentication_module
from collections import defaultdict

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets", "stylesheet.css")


class CustomListWidget(QWidget):
    """
    Creates a custom widget to be added in the listwidget. This will give us a lot more control over the tasks
    information we will want to add
    """
    def __init__(self, task_title, task_uid, task_list_uid, task_status, parent=None):
        """
        Init function of the task. This represent individual tasks of a task list and contain all the relevant
        information for that.
        :param task_title :type string:
        :param task_uid :type string:
        :param task_list_uid :type string:
        :param task_status :type string:
        :param parent :type QListWidget:
        """
        super(CustomListWidget, self).__init__(parent)
        self.task_title = task_title
        self._tasklist_uid = task_list_uid
        self.parent = parent
        self.widget_layout = QFormLayout()
        self._status = task_status
        self._uid = task_uid
        self.setObjectName(str(self._uid))

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
        """

        :return:
        """
        if str(self.task_title_textedit.toPlainText()) != self.task_title:
            self.update_task_text_button.setEnabled(True)
        else:
            self.update_task_text_button.setEnabled(False)

    def init_task(self):
        """

        :return:
        """
        self.task_title_textedit.setText(self.task_title)
        if self._status == "completed":
            self.checkbox_completion.setChecked(True)
            self.change_status_appearance()
        else:
            self.checkbox_completion.setChecked(False)
            self.change_status_appearance()

    def change_status_appearance(self):
        """

        :return:
        """
        if self._status == "completed":
            self.task_title_textedit.setStyleSheet("""text-decoration: line-through;
            font-style: italic;
            color: gray""")
        else:
            self.task_title_textedit.setStyleSheet("""text-decoration:;
            font-style: normal;
            color: white""")

    def pull_changes_gtasks(self):
        """

        :return:
        """
        service_obj = authentication_module.setup_authentication()
        tasks_pull_object = service_obj.tasks().get(tasklist=self._tasklist_uid, task=self._uid).execute()
        self.task_title_textedit.setText(tasks_pull_object['title'])
        if tasks_pull_object.get("deleted"):
            self.parent.delete_list_item(self)
            self.deleteLater()
            return
        if tasks_pull_object["status"] == "completed":
            self.checkbox_completion.blockSignals(True)
            self.checkbox_completion.setChecked(True)
            self.toggle_status_change(True)
            self.checkbox_completion.blockSignals(False)

    def update_tasks_gtasks(self):
        """

        :return:
        """
        task_body = {"title": str(self.task_title_textedit.toPlainText()),
                     "status": self.status,
                     "id": self._uid}
        service_obj = authentication_module.setup_authentication()
        service_obj.tasks().update(tasklist=self._tasklist_uid, task=self._uid, body=task_body).execute()
        self.update_task_text_button.setEnabled(False)

    def toggle_status_change(self, check_status):
        """

        :param check_status:
        :return:
        """
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
        """

        :param event:
        :return:
        """
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Return:
            if self.update_task_text_button.isEnabled():
                self.update_tasks_gtasks()

    @property
    def status(self):
        """

        :return:
        """
        return self._status

    @property
    def uid(self):
        """

        :return:
        """
        return self._uid

    @property
    def tasklist_uid(self):
        """

        :return:
        """
        return self._tasklist_uid

class ListWidgetObject(QListWidget):
    """

    """
    def __init__(self, parent, task_list_collection, tasklist_id):
        """

        :param parent:
        :param task_list_collection:
        :param tasklist_id:
        """
        super(ListWidgetObject, self).__init__(parent)
        self.parent = parent
        self.tasklist_id = tasklist_id
        self.task_list_collection = task_list_collection
        self.init_listwidget_items()
        self.setDragDropMode(QAbstractItemView.InternalMove)

    @property
    def uid(self):
        """

        :return:
        """
        return self.tasklist_id

    def sorted_task_list_items(self):
        """

        :return:
        """
        position_aware_items = {}
        for task_item_key, task_item_values in self.task_list_collection["task_items"].items():
            position_aware_items[task_item_values['position']] = {"task_item_key": task_item_key,
                                                                  "task_item_value": task_item_values}
        return position_aware_items

    def init_listwidget_items(self):
        """

        :return:
        """
        position_aware_dict = self.sorted_task_list_items()
        for position, position_values in sorted(position_aware_dict.items()):
            self.insert_list_item(task_title=position_values.get("task_item_value")['title'],
                                  task_uid=position_values.get("task_item_key"),
                                  task_list_uid=self.tasklist_id,
                                  task_status=position_values.get("task_item_value")['status'])

    def delete_list_item(self, list_item):
        """

        :param list_item:
        :return:
        """
        # self.parent.tasks_collection.pop(list_item.uid)
        to_remove_item = None
        for item_counter in range(0, self.count()):
            if list_item == self.itemWidget(self.item(item_counter)):
                to_remove_item = item_counter
        self.takeItem(to_remove_item)


    def insert_list_item(self, task_title, task_uid, task_list_uid, task_status):
        """

        :param task_title:
        :param task_uid:
        :param task_list_uid:
        :param task_status:
        :return:
        """
        list_item_object = CustomListWidget(task_title=task_title,
                                            task_uid=task_uid,
                                            task_list_uid=task_list_uid,
                                            task_status=task_status,
                                            parent=self)

        insert_widget_item = QListWidgetItem(self)
        insert_widget_item.setSizeHint(list_item_object.sizeHint())
        self.insertItem(0, insert_widget_item)
        self.setItemWidget(insert_widget_item, list_item_object)
        self.parent.tasks_collection[list_item_object.uid] = list_item_object


class TaskGoblin(QWidget):
    """

    """
    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(TaskGoblin, self).__init__(parent)
        # App basics
        self.setWindowTitle("TaskGoblin")
        self.goblin_icon = QIcon(":/Images/assets/images/icon.png")
        self.setWindowIcon(self.goblin_icon)
        self.setWhatsThis("""This links to your google tasks and uses the google 
        API to give you and easy windows desktop!""")

        # Lets do this in the future not now
        # with open(ASSETS_PATH, 'r') as file_open:
        #     self.setStyleSheet(file_open.read())

        self.task_list_items = defaultdict(dict)
        self.task_list_objects = {}
        self.tasks_collection = {}
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

        self.pull_changes_pushbutton = QPushButton(self)
        self.pull_changes_pushbutton.setIcon(QIcon(":/Images/assets/images/completed.png"))
        self.pull_changes_pushbutton.setMaximumSize(30, 30)
        self.pull_changes_pushbutton.setStyleSheet("border:None")
        self.pull_changes_pushbutton.clicked.connect(self.pull_gtask_changes)

        self.button_spacer = QSpacerItem(100, 30, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Fixed)
        self.pushbutton_layout = QHBoxLayout()
        self.pushbutton_layout.addWidget(self.add_pushbutton)
        self.pushbutton_layout.addWidget(self.pull_changes_pushbutton)
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
        """

        :return:
        """
        self.showNormal()
        self.tray.hide()

    def insert_tasks(self, task_list_id=None, task_item_obj=None, task_item_key=None):
        """

        :param task_list_id:
        :param task_item_obj:
        :param task_item_key:
        :return:
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if not task_list_id:
            current_tab = self.tasks_tab_widget.currentWidget()
            service = authentication_module.setup_authentication()
            new_task_object = {"title": ""}
            new_task_item = service.tasks().insert(tasklist=current_tab.tasklist_id, body=new_task_object).execute()
            new_listwidget_item = QListWidgetItem()
            list_item_object = CustomListWidget(task_title=new_task_item.get('title'), task_uid=new_task_item.get('id'),
                                                task_list_uid=current_tab.tasklist_id, task_status="needsAction",
                                                parent=current_tab)
            new_listwidget_item.setSizeHint(list_item_object.sizeHint())
            current_tab.insertItem(0, new_listwidget_item)
            current_tab.setItemWidget(new_listwidget_item, list_item_object)
        else:
            current_tab = self.task_list_objects[task_list_id]
            current_tab.insert_list_item(task_title=task_item_obj["title"], task_uid=task_item_key,
                                         task_list_uid=task_list_id, task_status=task_item_obj["status"])
        QApplication.restoreOverrideCursor()

    def setup_authentication(self):
        """

        :return:
        """
        self.service = authentication_module.setup_authentication()
        if not self.service:
            return None
        self.task_list_items = authentication_module.get_lists_task(self.service)

    def populate_task_list(self):
        """

        :return:
        """
        for task_list_item_key, task_list_item_values in self.task_list_items.items():
            if task_list_item_values["task_items"]:
                listwidget_item = ListWidgetObject(self, tasklist_id=task_list_item_key,
                                                   task_list_collection=task_list_item_values)
                self.task_list_objects[listwidget_item.uid] = listwidget_item
                self.tasks_tab_widget.addTab(listwidget_item, QIcon(":/Images/assets/images/list.png"),
                                             task_list_item_values["title"])

    def pull_gtask_changes(self):
        """

        :return:
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            for object_uid, object in self.tasks_collection.items():
                object.pull_changes_gtasks()
        except:
            self.tasks_collection.pop(object_uid)
        self.setup_authentication()
        for task_list_item_key, task_list_item_values in self.task_list_items.items():
            for task_item_key in task_list_item_values["task_items"].keys():
                if not task_item_key in self.tasks_collection.keys():
                    self.insert_tasks(task_list_item_key, task_list_item_values["task_items"][task_item_key],
                                      task_item_key)
        QApplication.restoreOverrideCursor()

    def closeEvent(self, event):
        """

        :param event:
        :return:
        """
        self.setWindowState(Qt.WindowMinimized)
        self.tray.show()
        self.setVisible(False)
        event.ignore()

    def changeEvent(self, event):
        """

        :param event:
        :return:
        """
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.window_state.setValue("geometry", self.saveGeometry())
                self.tray.show()
                self.setVisible(False)


def main():
    """

    :return:
    """
    if sys.platform == "win32":
        import ctypes
        task_goblin_app_id = u"pjain.task_goblin.version.3.0.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(task_goblin_app_id)
    app = QApplication(sys.argv)
    task_goblin_window = TaskGoblin()
    task_goblin_window.show()
    app.exec_()

if __name__ == "__main__":
    main()