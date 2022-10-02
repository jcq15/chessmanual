import chess as che
import urllib.parse
import os
import sys
import xml.etree.ElementTree as et
from copy import copy, deepcopy

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

# 定义Position对象，表示局面:
class Position(Base):
    # 表的名字:
    __tablename__ = 'Position'

    id = Column(Integer, primary_key=True, autoincrement=True) # 得有主键
    # 表的结构:
    SourceFile = Column(String(512))   # 源文件
    Turn = Column(Integer)         # 回合数
    Label = Column(String(64))                          # 标签儿

    Board = Column(String(90))                      # 盘面
    NextMove = Column(String(5))                    # 下一步着法
    NextMoveCn = Column(String(4))                    # 下一步着法中文
    #GameTime = Column(DateTime)                     # 开始对局的时间，暂时未处理，先保留吧
    # 左右翻转
    BoardLR = Column(String(90))                      # 盘面
    NextMoveLR = Column(String(5))                    # 下一步着法
    NextMoveCnLR = Column(String(4))                    # 下一步着法中文
    # 上下翻转
    BoardUD = Column(String(90))                      # 盘面
    NextMoveUD = Column(String(5))                    # 下一步着法
    NextMoveCnUD = Column(String(4))                    # 下一步着法中文
    # 上下左右翻转
    BoardLRUD = Column(String(90))                      # 盘面
    NextMoveLRUD = Column(String(5))                    # 下一步着法
    NextMoveCnLRUD = Column(String(4))                    # 下一步着法中文

    def __repr__(self):
        return "<Position(Turn=%d, NextMove='%s', NextMoveCn='%s', Label='%s')>" % (self.Turn, self.NextMove, self.NextMoveCn, self.Label)


# 立即执行，急急如律令
password = urllib.parse.quote_plus('Leifeng@flower1')
engine = create_engine(f"mysql+pymysql://root:{password}@localhost/Chess?charset=utf8mb4")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


# 返回Position数组
def parse_che(file):
    with open(file, 'r') as f:
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

    # sanity check
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
    
    pos_list = []
    # 棋谱儿开始了
    board = che.get_standard_init()
    save_board = []  # 保存每一状态的棋盘儿，用于处理分支

    for i in range(3, len(num_list), 10):
        sub_list = num_list[i:i+10]  # 每10位一个子列表
        #3-6位是坐标, [1, 3, 3, 5] 相七进五, [10, 2, 8, 3] 马2进3
        # 坐标转换
        if che_type == 1:
            converted = [9-sub_list[2], sub_list[3], 9-sub_list[4], sub_list[5]]
        else:
            converted = [10-sub_list[2], sub_list[3]-1, 10-sub_list[4], sub_list[5]-1]
        piece = board[converted[0]][converted[1]]   # 棋子儿
        move = [piece, *converted]              # 着法儿

        pos = Position(
            SourceFile = file,
            Turn = sub_list[7] - 1,            # 初始局面为0，红棋走一步以后的局面为1
            Board = che.board_to_string(board),
            NextMove = che.move_to_string(move),
            NextMoveCn = che.move_get_cn(move, board),
            # game_time = None
        )
        
        # 翻转
        if not che.check_lr_sym(board):
            rev_board, rev_move = che.lr_reverse(board, move)
            pos.BoardLR = che.board_to_string(rev_board)
            pos.NextMoveLR = che.move_to_string(rev_move)
            pos.NextMoveCnLR = che.move_get_cn(rev_move, rev_board)
        if not che.check_ud_sym(board):
            rev_board, rev_move = che.ud_reverse(board, move)
            pos.BoardUD = che.board_to_string(rev_board)
            pos.NextMoveUD = che.move_to_string(rev_move)
            pos.NextMoveCnUD = che.move_get_cn(rev_move, rev_board)
        if not che.check_lrud_sym(board):
            rev_board, rev_move = che.lrud_reverse(board, move)
            pos.BoardLRUD = che.board_to_string(rev_board)
            pos.NextMoveLRUD = che.move_to_string(rev_move)
            pos.NextMoveCnLRUD = che.move_get_cn(rev_move, rev_board)
        
        pos_list.append(pos)

        che.next_board(board, move, replace=True)                 # 更新棋盘
    
    return pos_list


