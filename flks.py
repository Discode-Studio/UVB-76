from flask import Flask, Response
import subprocess

app = Flask(__name__)

# Utiliser FFmpeg pour capturer le flux audio du WebSDR
@app.route('/stream')
def stream_audio():
    # Commande FFmpeg pour capturer et rediriger le flux audio
    command = ['ffmpeg', '-i', 'http://websdr.ewi.utwente.nl:8901', '-f', 'mp3', '-']
    return Response(subprocess.Popen(command, stdout=subprocess.PIPE).stdout, mimetype='audio/mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
