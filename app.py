'''
MendoBot
-Beta
'''

import errno
import os
import sys
import tempfile
from urllib.parse import quote

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
	SourceGroup, SourceRoom, LeaveEvent 
)

from main._handler import command_handler

app = Flask(__name__)

MendoBot = LineBotApi('CQcg1+DqDmLr8bouXAsuoSm5vuwB2DzDXpWc/KGUlxzhq9MSWbk9gRFbanmFTbv9wwW8psPOrrg+mHtOkp1l+CTlqVeoUWwWfo54lNh16CcqH7wmQQHT+KnkNataGXez6nNY8YlahgO7piAAKqfjLgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c116ac1004040f97a62aa9c3503d52d9')

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	'''
	Message Handler
	'''
	text = event.message.text
	if isinstance(event.source, SourceGroup):
		subject = MendoBot.get_group_member_profile(event.source.group_id,
                                                    event.source.user_id)
		set_id = event.source.group_id
	elif isinstance(event.source, SourceRoom):
		subject = MendoBot.get_room_member_profile(event.source.room_id,
                                                   event.source.user_id)
		set_id = event.source.room_id
	else:
		subject = MendoBot.get_profile(event.source.user_id)
		set_id = event.source.user_id
	
	def sendreply(*ms, mode=('text',)*5):
		'''
		reply message with ms as reply value.
		'''
		ms = ms[:5]
		value = []
		for idx, msg in enumerate(ms):
			if mode[idx] == 'text':
				if isinstance(msg, (tuple, list)):
					value = [TextSendMessage(text=item) for item in msg]
				else:
					value.append(TextSendMessage(text=msg))
			elif mode[idx] == 'image':
				if isinstance(msg, (tuple, list)):
					value = [ImageSendMessage(original_value_url=item,
												preview_image_url=item)
							   for item in msg]
				else:
					value.append(ImageSendMessage(
						original_value_url=msg,
						preview_image_url=msg))
			elif mode[idx] == 'custimg':
				if isinstance(msg, (tuple, list)):
					value = [ImageSendMessage(original_value_url=item[0],
												preview_image_url=item[1])
							   for item in msg]
				else:
					value.append(ImageSendMessage(
						original_value_url=msg[0],
						preview_image_url=msg[1]))
		MendoBot.reply_message(
			event.reply_token, value
		)
	
	def leave():
		'''
        Leave a chat room.
        '''
		if isinstance(event.source, SourceGroup):
			sendreply("Bye group.")
			MendoBot.leave_group(event.source.group_id)
		
		elif isinstance(event.source, SourceRoom):
			sendreply("Bye room.")
			MendoBot.leave_room(event.source.room_id)
		
		else:
			sendreply(">_< can't do...")
			
	def getprofile():
		'''
		Send display name and status message of a user.
		'''
		result = ("Display name: " + subject.display_name + "\n"
				  "Profile picture: " + subject.picture_url)
		try:
			profile = MendoBot.get_profile(event.source.user_id)
			if profile.status_message:
				result += "\n" + "Status message: " + profile.status_message
		except LineBotApiError:
			pass
		sendreply(result)
		
	if text[0] == '/':
		command = text[1:]
		result = command_handler(command, subject, me, set_id)
		if command.lower().strip().startswith('leave'):
			leave()
		elif command.lower().strip().startswith('profile'):
			getprofile()
		elif result:
			if result[0] in ('text', 'image', 'custimg'):
				sendreply(*result[1:], mode=(result[0],)*len(result[1:]))
			elif result[0] == 'multi':
				mode, value = [], []
				for item in result[1]:
					mode.append(item[0])
					value.append(item[1])
				sendreply(*value, mode=mode)
			else:
				sendreply(result)	
	
@handler.add(LeaveEvent)
def handle_leave():
	'''
	Leave event handler
	'''
	app.logger.info("Got leave event")
	
if __name__ == "__main__":
	
	port = int(os.getenv('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
