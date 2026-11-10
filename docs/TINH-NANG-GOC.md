# Hộp công cụ Văn phòng

Web app chạy **hoàn toàn trên trình duyệt** (không gửi file đi đâu, trừ khi bạn chọn dùng Claude ở các công cụ ghi "Dùng Claude", Dịch song ngữ, hoặc cách "AI đọc hình trang").

**Cách dùng:** trang chủ là lưới 37 công cụ chia 7 nhóm (Sắp xếp PDF, Chỉnh sửa PDF, Đọc và chuyển đổi, Bảo mật PDF, Văn bản và dịch, Excel và hóa đơn, Công cụ ảnh), lọc được theo nhóm. Bấm một công cụ để mở trang riêng của nó: chọn file, chỉnh tùy chọn của đúng việc đó, bấm nút chính để tải về. Mỗi công cụ có link riêng để gửi thẳng cho người khác, ví dụ `#gop-pdf`, `#tach-pdf`, `#nen-pdf`, `#so-trang`, `#dong-dau`, `#ky-pdf`, `#che-thong-tin`, `#pdf-sang-excel`, `#pdf-sang-word`, `#so-sanh-pdf`, `#song-ngu`, `#hoa-don-xml`, `#doi-chieu` (link cũ `#word`, `#pdf`, `#doc-pdf`… vẫn dùng được). `Ctrl+Enter` chạy nút chính của công cụ đang mở.

Các công cụ, theo chức năng:

