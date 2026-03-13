const API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';

async function getConfig() {
  const data = await chrome.storage.sync.get({
    glmApiKey: '',
  });
  return {
    apiKey: data.glmApiKey || '',
  };
}

async function callGLMApi(text) {
  const config = await getConfig();
  if (!config.apiKey) {
    return { error: '请先在扩展选项中配置 GLM API Key。' };
  }

  const isChinese = /[\u4e00-\u9fa5]/.test(text);
  const prompt = isChinese
    ? `请将以下文本翻译为英文：\n${text}`
    : `请将以下文本翻译为中文：\n${text}`;

  try {
    const resp = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify({
        model: 'glm-4-flash',
        messages: [
          { role: 'system', content: '你是一个专业翻译。只输出翻译结果，不要解释。' },
          { role: 'user', content: prompt },
        ],
        temperature: 0.3,
        max_tokens: 1024,
      }),
    });

    const data = await resp.json();
    if (data.choices && data.choices[0] && data.choices[0].message) {
      return { translation: data.choices[0].message.content.trim() };
    }
    return { error: data.error?.message || '翻译失败' };
  } catch (e) {
    return { error: `网络错误: ${e.message || e}` };
  }
}

// 处理来自 content script 的翻译请求
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === 'translate') {
    (async () => {
      const result = await callGLMApi(message.text || '');
      sendResponse(result);
    })();
    return true; // keep channel open for async sendResponse
  }
});

// 监听键盘快捷键命令
chrome.commands.onCommand.addListener(async (command) => {
  if (command !== 'translate-selection') return;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return;

  // 通知 content script 执行“翻译当前选区”
  chrome.tabs.sendMessage(tab.id, { type: 'translate-selection' });
});

// 右键菜单：对选中的文本进行翻译
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'click-translate-selection',
    title: 'Click Translate：翻译选中文本',
    contexts: ['selection'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'click-translate-selection') return;
  if (!tab || !tab.id) return;

  chrome.tabs.sendMessage(tab.id, {
    type: 'translate-selection',
  });
});
