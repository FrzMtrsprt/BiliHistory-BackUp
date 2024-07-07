import os
import json
import time
from datetime import datetime
from bili import bilibili

MAX_PAGE = 10000  # 设置最大的页数
PAGE_PER_NUM = 300  # 设置每页的数量
HISTORY_DIR = 'history/'  # 设置历史记录的保存目录、
delay_time = 1 # 每页获取间歇时间，0.6-5，随便设，别太快就行

# 用于保存数据的函数
def save(data, filename):
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    # 打开文件并保存数据，使用utf-8编码，添加indent参数使输出的JSON数据易读
    with open(HISTORY_DIR + filename, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)  # Add 'indent=4'

# 获取所有B站历史记录的函数
def get_all_bili_history(cookie_file):
    headers = bilibili.get_header(cookie_file)
    history = {'all': []}
    first_time = None
    last_time = None
    count = 0  # 初始化计数器
    # 对每一页进行循环
    for page_num in range(MAX_PAGE):
        time.sleep(delay_time)  # 每次请求之间暂停5秒
        # 构建URL
        url = 'https://api.bilibili.com/x/v2/history?pn={pn}&ps={ps}&jsonp=jsonp'.format(pn=page_num, ps=PAGE_PER_NUM)
        # 发送请求
        result = bilibili.req_get(headers, url)


        # 检查结果是否有效
        if result is None or 'data' not in result or result['data'] is None:
            print("Invalid result: ", result)
            break  # 如果结果无效，停止获取

        # 打印结果信息，code的值为0应该就是表示请求成功，直接访问网页就是code=0
        print('page = {} code = {} datalen = {}'.format(page_num, result['code'], len(result['data'])))
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
    # 将时间戳转换为日期时间字符串
    first_time_str = datetime.fromtimestamp(first_time).strftime('%Y%m%d%H%M')
    last_time_str = datetime.fromtimestamp(last_time).strftime('%Y%m%d%H%M')
    # 构建文件名
    filename = 'history_{}-{}_{}.json'.format(first_time_str, last_time_str, count)
    # 保存历史记录
    save(history, filename)
    print('Total records: ', count)  # 打印总记录数
