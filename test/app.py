from flasssk import Flask, request, redirect, render_template, url_for

# In-memory data store (resets when the app restarts).
transactions = [
    {'id': 1, 'date': '2023-06-01', 'amount': 100},
    {'id': 2, 'date': '2023-06-02', 'amount': -200},
    {'id': 3, 'date': '2023-06-03', 'amount': 300}
]

app = Flask(__name__)

@app.route('/')
def get_transactions():
    return render_template("transactions.html", transactions=transactions)

@app.route("/create", methods=["GET", "POST"])
def add_transaction():
    # POST saves a new transaction; GET shows the form.
    if request.method == "POST":
        transaction = {
            # Simple incremental ID based on current list length.
            'id': len(transactions) + 1,
            'date': request.form['date'],
            'amount': float(request.form['amount'])
        }
        transactions.append(transaction)
        return redirect(url_for("get_transactions"))
    return render_template("form.html")

@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    # POST updates an existing record; GET loads the edit form.
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])

        for transaction in transactions:
            if transaction['id'] == transaction_id:
                transaction['date'] = date
                transaction['amount'] = amount
                break

        return redirect(url_for("get_transactions"))

    for transaction in transactions:
        if transaction['id'] == transaction_id:
            return render_template("edit.html", transaction=transaction)

    # Return 404 when the requested transaction does not exist.
    return {"message": "Transaction not found"}, 404

@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):
    for transaction in transactions:
        if transaction['id'] == transaction_id:
            transactions.remove(transaction)
            break

    return redirect(url_for("get_transactions"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
