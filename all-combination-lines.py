"""
アクティブレイヤーのポイントに対して、総当たりのラインを作成するスクリプトです。
一列目のフィールドのIDをもとにポイントのペアを作成しラインを作成します。
そのため、スクリプト実行前に、ポイントレイヤのフィールドに連番IDを割り当ててください。
連番IDが付与されていない場合にはフィールド計算機より、式に「　$id　」と入力しIDを割り当ててください。フィールド名は何でもOKです。
その後、上部メニューの「プロセシング」より「ツールボックス」を選択し、
「ベクターテーブル」より「属性のリファクタリング」を起動し、
作成した連番IDのフィールドを一番左（一番上）に移動させてください。
上記準備が完了した後、本スクリプトを実行してください。

なお、元となるポイントレイヤのCRSが設定されていない場合には、CRSを設定してから実行してください。
"""

import itertools

id_list = []
point_name_index = 0

# アクティブレイヤーのＩＤ読み取りとid_listへの追加
layer = iface.activeLayer()
features = layer.getFeatures()
for feature in features:
    id_list.append(feature[0])

# ＩＤ組み合わせ（新規ラインリスト）作成
combo_id = itertools.combinations(id_list, 2)
combo_id_list = list(combo_id)

# ジオメトリの辞書作成
geom_dict = {}
points = layer.getFeatures()
for p in points:
    geom = p.geometry()
    attrs = p.attributes()
    p = geom.asPoint()
    key = attrs[point_name_index]
    geom_dict[str(key)] = p #attrs[point_name_index] = name field

# レイヤーの作成
crs = layer.crs().authid()
new_layer = QgsVectorLayer('LineString?crs='+crs, 'New lines ', 'memory')
pr = new_layer.dataProvider()

# フィールドの追加
new_layer.startEditing()
pr.addAttributes([QgsField("From", QVariant.Int),
                    QgsField("To",  QVariant.Int)])
new_layer.updateFields() # tell the vector layer to fetch changes from the provider

# フィーチャーの作成
for line in combo_id_list:
    frPoint = geom_dict[str(line[0])]
    toPoint = geom_dict[str(line[1])]
    attrs = [line[0], line[1]] 
    new_line = QgsGeometry.fromPolyline([QgsPoint(frPoint), QgsPoint(toPoint)])
    feature = QgsFeature()
    feature.setGeometry(new_line)
    feature.setAttributes(attrs)
    pr.addFeatures([feature])
    new_layer.commitChanges()
    new_layer.updateExtents()

# 新規レイヤの描画
QgsProject.instance().addMapLayer(new_layer)