# LangConverter - 代码语言转换工具

LangConverter 是一个基于 DeepSeek API 的代码语言转换工具，可以帮助开发者快速将代码从一种编程语言转换为另一种编程语言。

## 功能特性

- 支持多种编程语言之间的转换
- 基于 DeepSeek 大语言模型，转换质量高
- 提供直观的 Web 界面
- 支持实时代码转换

## 技术栈

- **后端框架**: Flask
- **API 客户端**: DeepSeek API
- **前端技术**: HTML, CSS, JavaScript
- **代码高亮**: Pygments

## 安装和配置

### 1. 克隆项目

```bash
git clone https://github.com/lcxg-dev/ArchMind
cd lang-converter
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后填写 DeepSeek API 密钥：

```bash
cp .env.example .env
```

在 `.env` 文件中设置你的 DeepSeek API 密钥：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4. 运行项目

```bash
python src/web/server.py
```

项目将在 `http://127.0.0.1:5000` 上运行。

## 使用说明

1. 打开浏览器访问 `http://127.0.0.1:5000`
2. 在左侧选择源代码语言
3. 在右侧选择目标代码语言
4. 在左侧编辑器中输入要转换的代码
5. 点击 "转换" 按钮
6. 转换后的代码将显示在右侧编辑器中

## 支持的编程语言

理论上支持所有主流编程语言，包括但不限于：

- Python
- JavaScript
- Java
- C++
- C#
- Go
- Ruby
- PHP
- Swift
- Kotlin

## 注意事项

1. 请确保你已经获取了 DeepSeek API 密钥
2. 转换质量取决于代码的复杂性和语言之间的差异
3. 建议对转换后的代码进行人工检查和调整

## 许可证

[MIT License](LICENSE)