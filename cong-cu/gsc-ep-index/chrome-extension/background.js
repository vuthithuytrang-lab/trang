// Bấm biểu tượng tiện ích → mở cửa sổ điều khiển (hoặc đưa cửa sổ đang mở lên trước)
chrome.action.onClicked.addListener(async () => {
  const url = chrome.runtime.getURL('runner.html');
  const [old] = await chrome.tabs.query({ url });
  if (old) {
    await chrome.windows.update(old.windowId, { focused: true });
    return;
  }
  chrome.windows.create({ url, type: 'popup', width: 560, height: 760 });
});
