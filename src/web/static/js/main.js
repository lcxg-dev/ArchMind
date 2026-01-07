// 确保DOM完全加载后再执行JavaScript代码
document.addEventListener('DOMContentLoaded', function() {
    // 初始化语法高亮
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }

    // 获取DOM元素
    const sourceLangSelect = document.getElementById('source-lang');
    const targetLangSelect = document.getElementById('target-lang');
    const sourceCodeInput = document.getElementById('source-code-input');
    const sourceCodeDisplay = document.getElementById('source-code');
    const targetCodeDisplay = document.getElementById('target-code');
    const sourceLineNumbers = document.getElementById('source-line-numbers');
    const targetLineNumbers = document.getElementById('target-line-numbers');
    const convertBtn = document.getElementById('convert-btn');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const loading = document.getElementById('loading');
    const status = document.getElementById('status');

    // 初始化行号显示
sourceLineNumbers.textContent = '1';
targetLineNumbers.textContent = '1';

// 生成行号
function generateLineNumbers(text, lineNumbersElement) {
    // 当文本为空时，显示至少一行行号
    if (!text.trim()) {
        lineNumbersElement.textContent = '1';
        return;
    }
    const lines = text.split('\n').length;
    const lineNumbers = Array.from({ length: lines }, (_, i) => i + 1).join('\n');
    lineNumbersElement.textContent = lineNumbers;
}

// 同步输入框和高亮区域的内容
sourceCodeInput.addEventListener('input', function() {
    sourceCodeDisplay.textContent = this.value;
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(sourceCodeDisplay);
    }
    generateLineNumbers(this.value, sourceLineNumbers);
});

// 滚动同步
sourceCodeInput.addEventListener('scroll', function() {
    sourceCodeDisplay.scrollTop = this.scrollTop;
    sourceCodeDisplay.scrollLeft = this.scrollLeft;
    sourceLineNumbers.scrollTop = this.scrollTop;
});

sourceCodeDisplay.addEventListener('scroll', function() {
    sourceCodeInput.scrollTop = this.scrollTop;
    sourceCodeInput.scrollLeft = this.scrollLeft;
    sourceLineNumbers.scrollTop = this.scrollTop;
});

// 复制结果后更新行号
function updateTargetLineNumbers() {
    generateLineNumbers(targetCodeDisplay.textContent, targetLineNumbers);
}

// 清空按钮逻辑
clearBtn.addEventListener('click', function() {
    sourceCodeInput.value = '';
    sourceCodeDisplay.textContent = '';
    targetCodeDisplay.textContent = '';
    // 清空后仍然显示行号1
    sourceLineNumbers.textContent = '1';
    targetLineNumbers.textContent = '1';
    status.textContent = '';
    status.className = 'status';
});

// 复制结果按钮逻辑
copyBtn.addEventListener('click', async function() {
    const code = targetCodeDisplay.textContent;
    if (!code) {
        showStatus('暂无转换结果可复制', 'error');
        return;
    }
    try {
        await navigator.clipboard.writeText(code);
        showStatus('复制成功！', 'success');
    } catch (err) {
        showStatus('复制失败：' + err.message, 'error');
    }
});

// 转换按钮逻辑（先模拟，后续替换为真实接口调用）
convertBtn.addEventListener('click', async function() {
    const sourceLang = sourceLangSelect.value;
    const targetLang = targetLangSelect.value;
    const sourceCode = sourceCodeInput.value.trim();

    if (!sourceCode) {
        showStatus('请输入要转换的代码！', 'error');
        return;
    }

    // 显示加载状态
    loading.style.display = 'block';
    status.textContent = '';
    status.className = 'status';

    try {
        // 调用真实后端接口
        const res = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_lang: sourceLang,
                target_lang: targetLang,
                code: sourceCode
            })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || '转换失败');
        const mockResult = data.result;

        // 展示结果
        targetCodeDisplay.textContent = mockResult;
        if (typeof hljs !== 'undefined') {
            hljs.highlightElement(targetCodeDisplay);
        }
        updateTargetLineNumbers(); // 更新结果区的行号
        showStatus(`转换成功（${sourceLang} → ${targetLang}）`, 'success');
    } catch (err) {
        showStatus('转换失败：' + err.message, 'error');
        targetCodeDisplay.textContent = '';
    } finally {
        // 隐藏加载状态
        loading.style.display = 'none';
    }
});

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

// 初始化语言高亮样式
sourceLangSelect.addEventListener('change', function() {
    sourceCodeDisplay.className = `code-block ${this.value}`;
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(sourceCodeDisplay);
    }
});
targetLangSelect.addEventListener('change', function() {
    targetCodeDisplay.className = `code-block ${this.value}`;
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(targetCodeDisplay);
    }
});
});