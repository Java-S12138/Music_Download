import os
import re
import sys
import time
import xlwt
import json
import random
import requests
import datetime
import threading
import cloudmusic
import Music_Funciton
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import QObject, Signal, QUrl, QTimer, QByteArray
from PySide2.QtMultimedia import QMediaContent, QMediaPlayer
from PySide2.QtWidgets import QApplication, QTableWidgetItem, QAbstractItemView, QMessageBox, QListWidgetItem


class SignalStore(QObject):  # 进度条
    progress_update = Signal(int)
    top_progress_update = Signal(int)


so = SignalStore()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class DataList:
    def __init__(self):
        self.img_url = []  # 首页图片显示的url
        self.bt_name = []  # 首页按键的标题
        self.bt_id = []  # 首页按键的id值

        self.music_name = []  # 歌曲列表显示区域
        self.music_id = []  # 歌曲列表显示的ID
        self.music_url = []  # 音乐下载地址及信息

        self.pre_music_index = 0  # 上一首歌的index
        self.music_pages = 0  # 歌单码数
        self.music_count = 0  # 歌单总页数


def all_download(song_id, music, name):
    try:
        song_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
        Music_Funciton.music_download(song_url, music, name)
    except:
        pass


def title_txt(title):  # 主页歌单标题字数限制
    if len(title) > 18:
        return title[:9] + '\n' + title[9:18] + "..."
    elif len(title) > 9:
        return title[:9] + '\n' + title[9:]
    else:
        return title


