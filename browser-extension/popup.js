document.addEventListener('DOMContentLoaded', () => {
  const apiKeyInput = document.getElementById('apiKey');
  const saveBtn = document.getElementById('saveBtn');
  const statusEl = document.getElementById('status');

  // 读取已保存的 Key
  chrome.storage.sync.get(
    {
      glmApiKey: '',
    },
    (data) => {
      apiKeyInput.value = data.glmApiKey || '';
    }
  );

  // 保存 Key
  saveBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    chrome.storage.sync.set(
      {
        glmApiKey: key,
      },
      () => {
        statusEl.textContent = '已保存 ✅';
        setTimeout(() => {
          statusEl.textContent = '';
        }, 1500);
      }
    );
  });
});

