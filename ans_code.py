import cv2
import numpy as np
import  math
from scipy import ndimage
# 读取图像
wi=0
hi=0
idx=0
uu=16
k_list =np.arange(1500).reshape(500,3)
"""
规定
1-12上A
13-24左B
25-36右C
37-48下D
"""
kd=np.zeros(300)
ttt=0
qs=[]
#图像显示
def print(s):
    qs.append(s)
def showw(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def remove_spots(img, min_size=4):

    # 创建一个二值图像，只保留灰度值为100的像素
    binary_img = np.where(img == 100, 255, 0).astype(np.uint8)

    # 连通组件分析，找出所有白色区域
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8)

    # 创建一个与原图像相同大小的黑色图像
    result = np.zeros_like(img)

    # 遍历所有连通组件，除了背景（标签0）
    for label in range(1, num_labels):
        # 获取当前连通组件的面积
        area = stats[label, cv2.CC_STAT_AREA]

        # 如果面积大于最小阈值，则保留该区域
        if area >= min_size:
            result[labels == label] = 100  # 将符合条件的区域恢复为100
        else:
            result[labels == label] = 0  # 将小区域设置为黑色

    return result
def remove_small_white_spots(img,t,min_size=2):
    # 读取图像并转换为灰度图像
    # 创建一个结构元素，用于腐蚀操作
    kernel = np.ones((3, 3), np.uint8)

    # 应用腐蚀操作
    eroded = cv2.erode(img, kernel, iterations=1)

    # 连通组件分析，找出所有白色区域
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded, connectivity=8)

    # 创建一个与原图像相同大小的黑色图像
    result = np.zeros_like(img)

    # 遍历所有连通组件，除了背景（标签0）
    for label in range(1, num_labels):
        # 获取当前连通组件的面积
        area = stats[label, cv2.CC_STAT_AREA]

        # 如果面积大于最小阈值，则保留该区域
        if area >= min_size:
            result[labels == label] = t
    return result
#让图像旋转指定角度
def rotate_image(image, angle):

    # 获取图像的尺寸
    (h, w) = image.shape[:2]

    # 计算图像中心点
    center = (w // 2, h // 2)

    # 构造旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 进行图像旋转
    rotated_image = cv2.warpAffine(image, M, (w, h))

    # 显示原始图像和旋转后的图像
    cv2.imshow('Original Image', image)
    cv2.imshow('Rotated Image', rotated_image)

    # 等待按键按下后关闭所有窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
#图像矫正
def image_correction(img):
    # 边缘检测
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    # 霍夫变换
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 0)
    for rho, theta in lines[0]:

        a = np.cos(theta)  # 将极坐标转换为直角坐标
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))  # 保证端点够远能够覆盖整个图像
        y1 = int(y0 + 1000 * a)
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * a)
        if x1 == x2 or y1 == y2:
            return img
        t = float(y2 - y1) / (x2 - x1)
        # 得到角度后将角度范围调整至-45至45度之间
        rotate_angle = math.degrees(math.atan(t))
        if rotate_angle > 45:
            rotate_angle = -90 + rotate_angle
        elif rotate_angle < -45:
            rotate_angle = 90 + rotate_angle
        #print(rotate_angle)
        # 图像根据角度进行校正
        rotate_img = ndimage.rotate(img, rotate_angle)
        #showw('4',rotate_img)
        return rotate_img
# 在图像上画一条水平线并检查是否有灰度为255的点
def draw_horizontal_line_and_check(image, row):
    if image is None:
        raise ValueError("Image is not loaded properly.")

    # 获取图像的高度和宽度
    h, w = image.shape

    # 检查行是否在图像范围内
    if row < 0 or row >= h:
        raise ValueError(f"Row index {row} is out of bounds for the image height {h}.")

    # 初始化标志变量
    has_white_pixel = False

    # 遍历指定行上的每个像素
    for x in range(w):
        if image[row, x] == 255:
            has_white_pixel = True
            break

    # 在图像上画一条水平线
    line_image = image.copy()
    cv2.line(line_image, (0, row), (w - 1, row), (255), thickness=2)

    return line_image, has_white_pixel
