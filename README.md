Interactive chatbot for the campus dining menu at Oberlin College

# Installing the bot

https://discord.com/oauth2/authorize?client_id=1326720826258751549&permissions=274877908992&integration_type=0&scope=bot

Navigate to the above link, and select the server(s) where you'd like to install the bot. Click "allow" on all necessary permissions. The bot will ask for permission to read channel content (to detect the trigger command) and permission to post
in channels in order to send meal information.

# Sending commands

Commands to @obiedine must include the trigger phrase "what's for" in any capitalization. If a meal or meals are specified obiedine
will respond with the dining options for that meal ("breakfast", "lunch", and/or "dinner"). If a meal is not specified, obiedine defaults to the current or upcoming meal based on time of day.

Commands can also include the keyword "tomorrow", for the following days menus, or a specific date in YYYY-MM-DD format.

## Example commands

| Command | Response |
| ------- | -------- |
| @obiedine what's for dinner? | {current dinner menu} |
| @obiedine what's for breakfast and lunch tomorrow | {breakfast menu for the following day}, followed by, in a separate message, {dinner menu for the following day} |
| @obiedine what's for breakfast on 2025-01-26? | {breakfast menu on January 26th, 2025} |