document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const saveBtn = document.getElementById('saveBtn');
  const statusEl = document.getElementById('status');

  chrome.storage.sync.get(
    {
      glmApiKey: '',
    },
    (data) => {
      apiKeyInput.value = data.glmApiKey || '';
    }
  );

  saveBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    chrome.storage.sync.set(
      {
        glmApiKey: key,
      },
      () => {
        statusEl.textContent = '已保存。';
        setTimeout(() => {
          statusEl.textContent = '';
        }, 1500);
      }
    );
  });
});

// options.js — 设置页面逻辑

const apiKeyInput = document.getElementById('api-key');
const apiKeyShow = document.getElementById('api-key-show');
const btnSave = document.getElementById('btn-save');
const btnTest = document.getElementById('btn-test');
const statusMsg = document.getElementById('status-msg');

// 加载已保存的 key
chrome.storage.local.get(['glm_api_key'], (result) => {
  if (result.glm_api_key) {
    apiKeyInput.value = result.glm_api_key;
    apiKeyShow.value = maskKey(result.glm_api_key);
  }
});

// 保存
btnSave.addEventListener('click', () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    showStatus('请输入 API Key', 'error');
    return;
  }
  chrome.storage.local.set({ glm_api_key: key }, () => {
    apiKeyShow.value = maskKey(key);
    showStatus('✅ 保存成功！现在去网页试试划词翻译吧', 'success');
  });
});

// 测试连接
btnTest.addEventListener('click', async () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    showStatus('请先输入 API Key', 'error');
    return;
  }

  btnTest.disabled = true;
  btnTest.textContent = '⏳ 测试中...';

  try {
    const res = await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${key}`
      },
      body: JSON.stringify({
        model: 'glm-4-flash',
        messages: [{ role: 'user', content: 'Hello' }],
        max_tokens: 10
      })
    });

    if (res.ok) {
      showStatus('✅ 连接成功！GLM-4-Flash 可用', 'success');
    } else {
      const err = await res.json().catch(() => ({}));
      showStatus(`❌ 连接失败: ${err.error?.message || 'HTTP ' + res.status}`, 'error');
    }
  } catch (e) {
    showStatus(`❌ 网络错误: ${e.message}`, 'error');
  } finally {
    btnTest.disabled = false;
    btnTest.textContent = '🧪 测试连接';
  }
});

function showStatus(msg, type) {
  statusMsg.textContent = msg;
  statusMsg.className = `status-msg ${type}`;
}

function maskKey(key) {
  if (key.length <= 8) return '****';
  return key.slice(0, 4) + '****' + key.slice(-4);
}
