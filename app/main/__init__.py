from flask import Blueprint

main = Blueprint('main', __name__)

from . import views

# from PixivSpider import PixivSpiderApi as pix_api
# from PixivSpider import pixiv_spider as pix
#
# rev_1 = pix_api.get_a_picture(picture_id=68006435, account='332627946@qq.com', password='13752016524')
# # print(rev_1)
#
# picture_id = rev_1[0][0]
#
# rev_2 = pix_api.add_bookmark(picture_id=picture_id)
# print(rev_2)
