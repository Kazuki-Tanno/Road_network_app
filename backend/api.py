# 分離する側でBlueprintを用意して，それをメインのFlaskオブジェクトに登録する

from flask import Blueprint, jsonify, request, session
from flask_restful import Api, Resource
import time
import requests
import json


# loginを扱うapi(POSTメソッド)
post_geojson_bp = Blueprint('post_geojson', __name__, url_prefix='/api/post')
class Post_GeoJson(Resource):
    def post(self):
        
        # データをフロントエンドから受け取る
        input_data = request.json

        if 'status' in input_data:
            return_data = {'IsStatus':1}
        else:
            return_data = {'IsStatus':0}

        return jsonify(return_data)

post_geojson = Api(post_geojson_bp)
post_geojson.add_resource(Post_GeoJson, '')