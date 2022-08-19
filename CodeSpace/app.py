# coding:utf-8
import configparser
import json
import os
import shutil
import sys
import zipfile


from flask import Flask, url_for, request, jsonify, render_template, redirect, send_from_directory
from CodeSpace.lib import mongodb_tools


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads/"
mdb_ctrl = None


@app.route("/", methods=["GET"])
@app.route("/index/", methods=["GET"])
# 主页
def index():
    cp = configparser.ConfigParser()
    cp.read("./space_info.ini", encoding="utf-8-sig")
    code_count = int(cp.get("CodeSpace_Info", "cs_count"))
    return render_template("index.html", code_count=code_count)


@app.route("/code_data/", methods=["POST", "PUT", "DELETE"])
# 数据的新增，修改，删除
def code_data():
    # ini文件解析
    cp = configparser.ConfigParser()
    cp.read("./space_info.ini", encoding="utf-8-sig")

    # 仓库代码数量
    count = int(cp.get("CodeSpace_Info", "cs_count"))

    if request.method == "POST":
        # 新增
        count += 1

        save_code_info(request=request)

        # 更新记录文件(.ini)
        cp.set("CodeSpace_Info", "cs_count", str(count))
        cp.write(open("./space_info.ini", "w"))

        # 返回成功信息(json)
        return jsonify({"upload_status": "true"})

    elif request.method == "PUT":
        # 修改
        if mdb_ctrl.del_by_id(request.form['_id'], request.form['old_type']) == 'ok':
            save_code_info(request=request)

            path_dir = os.getcwd().replace('\\', '/') + r"/uploads/{}/{}/".format(request.form['old_type'],
                                                                                  request.form['_id'])
            if os.path.isdir(path_dir):
                remove_files(path_dir)

            return jsonify({'update_status': 'true'})
        else:
            return jsonify({'update_status': 'false'})

    elif request.method == "DELETE":
        # 删除
        print(request.form['d_id'], request.form['d_type'])
        if mdb_ctrl.del_by_id(request.form['d_id'], request.form['d_type']) == 'ok':
            path_dir = os.getcwd().replace('\\', '/') + r"/uploads/{}/{}/".format(request.form['d_type'],
                                                                                  request.form['d_id'])
            if os.path.isdir(path_dir):
                remove_files(path_dir)
            count -= 1
            # 更新记录文件(.ini)
            cp.set("CodeSpace_Info", "cs_count", str(count))
            cp.write(open("./space_info.ini", "w"))
            return jsonify({'del_status': 'true'})
        else:
            return jsonify({'del_status': 'false'})


def remove_files(rootdir):
    filelist = os.listdir(rootdir)
    for f in filelist:
        filepath = os.path.join(rootdir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(filepath + " removed!")

        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)
            print("dir " + filepath + " removed!")
    shutil.rmtree(rootdir, True)
    print("root dir removed!")


def save_code_info(request):
    # 新增的信息
    dict_code_info = {"code_name": request.form["code_name"], "code_type": request.form["code_type"],
                      "code_des": request.form["code_des"], "code_cnt": request.form["code_cnt"],
                      "code_file": "false"}
    # 上传的文件信息
    uploaded_files = request.files.getlist("code_files")

    # 判断是否有无文件 上传 打标记位
    if request.files["code_files"]:
        dict_code_info["code_file"] = "true"
    else:
        dict_code_info["code_file"] = ""

    one_id = str(mdb_ctrl.insert(codeData=dict_code_info))
    dir_path = app.config["UPLOAD_FOLDER"] + dict_code_info["code_type"] + "/" + \
                one_id + "/"

    # 判断有无文件上传 并保存文件
    if request.files["code_files"]:
        # 创建文件夹
        os.makedirs(dir_path)
        # 循环保存文件
        for file in uploaded_files:
            filename = file.filename
            # 保存文件
            file.save(os.path.join(dir_path, filename))
        zip_dir(dir_path, dir_path + '{}.zip'.format(one_id))

        for file in uploaded_files:
            path = os.path.join(dir_path, file.filename)
            os.remove(path)