class MusicDownload(QObject):
    def __init__(self):
        super(MusicDownload, self).__init__()
        self.lock = threading.Lock()
        self.date = DataList()
        self.img_list = []
        self.title_list = []
        self.player = QMediaPlayer()  # 音乐播放器
        self.player.setVolume(50)
        self.time = QTimer()
        self.time.start(1000)  # 定时一秒
        self.copyright_flag = False
        so.progress_update.connect(self.set_progress)  # 进度条
        so.top_progress_update.connect(self.top_set_progress)  # 进度条
        self.ongoing = False  # 下载警告
        # self.ui = QUiLoader().
        self.ui = QUiLoader().load(resource_path('download.ui'))  # 关联ui界面文件
        self.play()

    def play(self):
        self.ui.top_textEdit.setReadOnly(True)
        self.ui.comment_textEdit.setReadOnly(True)
        self.ui.lyrics_textEdit.setReadOnly(True)
        self.ui.comment_textEdit.setReadOnly(True)
        self.ui.textBrowser.setReadOnly(True)
        self.ui.textBrowser_2.setReadOnly(True)
        self.ui.seek_Button.clicked.connect(self.platform_netease)  # 搜索网易云
        self.ui.seek_Button_2.clicked.connect(self.platform_tencent)  # 搜索QQ音乐
        self.ui.seek_Button_3.clicked.connect(self.platform_kugou)  # 搜索酷狗音乐
        self.ui.download_Button.clicked.connect(self.download_type_thread)  # 下载按钮
        self.ui.all_download_Button.clicked.connect(self.all_music_download)  # 下载按钮
        self.ui.top_download_Button.clicked.connect(self.all_top_download)  # 下载按钮
        self.ui.open_Button.clicked.connect(self.open_file)  # 打开保存音乐的文件夹
        self.ui.open_Button_2.clicked.connect(self.open_file)  # 打开保存音乐的文件夹
        self.ui.open_Button_3.clicked.connect(self.open_file)  # 打开保存音乐的文件夹
        self.ui.open_Button_4.clicked.connect(self.open_file)  # 打开保存音乐的文件夹
        self.ui.comment_pushButton.clicked.connect(self.look_comments)  # 查看评论
        self.ui.comment_pushButton_2.clicked.connect(self.in_excel)  # 生成excel文件
        self.ui.comment_pushButton_3.clicked.connect(self.open_excel)  # 打开excel文件
        self.ui.lyrics_pushButton.clicked.connect(self.lyrics)  # 查看歌词
        self.ui.lyrics_pushButton_2.clicked.connect(self.lyrics_t)  # 查看歌词时间版
        self.ui.comboBox.currentIndexChanged.connect(self.top)  # 查看排行榜
        self.ui.home_comboBox_2.currentIndexChanged.connect(self.home_top)  # 查看主页排行榜
        self.ui.top_pushButton.clicked.connect(self.music_top_download)  # 下载排行榜里面的音乐
        self.ui.music_list_pushButton.clicked.connect(lambda: self.music_list("music_play"))  # 显示歌单内容
        self.ui.music_list_pushButton_album.clicked.connect(lambda: self.music_list("album"))  # 显示歌单内容
        self.ui.music_list_pushButton_2.clicked.connect(self.music_list_download)  # 下载歌单里面的音乐
        self.ui.music_list_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置歌单表格为只读
        self.ui.download_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置歌单表格为只读
        self.ui.music_start_stop.setObjectName("start")
        self.img_list = [
            self.ui.img0, self.ui.img1, self.ui.img2, self.ui.img3,
            self.ui.img4, self.ui.img5, self.ui.img6, self.ui.img7
        ]
        self.title_list = [
            self.ui.title0, self.ui.title1, self.ui.title2, self.ui.title3,
            self.ui.title4, self.ui.title5, self.ui.title6, self.ui.title7
        ]
        self.show_title_thread("说唱")  # 默认歌单为说唱
        self.ui.home_listWidget.itemDoubleClicked.connect(self.music_double_click_thread)  # 双击播放线程
        self.time.timeout.connect(self.timeout_process)
        self.ui.music_start_stop.clicked.connect(self.stop_or_start_song)  # 播放暂停
        self.ui.music_next.clicked.connect(self.next_music_thread)  # 下一首线程
        self.ui.music_pre.clicked.connect(self.pre_music_thread)  # 上一首线程
        self.ui.song_module.clicked.connect(self.change_module)  # 播放模式改变
        self.ui.home_comboBox.currentIndexChanged.connect(self.home_playlist_thread)  # 主页歌单切换
        self.ui.time_line.sliderMoved.connect(self.music_time_adjust)  # 拖动进度条改变播放进度
        self.ui.time_line.sliderReleased.connect(self.music_time_adjust_over)  # 拖动进度条改变播放进度完成
        self.ui.volume_line.valueChanged.connect(self.volume_adjust)  # 拖动音量条改变音量
        self.ui.home_Button_net.clicked.connect(self.search_show_net)  # 搜索结果
        self.ui.home_Button_qq.clicked.connect(lambda: self.search_show_qq("tencent"))  # 搜索结果
        self.ui.home_Button_ku.clicked.connect(lambda: self.search_show_qq("kugou"))  # 搜索结果
        self.ui.home_download_Button.clicked.connect(self.home_download_thread)  # 下载正在播放的音乐
        self.ui.change_Button.clicked.connect(self.change_title)  # 更换上方图片
        for i in self.title_list:
            i.clicked.connect(self.home_title_playlist)  # 首页歌单和电台点击播放
        self.ui.music_next_2.clicked.connect(self.music_pages_next_thread)
        self.ui.music_pre_2.clicked.connect(self.music_pages_previous_thread)

    def change_title(self):  # 更换上方图片
        title_image = ["title.png", "title1.png", "title2.png", "title3.png", "title4.png"]
        title = random.sample(title_image, 1)
        self.ui.label_5.setPixmap(QPixmap(f"{os.getcwd()}/Image/{title[0]}"))

    def home_download(self):  # 播放音乐下载
        os.makedirs("Music", exist_ok=True)
        url = self.date.music_url[0]
        music_name = self.date.music_url[1]
        Music_Funciton.music_download(url, music_name)

        self.ui.hmoe_show_label.setText('下载完成！')

    def top_home_show(self, list_info):
        self.date.music_name.clear()
        self.date.music_id.clear()
        self.ui.home_listWidget.clear()
        for i in range(len(list_info[0])):
            temp = QListWidgetItem(list_info[0][i])
            self.date.music_id.append(list_info[1][i])
            self.date.music_name.append(list_info[0][i])
            temp.setIcon(QIcon(f"{os.getcwd()}/Image/song1.png"))
            temp.setToolTip("双击播放")
            self.ui.home_listWidget.addItem(temp)

    def home_top(self):  # 网易云排行榜
        text = self.ui.home_comboBox_2.currentText()
        self.ui.home_id_Edit.insertPlainText("netease")
        music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=19723756")
        if text == "云音乐飙升榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=19723756")
        elif text == "云音乐新歌榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=3779629")
        elif text == "网易原创歌曲榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2884035")
        elif text == "云音乐热歌榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=3778678")
        elif text == "云音乐说唱榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=991319590")
        elif text == "云音乐古典音乐榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=71384707")
        elif text == "云音乐电音榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=1978921795")
        elif text == "抖音排行榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2250011882")
        elif text == "新声榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2617766278")
        elif text == "云音乐ACG音乐榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=71385702")
        elif text == "云音乐韩语榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=745956260")
        elif text == "云音乐国电榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=10520166")
        elif text == "英国Q杂志中文版周榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2023401535")
        elif text == "电竞音乐榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2006508653")
        elif text == "UK排行榜周榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=180106")
        elif text == "美国Billboard周榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=60198")
        elif text == "Beatport全球电子舞曲榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=3812895")
        elif text == "KTV唛榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=21845217")
        elif text == "iTunes榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=11641012")
        elif text == "日本Oricon周榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=60131")
        elif text == "Hit FM Top榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=120001")
        elif text == "台湾Hito排行榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=112463")
        elif text == "云音乐欧美热歌榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=2809513713")
        elif text == "法国 NRJ Vos Hits 周榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=27135204")
        elif text == "中国新乡村音乐排行榜":
            music_info = Music_Funciton.music_home_top("https://music.163.com/discover/toplist?id=3112516681")
        self.top_home_show(music_info)

    # 显示QQ音乐搜索结果
    def search_show_qq(self, type_in_method):

        self.ui.home_listWidget.clear()
        self.date.music_id.clear()
        self.date.music_name.clear()
        self.ui.home_id_Edit.clear()
        music_name = self.ui.home_input_Edit.text()
        self.ui.home_id_Edit.insertPlainText("tencent")
        list_info = Music_Funciton.home_show_music(type_in_method, music_name)
        # if type_in_method == "tencent":
        #     self.ui.home_id_Edit.insertPlainText("tencent")
        #     list_info = Music_Funciton.home_show_music(type_in_method, music_name)
        if type_in_method == "kugou":
            self.ui.home_id_Edit.insertPlainText("kugou")
            list_info = Music_Funciton.home_show_music(type_in_method, music_name)

        for i in range(len(list_info)):
            temp = QListWidgetItem(list_info[i][1] + "---" + list_info[i][2])
            self.date.music_id.append(list_info[i][0])
            self.date.music_name.append(list_info[i][1])
            temp.setIcon(QIcon(f"{os.getcwd()}/Image/song1.png"))
            temp.setToolTip("双击播放")
            self.ui.home_listWidget.addItem(temp)

    # 显示网易云搜索结果
    def search_show_net(self):
        self.lock.acquire()

        self.ui.home_listWidget.clear()
        self.date.music_id.clear()
        self.ui.home_id_Edit.clear()
        self.date.music_name.clear()
        self.ui.home_id_Edit.insertPlainText("netease")
        music_name = self.ui.home_input_Edit.text()

        list_info = Music_Funciton.home_show_music("netease", music_name)
        for i in range(len(list_info)):
            temp = QListWidgetItem(list_info[i][1] + "---" + list_info[i][2])
            self.date.music_id.append(list_info[i][0])
            self.date.music_name.append(list_info[i][1])
            temp.setIcon(QIcon(f"{os.getcwd()}/Image/song1.png"))
            temp.setToolTip("双击播放")
            self.ui.home_listWidget.addItem(temp)
        self.lock.release()

    # 播放方式改变
    def change_module(self):
        if self.ui.song_module.toolTip() == "列表循环":
            self.ui.song_module.setIcon(QIcon(f"{os.getcwd()}/Image/单曲循环.png"))
            self.ui.song_module.setToolTip("单曲循环")
        elif self.ui.song_module.toolTip() == "单曲循环":
            self.ui.song_module.setIcon(QIcon(f"{os.getcwd()}/Image/随机.png"))
            self.ui.song_module.setToolTip("随机播放")
        elif self.ui.song_module.toolTip() == "随机播放":
            self.ui.song_module.setIcon(QIcon(f"{os.getcwd()}/Image/列表循环.png"))
            self.ui.song_module.setToolTip("列表循环")

    # 播放和暂停
    def stop_or_start_song(self):
        if self.ui.music_start_stop.objectName() == "start":
            if self.ui.home_music_name_label.text():
                self.player.play()
                self.ui.music_start_stop.setObjectName("stop")
                self.ui.music_start_stop.setIcon(QIcon(f"{os.getcwd()}/Image/停在-01.png"))
        elif self.ui.music_start_stop.objectName() == "stop":
            self.player.pause()
            self.ui.music_start_stop.setObjectName("start")
            self.ui.music_start_stop.setIcon(QIcon(f"{os.getcwd()}/Image/播放-01.png"))

    # 音量图标显示
    def volume_adjust(self):
        self.player.setVolume(self.ui.volume_line.value())
        if self.ui.volume_line.value() == 0:
            self.ui.volume.setPixmap(QPixmap(f"{os.getcwd()}/Image/horn_0.png"))
        elif self.ui.volume_line.value() < 30:
            self.ui.volume.setPixmap(QPixmap(f"{os.getcwd()}/Image/horn_30.png"))
        elif self.ui.volume_line.value() < 80:
            self.ui.volume.setPixmap(QPixmap(f"{os.getcwd()}/Image/horn.png"))
        else:
            self.ui.volume.setPixmap(QPixmap(f"{os.getcwd()}/Image/horn_100.png"))

    # 调节播放进度
    def music_time_adjust(self):
        self.player.pause()
        self.player.setPosition(self.ui.time_line.value() * 1000)

    def music_time_adjust_over(self):
        self.player.play()

    # 下载进程
    def home_download_thread(self):
        dowload_music = threading.Thread(target=self.home_download)
        dowload_music.start()

    # 下一首线程
    def next_music_thread(self):
        next_music = threading.Thread(target=self.next_music)
        next_music.start()

    # 上一首线程
    def pre_music_thread(self):
        pre_music = threading.Thread(target=self.pre_music)
        pre_music.start()

    # 下一首歌曲
    def next_music(self):
        self.change_music_down()
        self.double_click_play()
        while self.copyright_flag:  # 防止歌单中下一首是没有版权的歌曲导致播放停止
            self.change_music_down()
            self.double_click_play()

    def pre_music(self):
        self.change_music_up()
        self.double_click_play()
        while self.copyright_flag:  # 防止歌单中下一首是没有版权的歌曲导致播放停止
            self.change_music_up()
            self.double_click_play()

    def change_music_up(self):
        index = self.ui.home_listWidget.currentRow()
        if not len(self.date.music_name) == 1:
            if not self.copyright_flag:
                self.date.pre_music_index = index
            if self.ui.song_module.toolTip() == "列表循环":
                if index == (len(self.date.music_name) - 1):
                    index = 0
                else:
                    index = index - 1
            elif self.ui.song_module.toolTip() == "随机播放":
                while True:
                    # 随机播放，防止下一首是本首歌
                    num = random.randint(0, len(self.date.music_name) - 1)
                    if not num == index:
                        index = num
                        break
        self.ui.home_listWidget.setCurrentRow(index)

    def change_music_down(self):
        index = self.ui.home_listWidget.currentRow()
        if not len(self.date.music_name) == 1:
            if not self.copyright_flag:
                self.date.pre_music_index = index
            if self.ui.song_module.toolTip() == "列表循环":
                if index == (len(self.date.music_name) - 1):
                    index = 0
                else:
                    index = index + 1
            elif self.ui.song_module.toolTip() == "随机播放":
                while True:
                    # 随机播放，防止下一首是本首歌
                    num = random.randint(0, len(self.date.music_name) - 1)
                    if not num == index:
                        index = num
                        break
        self.ui.home_listWidget.setCurrentRow(index)

    def timeout_process(self):  # 时间线显示
        if self.ui.music_start_stop.objectName() == "stop":
            time_value = self.ui.time_line.value()
            self.ui.time_line.setValue(time_value + 1)
            self.ui.time_pre_2.setText(
                str((time_value + 1) // 60).zfill(2) + ':' + str((time_value + 1) % 60).zfill(2)
            )
            if self.ui.time_pre_2.text() == self.ui.time_pre_3.text():
                self.player_stop_setting()
                self.ui.time_pre_2.setText("00:00")
                self.ui.time_line.setValue(0)
                self.next_music_thread()
            if self.ui.time_pre_2.text() == "00:02":
                time_long = self.player.duration()  # 获取到实际这首歌的播放长度
                self.ui.time_line.setRange(0, int(time_long / 1000) + 1)  # 设置进度条范围
                self.ui.time_pre_3.setText(  # 设置音频长度的显示
                    str(int(time_long / 1000) // 60).zfill(2) + ':' + str(int(time_long / 1000) % 60).zfill(2)
                )

    def music_double_click_thread(self):  # 首页音乐框 双击歌曲后播放 多线程运行
        double_click = threading.Thread(target=self.double_click_play)
        double_click.start()

    def player_setting(self):  # 播放开始
        self.ui.time_line.setValue(0)
        self.ui.time_pre_2.setText("00:00")
        self.player.play()
        self.ui.music_start_stop.setIcon(QIcon(f"{os.getcwd()}/Image/停在-01.png"))
        self.ui.music_start_stop.setObjectName("stop")

    def player_stop_setting(self):  # 播放停止
        self.player.stop()
        self.ui.music_start_stop.setObjectName("start")
        self.ui.music_start_stop.setIcon(QIcon(f"{os.getcwd()}/Image/播放-01.png"))
        self.player_setting()
        self.copyright_flag = False

    def double_click_play(self):  # 首页音乐框 双击歌曲后播放
        self.ui.hmoe_show_label.setText('')
        index = self.ui.home_listWidget.currentRow()  # 获取双击的标签的索引值
        music_type = self.ui.home_id_Edit.toPlainText()
        self.date.music_url.clear()

        if music_type == "tencent":
            music_id = self.date.music_id[index]
            url = Music_Funciton.home_play_music(music_id, music_type)
            self.player_stop_setting()  # 播放停止设置
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.date.music_url.append(url)
            self.date.music_url.append(self.date.music_name[index])
            self.ui.home_music_name_label.setText(self.date.music_name[index])
            self.player_setting()  # 播放开始设置
            self.copyright_flag = False
        elif music_type == "kugou":
            music_id = self.date.music_id[index]
            url = Music_Funciton.home_play_music(music_id, music_type)
            self.player_stop_setting()  # 播放停止设置
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.date.music_url.append(url)
            self.date.music_url.append(self.date.music_name[index])
            self.ui.home_music_name_label.setText(self.date.music_name[index])
            self.player_setting()  # 播放开始设置
            self.copyright_flag = False
        else:
            music_id = self.date.music_id[index]
            url = Music_Funciton.song_url(music_id)
            self.player_stop_setting()  # 播放停止设置
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.date.music_url.append(url)
            self.date.music_url.append(self.date.music_name[index])
            self.ui.home_music_name_label.setText(self.date.music_name[index])
            self.player_setting()  # 播放开始设置
            self.copyright_flag = False

    def home_title_playlist(self):  # 显示歌单音乐
        self.ui.home_id_Edit.clear()
        send = self.sender()
        id_str = send.objectName()
        self.date.music_name, self.date.music_id = Music_Funciton.playlist_info(id_str.split('=')[1])
        self.ui.home_listWidget.clear()  # 列表清空
        for i in range(len(self.date.music_name)):  # 加入选中歌单中的歌曲名
            temp = QListWidgetItem(self.date.music_name[i])
            temp.setIcon(QIcon(f"{os.getcwd()}/Image/song1.png"))
            temp.setToolTip("双击播放")
            self.ui.home_listWidget.addItem(temp)

    def show_title_thread(self, type_in_method):  # 主页歌单标题button 多线程运行
        first_page_display = threading.Thread(target=lambda: self.home_show_title(type_in_method))
        first_page_display.start()

    def music_pages_previous_thread(self):
        next_in_method = threading.Thread(target=self.music_pages_previous)
        next_in_method.start()

    def music_pages_next_thread(self):
        next_in_method = threading.Thread(target=self.music_pages_next)
        next_in_method.start()

    def home_playlist_thread(self):
        home_playlist_ing = threading.Thread(target=self.home_playlist)
        home_playlist_ing.start()

    def home_playlist(self):  # 网易云排行榜
        text = self.ui.home_comboBox.currentText()
        if text == "华语":
            self.show_title_thread(text)
        elif text == "欧美":
            self.show_title_thread(text)
        elif text == "日语":
            self.show_title_thread(text)
        elif text == "韩语":
            self.show_title_thread(text)
        elif text == "粤语":
            self.show_title_thread(text)
        elif text == "说唱":
            self.show_title_thread(text)
        elif text == "流行":
            self.show_title_thread(text)
        elif text == "民谣":
            self.show_title_thread(text)
        elif text == "爵士":
            self.show_title_thread(text)
        elif text == "乡村":
            self.show_title_thread(text)
        elif text == "古典":
            self.show_title_thread(text)
        elif text == "古风":
            self.show_title_thread(text)
        elif text == "清晨":
            self.show_title_thread(text)
        elif text == "夜晚":
            self.show_title_thread(text)
        elif text == "学习":
            self.show_title_thread(text)
        elif text == "工作":
            self.show_title_thread(text)

    def home_show_title(self, type_in_method):  # 主页歌单标题button

        self.ui.home_listWidget.clear()
        self.date.img_url, self.date.bt_name, self.date.bt_id = Music_Funciton.wyy_first_page(type_in_method)
        self.date.music_count = int(len(self.date.img_url) / 8)
        self.ui.hmoe_pages_label.setText(f'1/{str(self.date.music_count)}')

        for i in range(8):
            img = QPixmap()
            img.loadFromData(QByteArray(requests.get(self.date.img_url[i]).content))
            self.img_list[i].setPixmap(img)
            self.title_list[i].setText(title_txt(self.date.bt_name[i]))
            self.title_list[i].setObjectName(self.date.bt_id[i])

    def music_pages_next(self):  # 歌单页面下一页
        if self.date.music_pages + 1 < self.date.music_count:
            self.date.music_pages += 1
            self.ui.hmoe_pages_label.setText(f'{str(self.date.music_pages + 1)}/{str(self.date.music_count)}')
            for i in range(8):
                img = QPixmap()
                img.loadFromData(QByteArray(requests.get(self.date.img_url[(8 * self.date.music_pages) + i]).content))
                self.img_list[i].setPixmap(img)
                self.title_list[i].setText(title_txt(self.date.bt_name[(8 * self.date.music_pages) + i]))
                self.title_list[i].setObjectName(self.date.bt_id[(8 * self.date.music_pages) + i])
        else:
            self.ui.hmoe_show_label.setText('最后一页啦!')
            time.sleep(1)
            self.ui.hmoe_show_label.setText('')

    def music_pages_previous(self):  # 歌单页面上一页
        if self.date.music_pages + 1 == 1:
            self.ui.hmoe_show_label.setText('已经是第一页!')
            time.sleep(1)
            self.ui.hmoe_show_label.setText('')
        else:
            self.ui.hmoe_pages_label.setText(f'{str(self.date.music_pages)}/{str(self.date.music_count)}')
            self.date.music_pages -= 1
            for i in range(8):
                img = QPixmap()
                img.loadFromData(QByteArray(requests.get(self.date.img_url[(8 * self.date.music_pages) - i]).content))
                self.img_list[i].setPixmap(img)
                self.title_list[i].setText(title_txt(self.date.bt_name[(8 * self.date.music_pages) - i]))
                self.title_list[i].setObjectName(self.date.bt_id[(8 * self.date.music_pages) - i])

    # ------------------------------ 歌单 ------------------------------

    def set_progress(self, value):  # 歌单进度条
        self.ui.all_d_Bar.setValue(value)

    def all_music_download(self):
        music_name = []
        music_singe = []
        id_num = self.ui.music_list_id_Edit.toPlainText()
        id_info = id_num.split()
        method = self.ui.music_list_tableWidget.rowCount()
        self.ui.all_d_Bar.setRange(0, method)

        for i in range(method):
            music_n = self.ui.music_list_tableWidget.item(i, 0).text()
            music_s = self.ui.music_list_tableWidget.item(i, 1).text()
            music_name.append(music_n)
            music_singe.append(music_s)

        def do_download():
            self.ongoing = True
            for i in range(method):
                all_download(id_info[i], music_name[i], music_singe[i])
                so.progress_update.emit(i + 1)
            self.ongoing = False

        if self.ongoing:
            QMessageBox.warning(
                self.ui,
                '警告', '下载中，请等待完成')
            return
        t = threading.Thread(target=do_download, daemon=True)
        t.start()

    def music_list(self, type_in_method):  # 歌单
        self.ui.music_list_id_Edit.clear()
        method = self.ui.music_list_tableWidget.rowCount()
        for i in range(method):
            self.ui.music_list_tableWidget.removeRow(0)

        music_id = int(self.ui.music_list_Edit.text())
        if type_in_method == 'music_play':
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

    def music_list_download(self):  # 歌单音乐下载

        id_num = self.ui.music_list_id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.music_list_lineEdit.text())

        name = self.ui.music_list_tableWidget.item(d_num - 1, 0).text()

        song_id = id_info[d_num - 1]

        song_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
        Music_Funciton.music_download(song_url, name)

        self.ui.music_list_label.setText('下载成功！')
        time.sleep(1)
        self.ui.music_list_label.setText('')

    def open_file(self):  # 打开文件夹
        try:
            os.startfile(f'{os.getcwd()}/Music')
        except FileNotFoundError:
            self.ui.show_label.setText('你还没下载呢！')

    # ------------------------------ 歌单 ------------------------------

    # ------------------------------ 排行榜 ------------------------------

    def top_set_progress(self, value):  # 排行榜进度条
        self.ui.top_d_Bar.setValue(value)

    def all_top_download(self):  # 排行榜所有音乐下载
        music = self.ui.top_textEdit.toPlainText()
        music_info = music.split("\n")
        id_num = self.ui.top_id_Edit.toPlainText()
        id_info = id_num.split()
        music_info_remove = []
        self.ui.top_d_Bar.setRange(0, len(id_info))
        for i in range(len(music_info)):
            music_info_remove.append(re.findall(r'《(.*)》', music_info[i]))

        def top_dodownload():
            self.ongoing = True
            for i in range(len(id_info)):
                all_download(id_info[i], music_info_remove[i][0], name="")
                so.top_progress_update.emit(i + 1)
            self.ongoing = False

        if self.ongoing:
            QMessageBox.warning(
                self.ui,
                '警告', '下载中，请等待完成')
            return
        t = threading.Thread(target=top_dodownload, daemon=True)
        t.start()

    def top(self):  # 网易云排行榜
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

    def music_top_download(self):  # 排行榜音乐下载
        try:
            num = int(self.ui.top_lineEdit.text())

            id_num = self.ui.top_id_Edit.toPlainText()
            id_info = id_num.split()

            name = self.ui.top_textEdit.toPlainText()
            name_info = re.findall(r'《(.*)》', name)

            song_id = id_info[num - 1]
            song_name = name_info[num - 1]
            song_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

            os.makedirs("Music", exist_ok=True)
            Music_Funciton.music_download(song_url, song_name)

            self.ui.top_show_label.setText('下载完成！')
        except:
            self.ui.top_show_label.setText("你还没有输入序号哦！")

    def music_top(self, url):  # 网易云音乐排行榜显示
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
            text = res.text
            try:
                all_in_method = re.findall(r'<Ul Class="F-Hide">(.*?)</Ul>', text, re.I)
                str_in_method = all_in_method[0]
                str_list = re.findall(r'">(.*?)</a>', str_in_method)
                id_list = re.findall(r'id=(\d+)', str_in_method)
                for i in range(len(str_list)):
                    self.ui.top_textEdit.insertPlainText(f"{i + 1} 《{str_list[i]}》\n")
                    self.ui.top_id_Edit.insertPlainText(f"{id_list[i]}\n")
            except:
                self.ui.top_show_label.setText('提取文章出错！')
        except:
            self.ui.top_show_label.setText('网页提取出现问题！')

    # ------------------------------ 排行榜 ------------------------------

    # ------------------------------ 歌词 ------------------------------

    def lyrics_t(self):  # 歌词显示

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

            lrc_url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1'
            lyric = requests.get(lrc_url, headers=headers)
            json_obj = lyric.text  # 网页源码
            j = json.loads(json_obj)
            lrc = j['lrc']['lyric']
            self.ui.lyrics_textEdit.insertPlainText(lrc)

            self.ui.lyrics_show_label.setText(f"《{name}》")
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.lyrics_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.lyrics_show_label.setText("没有找到音乐信息,请先搜索吧！")

    def lyrics(self):  # 歌词显示 时间版
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

            lrc_url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1'
            lyric = requests.get(lrc_url, headers=headers)
            json_obj = lyric.text  # 网页源码
            j = json.loads(json_obj)
            lrc = j['lrc']['lyric']
            pat = re.compile(r'\[.*\\]')
            lrc = re.sub(pat, "", lrc)
            lrc = lrc.strip()
            self.ui.lyrics_textEdit.insertPlainText(lrc)

            self.ui.lyrics_show_label.setText(f"《{name}》")
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.lyrics_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.lyrics_show_label.setText("没有找到音乐信息,请先搜索吧！")

    # ------------------------------ 歌词 ------------------------------

    # ------------------------------ 评论 ------------------------------

    def in_excel(self):  # 把评论写入excel
        headers = {
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        """
        获取评论信息
        """
        id_in_method = self.ui.comment_id_Edit.toPlainText()
        name = self.ui.comment_name_textEdit.toPlainText()
        list_info_ct = []

        music = cloudmusic.getMusic(id_in_method)
        coms = music.getHotComments()
        for com in coms:
            time_stamp = (com['time']) / 1000
            date_array = datetime.datetime.fromtimestamp(time_stamp)
            other_style_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
            info = [com["nickName"], com["likeCount"], other_style_time,
                    com["content"].strip().replace('\n', '').replace(',', '，')]
            list_info_ct.append(info)

        try:
            for page in range(0, 1020, 20):
                url = f'https://music.163.com/api/v1/resource/comments/R_SO_4_{id_in_method}?limit=20&offset=' + str(page)
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
            col = ("用户昵称", "点赞数", "发布时间", "评论")
            for i in range(4):
                sheet.write(0, i, col[i])  # 列名
            for i in range(len(list_info_ct)):
                data = list_info_ct[i]
                for j in range(4):
                    sheet.write(i + 1, j, data[j])  # 数据
            os.makedirs("Excel", exist_ok=True)
            book.save(f"{os.getcwd()}\\Excel\\{name}.xls")

            self.ui.comment_show_label.setText("生成完毕！")
        except KeyError:
            self.ui.comment_show_label.setText("没有找到音乐信息哦，请先搜索吧！")

    def open_excel(self):  # 打开excel文件
        try:
            name = self.ui.comment_name_textEdit.toPlainText()
            os.startfile(f'{os.getcwd()}\\Excel\\{name}.xls')
        except FileNotFoundError:
            self.ui.comment_show_label.setText("没有找到Excel文件哦，请先生成吧！")

    def singer_show(self, name, id_in_method):  # 评论部分信息显示
        self.ui.comment_id_Edit.clear()
        self.ui.comment_name_textEdit.clear()
        self.ui.comment_show_label.setText(f'《{name}》')
        self.ui.comment_id_Edit.insertPlainText(f'{id_in_method}')
        self.ui.comment_name_textEdit.insertPlainText(f'{name}')

    def look_comments(self):  # 查看网易云歌曲评论
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
            self.singer_show(name, song_id)
        elif type_music == 'tencent' or type_music == 'kugou':
            self.ui.comment_show_label.setText("只支持网易云音乐哦！")
        else:
            self.ui.comment_show_label.setText("请先搜索音乐哦！")

    def output_comments(self, id_in_method):  # 显示爬取的评论

        music = cloudmusic.getMusic(id_in_method)

        coms = music.getHotComments()
        self.ui.comment_textEdit.insertPlainText("---------------热评---------------\n")
        for com in coms:
            time_stamp = (com['time']) / 1000
            date_array = datetime.datetime.fromtimestamp(time_stamp)
            other_style_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
            self.ui.comment_textEdit.insertPlainText(
                f'评论:[ {com["content"].strip()} ]\n用户昵称:({com["nickName"]})\n点赞数:{com["likeCount"]}\n时间:{other_style_time}\n\n')

        try:
            for i in range(0, 400, 20):
                self.ui.comment_textEdit.insertPlainText(
                    '---------------第 ' + str(i // 20 + 1) + ' 页---------------\n\n')
                list_info = self.get_comments(i, id_in_method)
                for j in range(20):
                    self.ui.comment_textEdit.insertPlainText(
                        f'评论:[ {list_info[j][1]} ]\n用户昵称:({list_info[j][0]})\n点赞数:{list_info[j][2]}\n时间:{list_info[j][3]}\n\n')
        except IndexError:
            self.ui.comment_textEdit.insertPlainText("---------------全部评论已经爬取完毕！---------------")

    def get_comments(self, page, id_in_method):
        headers = {
            'Host': 'music.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        """
        获取评论信息
        """
        url = f'https://music.163.com/api/v1/resource/comments/R_SO_4_{id_in_method}?limit=20&offset=' + str(page)
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

    # ------------------------------ 评论 ------------------------------

    # ------------------------------音乐下载------------------------------

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

    def show_music(self, source):  # 显示音乐
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

        list_info = Music_Funciton.musicSpider(url, data, headers)

        method = self.ui.download_tableWidget.rowCount()
        for i in range(method):
            self.ui.download_tableWidget.removeRow(0)

        for i in range(len(list_info)):
            self.ui.download_tableWidget.insertRow(0)
        for i in range(len(list_info)):
            self.ui.download_tableWidget.setItem(i, 0, QTableWidgetItem(f"{list_info[i][1]}"))
            self.ui.download_tableWidget.setItem(i, 1, QTableWidgetItem(f"{list_info[i][2]}"))
            self.ui.download_tableWidget.setItem(i, 2, QTableWidgetItem(f"《{list_info[i][3]}》"))
            self.ui.id_Edit.insertPlainText(f'{list_info[i][0]}\n')

    def download_type_thread(self):
        download_type_ing = threading.Thread(target=self.download_type)
        download_type_ing.start()

    def download_type(self):
        type_music = self.ui.type_Edit.toPlainText()
        if type_music == 'netease':
            self.download_music_netease()
        elif type_music == 'tencent':
            self.download_music('tencent')
        elif type_music == 'kugou':
            self.download_music('kugou')

    def download_music_netease(self):  # 网易云音乐下载

        id_num = self.ui.id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.input_Edit_2.text())

        name = self.ui.download_tableWidget.item(d_num - 1, 0).text()
        sing_name = self.ui.download_tableWidget.item(d_num - 1, 1).text()

        song_id = id_info[d_num - 1]
        song_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

        os.makedirs("Music", exist_ok=True)
        Music_Funciton.music_download(song_url, name, sing_name)

        self.ui.show_label.setText('下载成功！')
        time.sleep(1)
        self.ui.show_label.setText('')

    def download_music(self, source):  # 音乐下载

        id_num = self.ui.id_Edit.toPlainText()
        id_info = id_num.split()

        d_num = int(self.ui.input_Edit_2.text())

        name = self.ui.download_tableWidget.item(d_num - 1, 0).text()
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

        link = ""

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
            Music_Funciton.music_download(link, name, sing_name)
            self.ui.show_label.setText('下载完成！')
        except Exception:
            self.ui.show_label.setText('这首难搞哦！')


if __name__ == '__main__':
    if not os.path.exists('Music'):
        os.makedirs('Music')
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(f'{os.getcwd()}/Image/song.png'))
    music_download = MusicDownload()
    music_download.ui.show()
    sys.exit(app.exec_())
