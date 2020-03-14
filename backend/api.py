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


# loginを扱うapi(POSTメソッド)
post_geojson_bp = Blueprint('post_geojson', __name__, url_prefix='/api/post')
class Post_GeoJson(Resource):
    def post(self):
        
        # データをフロントエンドから受け取る
        input_data = request.json
        print(type(input_data))

        # 辞書 -> 文字列 -> geojsonに変換
        src = json.dumps(input_data)
        src = geojson.loads(src)
        print(type(src))

        # shapelyのポリゴン形式に変更
        ftr = src.get('features')[0]
        polygon = shape(ftr.get('geometry'))

        # ポリゴンからnetworkxオブジェクトを生成
        G_osm = ox.graph_from_polygon(polygon, simplify=False, network_type='drive')

        # xy座標系に変換
        # 変換の際の中心座標
        locating_point = fnc.culc_center_latlon(G_osm)
        print(locating_point)
        G, _ = fnc.G_geo_to_G_xy(G_osm, locating_point)

        del G_osm
        gc.collect()

        print(dict(G.nodes()))

        # limit
        limit_degree = 150
        simplify_G = fnc.recreate_G(G, 150)
        simplify_G = fnc.renumber(simplify_G)

        del G
        gc.collect()

        print(dict(simplify_G.nodes()))

        return_data = {'done':0}

        return jsonify(return_data)

post_geojson = Api(post_geojson_bp)
post_geojson.add_resource(Post_GeoJson, '')