1. **Dán AI → Word** — dán câu trả lời của Claude, ra văn bản Word chuẩn (Times New Roman, tự đánh số đề mục I./1./1.1., dựng bảng, bỏ dấu `**` `###`, cắt phần ghi chú sau `---`).
2. **Làm sạch Excel** — chuẩn hóa họ tên, số điện thoại (khôi phục số 0 đầu), ngày về dd/mm/yyyy, tiền "1tr2"/"500k" → số; tách Họ/Tên đệm/Tên; xóa dòng trùng, dòng trống.
3. **Gộp nhiều file** — gộp nhiều file/sheet thành một bảng, tự khớp cột khác tên, thêm cột Nguồn.
4. **Đối chiếu** — đối chiếu 2 danh sách theo cột mã; cột mã và cột so sánh chọn riêng cho từng file (tự ghép theo tên cột), xem riêng nhóm lệch / chỉ có ở A / chỉ có ở B.
5. **Soát lỗi** — soát file báo cáo (số lưu dạng chữ, #REF!, #DIV/0!, sheet ẩn), chỉ ra đúng địa chỉ ô, tải được danh sách ô lỗi.
6. **Hóa đơn XML → Bảng kê** — chọn nhiều hóa đơn điện tử `.xml` (chuẩn Tổng cục Thuế, TT78/NĐ123) hoặc file `.zip` chứa chúng → bảng kê mỗi hóa đơn một dòng (ký hiệu, số, ngày, MST/tên người bán – người mua, thuế suất, tiền chưa thuế, thuế GTGT, tổng thanh toán), tự bỏ hóa đơn trùng, đánh dấu HĐ thay thế/điều chỉnh. File tải về có 4 sheet: *Bang ke*, *Chi tiet hang hoa*, *Thue theo HD*, *Theo thue suat*.
7. **Dịch Word/Excel giữ bố cục** — đưa vào `.docx` / `.xlsx`, chọn **Kiểu kết quả**: *Song ngữ* (bản gốc trên, bản dịch ngay dưới) hoặc *Chỉ bản dịch* (thay chữ ngay tại chỗ, **giữ nguyên bố cục 100%** — số đoạn, định dạng, đánh số không đổi). Chọn **ngôn ngữ đích** (Anh, Trung, Nhật, Hàn, Pháp, hoặc ghi rõ ngôn ngữ khác); bản tiếng Anh theo đúng bộ quy chuẩn trình bày (`QUY-CHUAN.md`), ngôn ngữ khác dịch giữ bố cục. Giữ nguyên đề mục, đánh số tự động, bảng, chữ đậm/màu/liên kết, đầu/chân trang, trường số trang; Excel giữ nguyên ô số/công thức, ngày, và các ô là khóa của công thức, danh sách chọn, tiêu đề Bảng Excel. Ba cách dịch, đều bằng Claude của chính người dùng:
   - **Qua khung chat Claude** (dùng được ở bản GitHub): chép lời nhắc từng phần → dán vào Claude → dán câu trả lời JSON về → dựng file.
   - **Cài skill** `vp-dich-song-ngu` (tải ngay trong tab): Claude tự tách, dịch, kiểm tra, dựng file — hợp với file dài hoặc cả thư mục.
   - **Dịch ngay** (chỉ khi mở trong Claude dưới dạng Artifact): trang gọi Claude của người đang xem.
   Trước khi dựng có bảng duyệt để sửa từng câu tiếng Anh.
8. **PDF** — thả nhiều file PDF và ảnh chụp (ảnh tự xoay đúng chiều, chọn khổ A4, lề, màu đen trắng kiểu bản scan) → lưới trang: kéo thả đổi chỗ, xoay, xóa, chọn trang. Thêm vào trang: **số trang** (6 vị trí, nhiều kiểu), **chữ đóng dấu** tiếng Việt (BẢN SAO, MẬT…), **ảnh chữ ký / con dấu / logo** (tự xóa nền trắng, ký tay bằng chuột, kéo thả vị trí), **che thông tin** (tự tìm số CCCD, số tài khoản, số điện thoại, email, MST, ngày sinh hoặc chữ tự gõ; vẽ tay vùng che; trang bị che được chuyển thành ảnh nên chữ dưới vùng che mất hẳn), **cắt lề**. Tải về: cả file, chỉ trang chọn, **tách** (mỗi trang / cứ N trang / theo khoảng), **nén** (giữ chữ, nén ảnh bên trong; hoặc chuyển trang thành ảnh cho bản scan), **xuất ảnh** JPG/PNG, **đặt mật khẩu** AES-256 và cấm in/sửa/chép. Mở được file có mật khẩu (nhập mật khẩu) và file chỉ khóa quyền. File có ô điền (form) thì **điền form** ngay trong tab, gõ tiếng Việt có dấu. Xem trước từng trang đúng như file tải về.
### Công cụ thêm (11/2026)

- **PDF → Markdown** — lấy chữ trong PDF ra file `.md` (giữ đề mục, bảng; hợp đưa vào AI, ghi chú). Chạy trên máy.
- **Dịch PDF giữ bố cục** — Claude dịch PDF **ngay trên trang**: giữ nguyên ảnh, bảng, con dấu, đường kẻ, **chỉ thay phần chữ** bằng bản dịch đặt đúng vị trí (phủ trắng chữ cũ, vẽ lại bằng phông nhúng sẵn, tự thu nhỏ cho vừa ô). Áp dụng cho PDF có lớp chữ, ngôn ngữ đích dùng chữ Latinh (Anh, Pháp, Việt…). Bản scan (không có lớp chữ) hoặc đích là tiếng Trung/Nhật/Hàn thì xuất ra Word (dựng lại). File Word nên dùng **Dịch Word/Excel giữ bố cục**. *Lưu ý: chữ gốc vẫn nằm dưới lớp phủ — in/nhìn đúng, nhưng bôi đen copy có thể ra cả chữ gốc; cần chữ sạch thì dùng "PDF sang Word".* Các công cụ Đọc PDF (Tóm tắt, Markdown, Chữ → Word, So sánh) cũng nhận file Word.
- **Word → PDF, Excel → PDF** — chuyển Office sang PDF ngay trên máy (giữ chữ, đề mục, bảng; độ chính xác bố cục mức vừa — cần đúng 100% thì dùng "Lưu/In thành PDF" trong Office).
- **Thêm chữ lên PDF** — gõ chữ, ghi chú vào bất kỳ chỗ nào trên trang (điền bản không có ô form). Chạy trên máy.
- **Công cụ ảnh**: Nén ảnh, Đổi cỡ ảnh, Đổi định dạng ảnh (JPG/PNG/WebP) — chạy trên máy bằng canvas.

### Công cụ dùng Claude (độ chính xác cao, cần mở trong Claude)

- **Soát lỗi văn bản** — Claude soát chính tả, ngữ pháp, dùng từ và văn phong hành chính của PDF/Word; đưa ra bảng từng chỗ nên sửa (loại lỗi, chỗ sai, sửa thành, ngữ cảnh, giải thích) và **bản đã sửa** tải về dạng Word.
- **Hóa đơn scan ra Excel** — Claude đọc ảnh, bản scan hóa đơn hay chứng từ giấy (không có dữ liệu XML) thành **bảng kê Excel**: mỗi hóa đơn một dòng (ký hiệu, số, ngày, MST/tên người bán – người mua, tiền trước thuế, thuế, tổng); có cột **Kiểm tra** = Trước thuế + Thuế − Tổng và dòng **Tổng theo công thức** (SUBTOTAL). Số là số, MST/số hóa đơn là chữ, ngày là ngày thật.
- **Rút trích hợp đồng** — Claude đọc hợp đồng/thỏa thuận và rút các mục quan trọng (các bên, đối tượng, giá trị, thanh toán, thời hạn, nghĩa vụ, phạt, chấm dứt, hiệu lực…) ra **bảng Excel 2 cột** Mục – Nội dung, giữ đúng số tiền, ngày, tỷ lệ.

### Trang Công cụ kế toán (riêng, `#ke-toan`)

Trang riêng cho kế toán, tách khỏi công cụ văn phòng — bấm **Kế toán** trên đầu trang. Chạy hoàn toàn trên máy.

Mỗi công cụ ghi rõ ngay trên trang: **dùng khi nào · thả gì vào · ra kết quả gì**. Công cụ chỉ *khoanh vùng để soát*, không kết luận thay kế toán.

- **Soát khấu trừ thuế GTGT đầu vào** — thả bảng kê hóa đơn **mua vào** (tải từ cổng hóa đơn điện tử); tự nhận cột rồi đánh dấu hóa đơn **có nguy cơ không được khấu trừ**: từ 5 triệu ghi **thanh toán tiền mặt**, hóa đơn bị **thay thế/hủy/điều chỉnh**, **trùng** (cùng ký hiệu–số–MST người bán), **tiền thuế lệch** so với thuế suất, dấu hiệu **chia nhỏ hóa đơn** (nhiều HĐ cùng người bán/ngày, mỗi cái dưới 5 triệu). Kết quả: danh sách hóa đơn cần soát kèm lý do → tải Excel.
- **Đối chiếu sao kê ngân hàng với sổ 112** — thả **sao kê** và **sổ chi tiết tiền gửi 112**; tự ghép từng giao dịch theo **chiều tiền, số tiền và ngày** (cho phép lệch ngày tùy chọn). Kết quả: khoản hai bên **khớp**; khoản **ngân hàng có mà sổ chưa ghi** (phí, lãi…); khoản **sổ ghi mà ngân hàng chưa có**; khoản **khớp tiền nhưng lệch ngày** → tải Excel. *(Quy ước chiều tiền: tiền vào tài khoản là cột ghi Có của sao kê và cột Nợ của sổ 112 — trang tự nhận theo đó.)*
- **Biên bản đối chiếu công nợ 131/331** — thả bảng công nợ (sổ chi tiết phải thu 131 / phải trả 331), tự tìm dòng tiêu đề và nhận 6 cột (mã, tên, dư đầu kỳ, phát sinh Nợ/Có, dư cuối kỳ — chỉnh tay được) → xuất **mỗi khách hàng/nhà cung cấp một biên bản** đúng mẫu (Quốc hiệu, hai bên, bảng số liệu, **số tiền bằng chữ tự động**, chỗ ký), gộp vào **một file Word** chuẩn (mở được ở Word, LibreOffice, Google Docs).

**Định dạng số (bảng/file xuất ra):** số có dấu phân tách hàng nghìn — file Excel hiển thị theo ngôn ngữ máy, PDF dùng kiểu Việt Nam (1.500.000); **giữ nguyên phần thập phân, không tự làm tròn**.

9. **Đọc PDF** — bốn việc: **Bảng → Excel** (sao kê, bảng kê; dòng "Tổng theo công thức" là SUBTOTAL, dòng tổng có sẵn trên tài liệu được đặt riêng và so với công thức; ngày thành ngày thật, số thành số), **Chữ → Word** (file .docx thật, có nút chuyển thẳng sang tab Dịch song ngữ), **Tóm tắt**, **So sánh 2 bản** (chỗ thêm/bỏ tô màu, tải báo cáo .docx, AI tóm tắt các thay đổi). Hai cách đọc: *chữ có sẵn trong file* (chạy trên máy, dùng được ở bản GitHub) hoặc *AI đọc hình trang* cho bản scan, ảnh chụp, bảng phức tạp (chỉ khi mở trong Claude; gửi hình trang cho Claude bằng tài khoản của người dùng).

**Nguyên tắc file Excel xuất ra:** số lấy từ hóa đơn giữ nguyên là số; mọi ô tổng, kiểm tra, tổng hợp đều là **công thức** (SUBTOTAL cho dòng tổng nên lọc vẫn cộng đúng; cột Kiểm tra = Chưa thuế + Thuế − Tổng và SL × ĐG − Thành tiền, khác 0 là hóa đơn có vấn đề; sheet Theo thuế suất tính bằng công thức từ sheet Thue theo HD và tự đối chiếu ngược về Bảng kê). Sheet Lệch của công cụ Đối chiếu cũng có cột Chênh lệch dạng công thức.

Mọi nút đều có **"Chép"** (dán thẳng vào Excel/Word, chạy ở mọi nơi) và **"Tải file"** (.xlsx/.docx).

---

## Dùng ngay không cần cài

Mở file `index.html` bằng trình duyệt (nhấp đúp). Xong — dùng được luôn, kể cả khi không có mạng (cần mạng để tải thư viện xử lý Excel/Word/PDF lần đầu dùng).

## Đưa lên GitHub Pages (để có link `tên-bạn.github.io` dùng mọi lúc)

1. Tạo tài khoản GitHub (nếu chưa có) tại https://github.com
2. Bấm **New repository** → đặt tên, ví dụ `cong-cu-van-phong` → **Create repository**.
3. Vào repo vừa tạo → **Add file → Upload files** → kéo thả **cả thư mục này** (`index.html`, `README.md`, `.nojekyll`) → **Commit changes**.
4. Vào **Settings → Pages** → mục **Branch** chọn `main` (thư mục `/root`) → **Save**.
5. Đợi 1–2 phút, GitHub hiện link dạng **`https://tên-github-của-bạn.github.io/cong-cu-van-phong/`**. Mở link đó là dùng được, chia sẻ cho ai cũng mở được.

### Nếu quen dùng dòng lệnh (git)

```bash
cd tro-ly-excel-cua-toi
git init
git add .
git commit -m "Hộp công cụ Văn phòng"
git branch -M main
git remote add origin https://github.com/TEN-CUA-BAN/cong-cu-van-phong.git
git push -u origin main
```

Rồi bật GitHub Pages như bước 4 ở trên.

---

## Ghi chú kỹ thuật

- Toàn bộ xử lý nằm trong `index.html`. Thư viện dùng: [SheetJS](https://sheetjs.com) (đọc/ghi Excel), [html-docx-js](https://github.com/evidenceprime/html-docx-js) (xuất Word), [JSZip](https://stuk.github.io/jszip/) (dựng file song ngữ), [docx-preview](https://github.com/VolodymyrBaydalka/docxjs) (xem trước, chỉ nạp khi bấm), [pdf.js](https://mozilla.github.io/pdf.js/) (vẽ trang PDF), [@cantoo/pdf-lib](https://github.com/cantoo-scribe/pdf-lib) (sửa PDF, đặt/mở mật khẩu), [fontkit](https://github.com/Hopding/fontkit), [jsdiff](https://github.com/kpdecker/jsdiff) (so sánh); thư viện PDF chỉ nạp khi mở tab PDF, từ CDN công khai.
- Phông **Tinos** (bản rút gọn Latin + tiếng Việt, giấy phép SIL Open Font License 1.1, © The Tinos Project Authors) được nhúng sẵn để viết số trang, chữ đóng dấu, nội dung form tiếng Việt vào PDF.
- Tab Song ngữ chỉ gửi **phần chữ** cho Claude khi bạn bấm dịch (hoặc bạn tự chép sang khung chat); bố cục file được xử lý ngay trên máy.
- Tab PDF xử lý hoàn toàn trên máy. Tab Đọc PDF chỉ gửi hình trang hoặc chữ cho Claude khi bạn chọn cách **AI đọc hình trang** hoặc **Tóm tắt**.
- File `.nojekyll` để GitHub Pages phục vụ file nguyên trạng.
- Không có máy chủ, không có cơ sở dữ liệu, không thu thập dữ liệu. File bạn mở chỉ nằm trên máy bạn.