@app.route("/search_data/", methods=["POST"])
# 提交要查询的数据，展示查询结果
def search_data():
    res_list = []
    if request.method == "POST":
        para = search_data_analysis(request.form["search_data"])
        if len(para["text"]) == 0:
            return jsonify({"search_status": "false"})
        print(para)
        res = mdb_ctrl.find(para=para)
        print("END-----")

        for r in res.values():
            res_list.append(r)

        res.clear()
        res["res"] = res_list

        with open(sys.path[0] + r"\CodeSpace\tmp\code.json", "w", encoding="utf-8") as f:
            f.write(str(res).replace('\'', '"'))

    return render_template("search_res.html", code_collection=",".join(para["in"])
                           , in_text=",".join(para["+"])
                           , not_in_text=",".join(para["-"])
                           , text_cnt=",".join(para["text"]))
    # return jsonify({"search_status": "true"})


@app.route("/load_more/", methods=["POST"])
def load_more():
    if request.method == 'POST':
        if int(request.form['next']) <= 5:
            with open(sys.path[0] + r"\CodeSpace\tmp\code.json", "r", encoding="utf-8") as f:
                load_dict = json.load(f)
                print(load_dict)

            if len(load_dict['res']) == 0:
                return jsonify({"get_more_status": "empty"})

            if len(load_dict['res']) > int(request.form['next']):
                load_more_cnt = int(request.form['next'])
            else:
                load_more_cnt = len(load_dict['res'])

            if load_more_cnt == 0:
                return jsonify({"get_more_status": "end"})

            with open("./static/code_info.html", "r", encoding="utf-8") as f:
                str_res = f.read()
            str_res_copy = str_res
            res_list_str = ''

            for i in range(0, load_more_cnt, 1):
                c_id = load_dict['res'][i]['_id']
                c_name = load_dict['res'][i]['code_name']
                c_type = load_dict['res'][i]['code_type']
                c_des = load_dict['res'][i]['code_des']
                c_cnt = load_dict['res'][i]['code_cnt']
                c_file = load_dict['res'][i]['code_file']

                str_tmp = ''

                if len(c_file) > 0:
                    str_tmp = str_res.replace('__FILE__', '<a href="/uploads/__TYPE__/__ID__" style="display: block; '
                                                          'float: right;">  下载附件</a>')
                else:
                    str_tmp = str_res.replace('__FILE__', '<p style="display: block; float: right;">  无附件</p>')

                str_tmp = str_tmp.replace('__ID__', c_id).replace('__NAME__', c_name).replace('__TYPE__', c_type) \
                    .replace('__DES__', c_des).replace('__CNT__', c_cnt).replace('__TYPE__', c_type)

                res_list_str += str_tmp

                str_res = str_res_copy

            for i in range(0, load_more_cnt, 1):
                load_dict['res'].pop(0)

            with open(sys.path[0] + r"\CodeSpace\tmp\code.json", "w", encoding="utf-8") as f:
                f.write(str(load_dict).replace('\'', '"'))

            return jsonify({"code_info": res_list_str})
        else:
            return jsonify({"get_more_status": "false"})


@app.route("/uploads/<type>/<id>", methods=["GET"])
def download_files(type, id):
    if request.method == 'GET':
        dri_path = app.config["UPLOAD_FOLDER"] + r"{}/{}/".format(type, str(id))
        print(type, id)
        print(dri_path)
        return send_from_directory(dri_path, filename="{}.zip".format(str(id)), as_attachment=True)


def search_data_analysis(cmd):
    raw_para_list = cmd.strip().split(" ")
    # 去除空元素
    para_list = [i for i in raw_para_list if i != ""]

    search_para = {"+": [], "-": [], "in": [], "text": []}

    for pl in para_list:
        if pl[0] == "+":
            search_para["+"].append(pl[1:len(pl)])
        elif pl[0] == "-":
            search_para["-"].append(pl[1:len(pl)])
        elif pl[0] == "i" and pl[1] == "n" and pl[2] == ":":
            search_para["in"].append(pl[3:len(pl)])
        else:
            search_para["text"].append(pl)
    return search_para


def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        # print arcname
        zf.write(tar, arcname)
    zf.close()


mdb_ctrl = mongodb_tools.MongoDBCtrl()
