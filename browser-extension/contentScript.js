(() => {
  let bubbleEl = null;
  let contentEl = null;
  let copyBtnEl = null;
  let lastCtrlTime = 0;

  function createBubble() {
    if (bubbleEl) return;

    bubbleEl = document.createElement('div');
    bubbleEl.className = 'click-translate-bubble';
    bubbleEl.innerHTML = `
      <div class="ct-header">
        <span class="ct-title">Click Translate</span>
        <button class="ct-close">✕</button>
      </div>
      <div class="ct-body">
        <div class="ct-content"></div>
        <button class="ct-copy" title="复制翻译">📋</button>
      </div>
    `;

    document.documentElement.appendChild(bubbleEl);

    contentEl = bubbleEl.querySelector('.ct-content');
    copyBtnEl = bubbleEl.querySelector('.ct-copy');
    const closeBtn = bubbleEl.querySelector('.ct-close');

    closeBtn.addEventListener('click', () => {
      bubbleEl.style.display = 'none';
    });

    copyBtnEl.addEventListener('click', () => {
      const text = contentEl.textContent || '';
      if (!text.trim()) return;
      navigator.clipboard.writeText(text).then(() => {
        copyBtnEl.textContent = '✅';
        setTimeout(() => {
          copyBtnEl.textContent = '📋';
        }, 1200);
      });
    });
  }

  function getSelectionInfo() {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return null;
    const text = selection.toString().trim();
    if (!text) return null;
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    return { text, rect };
  }

  function positionBubble(rect) {
    if (!bubbleEl) return;
    const margin = 8;
    const bubbleRect = { width: 320, height: 160 };
    let left = rect.left + window.scrollX;
    let top = rect.bottom + window.scrollY + margin;

    if (left + bubbleRect.width > window.scrollX + window.innerWidth) {
      left = window.scrollX + window.innerWidth - bubbleRect.width - margin;
    }
    if (top + bubbleRect.height > window.scrollY + window.innerHeight) {
      top = rect.top + window.scrollY - bubbleRect.height - margin;
    }

    bubbleEl.style.left = `${left}px`;
    bubbleEl.style.top = `${top}px`;
  }

  async function startTranslateFromSelection() {
    const info = getSelectionInfo();
    if (!info) return;

    createBubble();
    positionBubble(info.rect);

    contentEl.textContent = '翻译中...';
    copyBtnEl.disabled = true;
    bubbleEl.style.display = 'block';

    chrome.runtime.sendMessage(
      { type: 'translate', text: info.text },
      (result) => {
        if (!result) {
          contentEl.textContent = '❌ 翻译失败：无法连接扩展。';
          copyBtnEl.disabled = true;
          return;
        }
        if (result.error) {
          contentEl.textContent = `❌ ${result.error}`;
          copyBtnEl.disabled = true;
        } else {
          contentEl.textContent = result.translation || '';
          copyBtnEl.disabled = false;
        }
      }
    );
  }

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message && message.type === 'translate-selection') {
      startTranslateFromSelection();
    }
  });

  // 监听页面内的按键事件，识别“双击 Ctrl”
  window.addEventListener(
    'keydown',
    (event) => {
      // 只在页面获得焦点且未重复触发时处理
      if (event.repeat) return;
      if (event.key !== 'Control') return;

      const now = Date.now();
      if (now - lastCtrlTime < 400) {
        // 认为是双击 Ctrl，触发当前选区翻译
        lastCtrlTime = 0;
        startTranslateFromSelection();
      } else {
        lastCtrlTime = now;
      }
    },
    true
  );
})();

