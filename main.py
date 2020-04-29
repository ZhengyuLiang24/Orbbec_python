#!/usr/bin/env python3

from datetime import datetime
import time
import argparse
import sys
import configparser
import os
from openni import openni2
from openni import _openni2 as c_api
import cv2
import numpy as np



def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type=int, default=640, help='resolutionX')
    parser.add_argument('--height', type=int, default=400, help='resolutionY')
    parser.add_argument('--fps', type=int, default=30, help='frame per second')
    parser.add_argument('--mirroring', default=False, help='mirroring [default: False]')
    parser.add_argument('--compression', default=True, help='compress or not, when saving the video [default: True]')

    return parser.parse_args()


def main(args):
    # 记载 openni
    try:
        if sys.platform == "win32":
            libpath = "lib/Windows"
        else:
            libpath = "lib/Linux"
        print("library path is: ", os.path.join(os.path.dirname(__file__),libpath))
        openni2.initialize(os.path.join(os.path.dirname(__file__),libpath))
        print("OpenNI2 initialized \n")
    except Exception as ex:
        print("ERROR OpenNI2 not initialized",ex," check library path..\n")
        return

    # 加载 orbbec 相机
    try:
        device = openni2.Device.open_any()
    except Exception as ex:
        print("ERROR Unable to open the device: ",ex," device disconnected? \n")
        return

    # 创建深度流
    depth_stream = device.create_depth_stream()
    depth_stream.set_mirroring_enabled(args.mirroring)
    depth_stream.set_video_mode(c_api.OniVideoMode(resolutionX=args.width, resolutionY=args.height, fps=args.fps,
                                                   pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM))
    # 设置 镜像 帧同步
    device.set_image_registration_mode(True)
    # dev.set_depth_color_sync_enabled(True)
    depth_stream.start()

    depth_scale_factor = 0.05
    depth_scale_beta_factor = 0
    while True:
        frame_depth = depth_stream.read_frame()
        frame_depth_data = frame_depth.get_buffer_as_uint16()
        depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype=np.uint16, buffer=frame_depth_data)
        depth_uint8 = depth_array * depth_scale_factor + depth_scale_beta_factor#？？？？？？
        depth_uint8[depth_uint8 > 255] = 255
        depth_uint8[depth_uint8 < 0] = 0
        depth_uint8 = depth_uint8.astype('uint8')

        cv2.imshow('depth', depth_uint8)
        # cv2.imshow('color', color_array)
        # cv2.waitKey(1)

        if cv2.waitKey(1) == ord('c'):
            break


    # 关闭窗口 和 相机
    cv2.destroyAllWindows()
    depth_stream.stop()
    try:
        openni2.unload()
        print("Device unloaded \n")
    except Exception as ex:
        print("Device not unloaded: ",ex, "\n")


if __name__ == '__main__':
    args = parse_args()
    main(args)
