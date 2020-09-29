import urllib.request
import json
import os


def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    # 判断路径是否存在
    isExists=os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录,创建目录操作函数
        #此处路径最好使用utf-8解码，否则在磁盘中可能会出现乱码的情况
        os.makedirs(path)
    else:
        return False


if __name__ == '__main__':
    # 开始信息
    print("========================================")
    print("欢迎使用通过百度地图分析某城市POI（兴趣点）")
    print("使用本程序，可自动爬取指定城市指定类型类别的建筑/坐标/电话等信息")
    print("========================================")

    # 地址和类别
    city = input("请输入想要分析的城市：")
    all_poi_type = ["美食", "酒店", "购物", "生活服务", "丽人", "旅游景点", "休闲娱乐", "运动健身", "教育培训", "文化传媒", "医疗", "汽车服务", "交通设施", "金融",
                    "房地产", "公司企业", "政府机构"]
    print("目前POI类型已包含：{}".format(all_poi_type))
    other_type = input("添加其他POI类型（留空结束）：")
    while (other_type):
        all_poi_type.append(other_type)
        other_type = input("添加其他POI类型（留空结束）：")

    ak = ""#百度API应用Key
    # 百度API接口
    url = "http://api.map.baidu.com/place/v2/search?page_size=20&query={}&region={}&output=json&page_num={}&ak={}"

    # 爬虫header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    allResults = []

    #创建结果路径
    mkdir("{}的POI分析".format(city))

    # 循环获取
    for poi_type in all_poi_type:
        print("====================")
        print("正在查询{}的{}".format(city, poi_type))
        # 爬虫访问
        page_num = 0  # 第几页（百度API一页给20个数据）
        total_num = 20  # 最多多少数据（20数据一页）
        poi_result = []  # 全部结果
        while (total_num == 20):  # 只有当前页有20条数据，才会查下一页
            # 爬虫获得数据
            req = urllib.request.Request(
                url=url.format(urllib.parse.quote(poi_type), urllib.parse.quote(city), str(page_num), ak),
                headers=headers)
            res = urllib.request.urlopen(req)
            json_result = res.read().decode('utf-8')
            # 转json
            result = json.loads(json_result)
            # 如果包含结果
            if ("results" in result):
                # 获取总数
                total_num = len(result["results"])
                # 插入当前POI数据列表
                for res in result["results"]:
                    poi_result.append(res)
                # 打印总数
                print("第{}页有{}个结果".format(str(page_num + 1), str(total_num)))
            else:  # 如果不包含结果
                if (result["status"] == 401):  # 如果是401错误码，代表爬太快了
                    # 重新查询
                    total_num = 20
                    page_num -= 1
                elif (result["status"] == 302):  # 如果是302错误码，代表API到限额了
                    print("百度API到达本日限额，无法继续查询")
                    total_num = 0
                else:
                    # 其他错误就代表查完了
                    total_num = 0
            # 换一页查
            page_num += 1
        print("{}的{}共有{}个结果".format(city, poi_type, str(len(poi_result))))  # 显示结果总数
        json_to_save = json.dumps(poi_result, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')  # 需要存的数据
        with open("{}的POI分析/{}的{}POI数据.txt".format(city,city, poi_type), "wb+") as fo:  # 读取文件
            fo.write(json_to_save)  # 存本地
        print("保存文件成功 ==========> {}的POI分析/{}的{}POI数据.txt".format(city,city, poi_type))
        # try:
        #
        # except:
        # print("保存文件失败")

    print("====================")
    print("查询完毕！")