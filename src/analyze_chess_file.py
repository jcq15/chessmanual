import chess as che
import urllib.parse
import os
import sys

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

    # 表的结构:
    SourceFile = Column(String(512), primary_key=True)   # 源文件
    Turn = Column(Integer, primary_key=True)         # 回合数

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
        return "<Position(SourceFile='%s', Turn=%d, Board='%s', NextMove='%s', NextMoveCn='%s')>" % (self.SourceFile, self.Turn, self.Board, self.NextMove, self.NextMoveCn)


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


def write_db(positions):
    global Base

    # 连接傻子库
    password = urllib.parse.quote_plus('Leifeng@flower1')
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost/Chess?charset=utf8mb4")
    Session = sessionmaker(bind=engine)
    session = Session()
    # 初始化
    Base.metadata.create_all(engine)

    for position in positions:
        session.add(position)

    session.commit()
    session.close()


# 参数：文件儿路径，格式('che', 'cbr')
if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[2] == 'che':
            write_db(parse_che(sys.argv[1]))
        elif sys.argv[2] == 'cbr':
            pass
            #write_db(parse_cbr(sys.argv[1]))
        print(True)  # 大成功
