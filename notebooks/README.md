# Notebooks

Notebook dùng cho khám phá, trực quan và launcher Colab. Canonical logic phải import từ `src/`; không copy một phiên bản `train.py` riêng vào notebook. Trước khi commit, xóa output chứa ảnh/video, token, đường dẫn cá nhân hoặc dữ liệu nhạy cảm.

Trainer/evaluator B chưa triển khai; chưa có launcher training dùng được. Các bước dưới chỉ áp dụng sau khi experiment/model/config và phạm vi xử lý trên Colab được owner duyệt.

Bootstrap Colab sau khi đạt gate:

1. clone repo và checkout commit cụ thể;
2. cài `requirements/ml.txt` và `requirements/dvc.txt`;
3. authenticate DVC bằng secret, `dvc pull`;
4. chạy smoke 1–3 epoch bằng trainer B canonical khi đã triển khai; launcher YOLO cũ đã gỡ;
5. sync checkpoint/metrics lên DVC remote ngay trong run;
6. commit experiment card/config/metrics nhỏ qua PR.
