<h1>基于多模态大模型的校园返校时段车辆违停感知与优化研究 Web UI</h1>

## 运行方法

1. 克隆本项目源码到本地
```
git clone https://github.com/yorkyang2333/illegal-parking-detection-webui
cd ./illegal-parking-detection-webui/
```
或者使用右上角的`Code` -> `Download ZIP`下载压缩包后解压。

2. 从`requirements.txt`中安装必要库
```
pip install -r requirements.txt
```

3. 在项目文件夹下，新建`.env`文件，写入自己的`Dashscope API Key`，格式如下：
```
DASHSCOPE_API_KEY=[your_api_key_here]
```
如还没有API Key，可前往[阿里云灵积官网](https://dashscope.aliyun.com)注册并生成。

4. 启动服务器
```
python app.py
```

5. 在浏览器中，输入`127.0.0.1:8080`，访问`Web UI`。
