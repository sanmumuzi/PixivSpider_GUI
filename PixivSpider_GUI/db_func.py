import sqlite3
from functools import wraps
from setting import db_path

__all__ = ['create_db_and_table', 'insert_picture_base_info_from_download', 'insert_picture_info_from_PixivPictureInfo',
           'insert_painter_base_info_from_picture_detail_page', 'search_picture_base_info', 'search_picture_info',
           'insert_picture_info_from_picture_detail_page', 'insert_painter_info', 'search_painter_info',
           'update_picture_base_info', 'search_all_painter', 'check_specific_painter']

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
    'CREATE TABLE BOOKMARK_COUNT (ID INT PRIMARY KEY NOT NULL, COUNT INT)',
    # 图片基本信息数据表
    'CREATE TABLE PICTURE (ID INT PRIMARY KEY NOT NULL, P INT, DATE TEXT NOT NULL, TYPE TEXT NOT NULL)',
    # 画师基本信息数据表
    'CREATE TABLE USER (ID INT PRIMARY KEY NOT NULL, Nickname TEXT, Website TEXT, "Self introduction" TEXT)',
    # 画师标签表
    'CREATE TABLE "USER_TAG" (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL UNIQUE)',
    # 图片标签表
    'CREATE TABLE "PICTURE_TAG" (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL UNIQUE)',
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
    'CREATE TABLE PICTURE_INFO (ID INT PRIMARY KEY NOT NULL, '
    'Title TEXT, Introduction TEXT, Bookmark INT)',
    # ...想加入用户表，然后加入mark关系和follow关系，绝望
    # 'CREATE TABLE USER (ID INT PRIMARY KEY NOT NULL, )'
)


def pre_connect(func):
    @wraps(func)
    def inner(*args, **kwargs):
        conn = sqlite3.connect(db_path)  # 这条指令如果数据库不存在,会自动创建数据库
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        try:
            result = func(c, conn, *args, **kwargs)
        except sqlite3.Error:
            raise
        finally:
            conn.close()
        return result

    return inner


@pre_connect
def create_db_and_table(cursor, connect):  # try的重复代码太多了...
    for table in create_table_tuple:
        try:
            cursor.execute(table)
        except sqlite3.OperationalError:
            print('Error: create table: {}.'.format(table.split(' (')[0]))
            raise
    try:
        connect.commit()
    except sqlite3.Error:
        print('Error: commit data.')
        raise


@pre_connect
def insert_picture_base_info_from_download(cursor, connect, *args):
    # picture_id, p, date, file_type = args
    try:
        cursor.execute("INSERT INTO PICTURE (ID, PID, P, DATE, TYPE) VALUES (?, ?, ?, ?, ?)", args)
    except sqlite3.IntegrityError as e:
        print(e)
        pass
        # raise
    except sqlite3.Error:
        print('Error: commit data.')
        raise
    else:
        connect.commit()


@pre_connect
def update_picture_base_info(cursor, connect, picture_id, painter_id):
    try:
        cursor.execute('UPDATE PICTURE SET PID = {} WHERE ID = {}'.format(painter_id, picture_id))
    except sqlite3.Error:
        raise
    else:
        connect.commit()


@pre_connect
def insert_picture_info_from_PixivPictureInfo(cursor, connect, *args):
    try:
        print(args)
        if len(args) == 3:
            cursor.execute('INSERT INTO PICTURE_INFO (ID, Title, Introduction) VALUES (?, ?, ?)', args)
        elif len(args) == 2:
            cursor.execute('INSERT INTO PICTURE_INFO (ID, Title) VALUES (?, ?)', args)
    except sqlite3.IntegrityError as e:
        print(e)
        pass
        # raise
    except sqlite3.Error:
        raise
    else:
        connect.commit()


@pre_connect
def insert_painter_base_info_from_picture_detail_page(cursor, connect, *args):
    try:
        cursor.execute('INSERT INTO PAINTER (ID, Nickname) VALUES (?, ?)', args)
    except sqlite3.IntegrityError as e:
        print(e)
        pass
    except sqlite3.Error:
        print('Error: commit data.')
        raise
    else:
        connect.commit()


@pre_connect
def search_picture_base_info(cursor, connect, picture_id):
    try:
        cursor.execute('SELECT ID, PID, P, DATE, TYPE FROM PICTURE WHERE ID = {}'.format(picture_id))
    except sqlite3.Error:
        raise
    else:
        picture_base_info = cursor.fetchone()
        connect.commit()
        return picture_base_info


@pre_connect
def search_picture_info(cursor, connect, picture_id):
    try:
        cursor.execute('SELECT * FROM PICTURE_INFO WHERE ID = {}'.format(picture_id))
    except sqlite3.Error:
        raise
    else:
        picture_info = cursor.fetchone()
        connect.commit()
        return picture_info


@pre_connect
def insert_picture_info_from_picture_detail_page(cursor, connect, *args):
    try:
        cursor.execute('INSERT INTO PICTURE_INFO (ID, Title, Introduction, Bookmark) VALUES (?, ?, ?, ?)', args)
    except sqlite3.IntegrityError as e:
        print(e)
        # we should use UPDATE statement.
    except sqlite3.Error:
        raise
    else:
        connect.commit()


