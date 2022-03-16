from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils import *
from linking import process as linking_proc

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += '.'.join(error.get('loc')) + ':' + error.get('msg') + ';'
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=message
    )


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
        json.dump(res.result, f, ensure_ascii=False)


# 图片转文字
@app.post('/'.join([prefix, 'parser', 'ocr']))
async def ocr(img_content: ocr_img):
    return convert(img_content)


@app.post('/'.join([prefix, 'parser', 'linking']))
async def linking(req: linking_req):
    return {
        'data': linking_proc(req.text, req.subject)
    }


if __name__ == '__main__':
    import uvicorn
    load_cfg()
    uvicorn.run('main:app', host='127.0.0.1', port=8002)
