import base64
import logging

from flask import render_template, jsonify, url_for, request

from . import main
from .func import illust_dict

logging.basicConfig(level=logging.DEBUG)


@main.route('/')
def index():
    return jsonify({'status': '200'})


@main.route('/illust')
def show_illust():
    illust_id = request.args.get('illust_id')  # get url arguments
    illust_p = request.args.get('illust_p')
    if illust_p is None:
        illust_p = str(0)
    try:
        illust_path = illust_dict[illust_id][illust_p]  # get illust abspath path from illust dict
    except KeyError:
        logging.error('Not exist: {}:p{}'.format(illust_id, illust_p))
    else:
        illust_type = illust_path.split('.')[1]
        with open(illust_path, 'rb') as f:
            illust_stream = base64.b64encode(f.read()).decode('ascii')  # open illust stream
        return render_template('illust.html', illust_type=illust_type, illust_stream=illust_stream)
    return jsonify({'status': 'error', 'message': 'Not exist.'})
