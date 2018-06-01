from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os
from collections import defaultdict


def setup_authentication():
    """
    This will setup the authentication with the google task's API. This uses crendentials stored on your home folder.
    To get your credentials file please look at how to authenticate your apps
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
    There is a very good explaination on how to setup your own credential file. Once received store it on
    your home folder. You will get a client secret json file which will get converted to credentials
    file for faster access.
    :return service :type google.api.object :
    """
    home_user_path = os.path.expanduser("~")
    scopes = 'https://www.googleapis.com/auth/tasks'
    store = file.Storage(os.path.join(home_user_path, 'credentials.json'))
    if not os.path.exists(os.path.join(home_user_path, 'credentials.json')):
        return None
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(home_user_path, 'client_secret.json'), scopes)
        creds = tools.run_flow(flow, store)
    service = build('tasks', 'v1', http=creds.authorize(Http()))
    return service


def get_lists_task(service):
    """
    Gets the task list and the tasks per list for the user whose login was used to create the authentication setup.
    This will generate a default dict whoese keys are the tasklist_ids and the values are the dict of task objects
    in those lists
    :param service: :type google.api.object:
    :return tasks_list_values :type defaultdict:
    """
    task_lists = service.tasklists().list().execute()
    if not task_lists:
        return None, None
    else:
        tasks_list_values = defaultdict(dict)
        for task_values in task_lists["items"]:
            tasks_list_values[task_values["id"]]["title"] = task_values["title"]
        tasks_items_values = {}
        for task_ids in tasks_list_values.keys():
            task_items = service.tasks().list(tasklist=task_ids).execute()
            task_items_dict = {}
            for task_item_value in task_items["items"]:
                if not task_item_value:
                    return None, None
                task_items_dict[task_item_value["id"]] = {'title': task_item_value['title'],
                                                          'status': task_item_value['status'],
                                                          'position': task_item_value['position']}
            if task_items_dict:
                tasks_items_values[task_ids] = task_items_dict
            else:
                tasks_items_values[task_ids] = []
        for keys in tasks_items_values.keys():
            tasks_list_values[keys]['task_items'] = tasks_items_values[keys]
    return tasks_list_values

