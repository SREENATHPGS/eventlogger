from flask import Flask, request, jsonify, render_template, Blueprint
import os, multiprocessing, string, random, time, argparse
from multiprocessing import Process, freeze_support
import logging as logger
import sqlite3, traceback, json, sys
from flask_cors import CORS, cross_origin

base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)

RUN_IN_DEBUG_MODE = os.environ.get('RUN_IN_DEBUG_MODE', False)
PORT = os.environ.get("PORT", 7000)
LOG_DIR = os.environ.get("LOG_DIR", "./logs")

if not os.path.isdir("./logs"):
    logger.info(f"Creating {LOG_DIR} dir")
    os.mkdir("./logs")

logger.basicConfig(level="INFO")


app = Flask(__name__,static_url_path='/event_logger/static', static_folder=os.path.join(base_dir, 'static'),
        template_folder=os.path.join(base_dir, 'templates'))
cors = CORS(app)

app.secret_key="addYourSecretKeyHere"


global taskQueue

def getUid(noOfCharecters=6):
    chars = string.ascii_letters + string.digits
    uid = ''.join(random.choice(chars) for n in range(noOfCharecters))
    return uid

def get_return_payload(status, message = "", data = None):
    return jsonify({"status": status, "message":message, "data" : data})

def createTempFile(path, ticket):
    try:    
        with open(path, "w") as fp:
            fp.write(json.dumps(ticket))
    except Exception as e:
        elog = "Error in creating tempfile"
        logger.error(elog)
        return False, elog
    
    return True, "OK"
        
general_view = Blueprint('general_bp', __name__)

@general_view.route("/", methods = ['GET'])
def homePage():
    return render_template("stats.html")

@general_view.route('/stats', methods = ['GET'])
def stats():
    try:
        db_path = os.environ.get("DB_PATH", "./log_database.db")
        logger.info(f"Looking for log db in {db_path}")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        a = c.execute("select * from log_database;")
        data = a.fetchall()
        conn.close()

        col_names = list(map(lambda x: x[0], c.description))

        jsl = []
        for item in data:
            js = {}
            for i in item:
                print(i)
                js[col_names[item.index(i)]] = i
            jsl.append(js)

        return get_return_payload(True, data=jsl, message="Data fetched successfully.")
    except Exception as e:
        logger.error(e)
        return get_return_payload(False, message="Error in fetching data.")

@general_view.route("/log/<tag>", methods = ["POST"])
def logData(tag = "default"):
    data = request.get_json()

    log_type = data.get("log_type",None)
    log_data = data.get("data", None)
    log_text = data.get("text", None)
    log_tag = tag

    if not log_type:
        return get_return_payload(False, message="log_type not given")
    
    if not log_type in ["data","text"]:
        return get_return_payload(False, message="Invalid log_type")
    
    if log_type == "data":
        if not log_data:
            return get_return_payload(False, message="data is null")
    else:
        if not log_text:
            return get_return_payload(False, message="text is null")
    
    task_id = getUid()
    task = {"task_id":task_id, "log_tag":tag, "log_data":log_data, "log_text":log_text, "log_type":log_type}
    tfile_name = f"./tempFiles/{task_id}.txt"
    tfile_status, message = createTempFile(tfile_name, task)

    if not tfile_status:
        return get_return_payload(False, message=message)

    taskQueue.put(tfile_name)

    return get_return_payload(True, data=task, message="Saving Logs..")

app.register_blueprint(general_view, url_prefix ="/event_logger/")

def queueMonitor():

    while True:
        if not taskQueue.empty():
            print("Found a task.")
            try:
                task_file_name = taskQueue.get()

                logger.info("Reading ticket")
                with open(task_file_name, "r") as fp:
                    task = json.loads(fp.read())

                logger.info(task)
                conn = sqlite3.connect('log_database.db')
                c = conn.cursor()
                c.execute("insert into log_database (log_type, log_tag, log_data, log_text) values  (?,?,?,?)",[task['log_type'],task['log_tag'],json.dumps(task['log_data']),task['log_text']])
                conn.commit()
                conn.close()
                logger.info(f"Deleting temp file {task_file_name}")
                os.remove(task_file_name)
            except Exception as e:
                logger.error("Error in saving data to db")
                logger.error(traceback.print_exc())
        else:
            time.sleep(0.1)


if __name__ == '__main__':
    freeze_support()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--PORT', help = "port to run", default = PORT)
    args = parser.parse_args()

    manager = multiprocessing.Manager()
    taskQueue = manager.Queue()

    queueMonitor = multiprocessing.Process(name = "queueMonitor", target = queueMonitor)

    print("Starting queue monitor.")
    queueMonitor.start()
    app.run(debug=False, host='0.0.0.0', port=args.PORT)