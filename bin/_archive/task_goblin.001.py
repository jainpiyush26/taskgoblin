from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import re
import sys
import resources
import authentication_module
from collections import defaultdict


class TaskGoblin(QWidget):
    def __init__(self, parent=None):
        super(TaskGoblin, self).__init__(parent)
        # App basics
        self.setWindowTitle("TaskGoblin")
        self.setWindowIcon(QIcon(":/Images/assets/images/icon.png"))
        self.setWhatsThis("""This links to your google tasks and uses the google 
        API to give you and easy windows desktop!""")

        self.task_list_items = defaultdict(dict)
        self.task_list_objects = {}
        self.service_object = None
        # Create the authentication module..
        self.setup_authentication()

        self.available_window_size = QDesktopWidget().availableGeometry()
        self.screen_window_size = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, 250, 350)
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

        # self.remove_pushbutton = QPushButton(self)
        # self.remove_pushbutton.setIcon(QIcon(":/Images/assets/images/minus.png"))
        # self.remove_pushbutton.setMaximumSize(30, 30)
        # self.remove_pushbutton.setStyleSheet("border:None")

        self.button_spacer = QSpacerItem(100, 30, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Fixed)
        self.pushbutton_layout = QHBoxLayout()
        self.pushbutton_layout.addWidget(self.add_pushbutton)
        # self.pushbutton_layout.addWidget(self.remove_pushbutton)
        self.pushbutton_layout.addItem(self.button_spacer)


        self.tasks_tab_widget = QTabWidget(self)
        self.tasks_tab_widget.setMovable(True)

        self.main_layout.addWidget(self.tasks_tab_widget)
        self.main_layout.addLayout(self.pushbutton_layout)

        self.setLayout(self.main_layout)

        # Populating the tasklists
        self.populate_task_list()

    def insert_tasks(self):
        current_tab = self.tasks_tab_widget.currentWidget()
        blank_listwidget_item = QListWidgetItem()
        blank_listwidget_item.setCheckState(False)
        blank_listwidget_item.setFlags(blank_listwidget_item.flags() | Qt.ItemIsEditable)
        blank_listwidget_item.setText("-- Insert Task Data --")
        current_tab.insertItem(current_tab.count()+1, blank_listwidget_item)
        blank_listwidget_item.setSelected(True)
        current_tab.setFocus()

    def setup_authentication(self):
        service = authentication_module.setup_authentication()
        if not service:
            return None
        self.task_list_items, self.service_object = authentication_module.get_lists_task(service)

    # def item_state_change(self, task_list_item):
    #     if task_list_item.checkState() == 2:
    #         print (self.sender().item(self.sender().currentRow()))
            # print (task_list_item)
            # task_list_item.setFlags(task_list_item.flags())
            # self.sender().takeItem(self.sender().currentRow())

    # def populate_task_list(self):
    #     if self.task_list_items:
    #         if len(self.task_list_items.keys()) == 0:
    #             return None
    #         for task_list_id, task_list_values in self.task_list_items.items():
    #             listwidget_object = QListWidget()
    #             listwidget_object.itemActivated.connect(self.item_state_change)
    #             listwidget_object.setObjectName(task_list_id)
    #             list_widget_counter =
    #             for task_ids, task_values in task_list_values['task_items'].items():
    #                 task_listwidget_item_object = QListWidgetItem()
    #                 task_listwidget_item_object.setFlags(task_listwidget_item_object.flags() | Qt.ItemIsEditable)
    #                 task_listwidget_item_object.setText(task_values)
    #                 task_listwidget_item_object.setWhatsThis(task_ids)
    #                 task_listwidget_item_object.setCheckState(False)
    #                 listwidget_object.insertItem(list_widget_counter, task_listwidget_item_object)
    #                 list_widget_counter += 1
    #             self.tasks_tab_widget.addTab(listwidget_object, QIcon(":/Images/assets/images/list.png"),
    #                                          task_list_values["title"])
    #     else:
    #         return None



def main():
    app = QApplication(sys.argv)
    task_goblin_window = TaskGoblin()
    task_goblin_window.show()
    app.exec_()

if __name__ == "__main__":
    main()