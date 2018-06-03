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
        self.checkbox_completion.setText("")

        self.task_title_textedit = QTextEdit()
        self.task_title_textedit.textChanged.connect(self.update_task_button)
        self.task_title_textedit.setMaximumHeight(50)

        self.update_task_text_button = QPushButton()
        self.update_task_text_button.setText("Update")
        self.update_task_text_button.setIcon(QIcon(":/Images/assets/images/update.png"))
        self.update_task_text_button.setFixedHeight(24)
        self.update_task_text_button.setEnabled(False)
        self.update_task_text_button.clicked.connect(self.update_tasks_gtasks)

        self.spacer_item = QSpacerItem(80, 10, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Fixed)

        self.button_layout = QHBoxLayout()
        self.button_layout.addItem(self.spacer_item)
        self.button_layout.addWidget(self.update_task_text_button)
        self.widget_layout.addRow(self.checkbox_completion, self.task_title_textedit)
        self.widget_layout.addRow(self.button_layout)

        self.setLayout(self.widget_layout)
        self.init_task()

    def update_task_button(self):
        """
        Updates the task button if there are any changes in the textedit to ensure that the user knows that
        they will have to hit that to push the changes to the google tasks
        :return:
        """
        if str(self.task_title_textedit.toPlainText()) != self.task_title:
            self.update_task_text_button.setEnabled(True)
        else:
            self.update_task_text_button.setEnabled(False)

    def init_task(self):
        """
        Initialise the task and sets up the widget's appearance depending on the status
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
        If the status is completed then the stylesheet changes
        :return:
        """
        if self._status == "completed":
            self.task_title_textedit.setStyleSheet("""text-decoration: line-through;
            font-style: italic;
            color: gray""")
        else:
            self.task_title_textedit.setStyleSheet("""text-decoration:;
            font-style: normal;
            color: rgb(20, 20, 20)""")

    def pull_changes_gtasks(self):
        """
        This pulls changes from the google tasks on hitting the refresh button and if the tasks are deleted then
        the widget is removed. The widget items are also updated depending on the status.
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
        This function is called when the update button is pressed. It sets up the authentication and pushes the changes
        to the tasklist.
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
        This calls the change_status_appearance when you hit the checkbox to either complete the task or remove
        the completion status for a task
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
        This enables you to hit Ctrl+Enter from the text edit so that when you do the change, you can hit the update
        button and push the changes.
        :param event:
        :return:
        """
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Return:
            if self.update_task_text_button.isEnabled():
                self.update_tasks_gtasks()

    @property
    def status(self):
        """
        Returns the status of the task
        :return _status :type string:
        """
        return self._status

    @property
    def uid(self):
        """
        Returns the uid of the task
        :return _uid :type string:
        """
        return self._uid

    @property
    def tasklist_uid(self):
        """
        Returns the parent tasklist id
        :return _tasklist_uid :type string:
        """
        return self._tasklist_uid

class ListWidgetObject(QListWidget):
    """
    List widget object to populate the listwidgetitem
    """
    def __init__(self, parent, task_list_collection, tasklist_id):
        """
        Initialize the listwidget object,
        :param parent :type TaskGoblin:
        :param task_list_collection :type dict:
        :param tasklist_id :type string:
        """
        super(ListWidgetObject, self).__init__(parent)
        self.parent = parent
        self.tasklist_id = tasklist_id
        self.task_list_collection = task_list_collection
        self.init_listwidget_items()
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def sorted_task_list_items(self):
        """
        Sorts the task items for the tasklist as per their positions, helps in keeping a chronological order
        maintained in the tasks app on the phone or web.
        :return position_aware_items :type dict:
        """
        position_aware_items = {}
        for task_item_key, task_item_values in self.task_list_collection["task_items"].items():
            position_aware_items[task_item_values['position']] = {"task_item_key": task_item_key,
                                                                  "task_item_value": task_item_values}
        return position_aware_items

    def init_listwidget_items(self):
        """
        Initialize the list widget items for all the key, value pair in the position aware items
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
        Removed the listitemwidget (CustomListWidget) when the task gets removed from the phone application
        or web application.
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
        Creates a custom listwidgetitem and adds to the self listwidget and adds to the parent's tasks_collection
        dictionary
        :param task_title :type string:
        :param task_uid :type string:
        :param task_list_uid :type string:
        :param task_status :type string:
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

    @property
    def uid(self):
        """
        Returns the uid
        :return tasklist_id :type string:
        """
        return self.tasklist_id


class TaskGoblin(QWidget):
    """
    Main Taskgoblin application
    """
    def __init__(self, parent=None):
        """
        Init function for the application
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
        with open(ASSETS_PATH, 'r') as file_open:
            self.setStyleSheet(file_open.read())

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
        self.add_pushbutton.setMaximumSize(50, 50)
        self.add_pushbutton.clicked.connect(self.insert_tasks)
        self.setToolTip("Add new task")

        self.pull_changes_pushbutton = QPushButton(self)
        self.pull_changes_pushbutton.setIcon(QIcon(":/Images/assets/images/completed.png"))
        self.pull_changes_pushbutton.setMaximumSize(50, 50)
        self.pull_changes_pushbutton.setStyleSheet("border:None")
        self.pull_changes_pushbutton.clicked.connect(self.pull_gtask_changes)
        self.pull_changes_pushbutton.setToolTip("Pull the updates")

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
        When you restores the application from the system tray
        :return:
        """
        self.showNormal()
        self.tray.hide()

    def insert_tasks(self, task_list_id=None, task_item_obj=None, task_item_key=None):
        """
        This inserts a new task button or on refresh a new task is found from the API. This adds in a new customwidget
        object to the tasklist depending on the current tab
        :param task_list_id :type string:
        :param task_item_obj :type dict:
        :param task_item_key :type string:
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
        Creates the setup authentication and gets the tasklist dictionary
        :return:
        """
        self.service = authentication_module.setup_authentication()
        if not self.service:
            return None
        self.task_list_items = authentication_module.get_lists_task(self.service)

    def populate_task_list(self):
        """
        For every task lists available from the google tasks api and populates the listwidget with the
        custom listwidgetitem. This also populates task_list_objects for further use.
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
        This gets called when you hit the refresh button, it goes through all the widgets in the tasklist_widget
        and calls the pull changes for those individual widgets
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
        Overriding the close event so that we can minimize the application and push the app to the systemtray
        :param event:
        :return:
        """
        self.setWindowState(Qt.WindowMinimized)
        self.tray.show()
        self.setVisible(False)
        event.ignore()

    def changeEvent(self, event):
        """
        When the user minimizes the systemtray icon is shown and the application hides itself from the taskbar
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
    Main function
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