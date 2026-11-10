# Hộp công cụ Văn phòng

**43 công cụ PDF, Word, Excel, kế toán, ảnh và văn bản — chạy trên trình duyệt.** Dùng cùng ChatGPT hoặc Claude, không cần nhập API key vào website.

## Chạy thử

```bash
git clone https://github.com/Hataianh/cong-cu-van-phong.git
cd cong-cu-van-phong
python3 -m http.server 8000
```

Mở trình duyệt trên cổng 8000. Không có backend, cơ sở dữ liệu hay bước npm install. Giữ nguyên thư mục `assets/` và `vendor/`. Nên dùng HTTP thay vì mở `file://` để PDF worker và tải file hoạt động ổn định.

## Có gì mới

- Giữ 40 công cụ gốc và các link cũ; mở nhóm kế toán/AI, bỏ khóa Zalo mẫu và giới hạn 3 file.
- Giao diện sáng/tối mới, tìm kiếm tiếng Việt không dấu, lọc nhóm, yêu thích và công cụ gần đây. Nhấn `/` để tìm; `Ctrl/Cmd+Enter` chạy công cụ.
- Thêm **Đếm & làm sạch văn bản**, **Kiểm tra & định dạng JSON**, **Chia nội dung gửi AI**.
- ChatGPT/Claude qua hộp chép yêu cầu → dán kết quả, có tải ảnh trang cho bản scan. Giữ kết nối Claude Artifact nếu host cung cấp capability `sample`.
- Tải gói dùng trong ChatGPT có chạy mã/tạo file: quy chuẩn và script dịch Word/Excel gốc, kèm hướng dẫn. Đây không phải App/GPT đã xuất bản trên ChatGPT.
- Thư viện JS chính được đóng gói local, giữ phiên bản cũ để hạn chế thay đổi hành vi. Script vendor kiểm tra SHA-512 từ npm; manifest lưu nguồn và SHA-256 từng bundle.
- Sửa ZIP ảnh ghi đè khi các ảnh trùng tên; escape tên ảnh khi hiển thị; xử lý link hash sai định dạng.

## Dùng với ChatGPT

1. Bấm **Dùng với ChatGPT** trên đầu trang để xem hướng dẫn hoặc tải gói trợ lý.
2. Chọn công cụ AI, chọn tài liệu và bấm xử lý.
3. Chép yêu cầu sang ChatGPT. Với bản scan, tải ảnh trang trong hộp rồi đính kèm ảnh cùng yêu cầu.
4. Dán toàn bộ kết quả về website. JSON trong khối mã được hỗ trợ; trang báo lỗi định dạng để sửa trước khi tiếp tục.
5. Duyệt kết quả rồi tải file. Tài liệu nhiều phần cần lặp lại cho từng phần.

Website **không tự gọi ChatGPT hoặc đọc lịch sử chat**. Gọi tự động cần một tích hợp backend/Apps SDK riêng. Gói ZIP cần chế độ chat có chạy mã/tạo file; script dịch cần Python và `lxml`. Nếu tài khoản không hỗ trợ, dùng luồng chép/dán trên web. Hướng dẫn cài Claude skill vẫn được giữ riêng trong công cụ dịch.

## Dữ liệu và giới hạn

- File/kết quả nằm trong bộ nhớ trang. Làm mới hoặc đóng trang sẽ mất phiên; tải kết quả trước khi đóng.
- Local storage chỉ giữ theme, ID công cụ yêu thích/gần đây, lựa chọn dịch vụ AI và trạng thái thông báo. Không lưu nội dung tài liệu.
- Luồng chép/dán không tự gửi tài liệu ra mạng. Trong Claude Artifact hỗ trợ kết nối, thao tác chạy AI gửi nội dung theo cơ chế cấp quyền của host.
- Không có analytics hay máy chủ ứng dụng. Một số phông/CMap bổ sung của PDF.js vẫn tải từ `cdn.jsdelivr.net` khi cần; không cam kết mọi tài liệu chạy offline.
- Dịch PDF tại chỗ dùng lớp phủ; chữ gốc có thể còn bên dưới. Muốn xóa dữ liệu nhạy cảm hãy dùng **Che thông tin**.
- Word/Excel → PDF có thể lệch bố cục với tài liệu phức tạp. Cần giống hoàn toàn thì xuất PDF từ Office.
- AI và các công cụ kế toán hỗ trợ soát xét; cần đối chiếu số liệu/điều khoản với bản gốc. Chưa kiểm chứng mọi mẫu hóa đơn và mọi định dạng PDF/Office.

## GitHub Pages

Sau khi push, vào **Settings → Pages**, chọn **Deploy from a branch → master → /(root) → Save**. Chờ GitHub triển khai xong.

Địa chỉ dự kiến: `https://hataianh.github.io/cong-cu-van-phong/`. Link chỉ hoạt động sau khi Pages được bật và triển khai thành công.

## Kiểm thử và phát triển

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m unittest discover -s tests -v
```

Test tự dùng Chromium hệ thống nếu có, tự mở HTTP server, dùng tài liệu tổng hợp và câu trả lời AI mô phỏng. Kiểm tra điều hướng 43 công cụ, Word/Excel/PDF/ảnh đầu ra, dịch giữ bố cục, scan hóa đơn, JSON lỗi, dừng tác vụ, Claude capability, gói ChatGPT, tìm kiếm/yêu thích và màn hình nhỏ. CI được cấu hình chạy cùng bộ test; kết quả CI cần xem sau khi push.

`python3 tools/vendor.py` tái tạo bundle có kiểm tra integrity; không cần chạy mỗi lần mở ứng dụng. `index.html` giữ engine gốc; `assets/ai-bridge.js` là cầu nối AI, `workspace.js` chứa tìm kiếm/công cụ mới, `workspace.css` là lớp giao diện.

Xem [đánh giá và ý tưởng phát triển](docs/DANH-GIA-VA-LO-TRINH.md), [giấy phép thành phần](THIRD_PARTY.md). [Tài liệu gốc](docs/TINH-NANG-GOC.md) giữ để đối chiếu; các mô tả chỉ-Claude/CDN trong tài liệu đó đã được cập nhật như trên.
