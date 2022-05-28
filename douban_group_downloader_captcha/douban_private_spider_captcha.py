import os
import json
import re
import requests
from bs4 import BeautifulSoup

def login(ss, ua_headers, username, password):
    # 登录的网址
    basic_url = 'https://accounts.douban.com/j/mobile/login/basic'
    # 提交的表单选项
    data = {
        'remember': 'false',
        'name': username,
        'password': password,
    }  
    # 需要预登录一次
    preres = ss.get(url=basic_url,headers=ua_headers)
    # 正式登录
    try:
        print("正在登录用户：{} ".format(username))
        response = ss.post(url=basic_url, headers=ua_headers, data=data)
        # 如果遇到图形验证码
        if re.search('需要图形验证码', response.text):
            try:
                # 先获取验证码图片到本地
                captcha_image_url = json.loads(response.text)['payload']['captcha_image_url']
                captcha_image = ss.get(captcha_image_url, headers=ua_headers)
                with open('temp.jpg','wb') as f:
                    f.write(captcha_image.content)
                print("图形验证码已下载到本地。打开文件 temp.jpg 查看。")
                # 准备把图形验证码内容附到data表单上重新发送
                captcha_solution = input("请输入图形验证码内容：")
                data["captcha_solution"]=captcha_solution
                data["captcha_id"]=json.loads(response.text)['payload']['captcha_id']
                response = ss.post(url=basic_url, headers=ua_headers, data=data)
                if re.search('\"status\":\"failed\"', response.text):
                    print(response.text)
                    print('无法通过图形验证码验证！')
                    return False
            except:
                print('无法通过图形验证码验证！')
                return False
        print("登录 {} 成功！".format(username))
        return True
    except:
        print("登录 {} 失败！".format(username))
        return False

def get_discussions(ss, ua_headers, groupid, groupname):
    print("准备开始下载 {}_{} 小组的内容。".format(groupname, groupid))
    discussion_urls = list()
    # 开始访问小组页面
    group_url = 'https://www.douban.com/group/' + groupid + '/discussion?start=0&type=new'
    while True:
        response = ss.get(url=group_url, headers=ua_headers)
        # 获取小组页面中所有帖子的链接
        soup = BeautifulSoup(response.text,'html.parser')
        results = soup.find_all('td', attrs={'class': 'title'})
        for result in results:
            s_result = result.find('a')
            link = s_result['href']
            title = s_result['title']
            discussion_urls.append({'link': link, 'title': title})
        # 查看是否有下一页，如果有的话需要继续访问下一页
        next_page = soup.find('span', attrs={'class': 'next'})
        if not next_page:
            break
        next_link = next_page.find('a')
        if not next_link:
            break
        group_url = next_link['href']
    return discussion_urls
 
def save_discussions(ss, ua_headers, groupid, groupname, discussion_urls):
    group_dir = groupname + '_' + groupid
    # 创建保存文件夹
    if os.path.exists(group_dir):
        print("{} 文件夹已存在，请注意不要误覆盖文件！输入大写字母 Y 继续保存文件：".format(group_dir))
        s = input()
        if s != 'Y':
            print("退出保存 {}。".format(group_dir))
            return
    else:
        os.mkdir(group_dir)
    # 开始保存帖子
    index = 1
    for discussion_url in discussion_urls:
        print("[{}/{}]保存帖子：{}".format(index, len(discussion_urls), discussion_url['title']))
        post_dir = os.path.join(group_dir, discussion_url['title'])
        if not os.path.exists(post_dir):
            os.mkdir(post_dir)
        discussion_url_link = discussion_url['link']
        count = 1
        while True:
            # 保存一个帖子
            response = ss.get(discussion_url_link, headers=ua_headers)
            with open(os.path.join(post_dir, str(count) + '.html'), 'w') as f:
                f.write(response.text)
            # 如果帖子有下一页，继续保存
            soup = BeautifulSoup(response.text,'html.parser')
            next_page = soup.find('span', attrs={'class': 'next'})
            if not next_page:
                break
            next_link = next_page.find('a')
            if not next_link:
                break
            discussion_url_link = next_link['href']
            count += 1
        index += 1
    print("{} 小组中所有帖子保存完成！".format(group_dir))
    return


def main():

    config = json.load(open('config.json', 'r', encoding="utf-8"))
    username = config['userinfo']['username']
    password = config['userinfo']['password']

    # 创建session保存登录状态
    ss = requests.Session()
    ua_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.3 Safari/605.1.15',
    }

    # 登录
    state = login(ss, ua_headers, username, password)

    # 携带登陆成功的cookie去请求
    if state:
        for group in config['grouplist']:
            groupid = group['groupid']
            groupname = group['groupname']
            discussion_urls = get_discussions(ss, ua_headers, groupid, groupname)
            save_discussions(ss, ua_headers, groupid, groupname, discussion_urls)
    
    return

if __name__ == '__main__':
    main()

