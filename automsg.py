import random
import sys
import time
from tkinter import *
from tkinter.ttk import *
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_label_resp_text = self.__tk_label_resp_text(self)
        self.tk_input_content = self.__tk_input_content(self)
        self.tk_label_resp_pic = self.__tk_label_resp_pic(self)
        self.tk_input_pic = self.__tk_input_pic(self)
        self.tk_button_start_button = self.__tk_button_start_button(self)
        self.tk_button_stop_button = self.__tk_button_stop_button(self)
        self.tk_button_select = self.__tk_button_select(self)

    def __win(self):
        self.title("视频号私信")
        # 设置窗口大小、居中
        width = 360
        height = 200
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_label_resp_text(self, parent):
        label = Label(parent, text="回复语：", anchor="center", )
        label.place(x=24, y=30, width=50, height=30)
        return label

    def __tk_input_content(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=93, y=32, width=150, height=30)
        return ipt

    def __tk_label_resp_pic(self, parent):
        label = Label(parent, text="回复图：", anchor="center", )
        label.place(x=23, y=78, width=50, height=30)
        return label

    def __tk_input_pic(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=93, y=81, width=150, height=30)
        return ipt

    def __tk_button_start_button(self, parent):
        btn = Button(parent, text="开始", takefocus=False, )
        btn.place(x=20, y=140, width=80, height=30)
        return btn

    def __tk_button_stop_button(self, parent):
        btn = Button(parent, text="停止", takefocus=False, )
        btn.place(x=115, y=140, width=80, height=30)
        return btn

    def __tk_button_select(self,parent):
        btn = Button(parent, text="选择文件", takefocus=False,)
        btn.place(x=250, y=81, width=100, height=30)
        return btn

class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)

    def __event_bind(self):
        self.tk_button_start_button.bind('<Button-1>', self.ctl.start)
        self.tk_button_stop_button.bind('<Button-1>', self.ctl.stop)
        self.tk_button_select.bind('<Button-1>', self.ctl.selectFile)
        self.protocol('WM_DELETE_WINDOW', self.ctl.quit)
        pass

    def __style_config(self):
        pass


class Controller:
    def __init__(self):
        self.win = None
        self.driver = None
        self.status = True
        self.content = ""
        self.pic = ""
        self.dzhxx = None
        self.sx = None

    def init(self, win):
        self.win = win

    # 打包进线程（耗时的操作）
    def thread_it(self, func, *args):
        self.t = threading.Thread(target=func, args=args)
        # t.daemon = True
        # t.setDaemon(True)  # 守护--就算主界面关闭，线程也会留守后台运行（不对!）
        self.t.start()  # 启动
        # t.join()          # 阻塞--会卡死界面！

    def quit(self):
        self.status = False
        if self.driver is not None:
            self.driver.quit()

        if self.win is not None:
            self.win.destroy()
        print("quit")
        sys.exit(0)

    def start(self, event):
        self.status = True
        self.thread_it(self.exec)

    def selectFile(self, event):
        from tkinter import filedialog
        self.win.tk_input_pic.delete(0, END)
        self.pic = filedialog.askopenfilename()
        self.win.tk_input_pic.insert(0, self.pic)

    def sendmsg(self):
        try:
            mainBody = self.driver.find_element(By.CLASS_NAME, "main-body")
            scrollList = mainBody.find_element(By.CLASS_NAME, "scroll-list__wrp")
            sessionWraps = scrollList.find_elements(By.CLASS_NAME, "session-wrap")
            for session in sessionWraps:
                try:
                    if session.find_element(By.CLASS_NAME, "dot").is_displayed():
                        session.click()

                        sessionDialog = mainBody.find_element(By.CLASS_NAME, "session-dialog")
                        sessionDialog.find_element(By.CLASS_NAME, "edit_area").send_keys(self.content)
                        sessionDialog.find_element(By.CLASS_NAME, "weui-desktop-btn_default").click()
                        if self.pic != "":
                            file_input = sessionDialog.find_element(By.CSS_SELECTOR, "input[type='file']")
                            file_input.send_keys(self.pic)

                        self.driver.get("https://channels.weixin.qq.com/platform/private_msg")
                        # 定位当前页必须是私信管理页
                        while True:
                            print("Waiting for the page to load")
                            if not self.status:
                                return
                            try:
                                routeName = self.driver.find_element(By.CLASS_NAME, "route-name")
                            except:
                                continue

                            if routeName.is_displayed() and routeName.text == "私信管理":
                                break

                        mainBody = self.driver.find_element(By.CLASS_NAME, "main-body")
                        self.sx = mainBody.find_element(By.PARTIAL_LINK_TEXT, "私信")
                        self.dzhxx = mainBody.find_element(By.PARTIAL_LINK_TEXT, "打招呼消息")
                except:
                    continue
            return False
        except:
            return False

    def exec(self):
        if self.driver is None:
            self.driver = webdriver.Chrome()
            self.driver.set_window_size(2560, 1415)
            self.driver.implicitly_wait(0.2)
            self.driver.get("https://channels.weixin.qq.com/platform/private_msg")
        else:
            self.driver.get("https://channels.weixin.qq.com/platform/private_msg")

        self.content = self.win.tk_input_content.get()
        self.pic = self.win.tk_input_pic.get()

        # 定位当前页必须是私信管理页
        while True:
            print("Waiting for the page to load")
            if not self.status:
                return
            try:
                routeName = self.driver.find_element(By.CLASS_NAME, "route-name")
            except:
                continue

            if routeName.is_displayed() and routeName.text == "私信管理":
                break

        mainBody = self.driver.find_element(By.CLASS_NAME, "main-body")
        self.sx = mainBody.find_element(By.PARTIAL_LINK_TEXT, "私信")
        self.dzhxx = mainBody.find_element(By.PARTIAL_LINK_TEXT, "打招呼消息")

        print("start")

        while True:
            if not self.status:
                return
            self.dzhxx.click()
            self.sendmsg()

            self.sx.click()
            self.sendmsg()


    def stop(self, event):
        self.status = False
        print("stop")
        pass


if __name__ == "__main__":
    win = Win(Controller())
    win.mainloop()
