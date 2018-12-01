from PIL import Image, ImageGrab
from aip import *
import os, json
import win32clipboard as wc
import win32con

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
            return {'success': True, 'words': words}

def get_ocr_result(img):
    client = baidu_client_create()
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

def set_clip_board(text):
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardText(text)
    wc.CloseClipboard()
    return text

def do_ocr(img_path):
    if not img_path:
        print('get clipboard image failed!')
        return ''
    else:
        img = get_file_content(img_path)
        result = get_ocr_result(img)
        print(result)
        set_clip_board(result)
        print('已复制到剪切板！')
        return result

if __name__ == '__main__':
    img_path = get_clipboard_image()
    do_ocr(img_path)