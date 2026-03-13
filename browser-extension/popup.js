// popup.js - 设置页面逻辑
document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const modelSelect = document.getElementById('model');
  const langSelect = document.getElementById('targetLang');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');

  // 加载已保存的设置
  chrome.storage.local.get(['apiKey', 'model', 'targetLang'], (result) => {
    if (result.apiKey) apiKeyInput.value = result.apiKey;
    if (result.model) modelSelect.value = result.model;
    if (result.targetLang) langSelect.value = result.targetLang;
  });

  // 保存设置
  saveBtn.addEventListener('click', () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
      status.textContent = '⚠️ 请输入 API Key';
      status.style.color = '#e74c3c';
      return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';

    chrome.storage.local.set({
      apiKey: apiKey,
      model: modelSelect.value,
      targetLang: langSelect.value
    }, () => {
      status.textContent = '✅ 设置已保存！';
      status.style.color = '#27ae60';
      saveBtn.disabled = false;
      saveBtn.textContent = '💾 保存设置';

      // 通知 content script
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { type: 'SETTINGS_UPDATED' }).catch(() => {});
        }
      });
    });
  });
});
