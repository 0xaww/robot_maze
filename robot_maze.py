#coding=utf-8
from PIL import Image
import time
import random
import sys
class Robot(object):

    def __init__(self,mode="all",size=400,move={"up":"u","down":"d","left":"l","right":"r"},debug=False, scan_mode="dst", pic_debug=False,wall= "#",path = " ",begin= "*",dst="D",pic_counter= 50 ):
        super(Robot, self).__init__()
        self.mode = mode
        self.start_time = time.time()
        self.end_time = time.time()
        self.x_size = size
        self.y_size = size
        self.array = [[9] * self.x_size for i in range(self.y_size) ]
        self.begin_x = self.x_size/4
        self.begin_y = self.y_size/4
        self.now_x = self.begin_x
        self.now_y = self.begin_y
        # now_x为x轴位置，now_y为y轴位置
        self.array[self.now_y][self.now_x]=7
        self.next_x = 0
        self.next_y = 0
        self.last = [self.begin_x,self.begin_y]
        self.lastoutput = []
        self.now_output = []
        self.output = []
        self.all_output = []
        self.min_output = []
        self.point_finish = 0
        self.next_exit =[]
        self.forks = []
        self.dst_finish = 0
        self.all_finish = 0
        # 字符意义
        self.wall = wall
        self.path = path
        self.dst = dst
        self.begin = begin
        # 上下左右
        self.move = move
        self.counter = 0
        self.debug = debug
        self.scan_mode = scan_mode
        self.pic_debug = pic_debug
        self.pic_counter = pic_counter
        self.directions = {"up":["right","up","left","down"],"down":["left","down","right","up"],"left":["up","left","down","right"],"right":["down","right","up","left"]}
        self.exits = self.directions["up"]
        self.round = {}

        # 单位
        # 1:通道 0:墙 9:未知 8:出口
        # 1:通道 0:墙 7:起点 8:终点
    def help(self):
        print("useage: ")
        print('● 初始化robot，mode分为all和right')
        print('    robot = Robot(mode="all",size=400,move={"up":"u","down":"d","left":"l","right":"r"},debug=False,scan_mode="all",pic_debug=True,pic_counter= 5000)')
        print('    robot = Robot(mode="right",size=400,move={"up":"u","down":"d","left":"l","right":"r"},debug=False,scan_mode="dst",pic_debug=True,wall= "#",path = " ",begin= "*",dst="D",pic_counter= 50)')
        print('● 获取下一步路径')
        print('    next_step = robot.next_step()')
        print('● 设置点的属性')
        print('    robot.set_point(1)')
        print('● 将字符串转为二维数组')
        print('    array = robot.str2array(string)')
        print('● 将图片转换成二维数组')
        print('    array = robot.pic2array(file="./sample.png",point_debug=True)')
        print('● 将二维数组转为图片')
        print('    robot.array2pic(array,wall ="#",path = " ",dst = "D",begin = "*",file="./array2pic.png")')
        print('● 将二维数组打印成迷宫')
        print('    robot.array2maze(array,wall_ori = "#",path_ori =  " ",dst_ori ="D" ,begin_ori = "*",wall ="#",path = " ",dst = "D",begin = "*")')
        print('● 生成随机迷宫')
        print('    array = robot.make_maze(width=11,height=11,wall ="#",path = " ",dst = "D",begin = "*",debug=True)')

    def exception(self,e="robot failed",func_name="unknown"):
        print(func_name +" has a problem:")
        print(str(e))
        if self.pic_debug:
            self.save_pic()
        print("\n")
        raise

    def str2array(self,string):
        #string通过回车换行，每一行中间没有间隔，前后不能有回车
        string = string.split("\n")
        array = []
        for line in string:
            array.append(list(line))
        return array


    def pic2array(self,file="./array2pic.png",point_debug=False,wall = 0,path=1):
        def get_block(pic):
            def four_ways(x,y,pic):
                try:
                    block = 1
                    p1 = pic.getpixel((x,y))
                    p2 = -1
                    p3 = -1
                    p4 = -1
                    p5 = -1
                    while 1:
                        # print pic.getpixel((x+block,y))
                        if p2 == -1 and p1 != pic.getpixel((x+block,y)):
                            p2 = block
                        if p3 == -1 and p1 != pic.getpixel((x-block,y)):
                            p3 = block
                        if p4 == -1 and p1 != pic.getpixel((x,y+block)) :
                            p4 = block
                        if p5 == -1 and p1 != pic.getpixel((x,y-block)) :
                            p5 = block
                        block += 1
                        if p2 != -1 and p3 != -1 and p4 != -1 and p5 != -1 :
                            x1 = p2 + p3
                            y1 = p4 + p5
                            return x1,y1
                except Exception as e:
                    print(str(e))
                    self.exception(e,func_name=sys._getframe().f_code.co_name)

            x_list=[]
            y_list=[]
            for i in range(1,10):
                for j in range(1,10):
                    try:
                        x1,y1 = four_ways((pic.size[0]*j)/10,(pic.size[1]*i)/10,pic)
                        x_list.append(x1)
                        y_list.append(y1)
                    except Exception as e:
                        print("pic2array get_block one point error")
                        self.exception(e,func_name=sys._getframe().f_code.co_name)

            return  min(x_list)-1,min(y_list)-1
        try:
            pic = Image.open(file)
            check_pic = pic
            pic=pic.convert("1")
            x_size,y_size = pic.size
            x_block,y_block = get_block(pic)
            if point_debug:
                print x_block,y_block
            array = []
            tmp = []
            for y in range(0,pic.size[1]/y_block+1):
                for x in range(0,pic.size[0]/x_block+1):
                    if (x_block/2 + x_block * x) >= x_size or (y_block/2 + y_block*y) >= y_size:
                        continue
                    out = pic.getpixel((x_block/2 + x_block * x, y_block/2 + y_block*y))
                    check_pic.putpixel([x_block/2 + x_block * x, y_block/2 + y_block*y], (0, 255, 127))
                    if  out == 0:
                        tmp.append(wall)
                    elif out == 255 :
                        tmp.append(path)
                if tmp != []:
                    array.append(tmp)
                tmp = []
            if point_debug:
                check_pic.save("check_point.png")
            return array
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)
            raise

    def array2pic(self,array,wall =0,path = 1,dst = 8,begin = 7,file="./array2pic.png"):
        try:
            pic = Image.new("RGB", (len(array[0]), len(array)))
            for y in range(0,len(array)):
                for x in range(0,len(array[0])):
                    if array[y][x] == path:
                        pic.putpixel([x, y], (255, 255, 255))
                    elif array[y][x] == wall:
                        pic.putpixel([x, y], (0, 0, 0))
                    elif array[y][x] == begin:
                        pic.putpixel([x, y], (255, 0, 0))
                    elif array[y][x] == dst:
                        pic.putpixel([x, y], (125, 255, 127))
            # pic = pic.resize((MAX*20, MAX*20))
            pic.save(file)
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)
            print(str(e))
            print(x, y)

    def array2maze(self,array,wall_ori = 0,path_ori =  1, begin_ori = 7, dst_ori =8 ,wall ="#",path = " ",dst = "D",begin = "*"):
        for i in range(len(array)):
            for j in range(len(array[0])):
                if array[i][j] == wall_ori:
                    sys.stdout.write(wall)
                elif array[i][j] == path_ori:
                    sys.stdout.write(path)
                elif array[i][j] == begin_ori:
                    sys.stdout.write(begin)
                elif array[i][j] == dst_ori:
                    sys.stdout.write(dst)
            print('')

    def make_maze(self,width=11,height=11, wall =0, path = 1, dst = 8,begin = 7,debug=False):
        # num 0 1 7 9 -> str wall path begin dst
        assert width >= 5 and height >= 5, "Length of width or height must be larger than 5."
        width = (width // 2) * 2 + 1
        height = (height // 2) * 2 + 1
        start = [1, 1]
        destination = [height - 2, width - 2]
        matrix = None

        # 地图初始化，并将出口和入口处的值设置为0
        matrix = [[-1.0] * width for i in range(height) ]

        def check(row, col):
            temp_sum = 0
            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                temp_sum += matrix[row + d[0]][col + d[1]]
            return temp_sum < -3

        queue = []

        row, col = (random.randint(1, height - 1) // 2) * 2 + 1, (random.randint(1, width - 1) // 2) * 2 + 1
        queue.append((row, col, -1, -1))
        while len(queue) != 0:
            row, col, r_, c_ = queue.pop(random.randint(0, len(queue)-1))
            if check(row, col):
                matrix[row][col] = 0
                if r_ != -1 and row == r_:
                    matrix[row][min(col, c_) + 1] = 0
                elif r_ != -1 and col == c_:
                    matrix[min(row, r_) + 1][col] = 0
                for d in [[0, 2], [0, -2], [2, 0], [-2, 0]]:
                    row_, col_ = row + d[0], col + d[1]
                    if row_ > 0 and row_ < height - 1 and col_ > 0 and col_ < width - 1 and matrix[row_][col_] == -1:
                        queue.append((row_, col_, row, col))

        matrix[start[0]][ start[1]] = 7
        matrix[destination[0]][destination[1]] = 8
        new_array = []
        for y in matrix:
            tmp = []
            for x in y:
                # 这里的0和-1不能更改，7和8可以更改
                if x == 0:
                    tmp.append(path)
                elif x == -1:
                    tmp.append(wall)
                elif x == 7:
                    tmp.append(begin)
                elif x == 8:
                    tmp.append(dst)
            new_array.append(tmp)
        matrix = new_array
        if debug:
            self.array2maze(matrix)
        return matrix


    def save_pic(self,file ="save_pic.png"):
        try:
            min_x = len(self.array[0])
            min_y = len(self.array)
            max_x = 0
            max_y = 0
            for y in range(0,len(self.array)):
                for x in range(0,len(self.array[0])):
                    if self.array[y][x] != 9:
                        if x > max_x :
                            max_x = x
                        if x < min_x:
                            min_x = x
                        if y > max_y:
                            max_y = y
                        if y < min_y:
                            min_y = y
            # MAX = len(self.array)
            pic = Image.new("RGB", (max_x-min_x+1, max_y-min_y+1))
            for y in range(min_y,max_y+1):
                for x in range(min_x,max_x+1):
                    if self.array[y][x] == 1:
                        pic.putpixel([x-min_x, y-min_y], (255, 255, 255))
                    elif self.array[y][x] == 0:
                        pic.putpixel([x-min_x, y-min_y], (0, 0, 0))
                    elif self.array[y][x] == 8:
                        pic.putpixel([x-min_x, y-min_y], (0, 255, 127))
                    elif self.array[y][x] == 7:
                        pic.putpixel([x-min_x, y-min_y], (255, 0, 0))
            x = self.begin_x-min_x
            y = self.begin_y-min_y
            if len(self.min_output) != 0:
                pic.putpixel([x, y], (0, 255, 127))
                for step in self.min_output:
                    if   step == self.move["right"]:
                        x = x + 1
                    elif step == self.move["down"]:
                        y = y + 1
                    elif step == self.move["left"]:
                        x = x - 1
                    elif step == self.move["up"]:
                        y = y - 1
                    pic.putpixel([x, y], (0, 255, 127))
            x = self.begin_x-min_x
            y = self.begin_y-min_y
            if self.all_finish == 0:
                pic.putpixel([x, y], (255, 0, 0))
                for step in self.output:
                    if   step == self.move["right"]:
                        x = x + 1
                    elif step == self.move["down"]:
                        y = y + 1
                    elif step == self.move["left"]:
                        x = x - 1
                    elif step == self.move["up"]:
                        y = y - 1
                    pic.putpixel([x, y], (255, 0, 0))

            # pic = pic.resize((pic.size[0]*20, pic.size[1]*20))
            pic.save(file)
        except Exception as e:
            print(min_x,max_x,min_y,max_y)
            print(str(e))
            print(x, y)
            print array
            self.exception(e,func_name=sys._getframe().f_code.co_name)




    def resize_array(self):
        try:
            if self.now_x == self.x_size-1 or self.now_y == self.y_size-1 or self.now_x == 0 or self.now_y == 0:
                # self.save_pic("sav2pic_"+str(self.x_size) +".png")
                print("array不够大，现扩大array")
                old_begin_x = self.begin_x
                old_begin_y = self.begin_y
                self.x_size = self.x_size * 4
                self.y_size = self.y_size * 4
                array_new = [[9] * self.x_size for i in range(self.y_size) ]
                self.begin_x = self.x_size/4
                self.begin_y = self.y_size/4
                self.now_x = self.begin_x + self.now_x - old_begin_x
                self.now_y = self.begin_y + self.now_y - old_begin_y
                self.next_x = self.begin_x + self.next_x - old_begin_x
                self.next_y = self.begin_y + self.next_y - old_begin_y
                for y,y_list in enumerate(self.array):
                    for x ,value in enumerate(y_list):
                        array_new[self.begin_y + y - old_begin_y][self.begin_x + x - old_begin_x] = value
                self.array = array_new
                if len(self.forks) > 0 :
                    for num in range(len(self.forks)):
                        self.forks[num]["next_position"] = [self.forks[num]["next_position"][0]+ self.begin_x - old_begin_x,self.forks[num]["next_position"][1]+ self.begin_y - old_begin_y]
                        self.forks[num]["before_position"] = [self.forks[num]["before_position"][0]+ self.begin_x - old_begin_x,self.forks[num]["before_position"][1]+ self.begin_y - old_begin_y]
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)

    # now_x,now_y为当前点的坐标
    # next_x,next_y为下一个检测的点的坐标
    # nextouput为下一个检测点的路径
    # point_finish为当前点的四个方向是否都检测完
    # now_output为当前点的路径
    # output为即将输出的点的路径
    def get_point_round(self,string=""):
        try:
            if self.mode == "right":
                def get_point_xy(array):
                    for i,y in enumerate(array):
                        for j,x in enumerate(y):
                            if array[i][j] == self.begin:
                                return j,i
                array = self.str2array(string)
                x,y = get_point_xy(array)
                self.round["up"] = array[y-1][x]
                self.round["down"] = array[y+1][x]
                self.round["left"] = array[y][x-1]
                self.round["right"] = array[y][x+1]
                for i in self.round:
                    if self.round[i] == self.wall:
                        self.round[i] = 0
                    elif self.round[i] == self.path:
                        self.round[i] = 1
                    if self.round[i] == self.dst:
                        self.round[i] =8
            elif self.mode == "all":
                # 判断矩阵是否够大
                self.resize_array()
                if   self.array[self.now_y + 1][self.now_x] == 9 :
                    self.next_x = self.now_x
                    self.next_y = self.now_y + 1
                    self.next_output = [self.move["down"]]
                    self.output = self.now_output + self.next_output
                elif self.array[self.now_y][self.now_x+1] == 9 :
                    self.next_x = self.now_x + 1
                    self.next_y = self.now_y
                    self.next_output = [self.move["right"]]
                    self.output = self.now_output + self.next_output
                elif self.array[self.now_y][self.now_x - 1] == 9 :
                    self.next_x = self.now_x - 1
                    self.next_y = self.now_y
                    self.next_output = [self.move["left"]]
                    self.output = self.now_output + self.next_output
                elif self.array[self.now_y - 1][self.now_x] == 9 :
                    self.next_x = self.now_x
                    self.next_y = self.now_y - 1
                    self.next_output = [self.move["up"]]
                    self.output = self.now_output + self.next_output
                else :
                    self.point_finish = 1
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)


    def set_point(self,value=0):
        try:
            if self.mode == "right":
                self.resize_array()
                # round = {"up":round[0],"down":round[1],"left":round[2],"right":round[3]}
                # exits = ["l","d","r","u"]
                self.array[self.now_y-1][self.now_x] = self.round["up"]
                self.array[self.now_y+1][self.now_x] = self.round["down"]
                self.array[self.now_y][self.now_x-1] = self.round["left"]
                self.array[self.now_y][self.now_x+1] = self.round["right"]
                for exit in self.exits:
                    if   exit == "left" and self.round["left"] >= 1:
                        self.next_x = self.now_x - 1
                        # if self.now_x - 1 != self.last[0]:
                        self.last = [self.now_x,self.now_y]
                        self.now_x = self.next_x
                        self.output = self.move["left"]
                        self.exits = self.directions[exit]
                        break

                    elif exit == "right" and self.round["right"] >= 1:
                        self.next_x = self.now_x + 1
                        # if self.next_x != self.last[0]:
                        self.last = [self.now_x,self.now_y]
                        self.now_x = self.next_x
                        self.output = self.move["right"]
                        self.exits = self.directions[exit]
                        break

                    elif exit == "down" and self.round["down"] >= 1:
                        self.next_y = self.now_y + 1
                        # if self.next_y != self.last[1]:
                        self.last = [self.now_x,self.now_y]
                        self.now_y = self.next_y
                        self.output = self.move["down"]
                        self.exits = self.directions[exit]
                        break

                    elif exit == "up" and self.round["up"] >= 1:
                        self.next_y = self.now_y - 1
                        # if self.next_y != self.last[1]:
                        self.last = [self.now_x,self.now_y]
                        self.now_y = self.next_y
                        self.output = self.move["up"]
                        self.exits = self.directions[exit]
                        break

                for i in self.round:
                    if self.round[i] == 8:
                        self.all_finish = 1

                if self.all_finish :
                    self.all_finish = 1
                    self.end_time = time.time()
                    print("已经发现终点，准备遍历剩下路径，如需停止，按下ctrl+c")
                    print("Robot running time : " + str(int((self.end_time-self.start_time)))+" s")
                    if self.pic_debug:
                        self.save_pic()
                self.counter +=1
                if self.counter > 500:
                    self.counter = 0
                    if self.pic_debug:
                        self.save_pic()
            elif self.mode == "all":
                if   value == 0:
                    self.array[self.next_y][self.next_x] = 0
                elif value == 1:
                    self.array[self.next_y][self.next_x] = 1
                    self.next_exit.append({"next_position":[self.next_x,self.next_y],
                                          "before_position":[self.now_x,self.now_y],
                                          "output":self.output})
                elif value == 8:
                    self.array[self.next_y][self.next_x] = 8
                    self.min_output = self.output
                    self.all_output = self.output
                    self.end_time = time.time()
                    print("已经发现终点，准备遍历剩下路径，如需停止，按下ctrl+c")
                    print("Robot running time : " + str(int((self.end_time-self.start_time)))+" s")
                    if self.scan_mode == "dst":
                        self.dst_finish = 1
                        self.all_finish = 1
                    elif self.scan_mode == "all":
                        self.dst_finish = 1
                    self.save_pic()
                self.counter += 1
                if self.debug:
                    print self.counter
                if self.counter >= self.pic_counter:
                    if self.pic_debug:
                        self.save_pic()
                    self.counter = 1
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)

    #用于第一步判断
    def next_step(self):
        try:
            if self.mode == "right":
                if  self.output == self.move["right"]:
                    output = self.move["left"]
                elif self.output == self.move["left"]:
                    output = self.move["right"]
                elif self.output == self.move["up"]:
                    output = self.move["down"]
                elif self.output == self.move["down"]:
                    output = self.move["up"]
                if len(self.min_output) > 0 and output == self.min_output[-1]:
                    self.min_output.pop(-1)
                else:
                    self.min_output.append(self.output)
                self.all_output.append(self.output)
                return self.output
            elif self.mode == "all":
                while 1:
                    self.get_point_round()
                    # 判断四个方向是否都检测完
                    # 如果没检测完，直接返回相邻点
                    if self.point_finish == 0:
                        if self.debug:
                            print(self.output)
                        return self.output
                    # 相邻点检测完，即将进行换点
                    else:
                        # 如果有两个以上的出口，将第一个以外的出口添加分岔口配置
                        if len(self.next_exit) >= 2:
                            for next in self.next_exit[1:]:
                                self.forks.append(next)
                        # 如果没有出口，则将分岔口中最新的一个出口配置
                        elif len(self.next_exit) == 0:
                            if len(self.forks) == 0:
                                self.all_finish = 1
                                self.end_time = time.time()
                                print("所有路径已全部遍历")
                                print("All running time : " + str(int((self.end_time-self.start_time)))+" s")
                                if self.pic_debug:
                                    self.save_pic()
                                return self.output
                            self.next_exit.append(self.forks.pop(-1))
                        # 默认处理第一个出口
                        self.now_x = self.next_exit[0]["next_position"][0]
                        self.now_y = self.next_exit[0]["next_position"][1]
                        self.now_output = self.next_exit[0]["output"]
                        self.next_exit = []
                        self.point_finish = 0
                        # 更换完点后，再次获取四个方向
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)

    def array2solve(self,array, wall = 0, path = 1, begin = 7, dst = 8, move={"up":"u","down":"d","left":"l","right":"r"}):
        try:
            # 参数中，wall、path、begin、dst必须设置，防止错误
            robot = Robot(move=move)
            end_x = end_y = begin_x = begin_y = -1
            # 根据字符，找到起点和终点坐标
            for y in range(len(array)):
                for x in range(len(array[0])):
                    if array[y][x] == dst:
                        end_x = x
                        end_y = y
                    elif array[y][x] == begin:
                        begin_x = x
                        begin_y = y
            if end_x == -1 or end_y == -1 or begin_x == -1 or begin_y == -1 :
                self.exception("获取起点和终点坐标失败",func_name=sys._getframe().f_code.co_name)
            while not robot.all_finish:
                x = begin_x
                y = begin_y
                next_step = robot.next_step()
                # print next_step
                for step in next_step:
                    if step == move["right"]:
                        x = x + 1
                    elif step == move["down"]:
                        y = y + 1
                    elif step == move["left"]:
                        x = x - 1
                    elif step == move["up"]:
                        y = y - 1
                # print num
                if x <0 or y < 0 or y >=len(array) or x >= len(array) :
                    robot.set_point(0)
                elif array[y][x] == wall:
                    robot.set_point(0)
                elif array[y][x] == path:
                    robot.set_point(1)
                elif array[y][x] == dst:
                    robot.set_point(8)
            return robot.all_output
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)
    def pic2solve(self,file,start_x=1,start_y=1,end_x=-2,end_y=-2,move={"up":"u","down":"d","left":"l","right":"r"}):
        try:
            # pic2solve中，file,start_x,start_y,end_x,end_y参数必须设置
            array = self.pic2array(file)
            print len(array)
            print len(array[0])
            array[start_y][start_x]= 7
            array[end_y][end_x]= 8
            output = self.array2solve(array, wall = 0, path = 1, begin = 7, dst = 8,move=move)
            return output
        except Exception as e:
            self.exception(e,func_name=sys._getframe().f_code.co_name)
