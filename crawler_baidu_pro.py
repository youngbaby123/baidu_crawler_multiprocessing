#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
0 香蕉
1 苹果
'''
import sys, os, re
import urllib
import urllib2
import argparse
import multiprocessing
import math

def Get_arg():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--labelFile", type = str, required = True, help = "file to label")
    ap.add_argument("-n", "--nums", type = int, required = True, help = "nums to crawl")
    ap.add_argument("-o", "--outputDir", type = str, required = True, help = "path to output")
    ap.add_argument("-p", "--proc", type = int, default = 1, help = "processes number")
    args = vars(ap.parse_args())
    args["outputDir"] = os.path.realpath(args["outputDir"])
    args["labelFile"] = os.path.realpath(args["labelFile"])
    return args

def Get_content_dict(labelFile):
    content_dict = {}
    with open(labelFile, 'r') as label_File:
        for line in label_File:
            if line[0] == '#':
                continue
            else:
                splitName = line.strip('\n').split()
                name = splitName[0]
                key_words = splitName[1:]
                key_words = '%20'.join(key_words).replace("&", "%26")
                content_dict[name] = key_words
    return content_dict

def Get_pool_dict(content_dict, keep_keys):
    res_dic = {}
    for k in keep_keys:
        res_dic[k] = content_dict[k]
    return res_dic

#关键程序，输入 args为相关路径配置，根据具体输入进行解析； content_dict为导入的关键词字典
def crawler_(args, content_dict):
    num = args["nums"]
    outputDir = args["outputDir"]
    url_base = "http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={}&pn={}"

    for content_id in content_dict:
        print (content_id)
        content = content_dict[content_id]
        dirname = os.path.join(outputDir, content_id)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        all_count = 0
        successcount = 0
        flag = 1
        logname = os.path.join(dirname, "ImageMessage.txt")
        flog = open(logname, "a+")

        page_content = [20 * x for x in range(num / 20)]
        for page_no, page_content_url in enumerate(page_content):
            url = url_base.format(content, page_content_url)
            # 下载图片
            try:
                if flag == 1:
                    sock = urllib.urlopen(url)
                    reg = re.compile("(?<=objURL\":\")(http.*?\.(jpg|gif|png|bmp|jpeg|JPG|BMP|PNG|JPEG))")
                    html = sock.read()
                    results = reg.findall(html)
            except Exception as e:
                print ('Error downloading...')
            if results:
                os.chdir(dirname)
                for count, one in enumerate(results):
                    # 统计
                    all_count += 1
                    if (count >= 20):
                        print ("down load this page finish: {}".format(page_no))
                        break

                    imgeurl = one[0]
                    print ("image from: {}".format(one[0]))
                    succname = imgeurl[int(imgeurl.rindex('.')) + 1:int(len(imgeurl))]

                    try:
                        savename = os.path.join(dirname, "{}_{}_{}.{}".format(content_id, page_no, count, succname))
                        print ("image save at: {}".format(savename))
                        downloadimge = urllib2.urlopen(one[0], timeout=5)  # , data, timeout)
                        f = open(savename, "wb")
                        f.write(downloadimge.read())
                        f.close()

                        size = os.path.getsize(savename)
                        flog.writelines("{} {} {}".format(savename, size, one[0]))
                        print ("Download Success\n{}".format("------"*10))
                        successcount += 1

                    except BaseException, e:
                        flog.writelines("{} {} {}\n".format(savename, e, one[0]))
                        print ("Fail download {} ... Error {}".format(imgeurl, e))
            if all_count > num:
                print ("down load finish: {}".format(content))
                flag = -1
                break

        print ("finished: ({}/{}) downloaded".format(successcount, num))
        flog.close()


def main():
    #导入配置文件
    args = Get_arg()
    #导入 搜索关键词 字典 {关键词存储标识： 用来搜索的关键词}
    content_dict = Get_content_dict(args["labelFile"])

    #开启进程个数设置， args["proc"]为进程数
    pool = multiprocessing.Pool(processes=args["proc"])

    #计算每个进程的关键词个数
    content_keys = content_dict.keys()
    content_keys_num = len(content_keys)
    step_size = int(math.ceil(1.0*content_keys_num/args["proc"]))

    #开启进程
    for i in range(args["proc"]):
        #分配每个进程的 关键词
        keep_keys = content_keys[i*step_size:(i+1)*step_size]
        keep_content_dict = Get_pool_dict(content_dict, keep_keys)
        #完成分配进程
        pool.apply_async(crawler_, (args, keep_content_dict,))
    pool.close()
    pool.join()
    print "Sub-process(es) done."

if __name__ == "__main__":
    main()
