// Đồng hồ chạy trong Worker: không bị Chrome làm chậm khi cửa sổ điều khiển bị che
onmessage = (e) => setTimeout(() => postMessage(e.data.id), e.data.ms);
