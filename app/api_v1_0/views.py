import base64

from flask import (
    flash, request, jsonify
)

from . import api
from app.main.func import illust_dict


# @api.route('/illust')
# def illust():
#     illust_id = request.args.get('illust_id')
#     illust_p =request.args.get('illust_p')
#     try:
#         int(illust_id)
#         int(illust_p)
#     except Exception:
#         return jsonify({'status': 'error', 'message': 'parameter error'})
#     else:
#         try:
#             illust_path = illust_dict[illust_id][illust_p]
#         except KeyError:
#             return ({'status': 'error', 'message': 'not exists'})
#         else:
#             illust_type = illust_path.split('.')[-1]
#             with open(illust_path, 'rb') as f:
#                 illust_stream = base64.b64encode(f.read()).decode('ascii')  # open illust stream.
#             illust_base64_data = 'data:image/{}base64,{}'.format(illust_type, illust_stream)
#             return jsonify({
#                 'status': 'success',
#                 'illust_base64_data': illust_base64_data,
#             })
