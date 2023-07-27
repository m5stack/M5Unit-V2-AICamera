import cv2
from flask import Flask, Response
import threading

app = Flask(__name__)

cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V'))
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

current_frame = None

def capture_loop():
    global current_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        current_frame = jpeg.tobytes()

threading.Thread(target=capture_loop, daemon=True).start()

@app.route('/')
def video_feed():
    def generate():
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
