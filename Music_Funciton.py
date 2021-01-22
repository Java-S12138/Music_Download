import json
import requests
import random
from pyquery import PyQuery as pq
import re

# 发送请求时的头文件
heades = [
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}
]

def music_download(song_url,name,sing_name=None):
    response = requests.get(song_url, headers=heades[random.randint(0, len(heades)-1)])
    if sing_name == None:
        with open("Music" + '/' + f"{name}.mp3", 'wb') as f:
            f.write(response.content)
    else:
        with open("Music" + '/' + f"{name}-{sing_name}.mp3", 'wb') as f:
            f.write(response.content)


def music_home_top(url):  # 网易云音乐排行榜首页显示

    try:
        headers = {
            'authority': 'music.163.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'sec-fetch-dest': 'iframe',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://music.163.com/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': '_ga=GA1.2.1412864897.1553836840; _iuqxldmzr_=32; _ntes_nnid=b757609ed6b0fea92825e343fb9dfd21,1568216071410; _ntes_nuid=b757609ed6b0fea92825e343fb9dfd21; WM_TID=Pg3EkygrDw1EBAVUVRIttkwA^%^2Bn1s1Vww; P_INFO=183605463^@qq.com^|1581593068^|0^|nmtp^|00^&99^|null^&null^&null^#not_found^&null^#10^#0^|^&0^|^|183605463^@qq.com; mail_psc_fingerprint=d87488b559a786de4942ad31e080b75f; __root_domain_v=.163.com; _qddaz=QD.n0p8sb.xdhbv8.k75rl6g4; __oc_uuid=2f4eb790-6da9-11ea-9922-b14d70d91022; hb_MA-BFF5-63705950A31C_source=blog.csdn.net; UM_distinctid=171142b7a6d3ba-0fbb0bf9a78375-4313f6a-144000-171142b7a6e30b; vinfo_n_f_l_n3=6d6e1214849bb357.1.0.1585181322988.0.1585181330388; JSESSIONID-WYYY=jJutWzFVWmDWzmt2vzgf6t5RgAaMOhSIKddpHG9mTIhK8fWqZndgocpo87cjYkMxKIlF^%^2BPjV^%^2F2NPykYHKUnMHkHRuErCNerHW6DtnD8HB09idBvHCJznNJRniCQ9XEl^%^2F7^%^2Bovbwgy7ihPO3oJIhM8s861d^%^2FNvyRTMDjVtCy^%^5CasJPKrAty^%^3A1585279750488; WM_NI=SnWfgd^%^2F5h0XFsqXxWEMl0vNVE8ZjZCzrxK^%^2F9A85boR^%^2BpV^%^2BA9J27jZCEbCqViaXw6If1Ecm7okWiL^%^2BKU2G8frpRB^%^2BRRDpz8RNJnagZdXn6KNVBHwK2tnvUL^%^2BxWQ^%^2BhGf2aeWE^%^3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84b64f86878d87f04fe9bc8fa3c84f878f9eafb65ab59498cccf48f7929fb5e72af0fea7c3b92a91b29987e670edeba8d1db4eb1af9899d64f8fb40097cd5e87e8968bd949baaeb8acae3383e8fb83ee5ae9b09accc4338aeef98bd94987be8d92d563a388b9d7cc6ef39bad8eb665a989a7adaa4197ee89d9e57ab48e8eccd15a88b0b6d9d1468ab2af88d9709cb2faaccd5e8298b9acb180aeaa9badaa74958fe589c66ef2bfabb8c837e2a3; playerid=67583529',
        }

        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        res.raise_for_status()
    except:
        pass

    text = res.text
    all = re.findall(r'<Ul Class="F-Hide">(.*?)</Ul>', text, re.I)
    str = all[0]
    strlist = re.findall(r'">(.*?)</a>', str)
    idlist = re.findall(r'id=(\d+)', str)

    info = []
    info.append(strlist)
    info.append(idlist)
    return info

