import os  # 操作文件和目录
import time  # 时间相关操作，如延时
import csv  # 读写CSV文件
from bili import bilibili  # 自定义模块，用于处理B站API请求等

MAX_PAGE = 10000  # 最大翻页数量
PAGE_PER_NUM = 300  # 每页获取的历史记录数量
HISTORY_DIR = 'history/'  # 历史记录保存的目录


def save_to_csv(data, filename):
    # 如果历史记录保存目录不存在，则创建
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    # 使用'utf-8-sig'编码打开CSV文件以避免中文乱码，并设置newline=''避免多余空行
    with open(HISTORY_DIR + filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头，基于第一条历史记录的键
        writer.writerow(data['all'][0]['data'][0].keys())
        # 遍历所有页面和每页中的历史记录，写入数据行
        for page in data['all']:
            for item in page['data']:
                writer.writerow(item.values())


def get_all_bili_history(cookie_file):
    # 根据cookie文件获取请求头
    headers = bilibili.get_header(cookie_file)
    history = {'all': []}  # 初始化历史记录容器

    # 遍历最大页数以获取历史记录
    for page_num in range(MAX_PAGE):
        # 每次请求后暂停0.6秒
        time.sleep(0.6)
        # 构造请求URL，包含当前页数和每页记录数
        url = f'https://api.bilibili.com/x/v2/history?pn={page_num}&ps={PAGE_PER_NUM}&jsonp=jsonp'
        result = bilibili.req_get(headers, url)  # 发起GET请求并获取响应

        # 获取当前页数据长度，如果结果为空或请求失败则长度为0
        datalen = len(result['data']) if result['data'] is not None else 0
        # 打印当前页码、返回码及数据长度用于调试
        print(f'page = {page_num} code = {result["code"]} datalen = {datalen}')

        # 当数据为空或请求返回非0错误码时，停止翻页
        if datalen == 0 or result['code'] != 0:
            break
        # 将当前页历史记录添加到总记录列表中
        history['all'].append(result)

    return history  # 返回所有历史记录



if __name__ == '__main__':
    cookie = 'cookies.txt'
    try:
        # 尝试获取B站历史记录并保存为CSV
        history = get_all_bili_history(cookie)
        save_to_csv(history, 'history.csv')
    except Exception as e:
        # 如果出现异常，则打印错误信息
        print(f"An error occurred: {e}")