# 图像是否歪检测
def dd(gray_im):
    for i in range(gray_im.shape[0]//5*2, gray_im.shape[0]//5*3):
        pd=1
        for j in range(gray_im.shape[1]):
            if gray_im[i, j]==255 or gray_im[i+1,j]==255 or gray_im[i+2,j] == 255:
                pd=0
                break
        if pd==1:
            return True
    return False  #图像检测
#灰度转变（特定值优化）
def col_turn(k,a1,a2,area):
    if k==2:
        #print(a1,a2)
        for j in range(int(im.shape[1]/2),im.shape[1]):
            for i in range(a1,a2):
                if im[i,j]==255:
                    im[i,j]=10
                else :
                    im[i,j]=0
    if k==1:
        #print(a1,a2)
        for j in range(int(im.shape[1]/2)):
            for i in range(a1,a2):
                if im[i,j]==255:
                    im[i,j]=10
                else :
                    im[i,j]=0
    if k==0:
        #print(a1,a2)
        for i in range(int(im.shape[0]/2)):
            for j in range(a1,a2):
                if im[i,j]==255:
                    im[i,j]=10
                else :
                    im[i,j]=0
    if k==3:
        #print(a1,a2)
        for i in range(int(im.shape[0]/2),im.shape[0]):
            for j in range(a1,a2):
                if im[i, j] == 255:
                    im[i, j] = 10
                else:
                    im[i, j] = 0

    if area<5:
        if k == 2:
            for j in range(im.shape[1]-int(im.shape[1] / 20), im.shape[1]-1):
                im[a1,j]=10
                im[a2,j]=10
            for i in range(a1, a2):
                im[i,im.shape[1]-int(im.shape[1] / 20)]=10
                im[i,im.shape[1]-1]=10
        if k == 1:
            # print(a1,a2)
            for j in range(int(im.shape[1] // 20)):
                im[a1,j]=10
                im[a2,j]=10
            for i in range(a1, a2):
                im[i,im.shape[1] // 20]=10
                im[i,0]=10
        if k == 0:
            #print(a1,a2)
            for i in range(int(im.shape[0] /20)):
                im[i,a1]=10
                im[i,a2]=10
            for j in range(a1, a2):
                im[0,j]=10
                im[int(im.shape[0] /20),j] = 10
        if k == 3:
            # print(a1,a2)
            for i in range(im.shape[0]-int(im.shape[0] //20), im.shape[0]-1):
                im[i,a1]=10
                im[i,a2]=10
            for j in range(a1, a2):
                im[im.shape[0]-1,j]=10
                im[im.shape[0]-int(im.shape[0] //20),j] = 10
#特定灰度值变为红色
def convert_gray_to_red(gray_image):
    # 创建一个与灰度图像相同大小的黑色彩色图像
    color_image = np.zeros((gray_image.shape[0], gray_image.shape[1], 3), dtype=np.uint8)

    # 将灰度图像复制到彩色图像的蓝色通道
    color_image[gray_image ==255] = [0, 255, 0]
    # 将灰度值为255的像素的红色通道设为255
    color_image[gray_image == 150] = [0, 0, 255]  # BGR格式，红色为[0, 0, 255]
    #showw('22', color_image)
    return color_image
#核心芯片检测
def jc(xx,k):
    ttt=sum(kd)/idx
    #print(ttt)
    t=int(len(xx))
    for i in range(len(xx)):
        if xx[i]==0:
            t=t-1
    mea=xx.sum()/t
    b =[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ans=[0]
    for i in range(xx.shape[0]):
        if abs(xx[i]-mea)>mea*0.59:
            ans[0]=1
            if xx[i]-mea>0:
                b[i+1]=1
            elif xx[i]-mea<0:
                b[i+1]=2
            ans.append(i+1)
    return ans,b
#行切适用于AC区
def hang_cut(imm,k):
    cs=1
    w = 0
    assn=np.array([])
    while (cs<=uu):
        pdt = 0
        t = 0
        area=0
        cc=0
        for i in range(w,imm.shape[0]):
            pdw = 0
            for j in range(imm.shape[1]):
                if imm[i][j]>80:
                    area+=1
                if imm[i][j] >80 and pdt == 0:
                    pdt = 1
                    t = i
                if imm[i][j] >80 or pdt==0:
                    pdw = 1
                if imm[i][j] ==100:
                    cc=cc+1
            if pdw == 0:
                w = i
                #print(w)
                break
        #showw('454',imm[:,t:w])
      #  imm=imm[:,w:]
        k_list[k * uu + cs][0] =t
        k_list[k * uu+ cs][1] = w
        kd[k * uu + cs]=abs(w-t)
        #print(k*12+cs,kd[k * 12 + cs])
        global idx
        idx=idx+1
        #print(kd.sum())
        cs+=1
        assn=np.append(assn,area-cc)
    return assn
#列切适用于BD区
def lie_cut(imm,k):
    cs=1
    w = 0
    assn=np.array([])
    while (cs<=uu):
        pdt = 0
        t = 0
        area=0
        cc=0
        for j in range(w,imm.shape[1]):
            pdw = 0
            for i in range(imm.shape[0]):
                if imm[i][j]>80:
                    area+=1
                if imm[i][j] >80 and pdt == 0:
                    pdt = 1
                    t = j
                if imm[i][j] >80 or pdt==0:
                    pdw = 1
                if imm[i][j] ==100:
                    cc=cc+1
            if pdw == 0:
                w = j
                #print(w)
                break
        #showw('454',imm[:,t:w])
      #  imm=imm[:,w:]
        k_list[k * uu + cs][0] =t
        k_list[k * uu+ cs][1] = w
        kd[k * uu + cs]=abs(w-t)
        #print(k*12+cs,kd[k * 12 + cs])
        global idx
        idx=idx+1
        #print(kd.sum())
        cs+=1
        assn=np.append(assn,area-cc)
    return assn
def convert_small_white_spots(img, min_size=10):

    # 创建一个二值图像，只保留灰度值为100的像素
    binary_img = np.where(img == 100, 255, 0).astype(np.uint8)

    # 连通组件分析，找出所有白色区域
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8)

    # 创建一个与原图像相同大小的副本
    result = img.copy()

    # 遍历所有连通组件，除了背景（标签0）
    for label in range(1, num_labels):
        # 获取当前连通组件的面积
        area = stats[label, cv2.CC_STAT_AREA]

        # 如果面积小于最小阈值，则将该区域的灰度值设置为255
        if area < min_size:
            result[labels == label] = 255

    return  result
#缩图
def small_picture(imm,k):
    hmi=10000
    hma=0
    wmi=10000
    wma=0
    if k!=1:
        for i in range(imm.shape[0]):  # 遍历高度
            for j in range(imm.shape[1]):
                if (imm[i][j] == 255):
                    hmi = i
                    break
        for i in range(imm.shape[0] - 1, -1, -1):
            for j in range(imm.shape[1]):
                if (imm[i][j] == 255):
                    hma = i
                    break
    if k!=2 :
        for j in range(imm.shape[1]):
            for i in range(imm.shape[0]):
                if (imm[i][j] == 255):
                    wmi = j
                    break
        for j in range(imm.shape[1] - 1, -1, -1):
            for i in range(imm.shape[0]):
                if (imm[i][j] == 255):
                    wma = j
                    break
    #print(hmi,hma,wmi,wma)
    anss = imm[hma:hmi, wma:wmi]
    h=hmi-hma
    w=wmi-wma
    return anss,h,w
def convert_colors(img_gray):
    # 将灰度图像转换为彩色图像
    img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

    # 遍历图像的每一个像素
    for y in range(img_gray.shape[0]):
        for x in range(img_gray.shape[1]):
            gray_value = img_gray[y, x]
            #print(gray_value,end=' ')

            if gray_value >=100:
                img_color[y, x] = [0, 255, 0]  # 绿色 (B, G, R)
            elif gray_value ==10:
                img_color[y, x] = [0, 0, 255]  # 红色 (B, G, R)
    return img_color
#分区画图，ABCD
def divide_and_label(image,s,x,z,y):
    # 获取图像的高度和宽度
    height, width, _ = image.shape

    # 计算中心点和四分之一点
    center_x = width // 2
    center_y = height // 2

    # 计算四分之一点
    quarter_width = width // 6
    quarter_height = height // 6

    # 定义分割线的起点和终点
    line1_start = (z+1, 0)
    line1_end = (z+1, height)
    line2_start = (width-y, 0)
    line2_end = (width-y, height)
    line3_start = (0, s+1)
    line3_end = (width,s+1)
    line4_start = (0, height-x-1)
    line4_end = (width, height-x-1)

    # 绘制蓝色线条
    cv2.line(image, line1_start, line1_end, (255, 0, 0), thickness=2)  # 垂直线1
    cv2.line(image, line2_start, line2_end, (255, 0, 0), thickness=2)  # 垂直线2
    cv2.line(image, line3_start, line3_end, (255, 0, 0), thickness=2)  # 水平线1
    cv2.line(image, line4_start, line4_end, (255, 0, 0), thickness=2)  # 水平线2

    # 添加文字标注
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 0, 255)  # 红色
    thickness = 2

    # 区域A
    text_a = 'A'
    text_size_a = cv2.getTextSize(text_a, font, font_scale, thickness)[0]
    text_x_a = z + text_size_a[0] // 2
    text_y_a = height//2 + text_size_a[1] // 2
    cv2.putText(image, text_a, (text_x_a, text_y_a), font, font_scale, font_color, thickness, cv2.LINE_AA)

    # 区域B
    text_b = 'B'
    text_size_b = cv2.getTextSize(text_b, font, font_scale, thickness)[0]
    text_x_b = width//2 - text_size_b[0] // 2
    text_y_b = s+10 + text_size_b[1]
    cv2.putText(image, text_b, (text_x_b, text_y_b), font, font_scale, font_color, thickness, cv2.LINE_AA)

    # 区域C
    text_c = 'C'
    text_size_c = cv2.getTextSize(text_c, font, font_scale, thickness)[0]
    text_x_c = width-y-10 - text_size_a[0]
    text_y_c = height//2 + text_size_a[1] // 2
    cv2.putText(image, text_c, (text_x_c, text_y_c), font, font_scale, font_color, thickness, cv2.LINE_AA)

    # 区域D
    text_d = 'D'
    text_size_d = cv2.getTextSize(text_d, font, font_scale, thickness)[0]
    text_x_d = width//2  - text_size_b[0] // 2
    text_y_d = height-x- text_size_b[1]//2
    cv2.putText(image, text_d, (text_x_d, text_y_d), font, font_scale, font_color, thickness, cv2.LINE_AA)

    # 区域E
    """ 
    text_e = 'E'
    text_size_e = cv2.getTextSize(text_e, font, font_scale, thickness)[0]
    text_x_e = center_x - text_size_e[0] // 2
    text_y_e = center_y + text_size_e[1] // 2
    cv2.putText(image, text_e, (text_x_e, text_y_e), font, font_scale, font_color, thickness, cv2.LINE_AA)
    """

    return image
def find_and_mark_missing_points(img):
    # 获取图像的宽度和高度
    height, width = img.shape

    # 记录缺失点的位置
    missing_points_left = []
    missing_points_right = []

    # 遍历每一行
    for y in range(height):
        # 遍历每一列的一半
        for x in range(width // 2):
            left_pixel = img[y, x]
            right_pixel = img[y, width - 1 - x]

            # 检查对称位置的点是否都是255
            if left_pixel == 255 and right_pixel != 255:
                missing_points_right.append((y, width - 1 - x))
                img[y, width - 1 - x] = 100  # 标记缺失点
            elif left_pixel != 255 and right_pixel == 255:
                missing_points_left.append((y, x))
                img[y, x] = 100  # 标记缺失点

    return img
# 初始化图像的函数
def Initialization_picture(out_path1):
    global im  # 使用全局变量 im
    if im is None:
        print("Error: Could not read the image.")
        return
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    for i in range(im.shape[0]):  # 遍历高度
        for j in range(im.shape[1]):  # 遍历宽度
            if im[i][j] > 200:
                im[i][j] = 255
            else:
                im[i][j] = 0
    im=image_correction(im)
 # 转换为灰度图像
    #showw('1',im)
    im,h,w=small_picture(im,3)
    im=remove_small_white_spots(im,255)
    ik=find_and_mark_missing_points(im)
    ik=convert_small_white_spots(ik)
    im=ik
    #cv2.imwrite("5.png", im)
    #showw('t',im)
    cv2.imwrite(out_path1,im)
    #showw('s88',ans)
    ww=int(w/9)
    hh=int(h/9)
    ss=np.array([])
    zuo,zh,zw=small_picture(im[0:h,0:ww],1)
    #showw('s88', zuo)
    ss=hang_cut(zuo,1)
    #print(ss)
    a,b=jc(ss,1)
    if a[0] or sum(b)>0:
        for i in range(1, len(a)):
            if b[a[i]]==1:
                print(f"芯片A区第{a[i]}个脚过长")
            elif b[a[i]]==2 :
                print(f"芯片A区第{a[i]}个脚过短或缺失")
            elif b[a[i]]==3:
                print(f"芯片A区第{a[i]}个脚歪曲")
            elif b[a[i]]==4:
                print(f"芯片A区第{a[i]}个脚缺失")
            col_turn(1, k_list[1 * uu + a[i]][0], k_list[1 * uu + a[i]][1],ss[a[i]-1])
    else :
        print("芯片A区无错误")
    shang,sh,sw=small_picture(im[0:hh,0:w],2)
    #showw('s88', shang)
    ss=lie_cut(shang,0)
    a,b=jc(ss,0)
    if a[0] or sum(b)>0:
        for i in range(1, len(a)):
            if b[a[i]]==1:
                print(f"芯片B区第{a[i]}个脚过长")
            elif b[a[i]]==2 :
                print(f"芯片B区第{a[i]}个脚过短或缺失")
            elif b[a[i]]==3:
                print(f"芯片B区第{a[i]}个脚歪曲")
            col_turn(0, k_list[0 * uu + a[i]][0], k_list[0 * uu + a[i]][1],ss[a[i]-1])
    else :
        print("芯片B区无错误")
    #print(ss)0
    you,yh,yw=small_picture(im[0:h,w-ww:w],1)
    yw=you.shape[1]
    #showw('s88', you)
    ss=hang_cut(you,2)
    a,b=jc(ss,2)
    if a[0] or sum(b)>0:
        for i in range(1, len(a)):
            if b[a[i]]==1:
                print(f"芯片C区第{a[i]}个脚过长")
            elif b[a[i]]==2 :
                print(f"芯片C区第{a[i]}个脚过短或缺失")
            elif b[a[i]]==3:
                print(f"芯片C区第{a[i]}个脚歪曲")
            col_turn(2,k_list[2*uu+a[i]][0],k_list[2*uu+a[i]][1],ss[a[i]-1])
    else :
        print("芯片C区无错误")
    xia,xh,xw=small_picture(im[h-hh:h,0:w],2)
    #showw('s88', xia)
    ss=lie_cut(xia,3)
    a,b=jc(ss,3)
    if a[0] or sum(b)>0:
        for i in range(1, len(a)):

            if b[a[i]]==1:
                print(f"芯片D区第{a[i]}个脚过长")
            elif b[a[i]]==2 :
                print(f"芯片D区第{a[i]}个脚过短或缺失")
            elif b[a[i]]==3:
                print(f"芯片D区第{a[i]}个脚歪曲")
            col_turn(3, k_list[3 * uu + a[i]][0], k_list[3 * uu + a[i]][1],ss[a[i]-1])
    else :
        print("芯片D区无错误")
    yw=min(yw,zw)
    zw=max(zw,yw)
    return im,sh,xh,zw,yw
# 主函数
def VoidMain(in_path,out_path1,out_path2):
    global im
    im = cv2.imread(in_path)
    im,s,x,z,y=Initialization_picture(out_path1)  # 调用初始化函数
    #showw("0",im)
    im = convert_colors(im)
    im = divide_and_label(im,s,x,z,y)
   #showw("1", im)
    cv2.imwrite(out_path2,im)
    return qs
 # 显示绘制了轮廓的图像显示绘制了轮廓的图像
# 程序入口
if __name__ == "__main__":
    VoidMain()