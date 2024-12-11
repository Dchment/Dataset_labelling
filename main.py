import sys  # 系统内置类
from PyQt5.QtCore import * # 主要包含了我们常用的一些类，汇总到了一块
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import cv2
import numpy as np
import json
class Thread_1(QThread):  # 线程1
    st = pyqtSignal(int)
    def __init__(self):
        super(Thread_1, self).__init__()
        self.label_dict_now=None
        self.label_dict=[]

    def accept(self,label_dict_path):
        self.label_dict_path=label_dict_path
        self.label_dict_now = json.load(open(self.label_dict_path,'r',encoding='utf-8'))
        self.label_dict=[0 for i in range(len(self.label_dict_now))]
        # self.new_dict_element=new_dict_element
        
    
    # def labelling(self,label):
    #     label_now={"id":self.id_now,"label":label}
    #     print(label_now)
    #     # label_dicts=json.load(fr)
    #     # print(self.label_dicts)
    #     def update(target,dict_list):
    #         for dictionary in dict_list:
    #             if dictionary["id"] == target["id"]:
    #                 dictionary["label"]=target["label"]
    #                 return dict_list
    #         dict_list.append(target)
    #         return dict_list
    #     self.label_dicts=update(label_now,self.label_dicts)
    #     self.label_dicts.sort(key=lambda x:x['id'])
    #     print(self.label_dicts)
    #     json.dump(self.label_dicts,open(self.label_dict_path,'w',encoding='utf-8'))

    def count(self):
        unlabelled_number=self.label_dict.count(0)
        return unlabelled_number
    
    def change(self,index):
        if self.label_dict[index]==0:
            self.label_dict[index]=1 
        else:
            self.label_dict[index]=0 
        
    def show(self,num):
        self.st.emit(num)

    def run(self):
        unlabelled_number=self.count()
        self.st.emit(unlabelled_number)
        print(unlabelled_number)
        # self.labelling()
        # print(len(self.label_dicts))



