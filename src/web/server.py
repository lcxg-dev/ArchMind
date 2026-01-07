from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import sys
import os
import logging
import tempfile
import zipfile
import shutil
from werkzeug.utils import secure_filename
import time
import threading
import json  # 添加json模块导入

# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.api_client.deepseek_client import DeepSeekAPIClient
from src.converter.general_converter import GeneralConverter
from src.converter.c_converter import CConverter
from src.converter.python_converter import PythonConverter
from config.api_config import APIConfig

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化 API 客户端
api_client = DeepSeekAPIClient(
    api_key=APIConfig.DEEPSEEK_API_KEY,
    api_base=APIConfig.DEEPSEEK_API_BASE,
    model=APIConfig.DEEPSEEK_MODEL
)

# 初始化转换器
converter_map = {
    'c': CConverter(api_client),
    'python': PythonConverter(api_client),
    # 默认使用通用转换器
    'default': GeneralConverter(api_client)
}

# 根据语言获取合适的转换器
def get_converter(lang: str) -> GeneralConverter:
    return converter_map.get(lang, converter_map['default'])

# 用于存储转换进度的字典
progress_dict = {}

# 支持的代码文件扩展名
supported_extensions = {
    'c': ['.c', '.h'],
    'python': ['.py'],
    'java': ['.java'],
    'js': ['.js', '.jsx']
}

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/project-convert')
def project_convert():
    """项目代码转换页面"""
    return render_template('project_convert.html')

@app.route('/api/convert', methods=['POST'])
def convert_code():
    """代码转换 API"""
    try:
        data = request.get_json()
        source_lang = data.get('source_lang')
        target_lang = data.get('target_lang')
        code = data.get('code')
        
        if not all([source_lang, target_lang, code]):
            return jsonify({'error': '缺少必要参数'}), 400
            
        # 获取适合的转换器
        converter = get_converter(source_lang)
        
        # 调用转换器进行代码转换
        result = converter.convert(source_lang, target_lang, code)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f'转换失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/convert-project', methods=['POST'])
