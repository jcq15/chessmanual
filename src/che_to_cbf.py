import chess as che
from analyze_chess_file import parse_che, Position
import os
import traceback

def che_move_to_cbf_move(move: str):
    move_ls = che.move_to_list(move)
    return f'{move_ls[2]}{move_ls[1]}-{move_ls[4]}{move_ls[3]}'

def che_to_cbf_single(file_path: str, out_path: str):
    # 读取棋谱
    pos_list = parse_che(file_path)

    move_list = ['00-00']
    for pos in pos_list:
        move_list.append(che_move_to_cbf_move(pos.NextMove))

    file_str = '''<?xml version="1.0" encoding="UTF-8"?>
                    <ChineseChessRecord Version="1.0">
                    <Head>
                    </Head>
                    <MoveList>
                '''
    for i in range(len(move_list)):
        if i == len(move_list) - 1:
            # 是最后一个
            file_str += f'<Move value="{move_list[i]}" end="1"/>\n'
        else:
            file_str += f'<Move value="{move_list[i]}"/>\n'
    file_str += '''
                </MoveList>
                </ChineseChessRecord>
                '''    

    # 准备名字
    _, tail = os.path.split(file_path)
    # file_str写入文件
    with open(os.path.join(out_path, f'{tail}.cbf'), 'w') as f:
        f.write(file_str)

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
    file_path = r'data\autofupan\2022-08-13_00-11-31_(170725434_1)_qqxqEX.che'
    che_to_cbf(file_path, '.')
