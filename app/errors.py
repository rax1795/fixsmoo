from flask import render_template
from app import app, db
import requests
import traceback

chat_id = 18420687
my_token = '795722150:AAGIFX6S9dT2OOYGEQtoSdZWkDeRwNKwwpM' # put your secret Telegram token here 
url_base = 'https://api.telegram.org/bot{}/'.format(my_token)
url_sendMsg = '{}sendMessage'.format(url_base)
def send_message(chat_id,text):
	params = {'chat_id':chat_id, 'text':text}
	r = requests.post(url_sendMsg, params)
	return

@app.errorhandler(404)
def not_found_error(error):
    print(traceback.format_exc())
    return render_template('error404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    print(traceback.format_exc())
    db.session.rollback()
    msg = ("New 500 error! Traceback below for action.\n\n" + error)
    send_message(chat_id,msg)
    return render_template('basicerror.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    error = traceback.format_exc()
    msg = ("New unhandled exception error! Traceback below for action.\n\n" + error)
    send_message(chat_id,msg)
    return render_template('basicerror.html'), 500