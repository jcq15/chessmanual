# 中国象棋相关工具

# 中国象棋棋子编号
# 黑方棋子儿：zpcmxsj
# 红方棋子儿：ZPCMXSJ

# 输入字母儿，获取棋子的汉子，返回俩：棋子名字，棋子颜色
def get_piece_char(char):
    if char == 'j':
        return '将', '黑'
    elif char == 's':
        return '士', '黑'
    elif char == 'x':
        return '象', '黑'
    elif char == 'm':
        return '马', '黑'
    elif char == 'c':
        return '车', '黑'
    elif char == 'p':
        return '炮', '黑'
    elif char == 'z':
        return '卒', '黑'
    elif char == 'J':
        return '帅', '红'
    elif char == 'S':
        return '仕', '红'
    elif char == 'X':
        return '相', '红'
    elif char == 'M':
        return '马', '红'
    elif char == 'C':
        return '车', '红'
    elif char == 'P':
        return '炮', '红'
    elif char == 'Z':
        return '兵', '红'
    elif char == 'O':
        return '', ''
    else:
        return '', ''

# 棋盘儿坐标：左上角儿为(0,0)，行儿优先，右下角儿为(9,8)
# 棋盘儿表示：
# 情绪里用二维list
# 字符串儿（长度固定90，棋盘每个交叉点占一位），空白是'O'

# 标准开局
# 永远红方在下，黑方在上
__standard_init = (
    ('c', 'm', 'x', 's', 'j', 's', 'x', 'm', 'c'),
    ('O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'),
    ('O', 'p', 'O', 'O', 'O', 'O', 'O', 'p', 'O'),
    ('z', 'O', 'z', 'O', 'z', 'O', 'z', 'O', 'z'),
    ('O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'),
    ('O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'),
    ('Z', 'O', 'Z', 'O', 'Z', 'O', 'Z', 'O', 'Z'),
    ('O', 'P', 'O', 'O', 'O', 'O', 'O', 'P', 'O'),
    ('O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'),
    ('C', 'M', 'X', 'S', 'J', 'S', 'X', 'M', 'C')
)

def get_standard_init(read_only=False):
    if read_only:
        return __standard_init
    else:
        return [list(i) for i in __standard_init]

# 棋盘字符串和list表示的转换
def board_to_string(board_ls):
    return ''.join([''.join(r) for r in board_ls])

def board_to_list(board_str):
    board_ls = [[0 for i in range(9)] for j in range(10)]
    for i in range(10):
        for j in range(9):
            board_ls[i][j] = board_str[i*9+j]
    return board_ls

# 棋谱儿标准表示（内部表示）
# 情绪里是长度为5的list：棋子，x1, y1, x2, y2
# 傻子库是长度为5的字符串儿，前两位是棋子儿号儿，后四位是棋盘儿坐标儿
# 例：m0726，表示黑马儿从(0,7)走到(2,6)，即马2进3

def move_to_string(move):
    return ''.join([str(i) for i in move])

def move_to_list(move):
    return [move[0], int(move[1]), int(move[2]), int(move[3]), int(move[4])]

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
    if x1 == x2:
        cn3 = '平'
    elif (x1 > x2 and is_red) or (x1 < x2 and is_black):
        cn3 = '进'
    else:
        cn3 = '退'
    
    if y1 == y2:
        distance = abs(x2 - x1)
        cn4 = __cn_nums[distance] if is_red else str(distance)
    else:
        cn4 = __get_column_name(y2, is_red)

    # 前两位
    # 先看这一列有几个
    this_column_count = 0       # 这一列有几个
    this_piece_order = 1        # 这玩意是第几个
    for j in range(10):
        if board[j][y1] == move[0]:
            this_column_count += 1
            if (is_red and j < x1) or (is_black and j > x1):
                this_piece_order += 1

    if this_column_count == 1:
        cn1 = name
        cn2 = __get_column_name(y1, is_red)
    else:
        # 查表看它叫啥
        cn1 = __cn1_ls[this_column_count][this_piece_order]
        
        # cn2: 多于一个，要看是不是兵卒
        if name == '兵' or name == '卒':
            # 检查每一纵线有几个这玩意
            ill_columns = []        # 有至少两个的纵线
            for c in range(9):
                count = 0
                for r in range(10):
                    if board[r][c] == move[0]:
                        count += 1
                if count >= 2:
                    ill_columns.append(c)
            if len(ill_columns) == 2:
                # 特例：当兵卒在两个纵线都达到两个以上时，二7平6
                cn2 = __get_column_name(y1, is_red)
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
        next_board = [[0 for i in range(9)] for j in range(10)]
        for i in range(10):
            for j in range(9):
                next_board[i][j] = board[i][j]
    else:
        next_board = board

    next_board[move_ls[3]][move_ls[4]] = move_ls[0]
    next_board[move_ls[1]][move_ls[2]] = 'O'

    return next_board


# 如果是对称的，傻子库留空即可，这样php那边就不用管这茬儿
# 是否左右对称
def check_lr_sym(board):
    for i in range(10):
        for j in range(9):
            if board[i][j] != board[i][8-j]:
                return False
    return True

# 是否上下对称，即上下对应位置正好大小写互换
def check_ud_sym(board):
    for i in range(5):
        for j in range(9):
            if board[i][j] == 'O' and board[9-i][j] == 'O':
                continue  # 空白是可以的
            if board[i][j].swapcase() != board[9-i][j]:
                return False
    return True

# 是否上下左右对称，即镜像后是上下对称
def check_lrud_sym(board):
    for i in range(5):
        for j in range(9):
            if board[i][j] == 'O' and board[9-i][j] == 'O':
                continue  # 空白是可以的
            if board[i][j].swapcase() != board[9-i][8-j]:
                return False
    return True

# 左右翻面儿，包括着法和棋盘儿
def lr_reverse(board, move):
    rev_board = [[row[8-i] for i in range(9)] for row in board]
    # move是内部表示，所以很容易
    if move:
        rev_move = [move[0], move[1], 8-move[2], move[3], 8-move[4]]
    else:
        rev_move = None
    return rev_board, rev_move

# 上下翻面儿，注意红还是在下
def ud_reverse(board, move):
    rev_board = [[p.swapcase() if p != 'O' else p for p in board[9-i] ] for i in range(10)]
    if move:
        rev_move = [move[0].swapcase(), 9-move[1], move[2], 9-move[3], move[4]]
    else:
        rev_move = None
    return rev_board, rev_move

# 上下左右翻面儿
def lrud_reverse(board, move):
    return ud_reverse(*lr_reverse(board, move))


if __name__ == '__main__':
    
    # 测试board_to_string和board_to_list
    board_ls = get_standard_init()
    print(board_ls)
    print(board_to_string(board_ls))
    print(board_to_list(board_to_string(board_ls)))
    
    '''
    # 测试move_get_cn
    board_ls = get_standard_init()
    move_ls = [14, 7, 9, 6, 7]
    print(move_get_cn(move_ls, board_ls))
    '''


# 术语中英文对照 https://www.douban.com/group/topic/30094591/?_i=0459882i48gFTh