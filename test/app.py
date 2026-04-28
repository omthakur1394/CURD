from flask import Flask, request, redirect, render_template, url_for, abort, jsonify
from datetime import datetime

# In-memory data store (resets when the app restarts).
transactions = [
    {"id": 1, "date": "2023-06-01", "amount": 100},
    {"id": 2, "date": "2023-06-02", "amount": -200},
    {"id": 3, "date": "2023-06-03", "amount": 300},
]

app = Flask(__name__)

def _next_transaction_id() -> int:
    """Generate a new unique transaction ID."""
    if not transactions:
        return 1
    return max(t["id"] for t in transactions) + 1


@app.route("/")
def get_transactions():
    """Render the list of transactions."""
    return render_template("transactions.html", transactions=transactions)


@app.route("/create", methods=["GET", "POST"])
def add_transaction():
    """Create a new transaction (GET shows form, POST processes it)."""
    if request.method == "POST":
        # Validate amount.
        try:
            amount = float(request.form["amount"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400

        # Validate date (expects YYYY-MM-DD).
        date_str = request.form.get("date", "")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

        transaction = {
            "id": _next_transaction_id(),
            "date": date_str,
            "amount": amount,
        }
        transactions.append(transaction)
        return redirect(url_for("get_transactions"))

    return render_template("form.html")


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    """Edit an existing transaction (GET shows form, POST updates it)."""
    if request.method == "POST":
        # Validate amount.
        try:
            amount = float(request.form["amount"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400

        # Validate date.
        date_str = request.form.get("date", "")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

        for transaction in transactions:
            if transaction["id"] == transaction_id:
                transaction["date"] = date_str
                transaction["amount"] = amount
                break
        else:
            abort(404)

        return redirect(url_for("get_transactions"))

    # GET – render edit form.
    for transaction in transactions:
        if transaction["id"] == transaction_id:
            return render_template("edit.html", transaction=transaction)

    abort(404)


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    """Delete a transaction. Only accepts POST to mitigate CSRF."""
    # Remove the transaction safely without mutating the list during iteration.
    # No `global` needed because we modify the list in place.
    for i, t in enumerate(transactions):
        if t["id"] == transaction_id:
            del transactions[i]
            break
    else:
        abort(404)

    return redirect(url_for("get_transactions"))


if __name__ == "__main__":
    # In production use a proper WSGI server and configure host/port via env vars.
    app.run(host="127.0.0.1", port=8080)