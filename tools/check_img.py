#-*-coding:utf-8-*-
import os
import os.path as osp
from PIL import Image
import cv2
import argparse

def GetimgList(dir, dir_rel='', fileList=[], dir_rel_list=[]):
    newDir = dir
    newdir_rel = dir_rel
    if os.path.isfile(dir):
        try:
            img=Image.open(dir)
            img.verify()
            fileList.append([dir, dir_rel])
            # dir_rel_list.append(dir_rel.decode('gbk'))
        except Exception as e:
            print (e)
            print ('IO error: ', dir)
            os.remove(dir)
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newDir = os.path.join(dir, s)
            if os.path.isdir(newDir):
                newdir_rel = os.path.join(dir_rel, s)
            GetimgList(newDir, newdir_rel, fileList, dir_rel_list)
    return fileList

def check_img_jpg(img_root):
    for root_i in os.listdir(img_root):
        img_root_i=osp.join(img_root,root_i)
        img_list=GetimgList(img_root_i, dir_rel='', fileList=[], dir_rel_list=[])
        for img_i in img_list:
            img_name = os.path.basename(img_i[0])
            img_dir = os.path.realpath(os.path.dirname(img_i[0]))
            try:
                img=cv2.imread(img_i[0])
                if img is None:
                    os.remove(img_i[0])
                    continue
                # print img_i[0].split('.')[0]+'.jpg'
                os.remove(img_i[0])
                # if img.shape[0]>=480 and img.shape[1]>=640:
                cv2.imwrite(os.path.join(img_dir, os.path.splitext(img_name)[0]+".jpg"),img)
            except Exception as e:
                print (e)
                print ('remove the image:', img_i[0])
                if os.path.isfile(img_i[0]):
                    os.remove(img_i[0])
                continue

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--img_root", required=True, help="path to image root")
    args = vars(ap.parse_args())
    img_root=args['img_root']
    check_img_jpg(img_root)
