# robot_maze



## 依赖

```
python2
pillow
```



## 安装

`python setup.py install`



### 使用方法

```python
from robot_maze import *
robot = Robot()
robot.move = {"up":"U","down":"D","left":"L","right":"R"}
while not robot.all_finish:
    try:
        next_step = robot.next_step()
        if #success:
            robot.set_point(8)
        elif #wall:
            robot.set_point(0)
        elif #path:
            robot.set_point(1)
    except Exception as e:
        print(str(e))

print("output:",robot.min_output)
```



### 帮助

```python
from robot_maze import *
robot = Robot()
robot.help()
```

