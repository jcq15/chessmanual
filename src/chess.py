# 中国象棋棋子编号
# 黑方棋子儿：将11、士12、象13、马14、车15、炮16、卒17
# 红方棋子儿：帅21、仕22、相23、马24、车25、炮26、兵27

# 输入编号儿，获取棋子的汉子，返回俩：棋子名字，棋子颜色
def get_piece_char(num):
    if num == 11:
        return '将', '黑'
    elif num == 12:
        return '士', '黑'
    elif num == 13:
        return '象', '黑'
    elif num == 14:
        return '马', '黑'
    elif num == 15:
        return '车', '黑'
    elif num == 16:
        return '炮', '黑'
    elif num == 17:
        return '卒', '黑'
    elif num == 21:
        return '帅', '红'
    elif num == 22:
        return '仕', '红'
    elif num == 23:
        return '相', '红'
    elif num == 24:
        return '马', '红'
    elif num == 25:
        return '车', '红'
    elif num == 26:
        return '炮', '红'
    elif num == 27:
        return '兵', '红'
    else:
        return '', ''

# 棋盘儿坐标：左下角儿为(0,0)，右上角儿为(8,9)
# 棋盘儿表示：
# 在情绪里是9*10的二维list，就像坐标系第一象限一样儿
# 在傻子库里会变成字符串儿（长度固定180，棋盘每个交叉点占两位）

# 标准开局
# 永远红方在下，黑方在上
__standard_init = (
    (25, 0, 0, 27, 0, 0, 17, 0, 0, 15),
    (24, 0, 26, 0, 0, 0, 0, 16, 0, 14),
    (23, 0, 0, 27, 0, 0, 17, 0, 0, 13),
    (22, 0, 0, 0, 0, 0, 0, 0, 0, 12),
    (21, 0, 0, 27, 0, 0, 17, 0, 0, 11),
    (22, 0, 0, 0, 0, 0, 0, 0, 0, 12),
    (23, 0, 0, 27, 0, 0, 17, 0, 0, 13),
    (24, 0, 26, 0, 0, 0, 0, 16, 0, 14),
    (25, 0, 0, 27, 0, 0, 17, 0, 0, 15)
)

def get_standard_init(read_only=False):
    if read_only:
        return __standard_init
    else:
        return [list(i) for i in __standard_init]

# 棋盘字符串和list表示的转换
def board_to_string(board_ls):
    s = ''
    for i in range(9):
        for j in range(10):
            if board_ls[i][j] == 0:
                s += '00'
            else:
                s += str(board_ls[i][j])
    return s

def board_to_list(board_str):
    board_ls = [[0 for i in range(10)] for j in range(9)]
    for i in range(90):
        board_ls[i // 10][i % 10] = int(board_str[i*2:i*2+2])
    return board_ls

# 棋谱儿标准表示（内部表示）
# 情绪里是长度为5的list：棋子编号，x1, y1, x2, y2
# 傻子库是长度为6的字符串儿，前两位是棋子儿号儿，后四位是棋盘儿坐标儿
# 例：147967，表示棋子14（黑马儿）从(7,9)走到(6,7)，即马2进3

def move_to_string(move):
    return ''.join([str(i) for i in move])

def move_to_list(move):
    return [int(move[:2]), int(move[2]), int(move[3]), int(move[4]), int(move[5])]

# utils
__cn_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
def __get_column_name(num, is_red):
    return __cn_nums[9-num] if is_red else str(num+1)

# 确定第一个字儿
__cn1_ls = [
    [], [],
    ['', '前', '后'],
    ['', '前', '中', '后'],
    ['', '前', '二', '三', '四'],
    ['', '前', '二', '三', '四', '五']
]

# 棋谱儿的汉字表示，就是汉子表示的棋谱儿，炮二平五这种
# 需要board信息
def move_get_cn(move, board):
    name, color = get_piece_char(move[0])
    is_black = color == '黑'
    is_red = not is_black
    x1, y1, x2, y2 = move[1], move[2], move[3], move[4]

    # 后两位最简单
    if y1 == y2:
        cn3 = '平'
    elif (y1 < y2 and is_red) or (y1 > y2 and is_black):
        cn3 = '进'
    else:
        cn3 = '退'
    
    if x1 == x2:
        distance = abs(y2 - y1)
        cn4 = __cn_nums[distance] if is_red else str(distance)
    else:
        cn4 = __get_column_name(x2, is_red)

    # 前两位
    # 先看这一列有几个
    this_column_count = 0       # 这一列有几个
    this_piece_order = 1        # 这玩意是第几个
    for j in range(10):
        if board[x1][j] == move[0]:
            this_column_count += 1
            if (is_red and j > y1) or (is_black and j < y1):
                this_piece_order += 1

    if this_column_count == 1:
        cn1 = name
        cn2 = __get_column_name(x1, is_red)
    else:
        # 查表看它叫啥
        cn1 = __cn1_ls[this_column_count][this_piece_order]
        
        # cn2: 多于一个，要看是不是兵卒
        if name == '兵' or name == '卒':
            # 检查每一纵线有几个这玩意
            ill_columns = []        # 有至少两个的纵线
            for i in range(9):
                count = 0
                for j in range(10):
                    if board[i][j] == move[0]:
                        count += 1
                if count >= 2:
                    ill_columns.append(i)
            if len(ill_columns) == 2:
                # 特例：当兵卒在两个纵线都达到两个以上时，二7平6
                cn2 = __get_column_name(x1, is_red)
            else:
                cn2 = name

        # 其他棋子，只能是前或后
        else:
            cn2 = name
    
    return cn1 + cn2 + cn3 + cn4


# 根据当前棋盘和棋谱儿，推出下一个棋盘状态
# replace=True则在原board上操作，False则是新board
def next_board(board, move_ls, replace=False):
    if not replace:
        # 棋盘儿的拷贝
        next_board = [[0 for i in range(10)] for j in range(9)]
        for i in range(9):
            for j in range(10):
                next_board[i][j] = board[i][j]
    else:
        next_board = board

    next_board[move_ls[3]][move_ls[4]] = move_ls[0]
    next_board[move_ls[1]][move_ls[2]] = 0

    return next_board


if __name__ == '__main__':
    '''
    # 测试board_to_string和board_to_list
    board_ls = [[0 for i in range(10)] for j in range(9)]
    board_ls[6][7] = 14
    print(board_to_string(board_ls))
    print(board_to_list(board_to_string(board_ls)))
    '''
    
    # 测试move_get_cn
    board_ls = get_standard_init()
    move_ls = [14, 7, 9, 6, 7]
    print(move_get_cn(move_ls, board_ls))


# 术语中英文对照 https://www.douban.com/group/topic/30094591/?_i=0459882i48gFTh