def convert_project():
    """项目代码转换 API"""
    try:
        logger.info('收到转换请求！')
        logger.info(f'请求表单数据: {request.form}')
        logger.info(f'请求文件数据: {request.files}')
        
        source_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        upload_type = request.form.get('type')  # 获取上传类型：'folder' 或 'zip'
        is_folder = upload_type == 'folder'  # 判断是否是文件夹上传
        
        logger.info(f'转换参数: source_lang={source_lang}, target_lang={target_lang}, upload_type={upload_type}, is_folder={is_folder}')
        
        if not source_lang or not target_lang:
            logger.error('缺少必要参数')
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 创建持久的临时目录
        temp_dir = tempfile.mkdtemp(prefix='project_convert_')
        
        # 生成唯一的进度ID
        progress_id = os.path.basename(temp_dir)
        progress_dict[progress_id] = {'current': 0, 'total': 0, 'current_file': '', 'status': 'preparing'}
        
        try:
            extract_dir = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            if upload_type == 'folder':
                # 处理文件夹上传
                logger.info('处理文件夹上传')
                
                if 'folder_files' not in request.files:
                    logger.error('未找到folder_files字段')
                    return jsonify({'success': False, 'error': '未找到上传文件'}), 400
                
                files = request.files.getlist('folder_files')
                
                if not files:
                    logger.error('没有收到任何文件夹文件')
                    return jsonify({'success': False, 'error': '没有收到任何文件夹文件'})
                
                # 保存所有上传的文件到extract_dir
                for file in files:
                    if file.filename == '':
                        continue
                    
                    logger.info(f'收到文件: {file.filename}')
                    
                    # 使用file.filename获取文件的原始名称
                    original_filename = file.filename
                    # 构建相对路径
                    relative_path = original_filename
                    file_path = os.path.join(extract_dir, relative_path)
                    logger.info(f'保存文件: {relative_path} 到 {file_path}')
                    # 创建父目录
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    # 保存文件
                    file.save(file_path)
            
            elif upload_type == 'zip':
                # ZIP文件上传处理
                logger.info('处理ZIP文件上传')
                
                if 'folder_files' not in request.files:
                    logger.error('未找到folder_files字段')
                    return jsonify({'success': False, 'error': '未找到上传文件'}), 400
                
                files = request.files.getlist('folder_files')
                
                if not files:
                    logger.error('没有收到任何ZIP文件')
                    return jsonify({'success': False, 'error': '没有收到任何ZIP文件'})
                
                for file in files:
                    if file.filename == '':
                        continue
                    
                    if not file.filename.endswith('.zip'):
                        logger.error(f'文件 {file.filename} 不是有效的ZIP文件')
                        continue
                    
                    # 保存ZIP文件
                    zip_path = os.path.join(temp_dir, file.filename)
                    logger.info(f'保存ZIP文件: {file.filename} 到 {zip_path}')
                    file.save(zip_path)
                    
                    # 解压缩ZIP文件到extract_dir
                    logger.info(f'解压缩ZIP文件到: {extract_dir}')
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                        
                    # 记录解压缩后的目录结构
                    logger.info(f'解压缩后extract_dir内容: {os.listdir(extract_dir)}')
                    for root, dirs, files in os.walk(extract_dir):
                        for name in files:
                            logger.info(f'  - {os.path.join(root, name)}')
            
            # 查找所有需要转换的文件
            all_files = []
            logger.info(f'开始查找需要转换的文件，extract_dir={extract_dir}')
            logger.info(f'支持的扩展名: {supported_extensions.get(source_lang, [])}')
            
            # 检查extract_dir是否存在
            if not os.path.exists(extract_dir):
                logger.error(f'extract_dir不存在: {extract_dir}')
            else:
                # 先列出extract_dir目录下的所有文件
                try:
                    dir_contents = os.listdir(extract_dir)
                    logger.info(f'extract_dir目录内容: {dir_contents}')
                except Exception as e:
                    logger.error(f'无法读取extract_dir目录: {e}')
            
            # 遍历目录查找需要转换的文件
            try:
                for root, _, files in os.walk(extract_dir):
                    logger.info(f'遍历目录: {root}, 文件列表: {files}')
                    for file_name in files:
                        # 检查文件扩展名
                        file_ext = os.path.splitext(file_name)[1].lower()
                        logger.info(f'检查文件: {file_name}, 扩展名: {file_ext}')
                        if file_ext in supported_extensions.get(source_lang, []):
                            file_path = os.path.join(root, file_name)
                            all_files.append(file_path)
                            logger.info(f'添加文件到转换列表: {file_path}')
            except Exception as e:
                logger.error(f'遍历目录时出错: {e}')
                import traceback
                traceback.print_exc()
            
            logger.info(f'找到需要转换的文件: {all_files}')
            # 更新总文件数
            progress_dict[progress_id]['total'] = len(all_files)
            progress_dict[progress_id]['status'] = 'converting'
            
            # 转换代码文件
            converted_files = []
            
            for index, file_path in enumerate(all_files):
                file_name = os.path.basename(file_path)
                
                # 更新当前转换文件
                progress_dict[progress_id]['current_file'] = file_name
                progress_dict[progress_id]['current_file_status'] = 'converting'
                progress_dict[progress_id]['current'] = index + 1
                
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # 转换代码
                    # 获取适合的转换器
                    file_converter = get_converter(source_lang)
                    converted_code = file_converter.convert(source_lang, target_lang, code)
                    
                    # 获取目标文件扩展名
                    target_ext = supported_extensions.get(target_lang, [''])[0]
                    
                    # 重命名文件
                    target_file_name = os.path.splitext(file_name)[0] + target_ext
                    target_file_path = os.path.join(os.path.dirname(file_path), target_file_name)
                    
                    # 写入转换后的代码
                    with open(target_file_path, 'w', encoding='utf-8') as f:
                        f.write(converted_code)
                    
                    # 如果扩展名不同，删除原文件
                    if os.path.splitext(file_name)[1].lower() != target_ext:
                        os.remove(file_path)
                    
                    # 更新进度，添加更详细的信息
                    progress_dict[progress_id]['current_file_status'] = 'completed'
                    
                    # 记录转换后的文件
                    relative_path = os.path.relpath(target_file_path, extract_dir)
                    converted_files.append(relative_path)
                    
                except Exception as e:
                    # 记录转换错误
                    progress_dict[progress_id]['error'] = str(e)
                    progress_dict[progress_id]['status'] = 'error'
                    # 清理临时目录
                    shutil.rmtree(extract_dir, ignore_errors=True)
                    return jsonify({'success': False, 'error': f'转换文件 {file_name} 时出错: {str(e)}'})
            
            # 压缩转换后的文件
            result_zip_path = os.path.join(temp_dir, 'converted_project.zip')
            
            with zipfile.ZipFile(result_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, _, files in os.walk(extract_dir):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        arcname = os.path.relpath(file_path, extract_dir)
                        zip_ref.write(file_path, arcname)
            
            # 更新进度为完成
            progress_dict[progress_id]['status'] = 'completed'
            
            # 返回转换结果
            return jsonify({
                'success': True,
                'files': converted_files,
                'download_url': f'/download/{os.path.basename(result_zip_path)}?temp_dir={temp_dir}',
                'progress_id': progress_id
            })
            
        except Exception as e:
            # 更新进度为错误
            if progress_id in progress_dict:
                progress_dict[progress_id]['status'] = 'error'
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
            
    except Exception as e:
        logger.error(f'项目转换失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/progress/<progress_id>')
def progress_stream(progress_id):
    """进度流 SSE 端点"""
    def generate():
        while True:
            if progress_id not in progress_dict:
                yield f'data: {{"error": "进度ID不存在"}}\n\n'
                break
            
            progress = progress_dict[progress_id]
            
            # 发送进度信息
            yield f'data: {json.dumps(progress)}\n\n'
            
            # 如果转换完成或出错，停止流
            if progress['status'] in ['completed', 'error']:
                # 从进度字典中移除
                time.sleep(1)  # 给客户端足够的时间接收完成消息
                if progress_id in progress_dict:
                    del progress_dict[progress_id]
                break
            
            time.sleep(0.5)  # 每500毫秒发送一次更新
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<filename>')
def download_file(filename):
    """下载转换后的项目文件"""
    try:
        temp_dir = request.args.get('temp_dir')
        if not temp_dir or not os.path.exists(temp_dir):
            return jsonify({'error': '文件不存在或已过期'}), 404
        
        # 发送文件
        response = send_from_directory(temp_dir, filename, as_attachment=True)
        
        # 发送文件后清理临时目录
        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f'清理临时目录失败: {str(e)}')
        
        return response
        
    except Exception as e:
        logger.error(f'下载文件失败: {str(e)}')
        # 尝试清理临时目录
        try:
            temp_dir = request.args.get('temp_dir')
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        return jsonify({'error': '下载失败'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)