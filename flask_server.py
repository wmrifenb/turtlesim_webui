from flask_socketio import SocketIO
from flask import Flask, render_template
from threading import Thread, Event
from random import random
import roslibpy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    client = roslibpy.Ros(host='localhost', port=9090)
    client.run()
    listener = roslibpy.Topic(client, '/turtle1/pose', 'turtlesim/Pose')
    listener.subscribe(lambda message: socketio.emit('newnumber', {'number': message['x']}, namespace='/test'))
    try:
        while not thread_stop_event.isSet():
            pass
    finally:
        client.terminate()


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@app.route('/starter')
def starter():
    return render_template('starter.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
