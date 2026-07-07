# BTL_Phan_Loai_Khoi_U

## Tổng quan

Dự án này xây dựng một hệ thống trí tuệ nhân tạo nhằm hỗ trợ nhận diện và phân loại khối u não từ ảnh MRI. Hệ thống sử dụng một mô hình mạng nơ-ron tích chập (CNN) để phân biệt các loại bệnh lý phổ biến trên ảnh chụp não, bao gồm:

- Glioma (u thần kinh đệm)
- Meningioma (u màng não)
- No-tumor (không có u)
- Pituitary (u tuyến yên)

## Cách hệ thống hoạt động

1. Người dùng tải ảnh MRI lên giao diện web.
2. Ảnh được chuẩn hóa và chuyển đổi về định dạng phù hợp để đưa vào mô hình.
3. Mô hình CNN thực hiện dự đoán và trả về nhãn phân loại cùng với độ tin cậy của kết quả.
4. Giao diện hiển thị hình ảnh đầu vào và kết quả phân loại một cách trực quan.

## Cấu trúc dự án

- Model.py: định nghĩa kiến trúc mạng CNN dùng cho huấn luyện và dự đoán.
- Main.py: xử lý dữ liệu ảnh từ bộ dữ liệu MRI và chuẩn bị dữ liệu cho mô hình.
- app.py: giao diện ứng dụng web bằng Streamlit, cho phép người dùng nhập ảnh và xem kết quả.
- brain_tumor_model.pth: file trọng số mô hình đã được huấn luyện trước.
- Get_Test_Images.py, Viewdata.py, bieudophanbo.py: các thành phần hỗ trợ xem dữ liệu và trực quan hóa kết quả.

## Công nghệ sử dụng

- Python
- PyTorch
- Torchvision
- Streamlit
- Pillow
- Datasets

## Quy trình dự án

- Bước 1: Thu thập và tiền xử lý dữ liệu ảnh MRI.
- Bước 2: Xây dựng và huấn luyện mô hình CNN.
- Bước 3: Lưu trọng số mô hình vào file .pth.
- Bước 4: Tải mô hình vào ứng dụng web để thực hiện dự đoán trực tiếp trên ảnh mới.

## Cách chạy ứng dụng

Cài đặt các thư viện cần thiết:

```bash
pip install streamlit torch torchvision pillow datasets
```

Chạy giao diện web:

```bash
streamlit run app.py
```

## Lưu ý

Để mô hình có thể load đúng từ file brain_tumor_model.pth, kiến trúc CNN trong Model.py và app.py phải khớp với kiến trúc đã dùng khi huấn luyện.
