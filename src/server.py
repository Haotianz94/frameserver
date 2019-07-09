from hwang import Decoder
from storehouse import StorageConfig, StorageBackend, RandomReadFile
from flask import Flask, request, send_file, Response
import cv2
import os
import io
import sys
import traceback
import json
import pickle

app = Flask(__name__)

FILESYSTEM = os.environ['FILESYSTEM']
if FILESYSTEM == 'google':
    config = StorageConfig.make_gcs_config(os.environ['BUCKET'])
else:
    config = StorageConfig.make_posix_config()
storage = StorageBackend.make_from_config(config)


@app.route("/fetch")
def fetch():
    try:
        path = request.args.get('path')
        frame_ids = json.loads(request.args.get('frame'))

        if FILESYSTEM == 'local':
            path = '/host' + path

        video_file = RandomReadFile(storage, path.encode('ascii'))
        video = Decoder(video_file)

        img_list = video.retrieve(frame_ids)
        img_list = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in img_list]

        # store imgs to disk
        os.makedirs('/frameserver/tmp/', exist_ok=True)
        pickle.dump(img_list, open('/frameserver/tmp/test.pkl', 'wb'))
        return Response(traceback.format_exc(), mimetype='text/plain')

        # send imgs through http
        # img_list_encode = [cv2.imencode('.jpg', img)[1] for img in img_list]
        # import base64
        # with open('test.pkl', 'wb') as fp:
        #     data = pickle.dumps(img_list_encode)
        #     encoded = base64.b64encode(data)
        #     fp.write(encoded)
        # return send_file('test.pkl', as_attachment=True)

    except Exception:
        return Response(traceback.format_exc(), mimetype='text/plain')


@app.route("/cache")
def cache():
    path = request.args.get('path')
    frame = [int(s) for s in request.args.get('frames').split(',')]
    # TODO
