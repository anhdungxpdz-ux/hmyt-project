# HMYT Project — Repo Nộp Bài Chung Của Lớp

Repo này là nơi **sinh viên môn Học Máy trong Y Tế (ET4248)** nộp bài đồ án
theo đề tài đã chọn trong [Ngân hàng đề tài](https://fossbk-spec.github.io/hmyt-book/du_an_mon_hoc).

- **Đề bài, y văn, workflow chi tiết:** xem tại
  [hmyt-book](https://fossbk-spec.github.io/hmyt-book/) — repo này **không**
  chứa lại đề bài, chỉ chứa bài làm của sinh viên.
- **Mỗi nhóm = 1 thư mục riêng** dưới `submissions/`, đặt tên theo đúng quy
  ước ở [CONTRIBUTING.md](CONTRIBUTING.md).
- **Nộp bài qua Pull Request** — không push trực tiếp vào `main`. Xem quy
  trình đầy đủ trong [CONTRIBUTING.md](CONTRIBUTING.md).

## Vì sao dùng Pull Request thay vì push trực tiếp?

1. **Cách ly giữa các nhóm** — mỗi PR chỉ được phép đổi file trong đúng 1
   thư mục `submissions/<đề-tài>_<mã-nhóm>/` của nhóm đó. CI tự động chặn
   PR nếu đụng vào thư mục của nhóm khác (xem
   `.github/workflows/validate-submission.yml`).
2. **Không mất bài** — lịch sử Git giữ nguyên toàn bộ commit của từng nhóm;
   `main` chỉ nhận bản đã qua kiểm tra tự động + giảng viên duyệt.
3. **Không nộp nhầm/nộp thiếu** — CI kiểm tra cấu trúc thư mục, file bắt
   buộc (`submission.json`, `README.md`), và chặn các mẫu hình dữ liệu
   nhạy cảm phổ biến (khóa API, thông tin bệnh nhân thật) trước khi merge.

## Cấu trúc repo

```
htmy-project/
├── submissions/
│   ├── _TEMPLATE/                  ← Copy thư mục này để bắt đầu nộp bài
│   │   ├── submission.json         ← Thông tin nhóm + đề tài (bắt buộc)
│   │   ├── README.md               ← Tóm tắt bài làm (bắt buộc)
│   │   ├── report/                 ← Báo cáo (PDF/Markdown)
│   │   ├── src/                    ← Mã nguồn
│   │   └── slides/                 ← Slide thuyết trình (tuỳ chọn)
│   │
│   └── <topic_slug>_<ma_nhom>/     ← 1 thư mục nộp bài của 1 nhóm
│       └── ... (giống cấu trúc _TEMPLATE)
│
├── scripts/validate_submission.py  ← Script CI dùng để kiểm tra PR
├── .github/workflows/validate-submission.yml
├── CONTRIBUTING.md                 ← Hướng dẫn nộp bài chi tiết từng bước
└── CODEOWNERS                      ← Định tuyến review PR tới giảng viên/TA
```
