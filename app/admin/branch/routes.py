from flask import Blueprint, jsonify

branch_bp = Blueprint("branch", __name__)

@branch_bp.route("/")
def list_branches():
    return jsonify({"message": "Branches working"})