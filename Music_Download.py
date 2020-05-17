import os
import re
import time
import xlwt
import json
import requests
import datetime
import cloudmusic
import threading
from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QTableWidgetItem, QAbstractItemView, QMessageBox
from PySide2.QtUiTools import QUiLoader
from urllib.request import urlretrieve

class SignalStore(QObject):
    progress_update = Signal(int)
    top_progress_update = Signal(int)
so = SignalStore()


class Music_Dowload:
    def __init__(self):
        so.progress_update.connect(self.setProgress)                    #进度条
        so.top_progress_update.connect(self.top_setProgress)            #进度条
        self.ongoing = False                                            #下载警告
        self.ui = QUiLoader().load('dowload.ui')                        #关联ui界面文件
        self.ui.top_textEdit.setReadOnly(True)
        self.ui.comment_textEdit.setReadOnly(True)
        self.ui.lyrics_textEdit.setReadOnly(True)
        self.ui.comment_textEdit.setReadOnly(True)
        self.ui.textBrowser.setReadOnly(True)
        self.ui.textBrowser_2.setReadOnly(True)
        self.ui.seek_Button.clicked.connect(self.platform_netease)      #搜索网易云
        self.ui.seek_Button_2.clicked.connect(self.platform_tencent)    #搜索QQ音乐
        self.ui.seek_Button_3.clicked.connect(self.platform_kugou)      #搜索酷狗音乐
        self.ui.download_Button.clicked.connect(self.download_type)     #下载按钮
        self.ui.all_download_Button.clicked.connect(self.all_music_download)     #下载按钮
        self.ui.top_download_Button.clicked.connect(self.all_top_download)     #下载按钮
        self.ui.open_Button.clicked.connect(self.open_file)             #打开保存音乐的文件夹
        self.ui.open_Button_2.clicked.connect(self.open_file)           #打开保存音乐的文件夹
        self.ui.open_Button_3.clicked.connect(self.open_file)           #打开保存音乐的文件夹
        self.ui.comment_pushButton.clicked.connect(self.look_comments)  #查看评论
        self.ui.comment_pushButton_2.clicked.connect(self.in_excel)     #生成excel文件
        self.ui.comment_pushButton_3.clicked.connect(self.open_excel)   #打开excel文件
        self.ui.lyrics_pushButton.clicked.connect(self.lyrics)          #查看歌词
        self.ui.lyrics_pushButton_2.clicked.connect(self.lyrics_T)      #查看歌词时间版
        self.ui.comboBox.currentIndexChanged.connect(self.top)          #查看排行榜
        self.ui.top_pushButton.clicked.connect(self.music_top_dowload)  #下载排行榜里面的音乐
        self.ui.music_list_pushButton.clicked.connect(lambda:self.music_list("music_paly"))  #显示歌单内容
        self.ui.music_list_pushButton_album.clicked.connect(lambda:self.music_list("album") ) #显示歌单内容
        self.ui.music_list_pushButton_2.clicked.connect(self.music_list_downlodn)#下载歌单里面的音乐
        self.ui.music_list_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)#设置歌单表格为只读
        self.ui.download_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)#设置歌单表格为只读

    def setProgress(self, value):
        self.ui.all_d_Bar.setValue(value)

    def top_setProgress(self, value):
        self.ui.top_d_Bar.setValue(value)

    def all_top_download(self):
        music = self.ui.top_textEdit.toPlainText()
        music_info = music.split("\n")
        id_num = self.ui.top_id_Edit.toPlainText()
        id_info = id_num.split()

        music_info_remove = []
        for i in range(len(music_info)):
            music_info_remove.append(re.findall(r'《(.*)》', music_info[i]))
        def top_dodownload():
            self.ongoing = True
            for i in range(len(id_info)):
                self.all_download(id_info[i], music_info_remove[i][0],name= None)
                so.top_progress_update.emit(i + 1)
            self.ongoing = False
        if self.ongoing:
            QMessageBox.warning(
                self.ui,
                '警告', '下载中，请等待完成')
            return
        t = threading.Thread(target=top_dodownload, daemon=True)
        t.start()


    def all_download(self,song_id,music,name):
        try:
            song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

            os.makedirs("Music", exist_ok=True)
            path = f"Music\{music}-{name}.mp3"

            urlretrieve(song_url, path)
        except:
            pass

    def all_music_download(self):
        music_name = []
        music_singe = []
        id_num = self.ui.music_list_id_Edit.toPlainText()
        id_info = id_num.split()
        method = self.ui.music_list_tableWidget.rowCount()
        self.ui.all_d_Bar.setRange(0,method)

        for i in range(method):
            music_n = self.ui.music_list_tableWidget.item(i, 0).text()
            music_s = self.ui.music_list_tableWidget.item(i, 1).text()
            music_name.append(music_n)
            music_singe.append(music_s)
        def dodownload():
            self.ongoing = True
            for i in range(method):
                self.all_download(id_info[i],music_name[i],music_singe[i])
                so.progress_update.emit(i+1)
            self.ongoing = False
        if self.ongoing:
            QMessageBox.warning(
                self.ui,
                '警告', '下载中，请等待完成')
            return
        t = threading.Thread(target=dodownload,daemon=True)
        t.start()

    def music_list(self,type):
        self.ui.music_list_id_Edit.clear()
        method = self.ui.music_list_tableWidget.rowCount()
        for i in range(method):
            self.ui.music_list_tableWidget.removeRow(0)

        music_id = int(self.ui.music_list_Edit.text())
        if type =='music_paly':
            music_play_list = cloudmusic.getPlaylist(music_id)
        else:
            music_play_list = cloudmusic.getAlbum(music_id)

        self.ui.music_list_label.setText(f'搜索成功！共{len(music_play_list)}首')

        for i in range(len(music_play_list)):
            self.ui.music_list_tableWidget.insertRow(0)
        for i in range(len(music_play_list)):
            self.ui.music_list_tableWidget.setItem(i, 0, QTableWidgetItem(f"{music_play_list[i].name}"))
            self.ui.music_list_tableWidget.setItem(i, 1, QTableWidgetItem(f"{music_play_list[i].artist[0]}"))
            self.ui.music_list_tableWidget.setItem(i, 2, QTableWidgetItem(f"《{music_play_list[i].album}》"))
            self.ui.music_list_id_Edit.insertPlainText(f'{music_play_list[i].id}\n')

    def music_list_downlodn(self):

        id_num = self.ui.music_list_id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.music_list_lineEdit.text())

        name = self.ui.music_list_tableWidget.item(d_num-1,0).text()

        song_id = id_info[d_num - 1]


        song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

        os.makedirs("Music", exist_ok=True)
        path = "Music\%s.mp3" % name

        urlretrieve(song_url, path)

        self.ui.music_list_label.setText('下载成功！')

    def open_file(self):#打开文件夹
        try:
            os.startfile('Music')
        except FileNotFoundError:
            self.ui.show_label.setText('你还没下载呢！')

    def top(self):#网易云排行榜
        text = self.ui.comboBox.currentText()
        if text == "云音乐飙升榜":
            self.music_top("https://music.163.com/discover/toplist?id=19723756")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐新歌榜":
            self.music_top("https://music.163.com/discover/toplist?id=3779629")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "网易原创歌曲榜":
            self.music_top("https://music.163.com/discover/toplist?id=2884035")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐热歌榜":
            self.music_top("https://music.163.com/discover/toplist?id=3778678")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐说唱榜":
            self.music_top("https://music.163.com/discover/toplist?id=991319590")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐古典音乐榜":
            self.music_top("https://music.163.com/discover/toplist?id=71384707")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐电音榜":
            self.music_top("https://music.163.com/discover/toplist?id=1978921795")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "抖音排行榜":
            self.music_top("https://music.163.com/discover/toplist?id=2250011882")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "新声榜":
            self.music_top("https://music.163.com/discover/toplist?id=2617766278")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐ACG音乐榜":
            self.music_top("https://music.163.com/discover/toplist?id=71385702")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐韩语榜":
            self.music_top("https://music.163.com/discover/toplist?id=745956260")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐国电榜":
            self.music_top("https://music.163.com/discover/toplist?id=10520166")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "英国Q杂志中文版周榜":
            self.music_top("https://music.163.com/discover/toplist?id=2023401535")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "电竞音乐榜":
            self.music_top("https://music.163.com/discover/toplist?id=2006508653")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "UK排行榜周榜":
            self.music_top("https://music.163.com/discover/toplist?id=180106")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "美国Billboard周榜":
            self.music_top("https://music.163.com/discover/toplist?id=60198")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "Beatport全球电子舞曲榜":
            self.music_top("https://music.163.com/discover/toplist?id=3812895")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "KTV唛榜":
            self.music_top("https://music.163.com/discover/toplist?id=21845217")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "iTunes榜":
            self.music_top("https://music.163.com/discover/toplist?id=11641012")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "日本Oricon周榜":
            self.music_top("https://music.163.com/discover/toplist?id=60131")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "Hit FM Top榜":
            self.music_top("https://music.163.com/discover/toplist?id=120001")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "台湾Hito排行榜":
            self.music_top("https://music.163.com/discover/toplist?id=112463")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "云音乐欧美热歌榜":
            self.music_top("https://music.163.com/discover/toplist?id=2809513713")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "法国 NRJ Vos Hits 周榜":
            self.music_top("https://music.163.com/discover/toplist?id=27135204")
            self.ui.top_show_label.setText(f'《{text}》')
        elif text == "中国新乡村音乐排行榜":
            self.music_top("https://music.163.com/discover/toplist?id=3112516681")
            self.ui.top_show_label.setText(f'《{text}》')

    def music_top_dowload(self):#排行榜音乐下载
        try:
            num = int(self.ui.top_lineEdit.text())

            id_num = self.ui.top_id_Edit.toPlainText()
            id_info = id_num.split()

            name = self.ui.top_textEdit.toPlainText()
            name_info = re.findall(r'《(.*)》', name)

            song_id = id_info[num - 1]
            song_name = name_info[num - 1]
            song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

            os.makedirs("Music", exist_ok=True)
            path = "Music\%s.mp3" % song_name

            urlretrieve(song_url, path)
            self.ui.top_show_label.setText('下载完成！')
        except:
            self.ui.top_show_label.setText("你还没有输入序号哦！")

    def music_top(self,url):#网易云音乐排行榜显示
        self.ui.top_textEdit.clear()
        self.ui.top_id_Edit.clear()

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
            self.ui.top_show_label.setText('网页提取出现问题！')
        text = res.text
        try:
            all = re.findall(r'<Ul Class="F-Hide">(.*?)</Ul>', text, re.I)
            str = all[0]
            strlist = re.findall(r'">(.*?)</a>', str)
            idlist = re.findall(r'\d+', str)
            for i in range(len(strlist)):
                self.ui.top_textEdit.insertPlainText(f"{i+1} 《{strlist[i]}》\n")
                self.ui.top_id_Edit.insertPlainText(f"{idlist[i]}\n")
        except:
            self.ui.top_show_label.setText('提取文章出错！')


    def lyrics_T(self):#歌词显示

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
        self.ui.lyrics_textEdit.clear()

        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            id_num = self.ui.id_Edit.toPlainText()
            id_info = id_num.split()
            d_num = int(self.ui.lyrics_Edit.text())

            name = self.ui.download_tableWidget.item(d_num - 1, 0).text()

            song_id = id_info[d_num - 1]

            lrc_url = f'http://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1'
            lyric = requests.get(lrc_url,headers = headers)
            json_obj = lyric.text  # 网页源码
            j = json.loads(json_obj)
            lrc = j['lrc']['lyric']
            self.ui.lyrics_textEdit.insertPlainText(lrc)

            self.ui.lyrics_show_label.setText(f"《{name}》")
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.lyrics_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.lyrics_show_label.setText("没有找到音乐信息,请先搜索吧！")

    def lyrics(self):#歌词显示 时间版
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
        self.ui.lyrics_textEdit.clear()


        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            id_num = self.ui.id_Edit.toPlainText()
            id_info = id_num.split()

            d_num = int(self.ui.lyrics_Edit.text())
            name = self.ui.download_tableWidget.item(d_num - 1, 0).text()
            song_id = id_info[d_num - 1]

            lrc_url = f'http://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1'
            lyric = requests.get(lrc_url,headers = headers)
            json_obj = lyric.text  # 网页源码
            j = json.loads(json_obj)
            lrc = j['lrc']['lyric']
            pat = re.compile(r'\[.*\]')
            lrc = re.sub(pat, "", lrc)
            lrc = lrc.strip()
            self.ui.lyrics_textEdit.insertPlainText(lrc)

            self.ui.lyrics_show_label.setText(f"《{name}》")
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.lyrics_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.lyrics_show_label.setText("没有找到音乐信息,请先搜索吧！")

    def in_excel(self):#把评论写入excel
        headers = {
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        """
        获取评论信息
        """
        id = self.ui.comment_id_Edit.toPlainText()
        name = self.ui.comment_name_textEdit.toPlainText()
        list_info_ct = []

        music = cloudmusic.getMusic(id)
        coms = music.getHotComments()
        for com in coms:
            timeStamp = (com['time']) / 1000
            dateArray = datetime.datetime.fromtimestamp(timeStamp)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            info = []
            info.append(com["nickName"])
            info.append(com["likeCount"])
            info.append(otherStyleTime)
            info.append(com["content"].strip().replace('\n', '').replace(',', '，'))
            list_info_ct.append(info)

        try:
            for page in range(0,1020,20):
                url = f'http://music.163.com/api/v1/resource/comments/R_SO_4_{id}?limit=20&offset=' + str(page)
                response = requests.get(url=url, headers=headers)
                # 将字符串转为json格式
                result = json.loads(response.text)
                items = result['comments']
                for item in items:
                    info = []
                    # 用户名
                    user_name = item['user']['nickname'].replace(',', '，')
                    # 评论内容
                    comment = item['content'].strip().replace('\n', '').replace(',', '，')
                    # 评论点赞数
                    praise = str(item['likedCount'])
                    # 评论时间
                    date = time.localtime(int(str(item['time'])[:10]))
                    date = time.strftime("%Y-%m-%d %H:%M:%S", date)
                    info.append(user_name)
                    info.append(praise)
                    info.append(date)
                    info.append(comment)
                    list_info_ct.append(info)
            book = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 创建workbook对象
            sheet = book.add_sheet("网易云评论", cell_overwrite_ok=True)  # 创建工作表
            col = ("用户昵称","点赞数","发布时间","评论")
            for i in range(4):
                sheet.write(0, i, col[i])  # 列名
            for i in range(len(list_info_ct)):
                data = list_info_ct[i]
                for j in range(4):
                    sheet.write(i + 1, j, data[j])  # 数据
            book.save(f"{name}.xls")

            self.ui.comment_show_label.setText("生成完毕！")
        except KeyError:
            self.ui.comment_show_label.setText("没有找到音乐信息哦，请先搜索吧！")


    def open_excel(self):#打开excel文件
        try:
            name = self.ui.comment_name_textEdit.toPlainText()
            os.startfile(f'{name}.xls')
        except FileNotFoundError:
            self.ui.comment_show_label.setText("没有找到Excel文件哦，请先生成吧！")

    def singer_show(self,name,id):#评论部分信息显示
        self.ui.comment_id_Edit.clear()
        self.ui.comment_name_textEdit.clear()
        self.ui.comment_show_label.setText(f'《{name}》')
        self.ui.comment_id_Edit.insertPlainText(f'{id}')
        self.ui.comment_name_textEdit.insertPlainText(f'{name}')

    def look_comments(self):#查看网易云歌曲评论
        self.ui.comment_textEdit.clear()
        self.ui.comment_id_Edit.clear()
        self.ui.comment_name_textEdit.clear()

        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            id_num = self.ui.id_Edit.toPlainText()
            id_info = id_num.split()
            d_num = int(self.ui.comment_Edit.text())

            name = self.ui.download_tableWidget.item(d_num - 1, 0).text()

            song_id = id_info[d_num - 1]
            self.output_comments(song_id)
            self.singer_show(name,song_id)
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.comment_show_label.setText("只支持网易云音乐哦！")
        else :
            self.ui.comment_show_label.setText("请先搜索音乐哦！")


    def output_comments(self,id):#显示爬取的评论
        music = cloudmusic.getMusic(id)

        coms = music.getHotComments()
        self.ui.comment_textEdit.insertPlainText("---------------热评---------------\n")
        for com in coms:
            timeStamp = (com['time']) / 1000
            dateArray = datetime.datetime.fromtimestamp(timeStamp)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            self.ui.comment_textEdit.insertPlainText(
                f'评论:[ {com["content"].strip()} ]-----用户昵称:({com["nickName"]})-----点赞数:{com["likeCount"]}-----时间:{otherStyleTime}\n\n')


        try:
            for i in range(0, 400, 20):
                self.ui.comment_textEdit.insertPlainText('---------------第 ' + str(i // 20 + 1) + ' 页---------------\n\n')
                list_info = self.get_comments(i,id)
                for j in range(20):
                    self.ui.comment_textEdit.insertPlainText(
                        f'评论:[ {list_info[j][1]} ]-----用户昵称:({list_info[j][0]})-----点赞数:{list_info[j][2]}-----时间:{list_info[j][3]}\n\n')
        except IndexError:
            self.ui.comment_textEdit.insertPlainText("---------------全部评论已经爬取完毕！---------------")

    def get_comments(self, page, id):
        headers = {
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        """
        获取评论信息
        """
        url = f'http://music.163.com/api/v1/resource/comments/R_SO_4_{id}?limit=20&offset=' + str(page)
        response = requests.get(url=url, headers=headers)
        # 将字符串转为json格式
        result = json.loads(response.text)
        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            items = result['comments']
            list_info_ct = []
            for item in items:
                info = []
                # 用户名
                user_name = item['user']['nickname'].replace(',', '，')
                # 评论内容
                comment = item['content'].strip().replace('\n', '').replace(',', '，')
                # 评论点赞数
                praise = str(item['likedCount'])
                # 评论时间
                date = time.localtime(int(str(item['time'])[:10]))
                date = time.strftime("%Y-%m-%d %H:%M:%S", date)
                info.append(user_name)
                info.append(comment)
                info.append(praise)
                info.append(date)
                list_info_ct.append(info)
            return list_info_ct
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.lyrics_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.lyrics_show_label.setText("没有找到音乐信息,请先搜索吧！")


    def platform_netease(self):
        name = self.ui.input_Edit.text()
        if name == '':
            self.ui.show_label.setText('请先搜索音乐哦！')
        else:
            self.show_music('netease')

    def platform_tencent(self):
        name = self.ui.input_Edit.text()
        if name == '':
            self.ui.show_label.setText('请先搜索音乐哦！')
        else:
            self.show_music('tencent')

    def platform_kugou(self):
        name = self.ui.input_Edit.text()
        if name == '':
            self.ui.show_label.setText('请先搜索音乐哦！')
        else:
            self.show_music('kugou')


    def show_music(self,source):#显示音乐
        self.ui.type_Edit.clear()
        self.ui.type_Edit.insertPlainText(source)
        self.ui.id_Edit.clear()
        self.ui.show_label.setText('搜索完成！')

        name = self.ui.input_Edit.text()


        url = 'https://api.zhuolin.wang/api.php?callback=jQuery111303334237052043867_1589428664685&types=playlist&id=3778678&_=1589428664686'
        data = {
            'types': 'search',
            'count': '20',
            'source': f'{source}',
            'pages': '1',
            'name': name
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }


        list_info = self.musicSpider(url, data, headers)


        method = self.ui.download_tableWidget.rowCount()
        for i in range(method):
            self.ui.download_tableWidget.removeRow(1)

        for i in range(len(list_info) ):
            self.ui.download_tableWidget.insertRow(0)
        for i in range(len(list_info)):
            self.ui.download_tableWidget.setItem(i, 0, QTableWidgetItem(f"{list_info[i][1]}"))
            self.ui.download_tableWidget.setItem(i, 1, QTableWidgetItem(f"{list_info[i][2]}"))
            self.ui.download_tableWidget.setItem(i, 2, QTableWidgetItem(f"《{list_info[i][3]}》"))
            self.ui.id_Edit.insertPlainText(f'{list_info[i][0]}\n')



    def musicSpider(self,url, data, headers):#音乐爬取

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

    def download_type(self):
        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            self.download_music_netease()
        elif type_music == 'tencent':
            self.download_music('tencent')
        elif type_music == 'kugou':
            self.download_music('kugou')

    def download_music_netease(self):#网易云音乐下载


        id_num = self.ui.id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.input_Edit_2.text())

        name = self.ui.download_tableWidget.item(d_num-1,0).text()
        sing_name = self.ui.download_tableWidget.item(d_num-1,1).text()

        song_id = id_info[d_num - 1]
        song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

        os.makedirs("Music",exist_ok=True)
        path = f"Music\{name}-{sing_name}.mp3"

        urlretrieve(song_url,path)

        self.ui.show_label.setText('下载成功！')

    def download_music(self,source):#音乐下载

        id_num = self.ui.id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.input_Edit_2.text())

        name = self.ui.download_tableWidget.item(d_num-1,0).text()
        sing_name = self.ui.download_tableWidget.item(d_num - 1, 1).text()

        song_id = id_info[d_num - 1]

        url = "https://api.zhuolin.wang/api.php?callback=jQuery111305940605786929793_1588688866522&types=playlist&id=112504&_=1588688866523"
        data = {
            'types': 'url',
            'id': f'{song_id}',
            'source': f'{source}'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }

        try:
            rsp = requests.post(url, data=data, headers=headers)
            if source == 'tencent':
                link = rsp.text[rsp.text.index('http'):rsp.text.index('",')]
                link = link.replace('\\', '')
            elif source == 'kugou':
                link = rsp.text[rsp.text.index('http'):rsp.text.index('mp3')] + 'mp3'
                link = link.replace('\\', '')
        except:
            self.ui.show_label.setText('音乐文件丢失！')


        try:
            os.makedirs("Music", exist_ok=True)
            path = f"Music\{name}-{sing_name}.mp3"
            urlretrieve(link, path)
            self.ui.show_label.setText('下载完成！')
        except Exception:
            self.ui.show_label.setText('这首难搞哦！')


if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('./Image/song.png'))
    music_dowload = Music_Dowload()
    music_dowload.ui.show()
    app.exec_()