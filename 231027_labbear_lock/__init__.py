# add these
device_status = {
    "santec-ts750": {"locked": False, "user": None},
    # ... Add other devices as needed
}


@app.route("/device/<device_name>/status", methods=["GET"])
def get_device_status(device_name):
    status = device_status.get(device_name)
    if status:
        return jsonify(status)
    else:
        return jsonify({"error": "Device not found"}), 404


@app.route("/device/<device_name>/lock", methods=["POST"])
def lock_device(device_name):
    status = device_status.get(device_name)
    if status:
        if not status["locked"]:
            # You can capture the user info if required here
            status["locked"] = True
            status[
                "user"
            ] = "current_user"  # replace with actual user info if available
            return jsonify({"success": "Device locked successfully"})
        else:
            return (
                jsonify({"error": f"Device is already in use by {status['user']}"}),
                400,
            )
    else:
        return jsonify({"error": "Device not found"}), 404


@app.route("/device/<device_name>/unlock", methods=["POST"])
def unlock_device(device_name):
    status = device_status.get(device_name)
    if status:
        if status["locked"]:
            status["locked"] = False
            status["user"] = None
            return jsonify({"success": "Device unlocked successfully"})
        else:
            return jsonify({"error": "Device is not locked"}), 400
    else:
        return jsonify({"error": "Device not found"}), 404
