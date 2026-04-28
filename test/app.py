from flask import Flask, request, redirect, render_template, url_for, abort, jsonify

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
    return render_template("transactions.html", transactions=transactions)


@app.route("/create", methods=["GET", "POST"])
def add_transaction():
    # POST saves a new transaction; GET shows the form.
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
        except (ValueError, TypeError):
            # Simple validation – in real apps use WTForms.
            return jsonify({"error": "Invalid amount"}), 400

        transaction = {
            "id": _next_transaction_id(),
            "date": request.form["date"],
            "amount": amount,
        }
        transactions.append(transaction)
        return redirect(url_for("get_transactions"))

    return render_template("form.html")


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    # POST updates an existing record; GET loads the edit form.
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400

        for transaction in transactions:
            if transaction["id"] == transaction_id:
                transaction["date"] = request.form["date"]
                transaction["amount"] = amount
                break
        else:
            abort(404)

        return redirect(url_for("get_transactions"))

    for transaction in transactions:
        if transaction["id"] == transaction_id:
            return render_template("edit.html", transaction=transaction)

    abort(404)


@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):
    # Remove the transaction safely without mutating the list during iteration.
    global transactions
    transactions = [t for t in transactions if t["id"] != transaction_id]
    return redirect(url_for("get_transactions"))


if __name__ == "__main__":
    # In production use a proper WSGI server and configure host/port via env vars.
    app.run(host="127.0.0.1", port=8080)