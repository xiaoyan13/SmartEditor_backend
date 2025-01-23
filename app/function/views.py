import os
from time import sleep
import base64
import requests
from flask import jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..utils.erniebot import erniebot
from . import function
from ..prompt.models import Prompt

@function.route('/ocr', methods=['POST'])
def ocr():
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return jsonify({'message': '无文件上传!', 'code': 400})
    file = request.files['file']
    # 如果用户没有选择文件，浏览器也会提交一个空的文件部分，所以需要检查文件是否存在
    if file.filename == '':
        return jsonify({'message': '无文件上传!', 'code': 400})
    # 二进制读取文件内容
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode('ascii')
    # 设置鉴权信息
    headers = {
        "Authorization": f"token {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }
    # 设置请求体
    payload = {
        "image": image_base64  # Base64编码的文件内容或者文件链接
    }
    try:
        resp = requests.post(url=os.getenv('OCR_API_URL'), json=payload, headers=headers)
        resp.raise_for_status()  # 将引发异常，如果状态码不是 200-399
        ocr_result = resp.json()["result"]
        result = ''
        for text in ocr_result["texts"]:
            result += text["text"]
            result += '\n'
        return jsonify({'message': result, 'code': 200})
    except Exception as e:
        print(f"处理响应时发生错误: {e}")
        return jsonify({'message': '后端小模型OCR服务未启动！', 'code': 400})


@function.route('/asr', methods=['POST'])
def asr():
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return jsonify({'message': '无文件上传!', 'code': 400})

    file = request.files['file']

    # 如果用户没有选择文件，浏览器也会提交一个空的文件部分，所以需要检查文件是否存在
    if file.filename == '':
        return jsonify({'message': '无文件上传!', 'code': 400})

    # TODO：调用后端小模型ASR服务
    sleep(1.33)
    return jsonify({'message': '后端小模型ASR服务未启动！', 'code': 400})

    # Demo：返回固定文本
    # return jsonify({'message': '早上八点我从北京到广州花了四百二十六元', 'code': 200})


@function.route('/AIFunc', methods=['POST'])
@jwt_required()
def AIFunc():
    data = request.get_json()
    command = data['command']
    text = data['text']
    
    user_id = get_jwt_identity()
    prompts = Prompt.query.filter_by(user_id=user_id).all()
    
    prompt = next((p["content"].format(text=text) for p in prompts if p["title"] == command), "")

    def generate():
        response = erniebot.ChatCompletion.create(model="ernie-4.0",
                                                  messages=[{"role": "user", "content": prompt}],
                                                  stream=True)
        for chunk in response:
            result = chunk.get_result()
            yield f"{result}"

    return Response(generate(), content_type='text/event-stream')


@function.route('/typography', methods=['POST'])
# @jwt_required()
def typography():
    data = request.get_json()
    text = data['text']
    title = data['title']
    font = data['font']
    font_size = data['font_size']
    line_spacing = data['line_spacing']
    paragraph = data['paragraph']
    prompt = (
        f"这是一份文档的HTML文本内容。\n"
        f"{text}\n"
        f"请将上述HTML内容重新排版为{title}的格式。要求如下：\n"
        f"- 字体：{font}\n"
        f"- 字号：{font_size}\n"
        f"- 行距：{line_spacing}\n"
        f"- 段落：{paragraph}\n"
        f"只需要返回生成后的HTML文本，不需要返回其他内容。"
    )

    def generate():
        response = erniebot.ChatCompletion.create(model="ernie-4.0",
                                                  messages=[{"role": "user", "content": prompt}],
                                                  stream=True)
        for chunk in response:
            result = chunk.get_result()
            yield f"{result}"

    return Response(generate(), content_type='text/event-stream')
