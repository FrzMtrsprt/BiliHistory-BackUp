import os
import json
import time
from datetime import datetime
from bili import bilibili

MAX_PAGE = 10000  # 最大的页数
PAGE_PER_NUM = 300  # 每页条数
HISTORY_DIR = 'history/'  # 历史记录的保存目录
delay_time = 1 # 每页获取间歇时间，0.6-5，随便设，别太快就行



##########################
# 以下为旧数据合并部分
OLD_HISTORY_FILE = 'history.json'  # 旧的历史记录文件名

# 合并功能函数1：加载数据
def load(filename):
    with open(HISTORY_DIR + filename, 'r', encoding='utf-8') as fp:
        return json.load(fp)


# 合并功能函数2：合并历史记录
def merge_histories(old, new):
    view_at_set = {item['view_at'] for item in old['all']}  # 创建一个集合，包含旧数据的所有view_at值
    merged = old['all']  # 创建一个新列表，初始包含所有旧数据
    for item in new['all']:
        if item['view_at'] not in view_at_set:  # 如果新数据的view_at值不在集合中，就添加到列表中
            merged.append(item)
    return {'all': merged}

# 合并功能函数3：排序历史记录
def process_history(history):
    # 将历史记录按照时间戳排序，从大到小（reverse）
    history['all'].sort(key=lambda x: x['view_at'], reverse=True)
    # 获取最早和最晚的时间戳，以及总计数
    first_time = history['all'][0]['view_at']
    last_time = history['all'][-1]['view_at']
    count = len(history['all'])
    return history, first_time, last_time, count



##########################


# 保存数据
def save(data, filename):
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    # 打开文件并保存数据，使用utf-8编码，添加indent参数使输出的JSON数据易读
    with open(HISTORY_DIR + filename, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)  # Add 'indent=4'

# 获取所有B站历史记录（列表里面包字典）、获取头尾视频时间戳、获取视频数
def get_all_bili_history(cookie_file):
    headers = bilibili.get_header(cookie_file)
    history = {'all': []}
    first_time = None
    last_time = None
    count = 0  # 初始化计数器

    print('数据获取状态代码为0,则为正常\n')

    # 对每一页进行循环
    for page_num in range(MAX_PAGE):
        time.sleep(delay_time)  # 每次请求之间暂停5秒
        # 构建URL
        url = 'https://api.bilibili.com/x/v2/history?pn={pn}&ps={ps}&jsonp=jsonp'.format(pn=page_num, ps=PAGE_PER_NUM)
        # 发送请求
        result = bilibili.req_get(headers, url)

        # 检查结果是否有效
        if result is None or 'data' not in result or result['data'] is None:
            # print("Invalid result: \n", result)

            print("没记录了哦(=￣ω￣=)\n\n\n")

            break  # 如果结果无效，停止获取

        # 打印结果信息，code的值为0应该就是表示请求成功，直接访问网页就是code=0
        print('第{}页，有{}条数据，数据获取状态：{}'.format(page_num+1, len(result['data']),result['code']))
        # 将结果添加到历史记录中
        history['all'].extend(result['data'])
        # 更新计数器
        count += len(result['data'])

        # 记录第一个和最后一个时间戳
        if last_time is None:
            last_time = result['data'][0]['view_at']
        first_time = result['data'][-1]['view_at']

    return history, first_time, last_time, count  # 返回计数器

if __name__ == '__main__':
    cookie = 'cookies.txt'
    # 获取历史记录
    history, first_time, last_time, count = get_all_bili_history(cookie)


    # 如果需要合并历史记录，取消下面三行的注释
    old_history = load(OLD_HISTORY_FILE)
    history = merge_histories(old_history, history)
    history = process_history(history)
    count = history[-1]
    print('以下为融合过的结果：')

    # 将时间戳转换为日期时间字符串
    first_time_str = datetime.fromtimestamp(first_time).strftime('%Y%m%d%H%M')
    last_time_str = datetime.fromtimestamp(last_time).strftime('%Y%m%d%H%M')
    # 构建文件名
    filename = 'history_{}-{}_{}.json'.format(first_time_str, last_time_str, count)
    # 保存历史记录到文件
    save(history, filename)
    print(f"数据已经保存到{filename}")
    print(f"总数据条数: {count}")
