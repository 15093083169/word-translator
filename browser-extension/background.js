// background.js - 扩展后台脚本
chrome.commands.onCommand.addListener((command) => {
  if (command === 'translate-selection') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: () => {
            const selection = window.getSelection().toString().trim();
            if (selection) {
              // 触发自定义事件让 content.js 处理
              window.dispatchEvent(new CustomEvent('word-translator-trigger', {
                detail: { text: selection }
              }));
            }
          }
        });
      }
    });
  }
});

// 安装时打开设置页
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.runtime.openOptionsPage
      ? chrome.runtime.openOptionsPage()
      : chrome.tabs.create({ url: chrome.runtime.getURL('popup.html') });
  }
});
