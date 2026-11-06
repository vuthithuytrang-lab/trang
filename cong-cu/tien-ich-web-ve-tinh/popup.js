document.getElementById("go").addEventListener("click", async () => {
  const btn = document.getElementById("go"), msg = document.getElementById("msg");
  btn.disabled = true; msg.className = ""; msg.textContent = "Đang đọc trang…";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !/^https?:/.test(tab.url || "")) throw new Error("Hãy mở một website (địa chỉ bắt đầu bằng http) rồi bấm lại.");
    const [res] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extractPageData });
    if (!res || !res.result) throw new Error("Không đọc được trang này.");
    if (/challenge|captcha|just a moment|attention required|xác minh|verify/i.test(res.result.title || ""))
      throw new Error("Trang đang hiện màn xác minh chống bot. Hãy làm xác minh (nếu có), đợi trang hiện đủ nội dung rồi bấm lại.");
    await chrome.storage.local.set({ raw: res.result, at: Date.now() });
    await chrome.tabs.create({ url: chrome.runtime.getURL("editor.html") });
    window.close();
  } catch (e) {
    msg.className = "err"; msg.textContent = e.message || String(e); btn.disabled = false;
  }
});
