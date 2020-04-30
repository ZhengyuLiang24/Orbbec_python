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
    parser.add_argument('--mirroring', default=True, help='mirroring [default: False]')
    parser.add_argument('--compression', default=True, help='compress or not, when saving the video [default: True]')

    return parser.parse_args()


def getOrbbec():
    # 记载 openni
    try:
        if sys.platform == "win32":
            libpath = "lib/Windows"
        else:
            libpath = "lib/Linux"
        print("library path is: ", os.path.join(os.path.dirname(__file__), libpath))
        openni2.initialize(os.path.join(os.path.dirname(__file__), libpath))
        print("OpenNI2 initialized \n")
    except Exception as ex:
        print("ERROR OpenNI2 not initialized", ex, " check library path..\n")
        return

    # 加载 orbbec 相机
    try:
        device = openni2.Device.open_any()
        return device
    except Exception as ex:
        print("ERROR Unable to open the device: ", ex, " device disconnected? \n")
        return




def main(args):
    device = getOrbbec()
    # 创建深度流
    depth_stream = device.create_depth_stream()
    depth_stream.set_mirroring_enabled(args.mirroring)
    depth_stream.set_video_mode(c_api.OniVideoMode(resolutionX=args.width, resolutionY=args.height, fps=args.fps,
                                                   pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM))

    # 获取uvc
    cap = cv2.VideoCapture(0)

    # 设置 镜像 帧同步
    device.set_image_registration_mode(True)
    device.set_depth_color_sync_enabled(True)
    depth_stream.start()

    while True:
        # 读取帧
        frame_depth = depth_stream.read_frame()
        frame_depth_data = frame_depth.get_buffer_as_uint16()
        # 读取帧的深度信息 depth_array 也是可以用在后端处理的 numpy格式的
        depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype=np.uint16, buffer=frame_depth_data)
        # 变换格式用于 opencv 显示
        depth_uint8 = 1 - 250 / (depth_array )
        depth_uint8[depth_uint8 > 1] = 1
        depth_uint8[depth_uint8 < 0] = 0
        cv2.imshow('depth', depth_uint8)

        # 读取 彩色图
        _, color_array = cap.read()
        cv2.imshow('color', color_array)

        # 对彩色图 color_array 做处理

        # 对深度图 depth_array 做处理

        # 键盘监听
        if cv2.waitKey(1) == ord('q'):
            # 关闭窗口 和 相机
            depth_stream.stop()
            cap.release()
            cv2.destroyAllWindows()
            break

    # 检测设备是否关闭（没什么用）
    try:
        openni2.unload()
        print("Device unloaded \n")
    except Exception as ex:
        print("Device not unloaded: ", ex, "\n")


if __name__ == '__main__':
    args = parse_args()
    main(args)

    # main(args,device)
