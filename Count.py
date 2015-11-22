# Creates and prints items sold and quantity of each from gmail messages for sold eBay items

#!/usr/bin/python

import httplib2
import base64
import re
import email.parser


from apiclient.discovery import build
from apiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
  
# Location of the credentials storage file
STORAGE = Storage('gmail.storage')

# Start the OAuth flow t o retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)

# Retrieve a page of threads
#threads = gmail_service.users().threads().list(userId='me').execute()

Unparsed = 'Label_27'


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,labelIds=label_ids,pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def ReturnMessageBody(service, user_id, msg_id):
  """Get a Message with given ID. Then decode message body and return

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. Use 'me'
    msg_id: The ID of the Message required.

  Returns:
    A string
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,).execute()
    bodyunconverted = message['payload']['parts'][0]['body']['data']
    body = base64.urlsafe_b64decode(bodyunconverted.encode('ASCII'))
    return body
  except errors.HttpError, error:
      print 'An error occurred: %s' % error

def GetQuantitySold(message):
	QuantitySold = re.search(r'Quantity sold:\s*\d', message)
	QuantitySold = QuantitySold.group()
	QuantitySold = re.search(r'\d',QuantitySold)
	return int(QuantitySold.group())

def GetItemName(message):
	ItemStart = message.find("Item name:") + 11; 
    
	ItemEndCoords = message.find("\r\nhttp:", ItemStart); 

	messageslice = message[ItemStart:ItemEndCoords];
	messageslice = messageslice.strip();
	messageslice = messageslice.replace('\r','');
	messageslice = messageslice.replace('\n','');
	return messageslice

def PrintDict(dictionary):
	for item in sorted(dictionary):
		print "Item: %s \n Sold: %s" %(item, dictionary[item])
	
messageList = ListMessagesWithLabels(gmail_service, 'me', Unparsed)
# Retrieve a list with IDs of all messages using unparsed Label
 

sold = {}



count = -1
print "Beginning Operation..."
print "..."
for message in messageList:
    count += 1
     
    message = ReturnMessageBody(gmail_service,'me',messageList[count]['id'])
    QuantitySold = GetQuantitySold(message)
	
    ItemName = GetItemName(message)
   
    if ItemName in sold:
        sold[ItemName] += QuantitySold
        print "%s exists! Adding %s." % (ItemName,QuantitySold)
    else:
        sold[ItemName] = QuantitySold
        print "%s does not exist! Creating and adding %s." %(ItemName,QuantitySold)
print "..."
print "..."
print "Operation Complete"
	
print "\n \n \nPrinting out totals"
PrintDict(sold)

