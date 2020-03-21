import osmnx as ox
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import geojson
import json
from shapely.geometry import shape


def calc_xy(phi_deg, lambda_deg, phi0_deg, lambda0_deg):
    """ 緯度経度を平面直角座標に変換する
    - input:
        (phi_deg, lambda_deg): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
    - output:
        x: 変換後の平面直角座標[m]
        y: 変換後の平面直角座標[m]
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi_rad = np.deg2rad(phi_deg)
    lambda_rad = np.deg2rad(lambda_deg)
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. ) 
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])

    def alpha_array(n):
        a0 = np.nan # dummy
        a1 = (1./2)*n - (2./3)*(n**2) + (5./16)*(n**3) + (41./180)*(n**4) - (127./288)*(n**5)
        a2 = (13./48)*(n**2) - (3./5)*(n**3) + (557./1440)*(n**4) + (281./630)*(n**5)
        a3 = (61./240)*(n**3) - (103./140)*(n**4) + (15061./26880)*(n**5)
        a4 = (49561./161280)*(n**4) - (179./168)*(n**5)
        a5 = (34729./80640)*(n**5)
        return np.array([a0, a1, a2, a3, a4, a5])

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999 
    a = 6378137.
    F = 298.257222101

    # (1) n, A_i, alpha_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    alpha_array = alpha_array(n)

    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0] # [m]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) ) # [m]

    # (3) lambda_c, lambda_sの計算
    lambda_c = np.cos(lambda_rad - lambda0_rad)
    lambda_s = np.sin(lambda_rad - lambda0_rad)

    # (4) t, t_の計算
    t = np.sinh( np.arctanh(np.sin(phi_rad)) - ((2*np.sqrt(n)) / (1+n))*np.arctanh(((2*np.sqrt(n)) / (1+n)) * np.sin(phi_rad)) )
    t_ = np.sqrt(1 + t*t)

    # (5) xi', eta'の計算
    xi2  = np.arctan(t / lambda_c) # [rad]
    eta2 = np.arctanh(lambda_s / t_)

    # (6) x, yの計算
    x = A_ * (xi2 + np.sum(np.multiply(alpha_array[1:],
                                       np.multiply(np.sin(2*xi2*np.arange(1,6)),
                                                   np.cosh(2*eta2*np.arange(1,6)))))) - S_ # [m]
    y = A_ * (eta2 + np.sum(np.multiply(alpha_array[1:],
                                        np.multiply(np.cos(2*xi2*np.arange(1,6)),
                                                    np.sinh(2*eta2*np.arange(1,6)))))) # [m]
    # return
    return x, y # [m]



def culc_weight(start_pos, end_pos):
    """入力した値から2地点間のユークリッド距離を返す関数
    -input:
        start_pos, end_pos : 長さ2の配列　[x座標, y座標]
    
    -output:
        weight : start_pos, end_pos間のユークリッド距離
    """
    weight = ((start_pos[0] - end_pos[0])**2 + (start_pos[1] - end_pos[1])**2)**0.5
    
    return weight


# 座標変換のときの中心緯度経度を求める関数
def culc_center_latlon(G_osm):

    max_x = np.array(list(G_osm.nodes(data='x'))).max(axis=0)[1]
    min_x = np.array(list(G_osm.nodes(data='x'))).min(axis=0)[1]
    max_y = np.array(list(G_osm.nodes(data='y'))).max(axis=0)[1]
    min_y = np.array(list(G_osm.nodes(data='y'))).min(axis=0)[1]

    return [ (max_y+min_y)/2, (max_x+min_x)/2 ]


def G_geo_to_G_xy(G_geo, locating_point):
    """xy座標かつノード番号が0から通し番号のグラフを作成(無効グラフ)
    -input:
        G_geo : osmnxから作成されたnetworkxのグラフ
        locationg_point : 緯度経度変換の際に中心にする地点の緯度経度 [緯度, 経度]
        
    -output:
        G_xy : xy座標系に変換済みかつノード番号を通しで振っている道路網ネットワーク
        reverse_dict : 変換後のノード番号numの変換前のノード番号がわかる辞書
    """
    G_xy = nx.Graph()
    
    G_geo_all_node = dict(G_geo.nodes)
    G_geo_all_edge= dict(G_geo.edges)
    
    num = 0
    change_dict = {}
    reverse_dict = {}
    
    for i in G_geo_all_node:
        
        change_dict[i] = num
        reverse_dict[num] = i
        
        x = G_geo_all_node[i]['x']
        y = G_geo_all_node[i]['y']
        
        d_x,d_y = calc_xy(y, x, locating_point[0], locating_point[1])
        G_xy.add_node(num,pos=[round(d_y,4),round(d_x,4)], latlon=[y,x])
        
        num += 1
        
    G_xy_all_node = dict(G_xy.nodes)
    
    for i in G_geo_all_edge:
        
        start_node = change_dict[i[0]]
        end_node = change_dict[i[1]]
        #weight = culc_weight(G_xy_all_node[start_node]['pos'], G_xy_all_node[end_node]['pos'])
        
        G_xy.add_edge(start_node,end_node)
    
    return G_xy, reverse_dict



def remove_G(G, remove_node, new_edge):
    """グラフから配列で与えられたノードとエッジを削除し，新しいエッジを張る
    -input:
        G : グラフ
        remove_node : 削除するノード
        new_edge : 新たに結びなおすエッジ
    -output:
        G : 変更後のグラフ
    """
    
    G_all_node = dict(G.nodes)
    
    G.remove_node(remove_node)
        
    #weight = culc_weight(G_all_node[new_edge[0]]['pos'], G_all_node[new_edge[1]]['pos'])
    #G.add_edge(new_edge[0],new_edge[1],weight=weight)
    
    return G



def renumber(G):
    
    """ノード番号を振りなおす関数"""
    
    new_G = nx.Graph()
    all_node = dict(G.nodes)
    all_edge= dict(G.edges)
    
    num = 0
    change_dict = {}
    
    for i in all_node:
        
        change_dict[i] = num
        
        x = all_node[i]['pos']
        y = all_node[i]['latlon']
        new_G.add_node(num,pos=x, latlon=y)
        
        num += 1
    
    # 辺の長さは計算しない
    """
    for i in all_edge:
        
        start_node = change_dict[i[0]]
        end_node = change_dict[i[1]]
        weight = all_edge[i]['weight']
        
        new_G.add_edge(start_node,end_node,weight=weight)
    """
    
    return new_G


def calc_degree(start_1, end_1, start_2, end_2):
    """4地点の座標から角度を計算する関数
    -input:
        start_1, end_1 : 1つめの直線の通過する2地点の座標 [x座標, y座標]
        start_2, end_2 : 2つめの直線の通過する2地点の座標 [x座標, y座標]
    -output:
        2直線のなす角度
    """
    # 1つ目の直線を表すベクトルの作成
    vector_1 = [ i - j for i,j in zip(start_1, end_1)]
    
    # 2つ目の直線を表すベクトルの作成
    vector_2 = [ i - j for i,j in zip(start_2, end_2)]
    
    # 2つのベクトルの内積を計算
    inner_product = np.dot(vector_1, vector_2)
    
    # ベクトルの長さを計算
    length_1 = np.linalg.norm(vector_1)
    length_2 = np.linalg.norm(vector_2)
    
    # 2つのベクトルがなす角度のcosの値を計算
    cos_theta = inner_product / (length_1 * length_2)
    
    radian = math.acos(cos_theta)
    
    degree = math.degrees(radian)
    
    return degree


def recreate_G(G, limit_degree):
    """ノードの次数とリンクの角度をもとにネットワークを単純化する関数"""
    
    # 全ノードの次数の辞書を作成
    node_order = dict(nx.degree(G))
    
    # 枝葉ノードの削除
    """one_order_nodes = [key for key, item in node_order.items() if item==1]

    while len(one_order_nodes) != 0:
        
        for i in one_order_nodes:
            G.remove_node(i)
        
        node_order = dict(nx.degree(G))
        one_order_nodes = [key for key, item in node_order.items() if item==1]
    """
    
    # 全ノードの辞書作成
    all_nodes = dict(G.nodes)
    
    # 次数が2であるノードのリストを作成
    two_order_nodes = [key for key, item in node_order.items() if item==2]
    
    for i in two_order_nodes:
        
        neighbors_node = list(G.neighbors(i))
        
        start_1, start_2 = all_nodes[i]['pos'], all_nodes[i]['pos']
        end_1 = all_nodes[neighbors_node[0]]['pos']
        end_2 = all_nodes[neighbors_node[1]]['pos']
        
        # ベクトルの角度がlimit_degreeを超えたとき
        if calc_degree(start_1, end_1, start_2, end_2) > limit_degree:
            
            new_edge = neighbors_node
            remove_G(G, i, new_edge)

    return G



def G_to_JSON(G):
    """
    ネットワークの情報をJSONに落とす関数
    -input:
        G : networkxのGraph
    -output:
        g_json : nodeとedgeが保存されたJSON
        {
            'node':[
                { 'id':0, 'pos':[65.4677, 23.3979], 'latlon':[35.67867, 139.564] },
                ...
            ],
            'edge': [
                {'id':0, 'head': 0, 'tail':1 },
            ]
        }
    """

    all_nodes = dict(G.nodes())

    # ノードのjsonを作成
    node_json = [
        {'id':index, 'pos':item['pos'], 'latlon':item['latlon']}
        for index, item in all_nodes.items()
    ]

    # エッジのjsonを作成
    edge_json = [
        {'id':i, 'head':list(edge)[0], 'tail':list(edge)[1]}
        for i, edge in enumerate(list(G.edges()))
    ]

    # jsonにまとめて整形
    g_json = {'node':node_json, 'edge':edge_json}

    return g_json


def JSON_to_G(json):
    """
    JSON(dict型)からnetworkxのグラフを生成する関数
    - input
        json:{
            'node':[
                {'id':0, 'pos':[65.4677, 23.3979], 'latlon':[35.67867, 139.564]},
                ...
            ],
            'edge':[{'id':0, 'head': 0, 'tail':1 }, ...]
        }
    - output:
        G: networkxのグラフ
    """
    # グラフインスタンスを作成
    G = nx.Graph()

    # リストからノードを追加
    node_list = [ (node['id'], {'pos':node['pos'], 'latlon':node['latlon']}) for node in json['node'] ]
    G.add_nodes_from(node_list)

    # リストからエッジを追加
    edge_list = [ tuple([edge['head'], edge['tail']]) for edge in json['edge'] ]
    G.add_edges_from(edge_list)

    return G

def G_to_Dataframe(G):
    
    """ネットワークの情報をデータフレームに落とす関数"""
    
    cols = ['node', 'x','y']
    node_df = pd.DataFrame(index=[], columns=cols)
    
    cols = ['start','end']
    edge_df = pd.DataFrame(index=[], columns=cols)
    
    all_node = dict(G.nodes)
    all_edge = dict(G.edges)
    
    for i in all_node:
        
        x = all_node[i]['pos'][0]
        y = all_node[i]['pos'][1]
        record = pd.Series([i,x,y], index=node_df.columns)
        
        node_df = node_df.append(record, ignore_index=True)
        
    for i in all_edge:
        
        record = pd.Series(i, index=edge_df.columns)
        edge_df = edge_df.append(record, ignore_index=True)
        
    return node_df,edge_df