def parse_cbf(file):
    tree = et.parse(file)
    root = tree.getroot()
    move_list = root.findall("MoveList")[0][1:]  # 第一个是00-00

    # 带有分支的情况相当于反向DFS，需要用栈来处理
    stack = []        # 遇到end出栈 (turn, board, branch)
    pos_list = []
    board = che.get_standard_init()
    stack.append((0, board, False))

    for move in move_list:
        value = move.attrib['value']
        # 在执行move之前，棋盘的回合数为turn，入库也是turn和move一起入
        # 我爸爸是栈顶元素
        board = deepcopy(stack[-1][1])
        turn = stack[-1][0]

        # 处理pos
        converted = [int(value[1]), int(value[0]), int(value[4]), int(value[3])]
        piece = board[converted[0]][converted[1]]   # 棋子儿
        standard_move = [piece, *converted]              # 着法儿
        pos = Position(
            SourceFile = file,
            Turn = turn,            # 初始局面为0，红棋走一步以后的局面为1
            Board = che.board_to_string(board),
            NextMove = che.move_to_string(standard_move),
            NextMoveCn = che.move_get_cn(standard_move, board),
            # game_time = None
        )
        pos_list.append(pos)

        # 下一局面
        che.next_board(board, standard_move, replace=True)

        # 自己入栈，然后检测end，如果有end就出栈
        stack.append((turn+1, board, 'branch' in move.attrib))
        if 'end' in move.attrib:
            while True:
                top = stack.pop()
                if top[2]:
                    break

        return pos_list


class DBManager:
    # 连接傻子
    def __init__(self, commit=False):
        self.commit = commit
        self.session = Session()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.commit:
            self.session.commit()
        self.session.close()
        return False # re-raise this exception

    # 如果指定label，则自动给这一批positions加label
    def write_db(self, positions, label=None):
        if label:
            for pos in positions:
                pos.Label = label
        self.commit = True
        for pos in positions:
            self.session.add(pos)
    
    # 返回所有棋谱儿，数据量巨大时避免用这个
    def query_all(self):
        pos = self.session.query(Position).all()
        return pos

    # 一键删库！不要随便儿调用！
    def remove_all(self, are_you_sure):
        if are_you_sure == '老子真的要删库！':
            self.commit = True
            self.session.query(Position).delete()


# 参数：文件儿路径，格式('che', 'cbr')
if __name__ == '__main__':
    # print(sys.argv)
    if len(sys.argv) == 4:
        if sys.argv[2] == 'che':
            with DBManager(commit=True) as dm:
                dm.write_db(parse_che(sys.argv[1]), label=sys.argv[3])
        elif sys.argv[2] == 'cbr':
            pass
            #write_db(parse_cbr(sys.argv[1]))
        # print(True)  # 大成功
    elif len(sys.argv) == 2 and sys.argv[1] == 'all':
        # 日所有
        # 遍历/var/www/html/chess_files/下的所有目录
        with DBManager(commit=True) as dm:
            root = '/var/www/html/chess_files/'
            for root, dirs, files in os.walk(root):
                # dirs = ['9月8日之前', 'test', 'web']
                for dir in dirs:
                    if dir == 'web':
                        continue
                    # print(dir)
                    # 遍历目录下的所有文件
                    for file in os.listdir(root + dir):
                        # print(file)
                        # 逐个解析
                        if file[-3:] == 'che':
                            try:
                                positions = parse_che(root + dir + '/' + file)
                                dm.write_db(positions, dir)
                            except Exception as e:
                                # print(e)
                                print(root + dir + '/' + file, '田了！')
                        elif file[-3:] == 'cbr':
                            pass
                            #dm.write_db(parse_cbr(root + dir + '/' + file), dir)
                        # print(True)  # 大成功
                break   # os.walk 会递归遍历，我们只要第一层
