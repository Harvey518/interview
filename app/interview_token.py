#!/usr/bin/env python
# encoding: utf-8


'''
@software: pycharm
@version: python3.7
@file: interview_token.py
@time: 2021/5/8
@desc:
'''
import re
import pymysql
import functools
from flask_sqlalchemy import SQLAlchemy
from flask import request,jsonify, Flask
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from settings import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS



pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SECRET_KEY']='eh2s2334ssdfcr3t'
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class UsersTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(50))

db.create_all()


def create_token(api_user):
    '''
    生成token
    :param api_user:用户id
    :return: token
    '''

    s = Serializer(app.config["SECRET_KEY"],expires_in=3600)
    access_token = s.dumps({"username":api_user}).decode("ascii")
    s = Serializer(app.config["SECRET_KEY"],expires_in=7200)
    refresh_token = s.dumps({"username":api_user}).decode("ascii")
    return access_token, refresh_token

def verify_token(token):
    '''
    校验token
    :param token:
    :return: 用户信息 or None
    '''

    #参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(app.config["SECRET_KEY"])
    try:
        #转换为字典
        data = s.loads(token)
    except Exception:
        return None
    #拿到转换后的数据，根据模型类去数据库查询用户信息
    user = UsersTest.query.filter(UsersTest.username == data['username']).first()
    return user


def login_required(view_func):
    @functools.wraps(view_func)
    def verify_token(*args,**kwargs):
        try:
            #在请求头上拿到token
            token = request.headers["Authorization"].split(' ')[1]
        except Exception:
            #没接收的到token,给前端抛出错误
            #这里的code推荐写一个文件统一管理。这里为了看着直观就先写死了。
            return jsonify(code = 4103,msg = '缺少参数token')

        s = Serializer(app.config["SECRET_KEY"])
        try:
            s.loads(token)
        except Exception:
            return jsonify(code = 4101,msg = "登录已过期")

        return view_func(*args,**kwargs)

    return verify_token

@app.route('/register', methods=['POST'])
def register():
    '''
    用户注册
    :return:
    '''
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    if not all([username, password, phone, first_name, last_name]):
        return jsonify(code=4102, msg="缺少注册参数")

    if not re.match(r"\+86-1[23456789]\d{9}",phone):
        return jsonify(code=4103,msg="手机号有误")

    user = UsersTest.query.filter(UsersTest.username == username).first()
    if user:
        return jsonify(code=4105,msg="该用户名已被注册")

    user = UsersTest(username=username, password=password, phone=phone, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return jsonify(code=0,msg="注册成功")

@app.route("/token", methods=["POST"])
def token():
    '''
    用户获取token
    :return:token
    '''
    res_dir = request.get_json(force=True)
    if res_dir is None:
        #这里的code，依然推荐用一个文件管理状态
        return jsonify(code = 4103,msg = "未接收到参数")

    #获取前端传过来的参数
    phone = res_dir.get("mobile")
    otp = res_dir.get("otp")
    #校验参数
    if not all([phone,otp]):
        return jsonify(code=4103, msg="请填写手机号或otp")

    if not re.match(r"\+86-1[23456789]\d{9}",phone):
        return jsonify(code=4103,msg="手机号有误")

    user = UsersTest.query.filter_by(phone=phone).first()
    if not user:
        return jsonify(code=4004,msg="该手机号未注册")
    access_token, refresh_token = create_token(user.username)
    return jsonify(access_token=access_token, refresh_token=refresh_token, expiry=12345)


@app.route("/profile", methods=['GET'])
@login_required
def userInfo():
    '''
    用户信息
    :return:data
    '''
    token = request.headers["Authorization"].split(' ')[1]
    #拿到token，去换取用户信息
    user = verify_token(token)
    return jsonify(id=user.id, first_name=user.first_name, last_name=user.last_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port='8778')

