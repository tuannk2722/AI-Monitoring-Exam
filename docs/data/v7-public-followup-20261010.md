# v7 public follow-up sau R8 execution

Status: Draft, bàn giao nghiên cứu ngày2026-10-10. Owner: chủ repository, nghiên cứu cá nhân. Hướng đi được yêu cầu là tìm nguồn mới trong lúc chờ author access; không train E004/release v7/model independent holdout.

[Báo cáo](../../artifacts/reports/pilot-b-v7-public-followup-20261009/README.md) và [review R4](../../outputs/v7-public-followup-review-20261009-r4/review-index.html) là snapshot mới, giữ R8 execution/R7/audit/v4–v6/historical artifacts bất biến. Owner báo đã gửi requests; receipt mới không hồi tố những receipt trước đó ghi chưa gửi.

367unique Commons metadata pages,206metadata eligible,95ảnh tải/xem,13crop Draft từ11source. Phone7P2N4U/looking2P5N6U;3fully-known,PP1PN1NP0NN1. Đúngclassroom desk-phone chỉ1P/2N;1same-image looking pair auxiliary,1same-room/session pair proposal classroom.10visualfamilies,0independence proven. Không có train-eligible mới; không dùng count10family để lập split.

Lưu ý review: A002 eyes che nên lookingU; A007 shared screen gazeU; C003 P phải owner xác nhận outside-own-workarea trong Q&A; D001 phone teacher không gán student; D002 own-mobile thuộc người phải, device người giữa unknown. A001 computer-room purpose chưa xác minh; workshop/home/event ngoài strictdomain. Masks0/targetsnull/splitnull/trainingfalse tách labelproposal khỏi canonical dataset.

Canonical intake/discovery/recovery/review/report nằm ở [module](../../src/ai_exam_monitoring/data/v7_public_photo_gapfill.py). [Config report](../../configs/datasets/pilot_b_v7_public_followup_report_20261010.yaml) pin metadata/ledger/observations/review; [config review R4](../../configs/datasets/pilot_b_v7_public_followup_review_r4_20261009.yaml) pin E003224RGBletterbox. CLI `python -m ai_exam_monitoring.data.v7_public_photo_gapfill {discover,recover,screen,review,report} --config <yaml>` từ repo với `PYTHONPATH=src`; mỗi output phải version mới. Không chạy lại ghi đè sealed output.

Theo [source research](../../artifacts/reports/pilot-b-v7-public-followup-20261009/source-research.md), ưu tiên follow-up HCMUE-SEGL inventory/access và public classroom galleries có room/session. Online-exam license còn blocked; CDED7 cần scope-use decision; UCB chưa file inventory. Các nguồn chưa payload có0yield, không coi public metadata thành sample hữu ích. [Owner decisions](../../artifacts/reports/pilot-b-v7-public-followup-20261009/owner-decisions.md) là bảng cần nghiệm thu, không chuyển proposal thành Accepted. Release/promotion vẫn cần thiếu hụt, graph/rights, holdout/experiment/gates được đóng theo canonical ADR/spec.
