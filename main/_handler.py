'''
Command Handler
'''

from functools import partial as pt
from . import (
	about, echo, wolfram
)

help_msg = ("Available commands:\n"
			"about, echo, wolfram\n"
			"Use /help <command> for more information.")

cmd_help = {'about': "/about, about me.",
			
			'echo': "/echo, echoing you.",
			
			'wolfram': "/wolfram, use wolfram."}

def get_help(command=None):
	'''
	Return a command's help message.
	'''
	if not command:
		return help_msg
	try:
		return cmd_help[command]
	except KeyError:
		return command + " is unavailable."
		
def command_handler(text, user, me, set_id):
	'''
	Command handler
	'''
	itsme = user.user_id == me.user_id
	command = text.split(maxsplit=1)
	cmd = text.lower().split(maxsplit=1)
	result = None

	no_args = {'about': about}

	single_args = {'echo': echo,
					'wolframs': wolfram}

	try:
		if cmd[0] in no_args:
			result = ('text', no_args[cmd[0]]())

		elif cmd[0] in single_args:
			result = ('text', single_args[cmd[0]](command[1]))

	except (IndexError, TypeError, ValueError):
		result = ("Invalid format.\n"
				  "Please see /help {} for more info."
				  .format(cmd[0]))

	return result