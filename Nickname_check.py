#-*-coding:utf-8 -*-

# import 这边需要注意的是只有一个rsa这个模块是需要install的，其他的都是内置
import re, urllib, urllib2, cookielib
import base64 , binascii , rsa
import time
import os
import string
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 以下4行代码说简单点就是让你接下来的所有get和post请求都带上已经获取的cookie，因为稍大些的网站的登陆验证全靠cookie
#cj = cookielib.LWPCookieJar()   #: 可以将cookie存起来，以后都不用登陆呢+++++++++++++++++++++
cookie = cookielib.MozillaCookieJar(u"sinawb_ck.txt")           #: haoxi add ++++++++++
cookie_support = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookie_support , urllib2.HTTPHandler)
urllib2.install_opener(opener)

# 封装一个用于get的函数，新浪微博这边get出来的内容编码都是utf-8
def getData(url) :
    #request = urllib2.Request(url) # No Request, save time
    response = urllib2.urlopen(url)
    text = response.read().decode('utf-8')
    return text

# 封装一个用于post的函数，验证密码和用户名都是post的，所以这个postData在本demo中专门用于验证用户名和密码
def postData(url , data) :
    # headers需要我们自己来模拟
    headers = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
    # 这里的urlencode用于把一个请求对象用'&'来接来字符串化，接着就是编码成utf-8
    data = urllib.urlencode(data).encode('utf-8') #: data type is str
    request = urllib2.Request(url , data , headers)
    #print(request.get_full_url())
    response = urllib2.urlopen(request)
    text = response.read().decode('gbk')
    #print(text)
    return text

#login_weibo('你的微博邮箱' , '你的微博密码')
def login_weibo(nick , pwd) :
    #==========================获取servertime , pcid , pubkey , rsakv===========================
    # 预登陆请求，获取到若干参数
    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % nick
    preLogin = getData(prelogin_url)
    # 下面获取的四个值都是接下来要使用的
    servertime = re.findall('"servertime":(.*?),' , preLogin)[0]
    pubkey = re.findall('"pubkey":"(.*?)",' , preLogin)[0]
    rsakv = re.findall('"rsakv":"(.*?)",' , preLogin)[0]
    nonce = re.findall('"nonce":"(.*?)",' , preLogin)[0]
    #===============对用户名和密码加密==================================
    # 登陆新浪微博最难部分，获取加密后的su和sp
    username = urllib.quote(nick)
    su = base64.encodestring(username)[:-1]
    #: 先创建一个rsa公钥，公钥的两个参数新浪微博都给了固定值，不过给的都是16进制的字符串，
    #: 第一个是登录第一步中的pubkey，第二个是js加密文件中的‘10001’(65537)
    rsaPublickey = int(pubkey , 16)
    key = rsa.PublicKey(rsaPublickey , 65537)   #: 创建公钥
    # rsa.encrypt
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
    passwd = rsa.encrypt(message , key)         #: 加密
    sp = binascii.b2a_hex(passwd)               #: 将加密信息转换为16进制
    #=======================登录====================================

    #param就是激动人心的登陆post参数，这个参数用到了若干个上面第一步获取到的数据
    param = {'entry' : 'weibo' , 'gateway' : 1 , 'from' : '' , 'savestate' : 7 , 'useticket' : 1 , 'pagerefer' : 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D' , 'vsnf' : 1 , 'su' : su , 'service' : 'miniblog' , 'servertime' : servertime , 'nonce' : nonce , 'pwencode' : 'rsa2' , 'rsakv' : rsakv , 'sp' : sp , 'sr' : '1680*1050' ,
             'encoding' : 'UTF-8' , 'prelt' : 961 , 'url' : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'}
    # 这里就是使用postData的唯一一处，也很简单
    s = postData('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)' , param)
    #print(s)
    # 假如跳过这里直接去执行获取粉丝，就会发现你获取的到还是让你登陆的页面
    # 这个urll是登陆之后新浪返回的一段脚本中定义的一个进一步登陆的url，之前还都是获取参数和验证之类的，这一步才是真正的登陆，所以你还需要再一次把这个urll获取到并用get登陆即可
    text = re.findall("location.replace\(\'(.*?)\'\);" , s)
    if not text:
        print("jump to the next page ERROR!")
        return None
    urll = text[0]
    getData(urll)  #: ===================================
    cookie.save(ignore_discard=True, ignore_expires=True)           #: haoxi add, save to local file +++++++++++++++
    # 如果你没有跳过刚才那个urll来到这里的话，那么恭喜你！你成功了，接下来就是你在新浪微博里畅爬的时候了，获取到任何你想获取到的数据了！
    print("login successfully")


login_weibo('13883060591', 'gump13883060591')

class PUB:
    def __init__(self):
        self.loginurl = 'http://keyanjianzhi.pub'
        self.cookies = cookielib.CookieJar()
        self.postdata = urllib.urlencode({
            'pw':'123456',
            })
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))

    def getpage(self):
        request = urllib2.Request(url = self.loginurl, data = self.postdata)
        result = self.opener.open(request)

    def publish(self, text):
        url = "http://keyanjianzhi.pub/connect.php"
        postdata = {
            'textfield':text,
            'textfield2':username,
            'submit':u'提交'
            }
        request = urllib2.Request(url, urllib.urlencode(postdata))
        i = self.opener.open(request)
        return self.cookies



rootdir = "/Users/ganlinhao/pic"
newdir = '/Users/ganlinhao/pic'
olddir = '/Users/ganlinhao/pic'
username = 'xx'
UIDlist = os.listdir(rootdir)
print UIDlist
htmllist = []
header = "http://weibo.com/u"

su_number = 0
fail_number = 0
list_number = 0
for dirname in UIDlist:
    UIDhtml = os.path.join(header, dirname)
    print UIDhtml

    try:
        request = urllib2.Request(UIDhtml)
        response = urllib2.urlopen(request)
        content = response.read().decode('utf-8')
        pattern = re.compile(r'span class=\\"username\\">(.*?)<\\/span>')
        nickname = pattern.findall(content, re.S)
        print nickname[0]
    except urllib2.URLError, e:
        if hasattr(e, "code"):
            print e.code
        if hasattr(e, "reason"):
            print e.reason

    pub = PUB()
    pub.getpage()

    temp =  pub.publish(nickname[0])
    flag = 1
    for ck in temp:
        lenth = len(ck.value)
        flag = flag-1
        if flag==0:
            break

    if lenth > 40: #faulse
        print ("this name is existed: "+nickname[0]+ dirname)
        fail_number = fail_number + 1
    if lenth != 40:#succesed
        try:
            os.rename(os.path.join(olddir,dirname), os.path.join(newdir, nickname[0]))
            print (nickname[0]+ " has been processed")
            su_number = su_number + 1
        except ValueError:
            print("valueError when rename the file "+ dirname)
        except NameError:
            print("nameError when rename the file "+ dirname)
        except OSError:
            print("osError when rename the file "+ dirname)
    time.sleep(0.5)

print("change file name end")
print su_number
print fail_number
print username
