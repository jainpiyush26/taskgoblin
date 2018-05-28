"""
Shows basic usage of the Tasks API. Outputs the first 10 task lists.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

# Setup the Tasks API
SCOPES = 'https://www.googleapis.com/auth/tasks'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('tasks', 'v1', http=creds.authorize(Http()))

# Call the Tasks API

results = service.tasklists().list(maxResults=10).execute()
task = service.tasks().list(tasklist="MTY5MDUxNjc0NDE5ODIyODAxMTk6MDow").execute()
print(json.dumps(results, sort_keys=True, indent=4))
print(json.dumps(task, sort_keys=True, indent=4))
# items = results.get('items', [])
# if not items:
#     print('No task lists found.')
# else:
#     print('Task lists:')
#     for item in items:
#         print('{0} ({1})'.format(item['title'], item['id']))