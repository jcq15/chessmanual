import os
import traceback
import xml.etree.ElementTree as et

# 需要先把che转成一棵树，然后dfs转化成cbf。che里面记录的是爹节点，而cbf是dfs的顺序

class Node:
    def __init__(self, value, parent=None):
        self.value = value        # value: cbf格式的5位字符串（例如：'77-74'）
        self.parent = parent      # 爹节点
        self.children = []
        self.branch = False
        self.end = False

    def add_child(self, child):
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0
    
    # xml节点
    def to_xml(self):
        element = et.Element('Move', {'value': self.value})
        if self.branch:
            element.set('branch', '1')
        if self.end:
            element.set('end', '1')
        return element
    
    def __dfs_core(self, path):
        if self.is_leaf():
            self.end = True
        path.append(self.to_xml())
        for i, child in enumerate(self.children):
            if i != len(self.children) - 1:
                child.branch = True   # 最后一个不设置branch
            child.__dfs_core(path)

    def dfs(self):
        path = []
        self.__dfs_core(path)
        return path


def che_to_cbf_single(file_path: str, out_path: str):
    # 读取che文件
    with open(file_path, 'r') as f:
        # 读取第一行
        line = f.readline()
    raw = line.split(' ')   # 后面有xml，田
    num_list = []           # 去掉xml
    # 找到data中第一个不是数字的位置
    for i in range(len(raw)):
        if raw[i].lstrip('-').isdigit():
            num_list.append(int(raw[i]))
        else:
            break

    # check
    if len(num_list) < 3:
        print(f'棋谱{file}前三位都没有，请检查')
        return None
    che_type = num_list[0]  # 第一个数是0表示qqxq，是1表示另一种
    length = num_list[1]  # 棋谱长度
    if len(num_list) == 3 + length * 10:
        pass
    elif len(num_list) == 2 + length * 10:
        # 如果最后一步不够10位，补齐，否则恶心
        num_list.append(0)
    else:
        print(f'棋谱{file}长度不对，请检查')
        return None

    # che弄成一颗树
    node_list = [Node('00-00')]
    for i in range(3, len(num_list), 10):
        sub_list = num_list[i:i+10]  # 每10位一个子列表
        # turn = sub_list[7]  # 7是turn
        # 3-6位是坐标, [1, 3, 3, 5] 相七进五, [10, 2, 8, 3] 马2进3
        # 坐标转换
        if che_type == 1:
            cbf_move = f'{sub_list[3]}{9-sub_list[2]}-{sub_list[5]}{9-sub_list[4]}'
        else:
            cbf_move = f'{sub_list[3]-1}{10-sub_list[2]}-{sub_list[5]-1}{10-sub_list[4]}'

        # 爹
        parent = node_list[sub_list[6]]
        node = Node(cbf_move, parent)
        parent.add_child(node)
        node_list.append(node)

    # dfs
    xml_list = node_list[0].dfs()
    
    # 开始构筑xml
    root = et.Element('ChineseChessRecord', {'Version': '1.0'})
    head = et.SubElement(root, 'Head')
    move_list = et.SubElement(root, 'MoveList')

    for xml in xml_list:
        move_list.append(xml)

    # 准备名字
    _, tail = os.path.split(file_path)
    # 写入文件儿
    tree = et.ElementTree(root)
    tree.write(os.path.join(out_path, tail + '.cbf'), encoding='utf-8', xml_declaration=True)


def che_to_cbf(filenames: list, out_path: str):
    fail_list = []
    for file in filenames:
        try:
            che_to_cbf_single(file, out_path)
        except Exception as e:
            print(f'转换文件{file}时出错：{e}')
            # 打印traceback
            traceback.print_exc()

            fail_list.append(file)
    return fail_list

if __name__ == '__main__':
    file_path = r'C:\Users\shitter\OneDrive\makelive\chessmanual\data\youfenzhi\2022-08-18_23-23-58_(1937932469_1)_qqxqEX.che'
    che_to_cbf_single(file_path, '.')
