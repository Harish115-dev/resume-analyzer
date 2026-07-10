from flask import Flask ,sessions,render_template


app=Flask(__name__)

@app.route("/")
def __init__():
    return "app is running"


if __name__ == "__main__":
    app.run(debug=True) 



