import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
import os

# --- 配置 ---
FILE_PATH = 'games.js'

class GameManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rhythmix 游戏内容管理器")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        self.games = []
        self.current_game_index = None
        
        # 用于保存文件时定位替换位置
        self.last_js_content = ""
        self.array_start_idx = -1
        self.array_end_idx = -1

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # 主布局：左侧列表，右侧编辑器
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#f0f0f0")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 左侧：游戏列表 ---
        left_frame = tk.Frame(main_pane, bg="#ffffff", relief=tk.SUNKEN, bd=1)
        main_pane.add(left_frame, width=250)

        # 列表标题
        lbl_list = tk.Label(left_frame, text="游戏列表", font=("Arial", 12, "bold"), bg="#ffffff")
        lbl_list.pack(pady=5)

        # 列表框
        self.listbox = tk.Listbox(left_frame, font=("Arial", 11), selectmode=tk.SINGLE, bd=0, highlightthickness=0)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_game)

        # 列表按钮区
        btn_frame_list = tk.Frame(left_frame, bg="#ffffff")
        btn_frame_list.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Button(btn_frame_list, text="新建游戏", command=self.add_game, bg="#4CAF50", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_list, text="删除选中", command=self.delete_game, bg="#f44336", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- 右侧：编辑区 ---
        right_frame = tk.Frame(main_pane, bg="#f0f0f0")
        main_pane.add(right_frame)

        # 滚动区域
        canvas = tk.Canvas(right_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.edit_frame = tk.Frame(canvas, bg="#f0f0f0")

        self.edit_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.edit_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 表单控件
        self.entries = {}
        fields = [
            ("ID", "id"),
            ("游戏标题 (Title)", "title"),
            ("流派 (Genre)", "genre"),
            ("平台 (Platform - 'pc' or 'mobile')", "platform"),
            ("图片链接 (Image URL)", "imageUrl"),
        ]

        for idx, (label_text, key) in enumerate(fields):
            lbl = tk.Label(self.edit_frame, text=label_text, font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w")
            lbl.grid(row=idx, column=0, sticky="ew", padx=10, pady=(10, 2))
            
            entry = tk.Entry(self.edit_frame, font=("Arial", 10))
            entry.grid(row=idx, column=1, sticky="ew", padx=10, pady=0)
            self.entries[key] = entry

        # 描述 (多行)
        tk.Label(self.edit_frame, text="描述 (Description)", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w").grid(row=5, column=0, sticky="ew", padx=10, pady=(10, 2))
        self.txt_description = tk.Text(self.edit_frame, height=4, font=("Arial", 10))
        self.txt_description.grid(row=5, column=1, sticky="ew", padx=10, pady=0)

        # --- 下载链接管理 ---
        tk.Label(self.edit_frame, text="下载按钮管理", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w").grid(row=6, column=0, sticky="ew", padx=10, pady=(20, 2))
        
        self.downloads_frame = tk.Frame(self.edit_frame, bg="#e0e0e0", bd=1, relief=tk.SOLID)
        self.downloads_frame.grid(row=6, column=1, sticky="ew", padx=10, pady=0)
        
        self.download_entries = []

        tk.Button(self.edit_frame, text="+ 添加下载按钮", command=self.add_download_field).grid(row=7, column=1, sticky="w", padx=10, pady=5)


        # --- 底部保存区 ---
        bottom_bar = tk.Frame(self, bg="#ddd", height=50)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(bottom_bar, text="保存所有更改到 games.js", command=self.save_to_file, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, padx=20, pady=10)

        # 配置grid权重
        self.edit_frame.columnconfigure(1, weight=1)

    def extract_js_array(self, content):
        """使用括号计数法提取数组，支持嵌套"""
        start_marker = "const games ="
        start_idx = content.find(start_marker)
        if start_idx == -1: return None, -1, -1
        
        # 找到数组开始的 '['
        array_start = content.find("[", start_idx)
        if array_start == -1: return None, -1, -1
        
        depth = 0
        in_string = False
        string_char = ''
        
        for i in range(array_start, len(content)):
            char = content[i]
            
            # 简单的字符串跳过逻辑
            if in_string:
                if char == string_char and content[i-1] != '\\':
                    in_string = False
            else:
                if char in ['"', "'", '`']:
                    in_string = True
                    string_char = char
                elif char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0:
                        # 找到结束位置
                        return content[array_start:i+1], array_start, i+1
        return None, -1, -1

    def load_data(self):
        if not os.path.exists(FILE_PATH):
            messagebox.showerror("错误", f"找不到文件: {FILE_PATH}")
            return

        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.last_js_content = content
            
            # 提取 JS 数组字符串
            js_array_str, start, end = self.extract_js_array(content)
            
            if js_array_str:
                self.array_start_idx = start
                self.array_end_idx = end
                
                # 转换为标准 JSON
                # 1. 已知 Key 加引号 (避免匹配到 url 中的 http:)
                known_keys = ['id', 'title', 'genre', 'platform', 'imageUrl', 'description', 'downloads', 'name', 'url']
                for key in known_keys:
                    # 匹配 key: 形式，替换为 "key":
                    js_array_str = re.sub(rf'\b{key}\s*:', f'"{key}":', js_array_str)
                
                # 2. 单引号 -> 双引号
                js_array_str = js_array_str.replace("'", '"')
                
                # 3. 清理末尾逗号
                js_array_str = re.sub(r',\s*]', ']', js_array_str)
                js_array_str = re.sub(r',\s*}', '}', js_array_str)
                
                try:
                    self.games = json.loads(js_array_str)
                    self.refresh_list()
                    if self.games:
                        self.listbox.selection_set(0)
                        self.on_select_game(None)
                except json.JSONDecodeError as je:
                    messagebox.showerror("解析失败", f"JSON 转换失败: {je}")
            else:
                messagebox.showwarning("解析警告", "无法在 games.js 中正确提取 'const games' 数组。")
                self.games = []

        except Exception as e:
            messagebox.showerror("加载错误", f"读取失败:\n{str(e)}")

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            self.listbox.insert(tk.END, game.get('title', '未命名'))

    def on_select_game(self, event):
        # 保存当前正在编辑的数据到内存
        if self.current_game_index is not None and self.current_game_index < len(self.games):
            self.update_current_game_data()

        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.current_game_index = index
        game = self.games[index]

        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(game.get(key, "")))

        self.txt_description.delete("1.0", tk.END)
        self.txt_description.insert("1.0", game.get('description', ""))

        for widgets in self.download_entries:
            for w in widgets: w.destroy()
        self.download_entries.clear()

        downloads = game.get('downloads', [])
        for dl in downloads:
            self.create_download_row(dl.get('name', ''), dl.get('url', ''))

    def create_download_row(self, name_val, url_val):
        row_frame = tk.Frame(self.downloads_frame, bg="#e0e0e0")
        row_frame.pack(fill=tk.X, pady=2)

        tk.Label(row_frame, text="按钮名:", bg="#e0e0e0").pack(side=tk.LEFT)
        e_name = tk.Entry(row_frame, width=15)
        e_name.pack(side=tk.LEFT, padx=2)
        e_name.insert(0, name_val)

        tk.Label(row_frame, text="链接:", bg="#e0e0e0").pack(side=tk.LEFT)
        e_url = tk.Entry(row_frame, width=30)
        e_url.pack(side=tk.LEFT, padx=2)
        e_url.insert(0, url_val)

        btn_del = tk.Button(row_frame, text="X", bg="#ffcccc", command=lambda: self.remove_download_row(row_frame, (e_name, e_url, row_frame)))
        btn_del.pack(side=tk.LEFT, padx=5)

        self.download_entries.append((e_name, e_url, row_frame))

    def add_download_field(self):
        self.create_download_row("", "")

    def remove_download_row(self, frame, entry_tuple):
        frame.destroy()
        if entry_tuple in self.download_entries:
            self.download_entries.remove(entry_tuple)

    def update_current_game_data(self):
        if self.current_game_index is None:
            return

        game = self.games[self.current_game_index]
        
        for key, entry in self.entries.items():
            val = entry.get()
            if key == "id":
                try:
                    game[key] = int(val)
                except:
                    game[key] = val
            else:
                game[key] = val
        
        game['description'] = self.txt_description.get("1.0", tk.END).strip()

        new_downloads = []
        for e_name, e_url, _ in self.download_entries:
            name = e_name.get().strip()
            url = e_url.get().strip()
            if name:
                new_downloads.append({'name': name, 'url': url})
        
        game['downloads'] = new_downloads

    def add_game(self):
        new_game = {
            "id": len(self.games) + 1,
            "title": "新游戏",
            "genre": "类型",
            "platform": "pc",
            "imageUrl": "https://via.placeholder.com/300",
            "description": "新游戏描述",
            "downloads": []
        }
        self.games.append(new_game)
        self.refresh_list()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.listbox.see(tk.END)
        self.on_select_game(None)

    def delete_game(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        if messagebox.askyesno("确认", "确定要删除这个游戏吗？"):
            index = selection[0]
            del self.games[index]
            self.current_game_index = None
            self.refresh_list()
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.txt_description.delete("1.0", tk.END)
            for widgets in self.download_entries:
                for w in widgets: w.destroy()
            self.download_entries.clear()

    def save_to_file(self):
        self.update_current_game_data()
        
        if self.array_start_idx == -1 or self.array_end_idx == -1:
             messagebox.showerror("错误", "无法定位原文件中的数组位置，无法保存。请重新启动程序。 ")
             return

        try:
            # 换行符
            NL = chr(10)
            
            js_array_str = "[" + NL
            for game in self.games:
                js_array_str += "        {"
                for key, val in game.items():
                    if key == 'downloads':
                        dl_str = "["
                        if val:
                            dl_list = [f"{{ name: '{d['name'].replace(chr(39), chr(92)+chr(39))}', url: '{d['url'].replace(chr(39), chr(92)+chr(39))}' }}" for d in val]
                            dl_str += ", ".join(dl_list)
                        dl_str += "]"
                        js_array_str += f"            {key}: {dl_str}," + NL
                    elif isinstance(val, int):
                        js_array_str += f"            {key}: {val}," + NL
                    else:
                        # 安全转义：将 ' 替换为 \'
                        # chr(39) = '
                        # chr(92) = \
                        safe_val = str(val).replace(chr(39), chr(92)+chr(39)).replace(NL, "\\n")
                        js_array_str += f"            {key}: '{safe_val}'," + NL
                js_array_str += "        }," + NL
            js_array_str += "    ]"

            # 拼接新文件内容：头部 + 新数组 + 尾部
            new_full_content = self.last_js_content[:self.array_start_idx] + js_array_str + self.last_js_content[self.array_end_idx:]

            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(new_full_content)
            
            # 更新内存中的记录，以便再次保存
            self.last_js_content = new_full_content
            # 更新 array_end_idx
            self.array_end_idx = self.array_start_idx + len(js_array_str)
            
            messagebox.showinfo("成功", "games.js 已成功更新！\n请刷新网页查看效果。 ")

        except Exception as e:
            messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    app = GameManager()
    app.mainloop()
