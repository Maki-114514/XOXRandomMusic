# 晒你纪偶研摊位二偶猜歌小游戏

🎵 这是一个为西电晒你纪偶研摊位设计的猜歌小游戏，基于Python 3.10+和PyQt5开发。玩家需要从播放的歌曲片段中猜出正确的歌曲名称，挑战自己的二偶厨力 or 抽查好厚米的成分！([现场盛况](https://www.bilibili.com/video/BV1VJj5z9ESN?p=3))



## 功能特点

- 🎮 完整游戏流程：歌单选择 → 难度选择 → 答题 → 结果显示
- 📁 灵活的歌单管理系统：支持多IP分类和子目录管理，歌单可混杂多选
- 🎚️ 三种难度模式：
  - 简单：只使用简单歌单（easy）
  - 普通：混合简单和困难歌单（easy + hard）
  - 困难：只使用困难歌单（hard）
- 🎧 实时音频播放功能
- 📊 分数系统：不同难度对应不同得分（简单1分，普通1.2分，困难1.5分）
- 🔁 游戏结束后可选择重新开始或退出

## 文件说明

| 文件名                 | 描述                                         |
| ---------------------- | -------------------------------------------- |
| `game.py` & `game.pyw` | 主游戏程序                                   |
| `tools\clean.py`       | 清理文本中书名号的工具                       |
| `tools\clear_name.py`  | 批量重命名文件的工具（移除文件名前17个字符） |
| `tools\flac2mp3.py`    | 将FLAC转换为MP3的工具（节省存储空间）        |
| `tools\music_test.py`  | 音乐播放测试脚本                             |
| `music`                | 待播放音乐MP3歌单文件夹(度盘下载)            |

## 运行环境要求

- Python 3.10+
- PyQt5
- PyQt5多媒体组件（用于音频播放）
- 可选：pydub（用于FLAC转换工具）

## 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/sunige-song-guessing-game.git
cd sunige-song-guessing-game
```

2. 创建虚拟环境（可选）：

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

3. 安装依赖：

```bash
pip install PyQt5 PyQt5-Qt5 PyQt5-sip
```

4. 运行游戏：

```bash
python game.py
```

## 游戏使用说明

1. **选择歌单**：
   - 在歌单选择界面，勾选你想要挑战的歌单
   - 支持多级目录选择（IP分类 → 子目录）
   - 点击"开始挑战"按钮进入下一步

2. **选择难度**：
   - 简单：只使用简单歌单
   - 普通：混合简单和困难歌单
   - 困难：只使用困难歌单

3. **开始答题**：
   - 游戏会自动播放歌曲片段
   - 从四个选项中选择你认为正确的歌曲名称
   - 点击"确认"提交答案

4. **查看结果**：
   - 完成5道题目后显示最终得分
   - 可选择"重新答题"或"关闭窗口"

## 工具脚本使用

### 清理文本中的书名号

```bash
python clean.py input.txt [output.txt]
```

### 批量重命名文件（移除前17个字符）

```bash
python clear_name.py target_dir [-r] [-d]
```

### FLAC转MP3（节省存储空间）

```bash
python flac2mp3.py target_dir [-o output_dir] [-b bitrate] [-r] [-d] [-t threads]
```

## 歌曲资源

晒你纪上使用的歌曲将稍后上传到网盘，下载后请放在`music/`目录下，按以下结构组织：

```
music/
├── IP名称1/
│   ├── 歌单1/
│   │   ├── easy/
│   │   └── hard/
│   └── 歌单2/
│       ├── easy/
│       └── hard/
└── IP名称2/
    └── 歌单1/
        ├── easy/
        └── hard/
```

## 贡献指南

欢迎提交Issue和Pull Request！

---

🎉 祝你在西电晒你纪玩得开心！记得来偶研摊位挑战一下你的音乐知识哦！（[nsy写真](https://pan.baidu.com/s/16JqrUhif_tIqg5qSf8GIYA?pwd=vwcu)）
