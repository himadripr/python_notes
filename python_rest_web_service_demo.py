from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/')

def hello_world():
    return "Hello, Himadri this is Flask"

@app.route('/username/<name>')
def getUserName(name):
    return "Hey there %s" %name

@app.route('/user', methods=['GET','POST'])
def get_user():
  username = request.form['username']
  password = request.form['password']
  #login(arg,arg) is a function that tries to log in and returns true or false
  #status = login(username, password)
  return username

@app.route('/json-example', methods=['POST']) #GET requests will be blocked
def json_example():

    #req_data = request.get_json()
    req_data = json.loads(request.form['jsondata'])
    language = req_data['language']
    framework = req_data['framework']
    python_version = req_data['version_info']['python'] #two keys are needed because of the nested object
    example = req_data['examples'][0] #an index is needed because of the array
    boolean_test = req_data['boolean_test']

    return '''
           The language value is: {}
           The framework value is: {}
           The Python version is: {}
           The item at index 0 in the example list is: {}
           The boolean value is: {}'''.format(language, framework, python_version, example, boolean_test)

@app.route('/cut/panel-details', methods=['POST']) #GET requests will be blocked
def panel_details():
    
    print('target received')
    #req_data = request.get_json()
    arr = json.loads(request.form['jsondata'])
    req_data = arr[0]
    typ = req_data['type']
    length = req_data['sheet_length']
    width = req_data['sheet_breadth']
    detailslength = len(req_data['details'])

    return '''
           The type value is: {}
           The width value is: {}
           The details length is : {}
           The height is: {}'''.format(typ, detailslength, length, width)

if __name__ == "__main__":
    app.run()