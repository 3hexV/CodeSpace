# coding: utf-8
import tkinter as tk
import tkinter.messagebox
import configparser
import os
import threading
import webbrowser
from tkinter import StringVar
import sys

top_flag = False
run_flag = False
threadLock = threading.Lock()
ls = None
window = tk.Tk()
text = StringVar()
text.set('-')
cp = configparser.ConfigParser()

ls = tk.Label(window, textvariable=text, fg='white', bg='red', font=('宋体', 10), width=2, height=1)


class myThread(threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        thread_rcs(self.name)
        print("退出线程：" + self.name)


threadCS = None


def run_CS():
    global threadCS, run_flag
    cp = configparser.ConfigParser()
    cp.read("./space_info.ini", encoding="utf-8-sig")
    state = cp.get("CodeSpace_State", "state")
    if state == '0' and not run_flag:
        run_flag = True
        cp.set("CodeSpace_State", "state", "1")
        cp.write(open("./space_info.ini", "w"))
        threadCS = myThread(1, "run_cs")
        threadCS.setDaemon(True)
        threadCS.start()
        text.set('O')
        ls.configure(bg='green')
        b1.configure(state=tk.DISABLED)
        b2.configure(state=tk.NORMAL)

    else:
        tkinter.messagebox.showerror('失败', 'CodeSpace启动失败')
        return


def thread_rcs(threadName):
    print(threadName)
    os.system('flask run')


def open_home():
    webbrowser.open("http://127.0.0.1:5000/")


def stop_CS():
    global threadCS, run_flag
    cp = configparser.ConfigParser()
    cp.read("./space_info.ini", encoding="utf-8-sig")
    state = cp.get("CodeSpace_State", "state")
    if state == '1' and run_flag:
        run_flag = False
        cp.set("CodeSpace_State", "state", "0")
        cp.write(open("./space_info.ini", "w"))

        msg = os.system('taskkill /f /t /im flask.exe')
        print(msg)

        text.set('-')
        ls.configure(bg='red')
        b2.configure(state=tk.DISABLED)
        b1.configure(state=tk.NORMAL)
    else:
        tkinter.messagebox.showerror('失败', 'CodeSpace停止失败')


def exit_CS():
    global threadCS
    cp = configparser.ConfigParser()
    cp.read("./space_info.ini", encoding="utf-8-sig")
    state = cp.get("CodeSpace_State", "state")
    if state == '1' and run_flag:
        os.system('taskkill /f /t /im flask.exe')
    cp.set("CodeSpace_State", "state", "0")
    cp.write(open("./space_info.ini", "w"))
    sys.exit(1)

def closeWindow():
    exit_CS()
    window.destroy()


b1 = tk.Button(window, text="启动CodeSpace", command=run_CS)
b2 = tk.Button(window, text="停止CodeSpace", command=stop_CS)


def more():
    tk.messagebox.showinfo(title='作者', message='AHNU:3hex,吾爱不变,gzw\nVersion: v1.0.1')


def top():
    global top_flag
    if not top_flag:
        window.wm_attributes('-topmost', 1)
        top_flag = True
    else:
        window.wm_attributes('-topmost', 0)
        top_flag = False


def reset_count():
    a = tkinter.messagebox.showinfo('提示', '代码计数值清空为0')
    cp.set("CodeSpace_Info", "cs_count", '0')
    cp.write(open("./space_info.ini", "w"))


def main():
    cp.read("./space_info.ini", encoding="utf-8-sig")
    cp.set("CodeSpace_State", "state", "0")
    cp.write(open("./space_info.ini", "w"))

    window.title('CSC')
    window.iconbitmap('.\\favicon.ico')
    window.protocol('WM_DELETE_WINDOW', closeWindow)
    window.resizable(False, False)

    menubar = tk.Menu(window)

    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='更多', menu=filemenu)
    filemenu.add_checkbutton(label='窗口置顶', command=top)
    filemenu.add_command(label='关于软件', command=more)
    filemenu.add_command(label='退出', command=window.quit)
    window.config(menu=menubar)

    l = tk.Label(window, text='CodeSpace Console', bg='white', font=('宋体', 10), width=30, height=2)
    l.pack()

    lt = tk.Label(window, text='如果发现启动失败、CS无法使用', fg='red', font=('宋体', 8), width=30, height=2)
    lt.place(x=10, y=160)
    lt2 = tk.Label(window, text='检查本地的MongoDB服务是否启动', fg='red', font=('宋体', 8), width=30, height=2)
    lt2.place(x=10, y=190)

    ls.place(x=35, y=65)

    b1.place(x=80, y=40)
    b2.place(x=80, y=80)
    b3 = tk.Button(window, text="打开首页", command=open_home)
    b3.place(x=120, y=120)
    b4 = tk.Button(window, text=" 退 出 ", command=exit_CS)
    b4.place(x=70, y=120)

    b5 = tk.Button(window, text=" 重 置 ", command=reset_count)
    b5.place(x=10, y=120)

    window.geometry("200x230+600+300")

    window.mainloop()


if __name__ == '__main__':
    main()
