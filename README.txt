In order to start the bot, execute exec.sh.
You should also create a directory named private that contains a few files:

chats.db
	An SQL database containing the following tables:
	CREATE TABLE motd (chat_id INTEGER, message TEXT);

myself
	A text file containing your Telegram User ID.

token.txt
	A text file containing your Bot API token with no ending newline (echo -n)

youtube
	An empty directory
