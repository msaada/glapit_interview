from allauth.socialaccount.models import SocialAccount, SocialApp
import requests
from oauth2client.client import AccessTokenCredentials

import httplib2
import os

from apiclient import discovery
from apiclient import errors

from mail.models import Mail

def getMessages(request):
    google_app = SocialApp.objects.get(provider='google')
    user_account = SocialAccount.objects.get(user=request.user)
    # User should only have one SocialToken object per SocialApp
    # https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/models.py#L137
    user_token = user_account.socialtoken_set.first()

    # Credentials to make further requests
    client_key = google_app.client_id
    client_secret = google_app.secret
    resource_owner_key = user_token.token
    resource_owner_secret = user_token.token_secret

    credentials = AccessTokenCredentials(user_token.token, 'my-user-agent/1.0')

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    query = ''
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    #print(labels)

    response = service.users().messages().list(userId='me',
                                               q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    i = 0

    while 'nextPageToken' in response and i < 1:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId='me', q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
      print(i)
      i += 1

    return messages, service

def getMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
      message = service.users().messages().get(userId=user_id, id=msg_id).execute()
      return message["snippet"] + "..."
  except errors.HttpError as error:
      print ('An error occurred: %s' % error)


def formatMessages(messages, service, me):
    for m in messages[:100]:
        newMail = Mail(mailId=m['id'], snippet=getMessage(service, me, m['id']))
        newMail.save()



class MySingleton(object):
     INSTANCE = None

     def __init__(self, request):
        if self.INSTANCE is not None:
            raise ValueError("An instantiation already exists!")
        messages, service = getMessages(request)
        formatted_messages = formatMessages(messages, service, 'me')

        # do your init stuff

     @classmethod
     def get_instance(cls, request):
        if cls.INSTANCE is None:
             cls.INSTANCE = MySingleton(request)
        return cls.INSTANCE
