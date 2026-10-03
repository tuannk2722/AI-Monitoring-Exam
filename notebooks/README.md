# Notebooks

Notebook dùng cho khám phá, trực quan và launcher Colab. Canonical logic phải import từ `src/`; không copy một phiên bản `train.py` riêng vào notebook. Trước khi commit, xóa output chứa ảnh/video, token, đường dẫn cá nhân hoặc dữ liệu nhạy cảm.

Bootstrap Colab chuẩn:

1. clone repo và checkout commit cụ thể;
2. cài `requirements/ml.txt` và `requirements/dvc.txt`;
3. authenticate DVC bằng secret, `dvc pull`;
4. chạy `scripts/benchmark_training.py` trước full run;
5. sync checkpoint/metrics lên DVC remote ngay trong run;
6. commit experiment card/config/metrics nhỏ qua PR.
