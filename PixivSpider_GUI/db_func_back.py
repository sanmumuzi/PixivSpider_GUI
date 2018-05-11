import sqlite3
from functools import wraps
from setting import db_path

__all__ = ['create_table_tuple']
create_table_tuple = (
    # 用户数据表
    'CREATE TABLE PS_USER (ID INT PRIMARY KEY NOT NULL)',
    # 用户书签关联表
    'CREATE TABLE USER_BOOKMARK_RELATION (USER_ID INT NOT NULL, PICTURE_ID INT NOT NULL, '
    'COMMENT TEXT)',
    # 书签的标签表
    'CREATE TABLE BOOKMARK_TAG (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL UNIQUE)',
    # 书签的关联表
    'CREATE TABLE BOOKMARK_TAG_RELATION (TAG_ID INT NOT NULL, USER_ID INT NOT NULL, PICTURE_ID INT NOT NULL)',
    # 书签数表
    'CREATE TABLE BOOKMARK_COUNT (ID INT PRIMARY KEY NOT NULL, COUNT INT NOT NULL)',
    # 图片基本信息数据表
    'CREATE TABLE PICTURE (ID INT PRIMARY KEY NOT NULL, P INT, DATE TEXT NOT NULL, TYPE TEXT NOT NULL)',
    # 画师基本信息数据表
    'CREATE TABLE USER (ID INT PRIMARY KEY NOT NULL, Nickname TEXT, Website TEXT, "Self introduction" TEXT)',
    # 图片画师关联表
    'CREATE TABLE PICTURE_USER_RELATION (PICTURE_ID INT PRIMARY KEY NOT NULL, USER_ID INT NOT NULL)',
    # 画师标签表
    'CREATE TABLE USER_TAG (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL UNIQUE)',
    # 图片标签表
    'CREATE TABLE PICTURE_TAG (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL UNIQUE)',
    # 画师标签关联表
    'CREATE TABLE USER_TAG_RELATION (USER_ID INT NOT NULL, TAG_ID INT NOT NULL)',
    # 图片标签关联表
    'CREATE TABLE PICTURE_TAG_RELATION (PICTURE_ID INT NOT NULL, TAG_ID INT NOT NULL)',
    # 画师联系方式表
    'CREATE TABLE CONTACTS (USER_ID INT PRIMARY KEY NOT NULL, Twitter TEXT, Instagram TEXT, Tumblr TEXT, '
    'Facebook TEXT, Skype TEXT, "Windows Live" TEXT, "Google Talk" TEXT, "Yahoo! Messenger" TEXT, Circlems TEXT)',
    # 画师英文个人信息表
    'CREATE TABLE EN_PERSONAL_INFO (ID INT PRIMARY KEY NOT NULL, Gender TEXT, Location TEXT, '
    'Age TEXT, Birthday TEXT, Occupation TEXT)',
    # 画师中文个人信息表
    'CREATE TABLE ZH_PERSONAL_INFO (ID INT PRIMARY KEY NOT NULL, Gender TEXT, Location TEXT, '
    'Age TEXT, Birthday TEXT, Occupation TEXT)',
    # 图片信息表
    'CREATE TABLE PICTURE_INFO (ID INT PRIMARY KEY NOT NULL, Title TEXT, Introduction TEXT)',
    # ...想加入用户表，然后加入mark关系和follow关系，绝望
    # 'CREATE TABLE USER (ID INT PRIMARY KEY NOT NULL, )'
)


class GuiOperateDB(object):
    def __init__(self):
        self.conn = sqlite3.connect(db_path)

    def create_table(self):
        c = self.conn.cursor()
        for table in create_table_tuple:
            try:
                c.execute(table)
            except sqlite3.OperationalError as e:
                print('Error: create table: {}.'.format(table.split(' (')[0]))
                raise
        try:
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
            raise

    def insert_picture_base_info(self, *args):
        c = self.conn.cursor()
        try:
            c.execute('INSERT INTO PICTURE (ID, P, DATE, TYPE) VALUES (?, ?, ?, ?)', args)
        except sqlite3.IntegrityError as e:  # 貌似重复数据会引发这条报错
            print(str(e) + '图片基本信息--数据库中已有这条数据:{}'.format(args[0]))
            pass
        else:
            self.conn.commit()

    def insert_picture_info(self, *args):
        c = self.conn.cursor()
        try:
            c.execute('INSERT INTO PICTURE_INFO (ID, Title, Introduction) VALUES (?, ?, ?)', args)
        except sqlite3.IntegrityError as e:
            print(str(e) + '图片信息--数据库中已有这条数据:{}'.format(args[0]))
        else:
            self.conn.commit()

    def search_picture_base_info(self):
        c = self.conn.cursor()
        c.execute('SELECT ID, P, DATE, TYPE FROM PICTURE WHERE ID = ?'.format(picture))