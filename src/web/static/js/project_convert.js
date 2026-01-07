// 确保DOM完全加载后再执行JavaScript代码
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const projectFile = document.getElementById('project-file');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const changeFile = document.getElementById('change-file');
    const sourceLangSelect = document.getElementById('source-lang');
    const targetLangSelect = document.getElementById('target-lang');
    const convertBtn = document.getElementById('convert-btn');
    const clearBtn = document.getElementById('clear-btn');
    const downloadBtn = document.getElementById('download-btn');
    const loading = document.getElementById('loading');
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const fileList = document.getElementById('file-list');
    const convertedFiles = document.getElementById('converted-files');
    const status = document.getElementById('status');
    // 新增元素
    const uploadContent = document.getElementById('upload-content');
    const contentList = document.getElementById('content-list');
    const currentFile = document.getElementById('current-file');
    const currentFileName = document.getElementById('current-file-name');

    let selectedFile = null;
    let conversionResult = null;
    let eventSource = null;

    // 文件选择处理
    projectFile.addEventListener('change', function(e) {
        handleFileSelect(e); // 直接传递事件对象
    });

    // 点击上传区域触发文件选择
    uploadPlaceholder.addEventListener('click', function() {
        projectFile.click();
    });

    // 更换文件按钮
    changeFile.addEventListener('click', function() {
        projectFile.click();
    });

    // 拖拽功能
    uploadPlaceholder.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadPlaceholder.style.background = 'rgba(102, 126, 234, 0.1)';
        uploadPlaceholder.style.borderColor = '#5a6fd8';
    });

    uploadPlaceholder.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadPlaceholder.style.background = 'rgba(102, 126, 234, 0.05)';
        uploadPlaceholder.style.borderColor = '#667eea';
    });

    uploadPlaceholder.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadPlaceholder.style.background = 'rgba(102, 126, 234, 0.05)';
        uploadPlaceholder.style.borderColor = '#667eea';
        
        handleFileSelect(e); // 直接传递事件对象
    });

    // 处理文件选择
    function handleFileSelect(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // 修复：确保selectedFile始终是一个数组或FileList对象
        let files;
        if (e.dataTransfer && e.dataTransfer.files) {
            files = e.dataTransfer.files;
        } else if (e.target && e.target.files) {
            files = e.target.files;
        }
        
        console.log('原始文件:', files);
        
        // 修复：当files是单个File对象时，将其转换为数组
        if (files instanceof File) {
            selectedFile = [files];
        } else {
            selectedFile = files;
        }
        
        console.log('处理后的selectedFile:', selectedFile);
        console.log('selectedFile类型:', typeof selectedFile);
        console.log('selectedFile是否为数组:', Array.isArray(selectedFile));
        console.log('selectedFile是否为FileList:', selectedFile instanceof FileList);
        console.log('selectedFile长度:', selectedFile.length);
        
        if (!selectedFile || selectedFile.length === 0) {
            return;
        }
        
        // 检查是否是文件夹上传
        const isFileList = selectedFile instanceof FileList || Array.isArray(selectedFile);
        const isFolder = isFileList && (selectedFile.length > 1 || (selectedFile[0].webkitRelativePath && selectedFile[0].webkitRelativePath !== ''));
        
        if (isFolder) {
            // 文件夹上传
            fileName.textContent = `已选择文件夹，共${selectedFile.length}个文件`;
            // 显示上传内容
            displayUploadContent(selectedFile);
        } else {
            // 单个文件上传（可能是zip）
            const file = selectedFile[0];
            
            // 检查文件类型
            if (file.type !== 'application/zip' && !file.name.endsWith('.zip')) {
                showStatus('请上传文件夹或ZIP格式的压缩包', 'error');
                return;
            }
            
            fileName.textContent = `已选择：${file.name}（${formatFileSize(file.size)}）`;
            // 显示上传内容（ZIP文件显示文件名）
            displayUploadContent([file]);
        }
        
        // 检查文件大小（限制50MB）
        const maxSize = 50 * 1024 * 1024;
        let totalSize = 0;
        for (let i = 0; i < selectedFile.length; i++) {
            totalSize += selectedFile[i].size;
        }
        
        if (totalSize > maxSize) {
            showStatus('文件总大小不能超过50MB', 'error');
            return;
        }
        
        // 显示文件信息，隐藏上传占位符
        uploadPlaceholder.style.display = 'none';
        fileInfo.style.display = 'flex';
        uploadContent.style.display = 'block';
        
        // 启用转换按钮
        convertBtn.disabled = false;
        
        // 隐藏之前的结果
        hideResults();
    }

    // 转换按钮逻辑
    convertBtn.addEventListener('click', async function() {
        if (!selectedFile) {
            showStatus('请先选择文件或文件夹', 'error');
            return;
        }
        const sourceLang = sourceLangSelect.value;
        const targetLang = targetLangSelect.value;
        if (!sourceLang || !targetLang) {
            showStatus('请选择源语言和目标语言', 'error');
            return;
        }
        if (sourceLang === targetLang) {
            showStatus('源语言和目标语言不能相同', 'error');
            return;
        }
        
        // 禁用按钮
        convertBtn.disabled = true;
        
        // 显示加载和进度
        loading.style.display = 'block';
        progress.style.display = 'block';
        currentFile.style.display = 'block'; // 显示当前转换文件区域
        hideResults();
        
        // 重置进度条
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        currentFileName.textContent = '';
        
        // 构建表单数据
        const formData = new FormData();
        formData.append('source_lang', sourceLang);
        formData.append('target_lang', targetLang);
        
        // 检查是否是文件夹上传
        // 修复：当selectedFile是单个File对象时，selectedFile.length会导致错误
        const isFileList = selectedFile instanceof FileList || Array.isArray(selectedFile);
        const isFolder = isFileList && (selectedFile.length > 1 || (selectedFile[0].webkitRelativePath && selectedFile[0].webkitRelativePath !== ''));
        
        if (isFolder) {
            // 文件夹上传：添加所有文件
            for (let i = 0; i < selectedFile.length; i++) {
                formData.append('folder_files', selectedFile[i], selectedFile[i].webkitRelativePath);
            }
            formData.append('type', 'folder');
        } else {
            // 单个文件上传
            // 修复：确保正确获取File对象
            const fileToUpload = isFileList ? selectedFile[0] : selectedFile;
            formData.append('folder_files', fileToUpload);
            // 修复：根据文件扩展名设置正确的type参数
            formData.append('type', fileToUpload.name.endsWith('.zip') ? 'zip' : 'folder');
        }
        
        try {
            // 发送转换请求
            console.log('开始发送转换请求...');
            console.log('FormData内容:', [...formData.entries()]);
            
            const res = await fetch('/api/convert-project', {
                method: 'POST',
                body: formData
            });
            
            console.log('请求响应状态:', res.status);
            console.log('请求响应头:', res.headers);
            
            if (!res.ok) {
                const errorText = await res.text();
                console.error('请求失败:', errorText);
                throw new Error('转换请求失败: ' + res.status);
            }
            
            const data = await res.json();
            console.log('请求响应数据:', data);
            
            if (!data.success) {
                throw new Error(data.error || '转换失败');
            }
            
            // 获取进度ID并开始监听进度
            if (data.progress_id) {
                startProgressTracking(data.progress_id);
            }
            
            conversionResult = data;
            
        } catch (err) {
            showStatus('转换失败：' + err.message, 'error');
            loading.style.display = 'none';
            progress.style.display = 'none';
            currentFile.style.display = 'none';
        }
    });

    // 清空按钮逻辑
    clearBtn.addEventListener('click', function() {
        selectedFile = null;
        conversionResult = null;
        
        // 关闭事件源
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        
        // 重置文件选择
        projectFile.value = '';
        uploadPlaceholder.style.display = 'block';
        fileInfo.style.display = 'none';
        uploadContent.style.display = 'none';
        
        // 重置状态
        convertBtn.disabled = true;
        loading.style.display = 'none';
        progress.style.display = 'none';
        currentFile.style.display = 'none';
        fileList.style.display = 'none';
        downloadBtn.style.display = 'none';
        status.textContent = '';
        status.className = 'status';
        
        // 清空内容列表
        contentList.innerHTML = '';
    });

    // 下载按钮逻辑
    downloadBtn.addEventListener('click', function() {
        if (!conversionResult || !conversionResult.download_url) {
            showStatus('下载链接无效', 'error');
            return;
        }
        
        // 创建隐藏的下载链接
        const a = document.createElement('a');
        a.href = conversionResult.download_url;
        a.download = `converted_project_${new Date().getTime()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        showStatus('下载开始', 'success');
    });

    // 显示上传内容
    function displayUploadContent(files) {
        contentList.innerHTML = '';
        
        if (files.length === 1 && files[0].name.endsWith('.zip')) {
            // ZIP文件
            const zipItem = document.createElement('div');
            zipItem.className = 'content-item';
            zipItem.innerHTML = `<span class="file-type">📦</span> ${files[0].name} (${formatFileSize(files[0].size)})`;
            contentList.appendChild(zipItem);
        } else {
            // 文件夹上传的文件列表
            // 按目录组织文件
            const fileTree = {};
            
            for (let file of files) {
                const path = file.webkitRelativePath || file.name;
                const pathParts = path.split('/');
                
                let currentLevel = fileTree;
                for (let i = 0; i < pathParts.length - 1; i++) {
                    const dir = pathParts[i];
                    if (!currentLevel[dir]) {
                        currentLevel[dir] = {};
                    }
                    currentLevel = currentLevel[dir];
                }
                
                const fileName = pathParts[pathParts.length - 1];
                currentLevel[fileName] = file.size;
            }
            
            // 渲染文件树
            function renderTree(tree, parentElement, path = '') {
                for (let name in tree) {
                    const item = document.createElement('div');
                    item.className = 'content-item';
                    
                    if (typeof tree[name] === 'object') {
                        // 目录
                        item.innerHTML = `<span class="file-type">📁</span> ${name}`;
                        item.style.paddingLeft = (path.split('/').length) * 10 + 'px';
                        parentElement.appendChild(item);
                        renderTree(tree[name], parentElement, path + name + '/');
                    } else {
                        // 文件
                        item.innerHTML = `<span class="file-type">📄</span> ${name} (${formatFileSize(tree[name])})`;
                        item.style.paddingLeft = (path.split('/').length) * 10 + 'px';
                        parentElement.appendChild(item);
                    }
                }
            }
            
            renderTree(fileTree, contentList);
        }
    }

    // 开始进度跟踪
    function startProgressTracking(progressId) {
        // 关闭之前的事件源
        if (eventSource) {
            eventSource.close();
        }
        
        // 创建新的事件源
        eventSource = new EventSource(`/api/progress/${progressId}`);
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    showStatus('进度跟踪失败：' + data.error, 'error');
                    eventSource.close();
                    eventSource = null;
                    return;
                }
                
                // 更新进度条
                const percentage = data.total > 0 ? Math.round((data.current / data.total) * 100) : 0;
                progressBar.style.width = percentage + '%';
                progressText.textContent = percentage + '%';
                
                // 更新当前转换文件
                if (data.current_file) {
                    currentFileName.textContent = data.current_file;
                }
                
                // 如果转换完成
                if (data.status === 'completed') {
                    loading.style.display = 'none';
                    
                    // 显示转换文件列表
                    displayConvertedFiles(conversionResult.files);
                    
                    // 显示下载按钮
                    downloadBtn.style.display = 'inline-block';
                    
                    showStatus(`项目转换成功！共转换${conversionResult.files.length}个文件`, 'success');
                    
                    // 关闭事件源
                    eventSource.close();
                    eventSource = null;
                }
                
                // 如果转换出错
                if (data.status === 'error') {
                    loading.style.display = 'none';
                    showStatus('转换过程中出现错误', 'error');
                    
                    // 关闭事件源
                    eventSource.close();
                    eventSource = null;
                }
                
            } catch (e) {
                console.error('解析进度数据失败：', e);
            }
        };
        
        eventSource.onerror = function() {
            eventSource.close();
            eventSource = null;
        };
    }

    // 显示转换文件列表
    function displayConvertedFiles(files) {
        convertedFiles.innerHTML = '';
        
        files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            convertedFiles.appendChild(li);
        });
        
        fileList.style.display = 'block';
    }

    // 隐藏结果
    function hideResults() {
        fileList.style.display = 'none';
        downloadBtn.style.display = 'none';
    }

    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    // 辅助函数：显示状态提示
    function showStatus(text, type) {
        status.textContent = text;
        status.className = 'status ' + type;
        // 3秒后自动清空提示
        setTimeout(() => {
            status.textContent = '';
            status.className = 'status';
        }, 3000);
    }
});