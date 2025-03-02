# 网页版日语句子解析工具

## 关键词

中文 汉语 日文 学习 分析

## 用途

1. 解析一个句子
2. 翻译句子
3. 搜索单词含义
4. 辅助背单词
5. 拆分一个句子**注：分词服务暂不可用**

## 食用方法

1. 克隆仓库`git clone https://github.com/ZzzzzzzSkyward/LearnJapaneseSentence.git`
2. 进入仓库`cd LearnJapaneseSentence`
3. 安装python依赖
   1. 普通依赖`pip install -r requirements.txt`
   2. 如果有cuda，则再安装`requirements_gpu.txt`
   3. 在安装`python-lzo`时可能报错，此时先下载Visual Studio，然后去lzo官网下载源代码，编译完成后将某个文件夹塞到环境变量里。具体自行摸索
4. 打开config.py，输入百度翻译token、DeepSeek token、SERP token。
5. 启动后端服务器`python server.py`
6. 进入前端`cd front`
7. 安装前端依赖`npm i`
8. 启动前端服务器`npm run serve`
9. 在浏览器里打开网址`http://localhost:8080`

## 框架

### 前端

vue3+element-plus

### 后端

flask

翻译：百度

大语言模型：DeepSeek

搜索：SERP（Google）

词典：本地词典+weblio+jisho

分词：ginza。**注：分词服务暂不可用**

## 预览

![preview](Z:\LearnJapaneseSentence\preview.png)