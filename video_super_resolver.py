#! /usr/bin/python
# -*- coding: utf8 -*-

import os, time, pickle, random, time
from datetime import datetime
import numpy as np
from time import localtime, strftime
import logging, scipy

import tensorflow as tf
import tensorlayer as tl
from model import *
from utils import *
from config import config, log_config
import imageio
###====================== HYPER-PARAMETERS ===========================###
## Adam
batch_size = config.TRAIN.batch_size
lr_init = config.TRAIN.lr_init
beta1 = config.TRAIN.beta1
## initialize G
n_epoch_init = config.TRAIN.n_epoch_init
## adversarial learning (SRGAN)
n_epoch = config.TRAIN.n_epoch
lr_decay = config.TRAIN.lr_decay
decay_every = config.TRAIN.decay_every

ni = int(np.sqrt(batch_size))

def read_all_imgs(img_list, path='', n_threads=32):
    """ Returns all images in array by given path and name of each image file. """
    imgs = []
    for idx in range(0, len(img_list), n_threads):
        b_imgs_list = img_list[idx : idx + n_threads]
        b_imgs = tl.prepro.threading_data(b_imgs_list, fn=get_imgs_fn, path=path)
        # print(b_imgs.shape)
        imgs.extend(b_imgs)
        print('read %d from %s' % (len(imgs), path))
    return imgs



def evaluate():
    ## create folders to save result images
    save_dir = "images/srgan_frames/"
    tl.files.exists_or_mkdir(save_dir)
    checkpoint_dir = "checkpoint"
    
    read_video_filepath=os.getcwd()+'\\videos\\video_hq.mp4'
    
    reader = imageio.get_reader(read_video_filepath)
    W,H=reader.get_meta_data()['size']
    fps=reader.get_meta_data()['fps']
    num_frames=reader.get_meta_data()['nframes']
    print (reader.get_meta_data())
    C=3
    t_image = tf.placeholder('float32', [None, H/4, W/4, C], name='input_image')
    net_g = SRGAN_g(t_image, is_train=False, reuse=False)
    # # ###=============RESTORE G======================================================
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=False))
    tl.layers.initialize_global_variables(sess)
    tl.files.load_and_assign_npz(sess=sess, name=checkpoint_dir+'/g_srgan.npz', network=net_g)
    write_video_filepath=os.getcwd()+'\\videos\\srgan.mp4'
    srgan_writer=imageio.get_writer(write_video_filepath)
    for i, frame in enumerate(reader):
        resized_frame=scipy.misc.imresize(frame, size=0.25, interp='bilinear', mode=None)
        avg=resized_frame.max()-resized_frame.min()
        resized_frame = (resized_frame / avg) - 1  
        out = sess.run(net_g.outputs, {t_image: [resized_frame]})
        #tl.vis.save_image(out[0], save_dir+'/'+str(i)+'.png')
        meta={'fps': 29.97}
        srgan_writer.append_data(out[0], meta=meta)
    
    
    # # ###========================== DEFINE MODEL AND RESTORE G =============================###
    # print valid_lr_imgs.shape
    # batch_size=len(valid_lr_imgs)
    # H,W,C=valid_lr_imgs[0].shape
    # t_image = tf.placeholder('float32', [None, H, W, C], name='input_image')
    # net_g = SRGAN_g(t_image, is_train=False, reuse=False)
    # # ###=============RESTORE G======================================================
    # sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=False))
    # tl.layers.initialize_global_variables(sess)
    # tl.files.load_and_assign_npz(sess=sess, name=checkpoint_dir+'/g_srgan.npz', network=net_g)
    # # ###==========================EVALUATION============================###
    # for i in np.arange(batch_size):
        # input_image=valid_lr_imgs[i]
        # input_image = (input_image / 127.5) - 1  
        # out = sess.run(net_g.outputs, {t_image: [input_image]})
        # tl.vis.save_image(out[0], save_dir+'/'+str(i)+'.png')
    
        
    
    
    
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='srgan', help='evaluate')
    args = parser.parse_args()
    tl.global_flag['mode'] = args.mode
    evaluate()

    