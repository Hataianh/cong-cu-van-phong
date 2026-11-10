# Đánh giá và lộ trình

## Những vấn đề đã xác nhận và xử lý

Khóa nhóm Kế toán và 5 công cụ AI, cùng giới hạn 3 file mỗi lần chọn, là chủ ý của chủ sở hữu trong bản ZIP gốc. Bản public đã khôi phục đúng phạm vi này; đây không phải lỗi cần gỡ bỏ. Nút tải gói dịch ChatGPT cũng bị khóa ở bản dùng thử. Liên kết Zalo `xxxxxx` chỉ là chỗ chờ thông tin liên hệ thật, không dùng làm nút liên hệ công khai.

| Vấn đề trong ZIP | Ảnh hưởng | Bản cập nhật |
|---|---|---|
| Bản cập nhật trước vô tình mở khóa quyền dùng thử | Truy cập được tính năng dành cho bản Pro | Khôi phục đúng 10 mục bị khóa; kiểm thử cả link trực tiếp, link cũ và gói dịch ChatGPT |
| Bản cập nhật trước bỏ giới hạn 3 file | Phạm vi dùng thử khác bản gốc | Khôi phục giới hạn cả chọn file/kéo thả; giữ thông báo nhận 3 file đầu |
| AI phụ thuộc Claude `sample` | Ngoài Artifact không dùng được nhiều mục AI | Cầu nối chép/dán, kiểm tra JSON, tải ảnh trang, hủy tác vụ; giữ native Claude |
| Bundle từ CDN bị chặn ở môi trường thử | Trang hiện nhưng Excel/Word/ZIP không chạy đủ | Bundle local, tải từ npm có kiểm tra integrity |
| ZIP ảnh dùng tên gốc trực tiếp | Ảnh trùng tên ghi đè nhau | Tự thêm hậu tố; test ZIP 3 ảnh cùng tên trong giới hạn dùng thử |
| Tên ảnh ghép vào HTML trạng thái chưa escape | Tên file có thể được hiểu thành markup | Escape tên ảnh |
| Hash URL decode không bắt lỗi | Link sai escape làm hỏng điều hướng | Bắt lỗi, về trang chủ |
| 40 công cụ không có tìm kiếm | Khó tìm trên màn hình nhỏ | Tìm không dấu, yêu thích, gần đây, phím tắt |

## Những điểm nên giữ

Xử lý local hợp với hồ sơ văn phòng. Engine song ngữ sửa XML thay vì dựng lại tài liệu và có bảng duyệt. Excel dùng công thức tổng/đối chiếu, giữ mã số là chuỗi. Link riêng cho từng công cụ và tải từng phần thuận tiện cho người dùng không chuyên.

## Phạm vi kiểm tra

Test dùng Chromium, tài liệu tổng hợp và câu trả lời AI mô phỏng. Đã kiểm tra đầu ra file cho các luồng chính và những phần thay đổi. Chưa thử tài khoản ChatGPT/Claude thật, mọi tính năng trên Safari/iOS, mọi form PDF hoặc mẫu hóa đơn. Kết nối native Claude được kiểm tra bằng mock capability, cần kiểm tra thêm trong host thật. Không cam kết mọi tài liệu Office giữ bố cục tuyệt đối.

Giữ phiên bản thư viện để tránh thay đổi engine cùng lúc làm UI/cầu nối. Checksum xác minh bản tải, không xác nhận thư viện không có lỗ hổng. Cần đợt nâng cấp phụ thuộc có kiểm thử riêng trước production, đặc biệt SheetJS và PDF.js.

## Tối ưu nên làm tiếp

| Ưu tiên | Cải tiến | Nghiệm thu |
|---|---|---|
| 1 | Tách engine PDF/Excel/Word/dịch khỏi HTML lớn | Fixture tạo kết quả tương đương trước/sau |
| 1 | Kiểm tra schema JSON riêng từng công cụ AI | Thiếu ID đoạn, sai kiểu tiền/số phần phải báo cụ thể |
| 1 | Nâng cấp thư viện, quét phụ thuộc, hoàn thiện notice | Test đầu ra và tài liệu lỗi/lớn |
| 1 | Tác vụ nặng chạy Web Worker; thêm tiến độ/hủy | UI không đơ; hủy giải phóng canvas/worker |
| 2 | Fixture PDF form/mật khẩu/che thông tin; Office Track Changes/bảng phức tạp | Chữ bị che không còn ở lớp text/ảnh; công thức không đổi |
| 2 | Lưu phiên local tùy chọn, có xóa dữ liệu | Không bật mặc định; kiểm tra khôi phục/xóa |
| 2 | PWA/offline có version cache và font/CMap | Mất mạng vẫn chạy; cập nhật không dùng engine cũ |
| 3 | ChatGPT App qua MCP/Apps SDK | Server HTTPS, xác thực, chính sách dữ liệu và test trong ChatGPT; dự án riêng |

## Công cụ hay nên bổ sung

1. **Quy trình hồ sơ:** ảnh → PDF → sắp trang → đánh số → nén. Tái sử dụng engine hiện có, xem trước và quay lại từng bước.
2. **Đổi tên hàng loạt:** theo STT/ngày/khách hàng, xem trước, chống trùng tên, tải ZIP.
3. **Soát dữ liệu nhạy cảm:** tìm email, điện thoại, CCCD/MST; duyệt từng mục trước khi che.
4. **Soát công thức Excel:** công thức bị ghi đè, vùng SUM bỏ sót, công thức khác mẫu; xuất báo cáo ô, không tự sửa số liệu.
5. **Đối chiếu hóa đơn – thanh toán:** XML + sao kê; hỗ trợ nhiều hóa đơn trong một khoản thanh toán.
6. **Checklist hợp đồng:** thanh toán, gia hạn, chấm dứt; dẫn đoạn/trang nguồn, phân biệt “không tìm thấy” với “không có”.
7. **Ẩn danh dữ liệu mẫu:** thay tên/email/điện thoại mà giữ cấu trúc; người dùng duyệt mapping trước khi xuất.
8. **Bảng → CSV/JSON:** giữ số 0 đầu và mã dài, dùng cho hệ thống khác.

Nên làm quy trình hồ sơ và đổi tên hàng loạt trước; ưu tiên độ tin cậy dữ liệu hơn thêm nhiều nút AI trùng chức năng.
