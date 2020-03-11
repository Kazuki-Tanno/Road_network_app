# 分離する側でBlueprintを用意して，それをメインのFlaskオブジェクトに登録する

from flask import Blueprint, jsonify, request, session
from flask_restful import Api, Resource
import time
import requests
import json
import pickle

# データベースから店舗情報を持ってくるapi
get_user_bp = Blueprint('get_user', __name__, url_prefix='/data_api/user_get')
class ReturnShopData(Resource):
    def get(self):

        # Databaseインスタンスを作成
        db = firebase.database()

        # DBの値を取得(Pyrebase Respons型)
        data = db.child("shop_info").get()

        # val()でOrderedDict型に変換することができる
        print(type(data.val()))

        # json形式に変換して返す
        return jsonify(data.val())

get_user = Api(get_user_bp)
get_user.add_resource(ReturnShopData, '')


# loginを扱うapi(POSTメソッド)
login_bp = Blueprint('login', __name__, url_prefix='/data_api/login')
class Login(Resource):
    def post(self):
        
        # 認証インスタンスを作成
        auth = firebase.auth()

        # postされたデータを読み込み
        input_data = request.json
        mail_address = input_data['mail_address']
        password = input_data['password']

        # 認証を試みる
        try:
            user = auth.sign_in_with_email_and_password(mail_address, password)
            session['flag'] = True
            session['usr'] = mail_address
            session['auth'] = user
            
            # ログイン可能を返す
            return_data = {'CanLogin':1}

            return jsonify(return_data)

        # 認証できなかった場合
        except:
            # ログイン不可能を返す
            return_data = {'CanLogin':0}

            return jsonify(return_data)

login = Api(login_bp)
login.add_resource(Login, '')


# mypageにおいてログイン済みかを判断するapi
mypage_init_bp = Blueprint('mypage_init', __name__, url_prefix='/data_api/mypage_init')
class Mypage_init(Resource):
    def get(self):

        if 'flag' in session and session['flag']:
            
            return jsonify({'DoneLogin':1})

        else:

            return jsonify({'DoneLogin':0})

mypage_init = Api(mypage_init_bp)
mypage_init.add_resource(Mypage_init, '')


# mypageでのデータのやり取りを行うapi
# セッション変数から認証の要素を取り出す
data_update_bp = Blueprint('data_update', __name__, url_prefix='/data_api/data_push')
class Data_push(Resource):
    def post(self):

        db = firebase.database()
        input_data = request.json

        congestion = input_data['congestion']

        user_id = session['auth']['localId']

        db.child("shop_info").child(user_id).update({"congestion": congestion}, session['auth']['idToken'])

        data = db.child("shop_info").child(user_id).get()
        
        return jsonify(data.val())

data_update = Api(data_update_bp)
data_update.add_resource(Data_push, '')