class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        # 设置窗口标题
        self.setWindowTitle("图像标签")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 设置窗口尺寸
        self.resize(600, 400)
        # # 移动窗口位置
        # window.move(200, 200)
        self.setMouseTracking(True)
        self.image_dir=None
        self.image_files=[]
        self.id_now=0
        self.index_now=0
        self.label_dict_path='label.json'
        self.label_dicts=None#json.load(open(self.label_dict_path,'r',encoding='utf-8'))

        self.thread1=Thread_1()

        self.image = QLabel(self)
        self.image.move(10, 25)
        self.image.resize(256,256)
        self.image.setScaledContents(True)

        self.label1 = QLabel(self)
        self.label1.setText('图像：')
        self.label1.move(10, 10)

        self.bt1 = QPushButton(self)
        self.bt1.setText('上一张(A)')
        self.bt1.move(300, 150)
        self.bt1.clicked.connect(lambda: self.switch(-1))
        self.bt1.setShortcut('A')

        self.bt2 = QPushButton(self)
        self.bt2.setText('下一张(D)')
        self.bt2.move(400, 150)
        self.bt2.clicked.connect(lambda: self.switch(1))
        self.bt2.setShortcut('D')

        self.label2 = QLabel(self)
        self.label2.setText('请先选择数据集与存储标签的文件：')
        self.label2.move(300, 10)

        self.bt3_1 = QPushButton(self)
        self.bt3_1.setText('选择数据集文件夹')
        self.bt3_1.move(420, 30)
        self.bt3_1.clicked.connect(lambda: self.open_dir())

        self.bt3_2 = QPushButton(self)
        self.bt3_2.setText('选择存储标签的文件')
        self.bt3_2.move(300, 30)
        self.bt3_2.clicked.connect(lambda: self.open_labeldir())

        self.label3 = QLabel(self)
        self.label3.setText('按照图片索引切换：')
        self.label3.move(300, 200)

        self.index_imgpath = QComboBox(self) 
        self.index_imgpath.resize(80,20)
        self.index_imgpath.move(410, 200)
        self.index_imgpath.currentIndexChanged.connect(self.switch_by_number)
        
        
        self.bt4 = QPushButton(self)
        self.bt4.setText('是(J)')
        self.bt4.move(300, 100)
        self.bt4.clicked.connect(lambda: self.labelling('1'))
        self.bt4.setShortcut('J')

        self.bt5 = QPushButton(self)
        self.bt5.setText('否(K)')
        self.bt5.move(400, 100)
        self.bt5.clicked.connect(lambda: self.labelling('0'))
        self.bt5.setShortcut('k')

        self.label4 = QLabel(self)
        self.label4.setText('当前图像地址:')
        self.label4.move(10, 300)

        self.label_imgpath = QTextEdit(self)
        self.label_imgpath.resize(200,50)
        self.label_imgpath.move(10, 320)

        self.label5 = QLabel(self)
        self.label5.setText('结果：')
        self.label5.resize(200,50)
        self.label5.move(300, 50)

        self.bt6 = QPushButton(self)
        self.bt6.setText('跳转至未标注的图片')
        self.bt6.resize(200,30)
        self.bt6.move(300, 250)
        self.bt6.clicked.connect(self.jump_to_unlabelled)

    def open_dir(self):
        directory=''
        directory = QFileDialog.getExistingDirectory(None, "选择数据集文件夹", "")
        # print(directory)
        if directory!='':
            self.image_dir=directory
            files = os.listdir(directory)#[f for f in QFileDialog.getOpenFileNames(None, "选择文件", directory, "All Files (*)")[0]]
            self.image_files=files
            self.image_files.sort()
            self.index_now=len(self.label_dicts)-1
            for i in range(len(self.image_files)):
                self.index_imgpath.addItem(str(i))
            print(len(files))
            if self.image_files!=None:
                self.show_image(self.image_dir+'/'+self.image_files[self.index_now])
            
            
    def open_labeldir(self):
        file,file_type = QFileDialog.getOpenFileName(None, "选择存储标签的文件", "")
        # print(directory)
        if file!='':
            self.label_dict_path=file
            f=open(self.label_dict_path,'r',encoding='utf-8')
            self.label_dicts=json.load(f)
            # self.thread1.start()
            # self.thread1.accept(self.label_dict_path)

    def jump_to_unlabelled(self):
        ids_now=[j['id'] for j in self.label_dicts]
        is_changed=False
        for i in range(len(self.image_files)):
            id_now=self.search_id(self.image_files[i])
            if id_now not in ids_now:
                self.index_now=i
                self.show_image(self.image_dir+'/'+self.image_files[self.index_now])
                is_changed=True
                break
        if is_changed==False:
            self.index_now=0
            self.show_image(self.image_dir+'/'+self.image_files[self.index_now])

    def search_id(self,path):
        return int(path.split('/')[-1][:-4].split('_')[-1])
    
    def show_image(self,path):
        print(path)
        # image_now=cv2.imread(path)
        # image_now=cv2.cvtColor(image_now,cv2.COLOR_BGR2RGB)
        # image_now = cv2.resize(image_now,(256,256))
        # showed_image=QImage(path,width=256,height=256,format=QImage.Format_RGB888)
        self.image.setPixmap(QPixmap(path))
        self.id_now=self.search_id(path)
        self.label_imgpath.setText('第'+str(self.index_now)+'张'+'\n'+self.image_dir+'/'+self.image_files[self.index_now])
        txt=self.check_islabelled()
        self.label5.setText(txt)
        

    def labelling(self,label):
        label_now={"id":self.id_now,"label":label}
        print(label_now)
        # label_dicts=json.load(fr)
        # print(self.label_dicts)
        def update(target,dict_list):
            for dictionary in dict_list:
                if dictionary["id"] == target["id"]:
                    dictionary["label"]=target["label"]
                    return dict_list
            dict_list.append(target)
            return dict_list
        self.label_dicts=update(label_now,self.label_dicts)
        self.label_dicts.sort(key=lambda x:x['id'])
        # print(self.label_dicts)
        json.dump(self.label_dicts,open(self.label_dict_path,'w',encoding='utf-8'))
        txt=self.check_islabelled()
        # print(txt)
        self.label5.setText(txt)
        # fr.close()
        # fw.close()
        
    def switch(self,direction):
        self.index_now=(self.index_now+direction)%len(self.image_files)
        print(self.index_now)
        self.show_image(self.image_dir+'/'+self.image_files[self.index_now])


    def switch_by_number(self):
        self.index_now=int(self.index_imgpath.currentText())
        self.show_image(self.image_dir+'/'+self.image_files[self.index_now])

    def check_islabelled(self):
        txt='结果:未标注'
        for dictionary in self.label_dicts:
            if self.id_now == dictionary['id']:
                txt='结果:已标注，标签为：'+dictionary["label"]
                return txt
        return txt
    
    def start_thread(self,thread,label_dict_path,new_dict_element):
        try:
            thread.accept(label_dict_path,new_dict_element)
            thread.start()
        except Exception as e:
            print(e)    

    def onChange_prefix(self,text):
        self.prefix=text
        # print(text)
        # print("...", facename)

    def onChange_time(self,is_time):
        self.is_time= is_time


    def onChange_dupforbid(self,is_dupforbid):
        self.is_dupforbid= is_dupforbid








if __name__ == '__main__':
    # 创建一个应用程序对象
    app = QApplication(sys.argv)
    windows=MainWidget()
    windows.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())