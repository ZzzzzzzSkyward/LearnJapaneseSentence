import requests
from tqdm import tqdm
import time
import os
# 定义要爬取的页面范围
start_page = 100000
end_page = 600000
headers = {
    'GET': '/xml/list/sub/?page=1 HTTP/2',
    'Host': 'assrt.net',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh-TW;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Cookie': 'u3=6fdf024d0b908cca27f761479191bf4c',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Priority': 'u=0, i',
    'TE': 'trailers'
}
# 定义保存文件的函数
def save_page_content(page_content, page_number):
    with open(f'page_{page_number}.html', 'w', encoding='utf-8') as file:
        file.write(page_content)

# 爬取并保存每个页面
for page_number in tqdm(range(start_page, end_page + 1)):
    url = f'https://assrt.net/xml/sub/{page_number//1000:02d}/{page_number}.xml'
    print(url)
    if os.path.exists(f'page_{page_number}.html'):
        continue
    try:
        # 发送HTTP请求
        response = requests.get(url,headers=headers)
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML内容
            
            # 获取网页的HTML内容
            page_content = response.text
            
            # 保存页面内容到本地文件
            save_page_content(page_content, page_number)
            print(f'页面 {page_number} 已保存。')
        else:
            print(f'页面 {page_number} 请求失败，状态码：{response.status_code}')
        time.sleep(0.5)
    
    except requests.RequestException as e:
        print(f'请求页面 {page_number} 时发生错误：{e}')

print('所有页面已爬取完毕。')