@pre_connect
def search_all_painter(cursor, connect, *args, **kwargs):
    try:
        cursor.execute('SELECT ID, Nickname FROM PAINTER')
    except sqlite3.Error:
        raise
    else:
        painter = cursor.fetchall()
        connect.commit()
        return painter


@pre_connect
def check_specific_painter(cursor, connect, painter_id):
    """
    Only check painter id exists.
    """
    try:
        cursor.execute('SELECT ID FROM PAINTER WHERE ID = {}'.format(painter_id))
    except sqlite3.OperationalError as e:
        print(e)
        return None
    except sqlite3.Error:
        raise
    else:
        painter_id = cursor.fetchone()
        connect.commit()
        return True if painter_id is not None else False


@pre_connect
def insert_painter_info(cursor, connect, *args, **kwargs):
    try:
        print(kwargs)
        cursor.execute('INSERT INTO PAINTER (ID, Nickname, Website, "Self introduction") VALUES (?, ?, ?, ?)',
                       (kwargs.get('ID'), kwargs.get('Nickname'), kwargs.get('Website'),
                        kwargs.get('Self introduction')))
        cursor.execute(
            'INSERT INTO EN_PERSONAL_INFO (ID, Gender, Location, Age, Birthday, Occupation) VALUES (?, ?, ?, ?, ?, ?)',
            (kwargs.get('ID'), kwargs.get('Gender'), kwargs.get('Location'), kwargs.get('Age'), kwargs.get('Birthday'),
             kwargs.get('Occupation'))
        )
        cursor.execute(
            'INSERT INTO CONTACTS (PAINTER_ID, Twitter, Instagram, Tumblr, Facebook, Skype, "Windows Live",'
            '"Google Talk", "Yahoo! Messenger", Circlems) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (kwargs.get('ID'), kwargs.get('Twitter'), kwargs.get('Instagram'), kwargs.get('Tumblr'),
             kwargs.get('Facebook'), kwargs.get('Skype'), kwargs.get('Windows Live'), kwargs.get('Google Talk'),
             kwargs.get('Yahoo! Messenger'), kwargs.get('Circlems'))
        )
    except sqlite3.IntegrityError as e:
        print(e)
    except sqlite3.Error:
        raise
    else:
        connect.commit()  # the function should be to close the cursor.


@pre_connect
def search_painter_info(cursor, connect, *args, painter_id=None, picture_id=None):
    try:
        if painter_id is not None:
            # cursor.execute(
            #     'SELECT * FROM PAINTER INNER JOIN EN_PERSONAL_INFO ON PAINTER.ID = EN_PERSONAL_INFO.ID '
            #     'INNER JOIN CONTACTS ON PAINTER.ID = CONTACTS.PAINTER_ID WHERE PAINTER.ID = {}'.format(
            #         painter_id))
            cursor.execute(
                'SELECT PAINTER.ID, Nickname, Website, "Self introduction", Gender, Location, Age, Birthday, '
                'Occupation, Twitter, Instagram, Tumblr, Facebook, Skype, "Windows Live", "Google Talk", '
                '"Yahoo! Messenger", '
                'Circlems FROM PAINTER INNER JOIN EN_PERSONAL_INFO ON PAINTER.ID = EN_PERSONAL_INFO.ID '
                'INNER JOIN CONTACTS ON PAINTER.ID = CONTACTS.PAINTER_ID WHERE PAINTER.ID = {}'.format(
                    painter_id))
        elif picture_id is not None:
            cursor.execute(
                'SELECT PAINTER.ID, Nickname, Website, "Self introduction", Gender, Location, Age, Birthday, '
                'Occupation, Twitter, Instagram, Tumblr, Facebook, Skype, "Windows Live", "Google Talk", '
                '"Yahoo! Messenger", '
                'Circlems FROM PAINTER INNER JOIN EN_PERSONAL_INFO ON PAINTER.ID = EN_PERSONAL_INFO.ID '
                'INNER JOIN CONTACTS ON PAINTER.ID = CONTACTS.PAINTER_ID WHERE '
                'PAINTER.ID = (SELECT PID FROM PICTURE WHERE ID = {})'.format(picture_id))
    except sqlite3.Error:
        raise
    else:
        painter_info = cursor.fetchone()
        connect.commit()
        return painter_info


@pre_connect
def delete_picture_base_info(cursor, connect, picture_id):
    try:
        cursor.execute('DELETE FROM PICTURE WHERE ID = {}'.format(picture_id))
    except sqlite3.Error:
        raise
    else:
        connect.commit()


if __name__ == '__main__':
    s = picture_base_info = search_picture_base_info(60778836)
    print(s.keys())
    print(*s)
    # picture_info = search_picture_info(60778836)
    # print(picture_base_info, picture_info)
    # delete_picture_base_info(picture_id=67313183)
    # x = search_painter_info(picture_id=60960684)
    x = search_painter_info(painter_id=1655331)
    print(x.keys())
    # print(x.keys())
    # print(*x)
    # x = search_painter()
    # print(x)
    # for k in x:
    #     for j in k:
    #         print(j, k.keys())
    z = search_painter_info(painter_id=12321321312)
    print(z)
    pass
