# coding: utf-8
import configparser
import re
from bson.objectid import ObjectId
import pymongo
import pandas as pd
import os
import datetime


class MongoDBCtrl:
    mongodbClient = None
    collection = None
    usingDataBase = None
    usingCollection = None
    runMode = False

    def __init__(self):
        cp = configparser.ConfigParser()
        cp.read("./config.ini", encoding="utf-8-sig")
        self.mongodbHost = cp.get("MongoDB", "mongodbHost")
        self.mongodbDBName = cp.get("MongoDB", "database")
        self.mongodbPort = int(cp.get("MongoDB", "mongodbPort"))
        self.runMode = cp.get('MongoDB', 'runtest')

        self.mongodb_init(savePare=self.mongodbDBName)

    def mongodb_init(self, savePare):
        # 初始化mongodb
        self.mongodbClient = pymongo.MongoClient(host=self.mongodbHost, port=self.mongodbPort)
        self.usingDataBase = self.mongodbClient[savePare]
        print("[~]MongoDB连接信息\n\t连接地址：{}\n\t连接端口：{}\n\t连接数据库：{}".format(self.mongodbHost, self.mongodbPort, savePare))
        print("[~]MongoDB连接已经建立")
        if self.runMode == 'true':
            print('[~]测试模式')
        # print("[~]MongoDB连接成功信息：\n\t存在的数据库：{}".format(self.mongodbClient.list_database_names()))

    def insert(self, codeData={"": ""}):
        self.usingCollection = self.usingDataBase[codeData["code_type"]]
        objectId = self.usingCollection.insert_one(document=codeData).inserted_id
        print("[~]数据插入MongoDB完成")
        return objectId

    def update(self, codeData={"": ""}):
        myquery = {"code_name": codeData["code_name"]}
        newvalues = {"$set": codeData}
        print(myquery, newvalues)
        self.usingCollection = self.usingDataBase[codeData["code_type"]]
        objectId = self.usingCollection.update_one(myquery, newvalues).inserted_id
        print("[~]数据插入MongoDB完成")
        return objectId

    def find(self, para=[]):
        res = {}
        if len(para["in"]) == 0:
            print("[~]没有指定数据集")
            list_collection_name = self.usingDataBase.collection_names()
            ex_collection_name = ['space_info']
            para["in"] = list(set(list_collection_name).difference(set(ex_collection_name)))
        else:
            print("[~]指定了{}个数据集".format(str(len(para["in"]))))

        # 遍历数据集
        for usingCollectionNam in para["in"]:
            print("[~]现在查询的数据集：{}".format(usingCollectionNam))
            self.usingCollection = self.usingDataBase[usingCollectionNam]
            self.usingCollection.find()
            # 查找文本不为空
            if para["text"][0] == '*':
                for p_text in para["text"]:
                    print("[~]待查询文本：{}".format(p_text))
                    for u in self.usingCollection.find():
                        u["_id"] = str(u["_id"]).replace("ObjectId(", "").replace(")", "")
                        res[str(u["_id"]).replace("ObjectId(", "").replace(")", "")] = u
            elif para["text"]:
                for p_text in para["text"]:
                    print("[~]待查询文本：{}".format(p_text))
                    for u in list(self.usingCollection.find({"code_name": re.compile(u"{}".format(p_text))})) \
                            + list(self.usingCollection.find({"code_des": re.compile(u"{}".format(p_text))})):
                        check_flag = True
                        print("结果---")
                        print(u)
                        print("   ----")
                        print("1.check_flag:", check_flag)
                        # 判断是否有+
                        if para["+"]:
                            for p_in in para["+"]:
                                print(p_in, p_in in u["code_name"], p_in in u["code_des"])
                                if p_in not in u["code_name"] or p_in not in u["code_des"]:
                                    check_flag = False
                                    break
                        print("2.check_flag:", check_flag)

                        if para["-"]:
                            for p_not_in in para["-"]:
                                print(p_not_in, p_not_in in u["code_name"], p_not_in in u["code_des"])
                                if p_not_in in u["code_name"] or p_not_in in u["code_des"]:
                                    check_flag = False
                                    break
                        print("3.check_flag:", check_flag)

                        if check_flag:
                            u["_id"] = str(u["_id"]).replace("ObjectId(", "").replace(")", "")
                            res[str(u["_id"]).replace("ObjectId(", "").replace(")", "")] = u
            else:
                pass
        return res

    def del_by_id(self, _id, _type):
        self.usingCollection = self.usingDataBase[_type]
        try:
            self.usingCollection.find_one_and_delete({"_id": ObjectId(_id)})
            return 'ok'
        except:
            return 'error'

    def __del__(self):
        if self.mongodbClient is not None:
            self.mongodbClient.close()
            print("[!]MongoDB已经断开连接")
        else:
            # print("没有使用mongodb")
            pass


# def main():
#     mdb_ctrl = MongoDBCtrl()
#     res = mdb_ctrl.insert(codeData={"code_name": "24", "code_type": "12", "code_des": "23",
#                                     "code_cnt": "daf", "code_file": "true"})
#     print(res)
#
#
# if __name__ == "__main__":
#     main()
