import json
import os

import requests
import random
from pyquery import PyQuery
import re
# noinspection PyProtectedMember
from mutagen.id3 import ID3, TIT2, TPE1, TALB

# 发送请求时的头文件
html_head = [
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"},
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.130 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/76.0.3809.87 Safari/537.36"}
]


def make_meta_inf(title="", artist="", album=""):
    return {"title": title, "artist": artist, "album": album}


def set_mp3_info(path, info):
    song_file = ID3(path)
    song_file['TIT2'] = TIT2(  # 插入歌名
        encoding=3,
        text=info['title']
    )
    song_file['TPE1'] = TPE1(  # 插入第一演奏家、歌手、等
        encoding=3,
        text=info['artist']
    )
    song_file['TALB'] = TALB(  # 插入专辑名
        encoding=3,
        text=info['album']
    )
    song_file.save()


def half2full(s):
    ns = []
    for c in s:
        num = ord(c)
        if num == 0x20:
            num = 0x3000
        elif 0x21 <= num <= 0x7e:
            num += 0xfee0
        ns.append(chr(num))
    return ''.join(ns)


def full2half(s):
    ns = []
    for c in s:
        num = ord(c)
        if num == 0x3000:
            num = 0x20
        elif 0x21 + 0xfee0 <= num <= 0x7e + 0xfee0:
            num -= 0xfee0
        ns += chr(num)
    ns = ''.join(ns)
    return ns


def make_valid_name(name):
    bad_chars = r'/\:*?"<>|'
    nl = list(name)
    for i, c in enumerate(nl):
        if c in bad_chars:
            nl[i] = half2full(c)
    name = ''.join(nl)
    return name


def music_download(music_url, music_name, singer_name=None, meta_inf=None):
    response = requests.get(music_url, headers=html_head[random.randint(0, len(html_head) - 1)])

    os.makedirs('Music', exist_ok=True)
    music_name = make_valid_name(music_name)
    if singer_name is not None:
        singer_name = make_valid_name(singer_name)

    if singer_name is None:
        with open("Music" + '/' + f"{music_name}.mp3", 'wb') as f:
            f.write(response.content)
            if meta_inf is not None:
                set_mp3_info("Music" + '/' + f"{music_name} - {singer_name}.mp3", meta_inf)
    else:
        with open("Music" + '/' + f"{music_name} - {singer_name}.mp3", 'wb') as f:
            f.write(response.content)
            if meta_inf is not None:
                set_mp3_info("Music" + '/' + f"{music_name} - {singer_name}.mp3", meta_inf)


def music_home_top(url):  # 网易云音乐排行榜首页显示

    try:
        # noinspection SpellCheckingInspection
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
        string = re.findall(r'<Ul Class="F-Hide">(.*?)</Ul>', res.text, re.I)[0]
        str_list = re.findall(r'">(.*?)</a>', string)
        id_list = re.findall(r'id=(\d+)', string)

        info = [str_list, id_list]
        return info
    except:
        return None


def home_play_music(song_id, source):  # 腾讯酷狗音乐播放地址

    url = "https://api.zhuolin.wang/api.php?callback=jQuery111305940605786929793_1588688866522&types=playlist&id=112504&_=1588688866523"
    data = {
        'types': 'url',
        'id': f'{song_id}',
        'source': f'{source}'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    link = ""
    rsp = requests.post(url, data=data, headers=headers)
    if source == 'tencent':
        link = rsp.text[rsp.text.index('http'):rsp.text.index('",')]
        link = link.replace('\\', '')
    elif source == 'kugou':
        link = rsp.text[rsp.text.index('http'):rsp.text.index('mp3')] + 'mp3'
        link = link.replace('\\', '')
    return link


def home_show_music(source, name):  # 音乐首页显示
    url = 'https://api.zhuolin.wang/api.php?callback=jQuery111303334237052043867_1589428664685&types=playlist&id=3778678&_=1589428664686'
    data = {
        'types': 'search',
        'count': '20',
        'source': source,
        'pages': '1',
        'name': name
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    list_info = music_spider(url, data, headers)
    return list_info


def music_spider(url, data, headers):  # 音乐爬取

    rsp = requests.post(url, data=data, headers=headers)
    content = rsp.text
    info = content[content.index('('):content.index('])')] + '])'

    info_list = eval(info[1:-1])

    music_info_list = []
    for i in info_list:
        info_info = [i.get('id'), i.get('name').replace(' ', ''), i.get('artist')[0], i.get('album').replace(' ', '')]
        music_info_list.append(info_info)
    return music_info_list


# 获取首页,反回图片、名字、id号
def wyy_first_page(song_list):
    # 先对首页进行简单处理
    url = f"https://music.163.com/discover/playlist/?cat={song_list}"
    response = requests.get(url, headers=html_head[random.randint(0, len(html_head) - 1)])
    doc = PyQuery(response.text)
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


def ask_url(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
    request = requests.get(url, headers=head)

    try:
        response = request.text
        html_dict = json.loads(response)
        return html_dict
    except:
        return {}

    # 通过歌单playlist_id获取歌单信息


def playlist_info(playlist_id):
    # playlist_id = int(re.sub(r'\D', "",playlist_id))
    # html = askURL(f"http://api.no0a.cn/api/cloudmusic/playlist/{playlist_id}")
    html = ask_url(f"https://api.sunyj.xyz?site=netease&playlist={playlist_id}")
    # print(html)
    song_name_l = []
    song_id_l = []
    for i in html:
        song_name_l.append(i['name'])
        song_id_l.append(i['id'])
    return [song_name_l, song_id_l]


# 通过指定的歌曲song_id获取歌曲的音频二进制文件
def get_song_url(song_id):
    # 通过urls获取歌曲下载链接
    urls = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
    return urls


if __name__ == '__main__':
    pass
