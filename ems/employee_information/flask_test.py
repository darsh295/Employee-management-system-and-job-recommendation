from flask import Flask
app = Flask(__name__)
@app.route('/home')
def gft():
  return 'Welcome'

app.run()