import discord
import random
import xml.etree.ElementTree as ET
import sched, time
import threading
import os

#new version

client = discord.Client()
random.seed()
scheduler = sched.scheduler(time.time, time.sleep)

serverID = '232312359585185793'

# ID's of all users with admin privileges over bot (read from settings.xml)
botAdmins = []

# The room's ID to watch for users joining (read from settings.xml)
roomsToMonitor = []

# The chance (out of 100) to change a users name upon entering roomToMonitor
chanceToChange = 50

#bot command identifier
identifier = ''

# Parse settings.xml
tree = ET.parse('settings.xml')
root = tree.getroot()
print('Bot Admins:')
for child in root:
	for sub in child:
		if (sub.tag == 'admin'):
			botAdmins.append(sub.get('id'))
			print('  ', sub.get('name'))
		elif (sub.tag == 'room'):
			roomsToMonitor.append(sub.get('id'))
print('')

def printAdmins():
	print('Current Admins')
	for admins in root.iter('admins'):
		for admin in admins.iter('admin'):
			print(admin.get('name'), '\t', '(', admin.get('id'), ')')
	print('')

def addElement(head, sub):
	head.append(sub)
	return

def removeElement(head, subElementName, tagName, compareTo):
	for exAdmin in head.findall(subElementName):
		if (exAdmin.get(tagName) == compareTo):
			head.remove(exAdmin)
	return

def getElement(elementName):
	global root
	for element in root.iter(elementName):
		return element

def getName():
	members = list(client.get_all_members())
	membersCount = len(members) - 1
	member = members[random.randrange(0, membersCount)]
	return member.display_name

async def updateClient():
	pid=os.fork()
	if pid==0:
		os.system('nohup python3.6 ./update.sh & disown')
	else:
		exit()

async def exit():
#	global scheduler
#	while(not scheduler.empty()):
#		print('Deleting ', scheduler.queue[0])
#		scheduler.cancel(scheduler.queue[0])
	await client.close()

@client.event
async def on_message(message):
	# Per the discord.py docs this is to not have the bot respond to itself
	if message.author == client.user:
		return

	# Delete messages sent to bot
	await client.delete_message(message)

	# Checks that the message is for the bot
	if (not message.content.startswith(identifier)):
		return


	# NORMAL USER COMMANDS -------------------------------------------------
	# If the bot sees the command !hello we will respond with our msg string
	if message.content.startswith(identifier + 'hello'):
		msg = 'Hello {0.author.mention}'.format(message)
		await client.send_message(message.channel, msg)
		return


	# ADMIN ONLY COMMANDS --------------------------------------------------
	# Check that the message come from a bot admin
	if (message.author.id not in botAdmins):
		print('Normal boy sent: "' + message.content + '"')
		return

	# Add a new bot admin
	if (message.content.startswith(identifier + 'add')):
		command = message.content.split()
		if (command[1] == 'admin' ):
			parent = getElement('admins')
			sub = ET.SubElement(parent, 'admin')
			sub.set('id', command[2])
			sub.set('name', command[3])
			addElement(parent, sub)
		tree.write('settings.xml')

	elif message.content.startswith(identifier + 'remove'):
		command = message.content.split()
		if (command[1] == 'admin'):
			parent = getElement('admins')
			removeElement(parent, 'admin', 'id', command[2])
		tree.write('settings.xml')

	elif message.content.startswith(identifier + 'list'):
		command = message.content.split()
		if(command[1] == 'admins'):
			printAdmins()

	elif message.content.startswith(identifier + 'quit'):
		await client.send_message(message.channel, 'I can\'t do that, ' + message.author.mention)

	elif message.content.startswith(identifier + 'q'):
		await exit()


async def changeName(member):
	await asyncio.sleep(10)
	#time.sleep(10)
	#member = client.get_server(serverID).get_member(memberID)
	await client.change_nickname(member, getName())

@client.event
async def on_voice_state_update(before, after):
	for item in scheduler.queue:
		print(item)
	print('')

	if(after.voice_channel.id not in roomsToMonitor):
		return

	if (random.randrange(0,100) >= chanceToChange):
		newName = getName()
		print('Changing ' + after.display_name + ' to ' + newName)
		await client.change_nickname(after, newName)
	else:
		print(after.display_name + ' (' + after.name + ') will remain ' + after.display_name + ', for now')
	print('')


@client.event
async def on_member_update(before, after):
	if (after.voice_channel.id not in roomsToMonitor):
		return

	if(after.display_name != before.display_name):
		newRef = os.fork
		if newRef==0:
			await changeName(after)


		#newThread = threading.Thread(target=changeName, args=( str(after.id), ))
		#newThread.start()

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('----------')


# Start the bot loop
client.run('MzIwNjI2Mjc5NjgwNDQyMzkx.DBSOiQ.NE_wVCDegfme-NaVvPnZJVq9HIc')
