#! /usr/bin/env python

import praw
import time
import json
import sys

print "Loading data..."
f = open("config","r")
config = json.loads(f.read())
f.close()

subreddits = config["subreddits"] #Use this for testing

match_text = config["match_text"] #text to match, all lowercase
reply_text = config["reply_text"]

already_done = set(config["already_done"]) #stores commments already responded to
last_checked = dict(config["last_checked"]) #maybe optimize?
reply_count = config["reply_count"]

print "Logging in..."
r = praw.Reddit(user_agent="Minnesobot") #base Reddit object
r.login(username=config["username"], password=config["password"]) #log the bot in


##
## Updates the config variable for saving in config file
##
def update_config():
	global already_done, last_checked, reply_count

	config["already_done"] = list(already_done)
	config["last_checked"] = last_checked
	config["reply_count"] = reply_count

##
## Main program loop. Should never exit except for emergencies
##
def bot_loop():
	global reply_count, already_done, last_checked

	print "Running bot."
	while True:

		for subreddit in subreddits:
			s = r.get_subreddit(subreddit)
			comments = s.get_comments(limit=50)
			first = True
			for comment in comments:
				if first:
					first_comment = comment.id
					first = False
				if comment.id == last_checked[subreddit]:
					break
				for text in match_text:
#					print "checking " + text + " in " + comment.body.lower() + " in " + subreddit
					if text in comment.body.lower() and comment.id not in already_done:
						print "Match! Replying to " + comment.author.name
						try:
							reply = comment.reply(reply_text) #TODO: implement buffer, and check for ratelimit exceded
						except praw.errors.RateLimitExceeded as error:
							print "Waiting " + str(error.sleep_time) + " seconds due to rate limit..."
							time.sleep(error.sleep_time)
							print "Trying again..."
							reply = comment.reply(reply_text)
						already_done.add(comment.id)
						print "Done. See the comment here: " + reply.permalink
						reply_count += 1
						print "Bot count: " + str(reply_count)
			last_checked[subreddit] = first_comment

		update_config()
		f = open("config","w+")
		f.write(json.dumps(config))
		f.close()

		time.sleep(30) #Bot runs every 30 seconds

	print "Exiting."

if len(sys.argv) == 1:
	bot_loop()
#else:TODO
#	if sys.argv[1] == "a"