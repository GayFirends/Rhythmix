import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
import os

# --- 配置 ---
FILE_PATH = 'app.js'

class HomepageManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rhythmix 首页内容管理器")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        self.features_data = []
        self.news_data = []
        
        self.last_file_content = ""
        self.features_range = (-1, -1) # (start, end)
        self.news_range = (-1, -1)

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # 使用 Notebook (选项卡)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Tab 1: 特色 (Features) ---
        self.tab_features = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.tab_features, text="本站特色 (Features)")
        self.setup_features_tab()

        # --- Tab 2: 动态 (News) ---
        self.tab_news = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.tab_news, text="最新动态 (News)")
        self.setup_news_tab()

        # --- 底部保存区 ---
        bottom_bar = tk.Frame(self, bg="#ddd", height=50)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(bottom_bar, text="保存所有更改到 app.js", command=self.save_to_file, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, padx=20, pady=10)

    def setup_features_tab(self):
        # 布局：左列表，右编辑
        pane = tk.PanedWindow(self.tab_features, orient=tk.HORIZONTAL, bg="#f0f0f0")
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧列表
        left = tk.Frame(pane, bg="white", relief=tk.SUNKEN, bd=1)
        pane.add(left, width=250)

        self.feat_listbox = tk.Listbox(left, font=("Arial", 10), selectmode=tk.SINGLE)
        self.feat_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.feat_listbox.bind('<<ListboxSelect>>', self.on_feat_select)

        btn_frame = tk.Frame(left, bg="white")
        btn_frame.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="新建", command=self.add_feature, bg="#4CAF50", fg="white").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="删除", command=self.del_feature, bg="#f44336", fg="white").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 右侧编辑
        right = tk.Frame(pane, bg="#f0f0f0")
        pane.add(right)

        self.feat_entries = {}
        fields = [("图标 (Icon Class)", "icon"), ("标题 (Title)", "title")]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(right, text=label, bg="#f0f0f0", anchor="w").grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            entry = tk.Entry(right, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.feat_entries[key] = entry

        tk.Label(right, text="描述 (Description)", bg="#f0f0f0", anchor="w").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.feat_desc = tk.Text(right, height=5, width=40)
        self.feat_desc.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # 提示
        tk.Label(right, text="提示: 图标使用 FontAwesome 类名，如 'fas fa-bolt'", fg="#666", bg="#f0f0f0").grid(row=3, column=1, sticky="w", padx=5)

        self.current_feat_idx = None

    def setup_news_tab(self):
        pane = tk.PanedWindow(self.tab_news, orient=tk.HORIZONTAL, bg="#f0f0f0")
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧
        left = tk.Frame(pane, bg="white", relief=tk.SUNKEN, bd=1)
        pane.add(left, width=250)

        self.news_listbox = tk.Listbox(left, font=("Arial", 10), selectmode=tk.SINGLE)
        self.news_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.news_listbox.bind('<<ListboxSelect>>', self.on_news_select)

        btn_frame = tk.Frame(left, bg="white")
        btn_frame.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="新建", command=self.add_news, bg="#4CAF50", fg="white").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="删除", command=self.del_news, bg="#f44336", fg="white").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 右侧
        right = tk.Frame(pane, bg="#f0f0f0")
        pane.add(right)

        self.news_entries = {}
        fields = [("ID", "id"), ("标题 (Title)", "title"), ("日期 (Date)", "date")]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(right, text=label, bg="#f0f0f0", anchor="w").grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            entry = tk.Entry(right, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.news_entries[key] = entry

        tk.Label(right, text="摘要 (Summary)", bg="#f0f0f0", anchor="w").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.news_summary = tk.Text(right, height=5, width=40)
        self.news_summary.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.current_news_idx = None

    # --- 数据核心逻辑 ---
    def extract_array_from_ref(self, content, var_name):
        """
        查找 const var_name = ref([ ... ]); 结构，并提取 [ ... ] 部分
        返回: (json_obj, start_index, end_index)
        """
        # 1. 找到 const features = ref(
        # 使用简单的字符串拼接而不是 rf-string，避免换行问题
        # 匹配 "const var_name = ref"
        pattern = r'const\s+' + re.escape(var_name) + r'\s*=\s*ref\s*\('
        match = re.search(pattern, content)
        if not match:
            return None, -1, -1
        
        start_search = match.end()
        # 找到紧接着的 '['
        array_start = content.find('[', start_search)
        if array_start == -1:
            return None, -1, -1
        
        # 括号计数
        depth = 0
        in_string = False
        string_char = ''
        
        for i in range(array_start, len(content)):
            char = content[i]
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
                        return self.parse_loose_json(content[array_start:i+1]), array_start, i+1
        return None, -1, -1

    def parse_loose_json(self, js_str):
        """解析松散的 JS 对象字面量数组到 Python 对象"""
        # 1. 给 key 加引号
        js_str = re.sub(r'(\w+):', r'"\1":', js_str)
        # 2. 单引号转双引号
        js_str = js_str.replace("'", '"')
        # 3. 去掉末尾逗号
        js_str = re.sub(r',\s*]', ']', js_str)
        js_str = re.sub(r',\s*}', '}', js_str)
        try:
            return json.loads(js_str)
        except:
            return []

    def load_data(self):
        if not os.path.exists(FILE_PATH):
            messagebox.showerror("错误", f"文件未找到: {FILE_PATH}")
            return
        
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                self.last_file_content = f.read()

            # 提取 Features
            f_data, f_start, f_end = self.extract_array_from_ref(self.last_file_content, 'features')
            if f_data is not None:
                self.features_data = f_data
                self.features_range = (f_start, f_end)
            else:
                self.features_data = []
            
            # 提取 News
            n_data, n_start, n_end = self.extract_array_from_ref(self.last_file_content, 'news')
            if n_data is not None:
                self.news_data = n_data
                self.news_range = (n_start, n_end)
            else:
                self.news_data = []

            self.refresh_ui()
            
        except Exception as e:
            messagebox.showerror("读取错误", str(e))

    def refresh_ui(self):
        # 刷新 Features 列表
        self.feat_listbox.delete(0, tk.END)
        for item in self.features_data:
            self.feat_listbox.insert(tk.END, item.get('title', '无标题'))
        
        # 刷新 News 列表
        self.news_listbox.delete(0, tk.END)
        for item in self.news_data:
            self.news_listbox.insert(tk.END, item.get('title', '无标题'))

    # --- 事件处理: Features ---
    def on_feat_select(self, event):
        self.save_current_feat_edit() # 切换前保存当前编辑
        sel = self.feat_listbox.curselection()
        if not sel: return
        
        idx = sel[0]
        self.current_feat_idx = idx
        data = self.features_data[idx]
        
        self.feat_entries['icon'].delete(0, tk.END)
        self.feat_entries['icon'].insert(0, data.get('icon', ''))
        
        self.feat_entries['title'].delete(0, tk.END)
        self.feat_entries['title'].insert(0, data.get('title', ''))
        
        self.feat_desc.delete('1.0', tk.END)
        self.feat_desc.insert('1.0', data.get('description', ''))

    def save_current_feat_edit(self):
        if self.current_feat_idx is not None and self.current_feat_idx < len(self.features_data):
            item = self.features_data[self.current_feat_idx]
            item['icon'] = self.feat_entries['icon'].get()
            item['title'] = self.feat_entries['title'].get()
            item['description'] = self.feat_desc.get('1.0', tk.END).strip()

    def add_feature(self):
        self.features_data.append({
            "icon": "fas fa-star",
            "title": "新特色",
            "description": "描述..."
        })
        self.refresh_ui()
        self.feat_listbox.selection_set(tk.END)
        self.on_feat_select(None)

    def del_feature(self):
        sel = self.feat_listbox.curselection()
        if sel:
            del self.features_data[sel[0]]
            self.current_feat_idx = None
            self.refresh_ui()
            # 清空编辑区
            self.feat_entries['icon'].delete(0, tk.END)
            self.feat_entries['title'].delete(0, tk.END)
            self.feat_desc.delete('1.0', tk.END)

    # --- 事件处理: News ---
    def on_news_select(self, event):
        self.save_current_news_edit()
        sel = self.news_listbox.curselection()
        if not sel: return
        
        idx = sel[0]
        self.current_news_idx = idx
        data = self.news_data[idx]
        
        for key in ['id', 'title', 'date']:
            self.news_entries[key].delete(0, tk.END)
            self.news_entries[key].insert(0, str(data.get(key, '')))
            
        self.news_summary.delete('1.0', tk.END)
        self.news_summary.insert('1.0', data.get('summary', ''))

    def save_current_news_edit(self):
        if self.current_news_idx is not None and self.current_news_idx < len(self.news_data):
            item = self.news_data[self.current_news_idx]
            item['title'] = self.news_entries['title'].get()
            item['date'] = self.news_entries['date'].get()
            item['summary'] = self.news_summary.get('1.0', tk.END).strip()
            try:
                item['id'] = int(self.news_entries['id'].get())
            except:
                pass

    def add_news(self):
        self.news_data.append({
            "id": len(self.news_data) + 1,
            "title": "新动态",
            "summary": "内容...",
            "date": "2025年1月1日"
        })
        self.refresh_ui()
        self.news_listbox.selection_set(tk.END)
        self.on_news_select(None)

    def del_news(self):
        sel = self.news_listbox.curselection()
        if sel:
            del self.news_data[sel[0]]
            self.current_news_idx = None
            self.refresh_ui()
            for entry in self.news_entries.values(): entry.delete(0, tk.END)
            self.news_summary.delete('1.0', tk.END)

    # --- 保存 ---
    def list_to_js_string(self, data_list):
        """将列表转换为 JS 格式字符串"""
        NL = chr(10)
        js = "[" + NL
        for item in data_list:
            js += "            {"+ NL
            for k, v in item.items():
                if isinstance(v, int):
                    js += f"                {k}: {v}," + NL
                else:
                    # 安全转义：将 ' 替换为 \'\' 
                    safe_v = str(v).replace("'", "\'\'").replace(NL, "\\n")
                    js += f"                {k}: '{safe_v}'," + NL
            js += "            }," + NL
        js += "        ]"
        return js

    def save_to_file(self):
        self.save_current_feat_edit()
        self.save_current_news_edit()

        if self.features_range[0] == -1 or self.news_range[0] == -1:
            messagebox.showerror("错误", "无法定位原数据位置，无法保存。" )
            return

        try:
            # 构建新内容
            # 注意：如果先替换前面的内容，后面的索引会失效。
            # 所以我们应该先替换后面的内容 (news 通常在 features 后面，但最好通过索引判断)
            
            replacements = [
                (self.features_range, self.list_to_js_string(self.features_data)),
                (self.news_range, self.list_to_js_string(self.news_data))
            ]
            
            # 按起始位置倒序排序，这样替换后面的不会影响前面的索引
            replacements.sort(key=lambda x: x[0][0], reverse=True)
            
            new_content = self.last_file_content
            
            for (start, end), new_str in replacements:
                new_content = new_content[:start] + new_str + new_content[end:]
            
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            # 更新内存索引
            self.load_data() # 重新加载以更新索引
            messagebox.showinfo("成功", "app.js 已更新！")
            
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    app = HomepageManager()
    app.mainloop()