def home_play_music(song_id,source):#腾讯酷狗音乐播放地址

    url = "https://api.zhuolin.wang/api.php?callback=jQuery111305940605786929793_1588688866522&types=playlist&id=112504&_=1588688866523"
    data = {
        'types': 'url',
        'id': f'{song_id}',
        'source': f'{source}'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    rsp = requests.post(url, data=data, headers=headers)
    if source == 'tencent':
        link = rsp.text[rsp.text.index('http'):rsp.text.index('",')]
        link = link.replace('\\', '')
    elif source == 'kugou':
        link = rsp.text[rsp.text.index('http'):rsp.text.index('mp3')] + 'mp3'
        link = link.replace('\\', '')
    return link

def home_show_music(type,name):#音乐首页显示
    url = 'https://api.zhuolin.wang/api.php?callback=jQuery111303334237052043867_1589428664685&types=playlist&id=3778678&_=1589428664686'
    data = {
        'types': 'search',
        'count': '20',
        'source': type,
        'pages': '1',
        'name': name
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    list_info = musicSpider(url, data, headers)
    return list_info

def musicSpider(url, data, headers):#音乐爬取

    rsp = requests.post(url, data=data, headers=headers)
    content = rsp.text
    info = content[content.index('('):content.index('])')] + '])'

    info_list = eval(info[1:-1])

    music_info_list = []
    for i in info_list:
        id = i.get('id')
        name = i.get('name')
        artist = i.get('artist')
        album = i.get('album')
        info_info = []
        info_info.append(id)
        info_info.append(name.replace(' ', ''))
        info_info.append(artist[0])
        info_info.append(album.replace(' ', ''))
        music_info_list.append(info_info)
    return music_info_list



# 获取首页,反回图片、名字、id号
def wyy_first_page(type):
    # 先对首页进行简单处理
    url = f"https://music.163.com/discover/playlist/?cat={type}"
    response = requests.get(url, headers=heades[random.randint(0, len(heades)-1)])
    doc = pq(response.text)
    playlist = doc('li .u-cover.u-cover-1')  # 筛选出首页推荐的歌单
    playlist.find('.icon-play').remove()  # 移除多余的信息，便于后续提取信息
    playlist.find('div:contains(getPlayCount)').siblings().remove()
    playlist.find('div:contains(getPlayCount)').remove()

    # 获取首页推荐的歌单图片的url
    img = playlist.find('img').items()
    img_url_l = [i.attr('src') for i in img]  # 获取到所有歌单封面的url

    # 获取推荐歌单的名字
    name_list_l = [i.attr.title for i in playlist.find('a').items()]

    # 获取歌单的键值id
    id_list_l = [i.attr.href for i in playlist.find('a').items()]
    return [img_url_l, name_list_l, id_list_l]


def askURL(url):
    haed = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
    request = requests.get(url,headers=haed)

    try:
        response = request.text
        html_dict = json.loads(response)

    except :
        pass
    return html_dict

    # 通过歌单playlist_id获取歌单信息
def playlist_info(playlist_id):

    #playlist_id = int(re.sub(r'\D', "",playlist_id))
    # html = askURL(f"http://api.no0a.cn/api/cloudmusic/playlist/{playlist_id}")
    html = askURL(f"http://api.sunyj.xyz?site=netease&playlist={playlist_id}")
    # print(html)
    song_name_l = []
    song_id_l = []
    for i in html:
        song_name_l.append(i['name'])
        song_id_l.append(i['id'])
    return [song_name_l, song_id_l]


# 通过指定的歌曲song_id获取歌曲的音频二进制文件
def song_url(song_id):
    # 通过urls获取歌曲下载链接
    urls = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"
    return urls

def test(id):
    html = askURL(f"https://music.163.com/api/playlist/detail?id={id}")

    info_dict = html['result']['tracks']
    print(info_dict)

if __name__ == '__main__':
    pass
