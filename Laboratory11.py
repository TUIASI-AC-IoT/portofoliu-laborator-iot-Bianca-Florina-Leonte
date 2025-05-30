from flask import Flask
from flask import request
from os import listdir, stat, remove
from os.path import isfile, join, exists
from datetime import datetime
from time import strftime

app = Flask(__name__)

DIR_PATH = "C:\\Users\\bianca\\Desktop\\IoT\\"

if not exists(DIR_PATH):
    makedirs(DIR_PATH)

@app.route("/")
def start():
    return "IoT - Laboratory 11"


@app.route('/dir', methods=['GET'])
def getAllFiles():
    files = [f for f in listdir(DIR_PATH) if isfile(join(DIR_PATH, f))]
    return jsonify({"dir": DIR_PATH, "files": files})


@app.route('/dir/<filename>', methods=['GET'])
def getFile(filename):
    response = {}
    filepath = join(DIR_PATH, filename)
    if exists(filepath):
        response["path"] = filepath
        stats = stat(filepath)
        response["ctime"] = datetime.fromtimestamp(stats.st_ctime).strftime("%A, %B %d, %Y %I:%M:%S")
        response["utime"] = datetime.fromtimestamp(stats.st_mtime).strftime("%A, %B %d, %Y %I:%M:%S")
        response["size"] = stats.st_size
        with open(filepath) as f:
            response["content"] = f.read()
    else:
        response["status"] = "NOK"
        response["err_msg"] = "File not found."
    return jsonify(response)


@app.route('/dir/<filename>', methods=['DELETE'])
def deleteFile(filename):
    response = {}
    filepath = join(DIR_PATH, filename)
    if exists(filepath):
        remove(filepath)
        response["status"] = "OK"
    else:
        response["status"] = "NOK"
        response["err_msg"] = "File not found."
    return jsonify(response)


@app.route('/dir', methods=['POST'])
def createFileAuto():
    rsp = {}
    req = request.get_json()
    filename = strftime("%Y%m%d_%H%M%S.txt")
    filepath = join(DIR_PATH, filename)
    with open(filepath, "w") as f:
        f.write(req.get("content", ""))
    rsp["status"] = "OK"
    rsp["filename"] = filename
    return jsonify(rsp)


@app.route('/dir/create', methods=['PUT'])
def createFileWithName():
    rsp = {}
    req = request.get_json()
    filename = req.get("name")
    if not filename:
        return jsonify({"status": "NOK", "err_msg": "Filename is required."}), 400
    filepath = join(DIR_PATH, filename)
    with open(filepath, "w") as f:
        f.write(req.get("content", ""))
    rsp["status"] = "OK"
    rsp["filename"] = filename
    return jsonify(rsp)

@app.route('/dir/<filename>', methods=['PUT'])
def updateFile(filename):
    rsp = {}
    req = request.get_json()
    filepath = join(DIR_PATH, filename)
    if exists(filepath):
        with open(filepath, "w") as f:
            f.write(req.get("content", ""))
        rsp["status"] = "OK"
    else:
        rsp["status"] = "NOK"
        rsp["err_msg"] = "File not found."
    return jsonify(rsp)



if __name__ == "__main__":  
    app.run()
