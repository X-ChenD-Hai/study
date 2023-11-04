from time import sleep
from random import uniform
import os,logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)
logging.basicConfig(filename="log.log",filemode="w",level=logging.DEBUG,format="%(levelname)s:%(message)s")
loger=logging.getLogger(__name__)

class ChaoXing(object):
    def __init__(self,phNum:str,passwd:str) -> None:
        chrome_options = Options()
        self.rgsUrl="https://passport2.chaoxing.com/login"
        self.rgscourselistUrl="http://i.mooc.chaoxing.com/space/index"
        self.column:str=""
        self.columList=[]
        self.phNum=phNum
        self.passwd=passwd
        chrome_options.add_argument('--mute-audio')  # 浏览器静音
        # chrome_options.add_argument('--headless')  # 浏览器隐藏
        self.driver = webdriver.Chrome(chrome_options)
        self.login()

    @staticmethod
    def send_key(ele,data:str):
        for i in data:
            sleep(uniform(0.0,0.1))
            ele.send_keys(i)
        sleep(uniform(0.0,0.1))
    
    def login(self):
        self.driver.get(self.rgsUrl)
        WebDriverWait(self.driver,10)
        inpPhone=self.driver.find_element(By.ID,"phone")
        inppwd=self.driver.find_element(By.ID,"pwd")
        btnloginBtn=self.driver.find_element(By.ID,"loginBtn")
        self.send_key(inpPhone,self.phNum)
        self.send_key(inppwd,self.passwd)
        btnloginBtn.click()
        WebDriverWait(self.driver,10)
        print("登陆成功！")
    
    def courseList(self):
        rlist=[]
        self.driver.get(self.rgscourselistUrl)
        WebDriverWait(self.driver,10)
        self.driver.find_element(By.ID,"li_zne_kc_icon").click()
        self.driver.switch_to.frame("frame_content")
        WebDriverWait(self.driver,10)
        sleep(0.3)
        couses = self.driver.find_elements(By.CSS_SELECTOR, "#courseList a.color1")
        for i in couses:
            rlist.append((i.find_element(By.CSS_SELECTOR,"span").text,i.get_attribute("href")))
        print("成功获取课程列表！")
        return rlist

    def run(self):
        l=self.courseList()
        i=0
        for  tittle,href in l:
            # print(f"option{i}\t"+tittle)
            i+=1
        href=None
        while href is None:
            try:
                # href=int(input("输入option >"))
                # href=l[href][1]
                href=l[0][1]
            except Exception as e:
                # print(e)
                href=None
        self.driver.get(href)
        WebDriverWait(self.driver,10)
        self.driver.switch_to.default_content()
        self.driver.find_element(By.ID,"nav_26542").click()
        WebDriverWait(self.driver,10)
        sleep(0.5)
        self.driver.switch_to.frame("frame_content-zj")
        self.driver.find_element(By.CSS_SELECTOR, "span.catalog_points_yi").click()
        WebDriverWait(self.driver,10)
        sleep(0.5)
        self.start()
    
    def toFrams(self,PreFrames):
        self.driver.switch_to.default_content()
        for i in PreFrames:
            self.driver.switch_to.frame(i)
            WebDriverWait(self.driver,10)

    def dealVideoFm(self,preFra,label):
        # print("switch Frame")
        self.toFrams(preFra)
        try:
            self.driver.find_element(By.CSS_SELECTOR,'#video button').click()
            status=self.driver.find_element(By.CSS_SELECTOR,"#video > div.vjs-control-bar > button > span.vjs-control-text")
            btn=self.driver.find_element(By.CSS_SELECTOR,"#video > div.vjs-control-bar > button")
            # print("check to while")
            r,a=0,3
            print("播放\t"+self.column.rsplit("\n",1)[0])
            while not self.hasFinished(label,preFra[:-1]):
                try :
                    # print("check in while")
                    self.toFrams(preFra)
                    if(status.text=="播放" or status.text=="重播"):
                        # print(status.text)
                        r+=1
                        btn.click()
                    print(f"播放中{'.'*a+' '*(6-a)}\t中断次数：{r}    ",end="\r")
                    a+=1
                    if a == 7:
                        a=1
                    sleep(0.5)
                except:
                    pass
            else:
                print("播放完成！")
        except:
            loger.warning("do`nt find video")

    def hasFinished(self,ele,preFra:None|tuple=None):
        if preFra is not None:
            self.toFrams(preFra)
            # print(ele.find_element(By.CSS_SELECTOR,"div.ans-attach-ct").get_attribute("class"))
        return ele.find_element(By.CSS_SELECTOR,"div.ans-attach-ct").get_attribute("class").find("ans-job-finished") != -1

    def doTaskPoint(self):
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver,10)
        # print("find iframe")
        iframe = self.driver.find_element(By.CSS_SELECTOR,"#iframe")
        # print("swich iframe")
        self.driver.switch_to.frame(iframe)
        WebDriverWait(self.driver,10)
        sleep(0.3)
        # print("find")
        eles=self.driver.find_elements(By.XPATH,'//*/p[@tabindex="-1"]')
        for j in eles:
            # print("check start status")
            if not self.hasFinished(j):
                ifra=j.find_element(By.TAG_NAME,"iframe")
                # print("check Type")
                if ifra.get_attribute("class")=="ans-attach-online ans-insertvideo-online":
                    # print("deal video")
                    self.dealVideoFm((iframe,ifra),j)

    def updateClumnList(self):
        self.columList=self.driver.find_elements(By.CSS_SELECTOR,"span.catalog_points_yi")

    def start(self):
        loger.info("in fn start")
        self.driver.switch_to.default_content()
        self.updateClumnList()
        for i in range(len(self.columList)):
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver,10)
            try:
                ele = self.columList[i].find_element(By.XPATH,"..")
            except:
                self.updateClumnList()
                ele = self.columList[i].find_element(By.XPATH,"..")
            self.driver.execute_script("arguments[0].scrollIntoView();",ele)
            try:
                # print(f"click {ele.text.rsplit(' ',1)[0]}")
                ele.click()
                WebDriverWait(self.driver,10)
                sleep(0.3)
                self.column=ele.text
                self.doTaskPoint()
            except:
                loger.warning(f"Failed to click {ele.text}")
            sleep(0.3)

    def __del__(self):
        os.system("pause")

def main():
    x=ChaoXing("15554521770","Mine_xxt&22")
    x.run()

if __name__ == "__main__":
    main()

