import tkinter as tk
from tkinter.filedialog import (askopenfilename, 
                                askopenfilenames, 
                                askdirectory, 
                                asksaveasfilename)
from che_to_cbf import che_to_cbf

global_data = {}


top = tk.Tk()
# 进入消息循环

def choose_file():
    filenames = askopenfilenames()
    if len(filenames) > 0:
        str = f'您选择了{len(filenames)}个文件儿，他们是：\n'
        rows = 0
        for file in filenames:
            str += file + '\n'
            rows += 1
            if rows > 20:
                str += '...'
                break    # 最多显示20个文件
        lb.config(text = str)
    global_data['filenames'] = filenames

def choose_out_path():
    path = askdirectory()
    if len(path) > 0:
        lb2.config(text = f'您选择了输出目录：{path}')
    global_data['out_path'] = path

def convert():
    fail_list = che_to_cbf(global_data['filenames'], global_data['out_path'])
    total = len(global_data['filenames'])
    success = total - len(fail_list)
    text = f'转换完成，共{total}个文件，成功{success}个，失败{len(fail_list)}个'
    if len(fail_list) > 0:
        text += '，他们是：\n'
        for file in fail_list:
            text += file + '\n'
    lb3.config(text = text)


lb = tk.Label(top, text='')
lb.pack()
btn = tk.Button(top, text='打开文件', command=choose_file)
btn.pack()

lb2 = tk.Label(top, text='')
lb2.pack()
btn2 = tk.Button(top, text='选择输出目录', command=choose_out_path)
btn2.pack()

lb3 = tk.Label(top, text='')
lb3.pack()
btn3 = tk.Button(top, text='开始转换', command=convert)
btn3.pack()

top.mainloop()