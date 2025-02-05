from flask import Flask, render_template, request
from chatClient import response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['msg']
    return response(message)

if __name__ == "__main__":
    #app.run()
    pass
