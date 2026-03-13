// content.js — 划词检测 + 双击 Ctrl + 翻译气泡

let lastCtrlTime = 0;
const DOUBLE_CTRL_INTERVAL = 400; // ms

function getSelectedText() {
  const sel = window.getSelection();
  return sel ? sel.toString().trim() : '';
}

function createBubble(x, y) {
  removeBubble();
  const bubble = document.createElement('div');
  bubble.id = 'click-translate-bubble';
  bubble.innerHTML = `
    <div class="ct-header">
      <span class="ct-title">🌐 Click Translate</span>
      <span class="ct-close" title="关闭">✕</span>
    </div>
    <div class="ct-body">
      <div class="ct-loading">
        <div class="ct-spinner"></div>
        <span>翻译中...</span>
      </div>
    </div>
  `;
  document.body.appendChild(bubble);

  // 定位：确保不超出视口
  const rect = bubble.getBoundingClientRect();
  let left = x + 10;
  let top = y + 10;
  if (left + 320 > window.innerWidth) left = x - 330;
  if (top + 200 > window.innerHeight) top = y - 210;
  bubble.style.left = left + 'px';
  bubble.style.top = top + 'px';

  // 关闭按钮
  bubble.querySelector('.ct-close').addEventListener('click', removeBubble);

  return bubble;
}

function removeBubble() {
  const existing = document.getElementById('click-translate-bubble');
  if (existing) existing.remove();
}

async function translate(text, bubble) {
  const body = bubble.querySelector('.ct-body');

  try {
    const response = await chrome.runtime.sendMessage({
      type: 'translate',
      text: text
    });

    if (response.error) {
      body.innerHTML = `<div class="ct-error">❌ ${response.error}</div>`;
      return;
    }

    body.innerHTML = `
      <div class="ct-original">原文：${escapeHtml(text.length > 200 ? text.slice(0, 200) + '...' : text)}</div>
      <div class="ct-result">${escapeHtml(response.translation)}</div>
      <div class="ct-actions">
        <button class="ct-copy-btn" title="复制翻译">📋 复制翻译</button>
      </div>
    `;

    body.querySelector('.ct-copy-btn').addEventListener('click', () => {
      navigator.clipboard.writeText(response.translation).then(() => {
        const btn = body.querySelector('.ct-copy-btn');
        btn.textContent = '✅ 已复制';
        setTimeout(() => { btn.textContent = '📋 复制翻译'; }, 1500);
      });
    });

  } catch (e) {
    body.innerHTML = `<div class="ct-error">❌ 请求失败: ${escapeHtml(e.message)}</div>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// 监听键盘：双击 Ctrl
document.addEventListener('keydown', (e) => {
  if (e.key === 'Control' || e.code === 'ControlLeft' || e.code === 'ControlRight') {
    const now = Date.now();
    if (now - lastCtrlTime < DOUBLE_CTRL_INTERVAL) {
      // 双击 Ctrl！
      const text = getSelectedText();
      if (text) {
        const sel = window.getSelection();
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        const bubble = createBubble(rect.left, rect.bottom);
        translate(text, bubble);
      } else {
        showTip('请先选中要翻译的文本');
      }
      lastCtrlTime = 0; // 重置，防止三连击
    } else {
      lastCtrlTime = now;
    }
  }
});

// 3秒提示（无选中文字时）
function showTip(msg) {
  removeBubble();
  const tip = document.createElement('div');
  tip.id = 'click-translate-bubble';
  tip.innerHTML = `
    <div class="ct-header">
      <span class="ct-title">🌐 Click Translate</span>
      <span class="ct-close" title="关闭">✕</span>
    </div>
    <div class="ct-body">
      <div class="ct-error">💡 ${msg}</div>
    </div>
  `;
  document.body.appendChild(tip);
  tip.style.left = '50%';
  tip.style.top = '20px';
  tip.style.transform = 'translateX(-50%)';
  tip.querySelector('.ct-close').addEventListener('click', removeBubble);
  setTimeout(removeBubble, 2000);
}
