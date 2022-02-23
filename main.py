from fastapi import FastAPI
from utils import *

app = FastAPI()

prefix = ''


# 获取试卷列表
@app.get('/'.join([prefix, 'parser', 'get_exam_list']))
async def get_exam_list():
    return scan_files()


# 获取某张试卷的题目列表
@app.get('/'.join([prefix, 'parser', 'get_question_list', '{exam_id}']))
async def get_question_list(exam_id):
    return list_questions(exam_id)


# 获取一道题目
@app.get('/'.join([prefix, 'parser', 'get_question', '{exam_id}', '{question_id}']))
async def get_question(exam_id, question_id):
    return get_single_question(exam_id, question_id)


# 保存结果
@app.post('/'.join([prefix, 'parser', 'save']))
async def save(res: result):
    year = res.exam_id.split('_')[0]
    with open(
        '/'.join([json_root_path, year + 'GaoKao', res.exam_id, res.question_id + '.json']),
        'w'
    ) as f:
        f.write(res.result)


# 图片转文字
@app.post('/'.join([prefix, 'parser', 'ocr']))
async def ocr(img_content: ocr_img):
    pass


if __name__ == '__main__':
    import uvicorn
    load_cfg()
    uvicorn.run('main:app', host='0.0.0.0', port=8888)