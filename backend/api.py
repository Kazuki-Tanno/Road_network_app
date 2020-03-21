# 分離する側でBlueprintを用意して，それをメインのFlaskオブジェクトに登録する

from flask import Blueprint, jsonify, request, session
from flask_restful import Api, Resource
import time
import requests
import json
import osmnx as ox
import networkx as nx
import numpy as np
import geojson
from shapely.geometry import shape
import gc

# 自作モジュール
import functions as fnc


# geojsonを受け取るapi(POSTメソッド)
# ネットワークを作成し，Statusを返す
post_geojson_bp = Blueprint('post_geojson', __name__, url_prefix='/api/post_geojson')
class Post_GeoJson(Resource):
    def post(self):
        
        try:
            # データをフロントエンドから受け取る
            input_data = request.json

            # 辞書 -> 文字列 -> geojsonに変換
            src = json.dumps(input_data)
            src = geojson.loads(src)

            # shapelyのポリゴン形式に変更
            ftr = src.get('features')[0]
            polygon = shape(ftr.get('geometry'))

            # ポリゴンからnetworkxオブジェクトを生成
            G_osm = ox.graph_from_polygon(polygon, simplify=False, network_type='drive')

            # xy座標系に変換
            # 変換の際の中心座標
            locating_point = fnc.culc_center_latlon(G_osm)
            G, _ = fnc.G_geo_to_G_xy(G_osm, locating_point)

            del G_osm
            gc.collect()

            # ネットワークをjson形式に変更
            graph_json = fnc.G_to_JSON(G)
            
            # session変数に基礎ネットワークを作成済みかを入力
            session['done_network'] = 1

            # すべてが成功した場合
            return_data = {
                'Status':1,
                'Network':graph_json
            }

        except:
            # エラーの場合
            return_data = {'Status':0}
        

        """# limit
        limit_degree = 150
        simplify_G = fnc.recreate_G(G, 150)
        simplify_G = fnc.renumber(simplify_G)

        del G
        gc.collect()

        print(dict(simplify_G.nodes()))
        """

        return jsonify(return_data)

post_geojson = Api(post_geojson_bp)
post_geojson.add_resource(Post_GeoJson, '')


# json形式のネットワークを受け取るapi(POSTメソッド)/実験用
# json -> Graph -> jsonに変換し，齟齬がないか検証
ts_test_bp = Blueprint('ts_test', __name__, url_prefix='/api/ts_test')
class Ts_test(Resource):
    def post(self):
        
        # データをフロントエンドから受け取る
        input_data = request.json

        # ネットワークを生成
        G = fnc.JSON_to_G(input_data)
        
        # ネットワークからJsonを生成
        return_data = fnc.G_to_JSON(G)

        return jsonify(return_data)

ts_test = Api(ts_test_bp)
ts_test.add_resource(Ts_test, '')