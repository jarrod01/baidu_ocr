from PIL import Image, ImageGrab
from aip import *
import os, json
import win32clipboard as wc
import win32con

def get_settings():
    try:
        with open('settings.json', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except:
        return {}

# 获取剪切板图片
def get_clipboard_image():
    file_path = os.path.join(os.path.abspath('.'), 'grabed_img.png')
    img = ImageGrab.grabclipboard()
    if isinstance(img, Image.Image):
        img.save(file_path)
        return file_path
    else:
        return ''

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def baidu_client_create():
    user_path = os.path.expanduser("~")
    api_key_file = os.path.join(user_path, 'api_key.json')
    try:
        with open(api_key_file, encoding='utf-8') as f:
            api_key = json.load(f)
            APP_ID = api_key['BAIDU_APP_ID']
            API_KEY = api_key['BAIDU_API_KEY']
            SECRET_KEY = api_key['BAIDU_SECRET_KEY']
            ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
            # sr_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
            return ocr_client
    except FileNotFoundError:
        print('api_key_file not found!')
        return None

# 对结果进行解析，并把返回的文字列表整合成一个大字符串，如果遇到错误，把错误传递出去
def process_result(result):
    if result:
        if 'error_code' in result.keys():
            print('baidu_ocr failed, reason:')
            print(result['error_msg'])
            return {'success': False, 'error_code': int(result['error_code']), 'error_msg': result['error_msg']}  #返回错误码
        else:
            words_result = result['words_result']
            words = ''
            for wr in words_result:
                words += wr['words']
                words += '\n'
            # words = replace_eng_to_chs(words)
            return {'success': True, 'words': words}

# 将英文的标点符号批量替换为中文
def replace_eng_to_chs(text):
    to_be_replaced = {',': '，', ':': '：', ';': '；', '?': '？', '(': '（', ')': '）'}
    for key in to_be_replaced:
        text = text.replace(key, to_be_replaced[key])
        # print(key + '已被替换')
    return text

def replace_huanhang(text):
    text = text.replace('\n', '')
    return text

def get_ocr_result(img, client):
    # client = baidu_client_create()
    if not client:
        print('create client failed!')
        return ""
    result = process_result(client.basicAccurate(img))
    # 如果高精度OCR接口日调用次数500次用完了，换普通接口
    if not result['success']:
        if result['error_code'] == 17:
            result = process_result(client.basicGeneral(img))
            #如果再不行，放弃
            if not result['success']:
                return result['error_msg']
            else:
                return result['words']  #普通接口返回成功后
        else:  #其他错误先不管了
            return result['error_msg']
    else:
        return result['words']

# 把识别到的文字复制到剪切板
def set_clip_board(text):
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardText(text)
    wc.CloseClipboard()
    return text

# 主函数
def do_ocr(img_path, client):
    if not img_path:
        print('get clipboard image failed!')
        return ''
    else:
        img = get_file_content(img_path)
        result = get_ocr_result(img, client)
        result = replace_eng_to_chs(result)
        # 设置是否自动替换标点符号
        # if settings:
        #     try:
        #         if settings["replace_eng_to_chs"]:
        #             result = replace_eng_to_chs(result)
        #     except KeyError:
        #         print('没有设置是否替换标点符号')
        print(result)
        set_clip_board(result)
        print('已复制到剪切板！')
        return result

if __name__ == '__main__':
    client = baidu_client_create()
    settings = get_settings()
    img_path = get_clipboard_image()
    do_ocr(img_path, client)