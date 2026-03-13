// content.js - 划词翻译浏览器扩展内容脚本
(function () {
  'use strict';

  // 防止重复注入
  if (window.__wordTranslatorInjected) return;
  window.__wordTranslatorInjected = true;

  const API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';
  const DOUBLE_CTRL_INTERVAL = 400;

  let lastCtrlTime = 0;
  let popupEl = null;
  let isLoading = false;

  // 创建浮动翻译弹窗
  function createPopup() {
    if (popupEl) popupEl.remove();

    popupEl = document.createElement('div');
    popupEl.id = 'word-translator-popup';
    popupEl.innerHTML = `
      <div class="wt-header">
        <span class="wt-title">📖 划词翻译</span>
        <span class="wt-close" title="关闭">✕</span>
      </div>
      <div class="wt-source"></div>
      <div class="wt-divider"></div>
      <div class="wt-result"></div>
      <div class="wt-actions">
        <button class="wt-copy-btn" style="display:none;">📋 复制翻译</button>
      </div>
    `;

    document.body.appendChild(popupEl);

    popupEl.querySelector('.wt-close').addEventListener('click', () => {
      popupEl.style.display = 'none';
    });
  }

  function positionPopup(x, y) {
    if (!popupEl) createPopup();
    popupEl.style.display = 'block';

    const rect = popupEl.getBoundingClientRect();
    const ww = window.innerWidth;
    const wh = window.innerHeight;

    let left = x + 15;
    let top = y + 15;
    if (left + 360 > ww) left = x - 370;
    if (top + 200 > wh) top = y - 210;
    if (left < 5) left = 5;
    if (top < 5) top = 5;

    popupEl.style.left = left + 'px';
    popupEl.style.top = top + 'px';
  }

  async function translate(text, posX, posY) {
    if (!text.trim()) return;
    if (isLoading) return;
    isLoading = true;

    positionPopup(posX, posY);

    const sourceEl = popupEl.querySelector('.wt-source');
    const resultEl = popupEl.querySelector('.wt-result');
    const copyBtn = popupEl.querySelector('.wt-copy-btn');

    sourceEl.textContent = text.length > 200 ? text.slice(0, 200) + '...' : text;
    sourceEl.style.display = 'block';
    resultEl.textContent = '⏳ 翻译中...';
    resultEl.className = 'wt-result loading';
    copyBtn.style.display = 'none';

    try {
      const { apiKey, model, targetLang } = await chrome.storage.local.get([
        'apiKey', 'model', 'targetLang'
      ]);

      if (!apiKey) {
        resultEl.textContent = '❌ 请先点击扩展图标，设置 API Key';
        resultEl.className = 'wt-result error';
        isLoading = false;
        return;
      }

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: model || 'glm-4-flash',
          messages: [
            {
              role: 'system',
              content: `你是一个翻译专家。将用户输入的文本翻译为${targetLang || '中文'}。只输出翻译结果，不要添加任何解释、注释或额外格式。`
            },
            {
              role: 'user',
              content: text
            }
          ],
          temperature: 0.1,
          max_tokens: 1024
        })
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error.message || 'API 错误');
      }

      const translation = data.choices[0].message.content.trim();
      resultEl.textContent = translation;
      resultEl.className = 'wt-result success';
      copyBtn.style.display = 'inline-block';
      copyBtn.textContent = '📋 复制翻译';

      copyBtn.onclick = () => {
        navigator.clipboard.writeText(translation).then(() => {
          copyBtn.textContent = '✅ 已复制';
          setTimeout(() => { copyBtn.textContent = '📋 复制翻译'; }, 2000);
        });
      };

    } catch (err) {
      resultEl.textContent = `❌ 翻译失败: ${err.message}`;
      resultEl.className = 'wt-result error';
    }

    isLoading = false;
  }

  // 监听双击 Ctrl
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Control') {
      const now = Date.now();
      if (0 < now - lastCtrlTime < DOUBLE_CTRL_INTERVAL) {
        lastCtrlTime = 0;
        const selection = window.getSelection().toString().trim();
        if (selection) {
          const range = window.getSelection().getRangeAt(0);
          const rect = range.getBoundingClientRect();
          translate(selection, rect.left, rect.bottom);
        }
      } else {
        lastCtrlTime = now;
      }
    }
  });

  // 点击其他地方关闭弹窗
  document.addEventListener('mousedown', (e) => {
    if (popupEl && !popupEl.contains(e.target)) {
      popupEl.style.display = 'none';
    }
  });

  // 监听来自 popup 的消息（设置更新）
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'SETTINGS_UPDATED') {
      // 可以在这里做额外处理
    }
  });

  // 监听快捷键触发的自定义事件
  window.addEventListener('word-translator-trigger', (e) => {
    const text = e.detail.text;
    if (text) {
      const range = window.getSelection().getRangeAt(0);
      const rect = range.getBoundingClientRect();
      translate(text, rect.left, rect.bottom);
    }
  });

})();
