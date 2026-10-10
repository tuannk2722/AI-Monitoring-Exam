# Pilot B v7 — release local đã nghiệm thu

Owner quyết định **“Duyệt batch và ký release v7 local”** ngày 2026-10-10. Đã đóng canonical dataset **pilot-b-20261010-v7**, scope `local_classifier_research`.

[Config accepted](../../../configs/datasets/pilot_b_release_v7.yaml) · [Owner approval](owner-approval.json) · [Dataset card](../../../data/processed/pilot-b/pilot-b-20261010-v7/dataset-card.md) · [Release pointer](release-pointer.json).

| Nội dung | Count |
|---|---:|
| Train | 689 |
| Validation | 49 |
| Test giữ từ v6 | 11 |
| Manifest sử dụng | 749 |
| Review-only | 122 |
| Excluded | 29 |
| Toàn decision ledger | 900 |
| Crop được xuất | 871 |

**Chỉ dùng [manifest.jsonl](../../../data/processed/pilot-b/pilot-b-20261010-v7/manifest.jsonl) cho training/evaluation được duyệt riêng**, không lấy toàn thư mục crops. [Review ledger](../../../data/processed/pilot-b/pilot-b-20261010-v7/review-ledger.jsonl) giữ đầy đủ review-only/excluded. 122 crop review-only nằm ngoài supervision; 29 excluded chỉ có metadata.

## Đã thực hiện theo quyết định owner

Input là [gói owner execution đã sealed](../pilot-b-v7-owner-execution-20261010/README.md), [crop/source/input224 R3](../../../outputs/v7-owner-execution-20261010-r3/REVIEW.md) và [release preparation R2](../../../outputs/v7-local-release-preparation-20261010-r2/REVIEW.md). Receipt pin đúng assignment, whole-family, rights, crop ledger/checksums, parent corrections và pointer đã nghiệm thu. Không sửa package review lịch sử sau approval.

Pool bổ sung 402 crop gồm 274 R5 đã duyệt trước, 29 crop consolidated đã review và 99 crop mới từ nguồn được owner approve. 375 crop bổ sung vào train theo final acceptance; 21 U/U review-only, 5 crop còn blocker review-only và 1 evaluation-family excluded. 14 source reserve ngoài pool crop vẫn được giữ ở report review với lý do.

| Record giữ review-only | Lý do |
|---|---|
| V7-OE-S005-A01 | Flickr landing 404 |
| V7-OE-S020-A01 | Flickr landing 403 |
| V7-OE-S027-A01 | Metadata hiện tại thiếu license, không tự đổi license snapshot |
| V7-OE-S034-A01 | Flickr landing 404 |
| V7-OE-S080-A01 | Boundary liên quan parent group có val chưa đủ evidence giải phóng |

Quyền nguồn đã owner xác nhận được kế thừa; creator/title/source page/license và changes notice của public media giữ trong [source provenance](new-source-provenance.jsonl), selection và [rights acceptance](rights-acceptance.jsonl). Bốn blocker không được biến thành đủ quyền vì crop/label đã approve. Chỉ local, không redistribution, remote DVC hoặc media upload.

Parent v6 giữ nguyên trên đĩa. Trong v7, 49 parent reviews đã duyệt dẫn tới 9 record thay đổi: 6 target corrections, 2 domain notes và 1 exclusion; ba record U/U ra khỏi supervision. Parent đóng góp 314 train/49 val/11 test, cộng 375 train mới thành 689/49/11. [Parent delta và domain metadata](parent-corrections.jsonl). Domain notes nằm trong selection/provenance, không thêm target mới.

R8-C005 giữ U/U theo owner vì gaze mờ. S109 phone P khi giữ được mobile dưới bàn và đúng người cầm; S113 phone U khi evidence chưa đủ. Nhãn mobile-only theo ADR018; unknown luôn null/mask0. Không đổi calculator/book/badge thành mobile hoặc gán device người khác cho anchor.

## Whole-family, coverage và test freeze

900 record thuộc 449 conservative components; manifest749 dùng 392 group (375 train,14 val,3 test). Đã nghiệm thu whole-family và assignment cụ thể, không random split. Exact source/crop SHA và group không đi qua nhiều split. Unique hash/component không chứng minh session/person độc lập; **new independence proven vẫn 0**.

| Split | Phone P/N/U | Looking P/N/U | Fully-known |
|---|---|---|---:|
| Train689 | 233/184/272 | 210/277/202 | 215 |
| Val49 | 16/20/13 | 17/12/20 | 16 |
| Test11 | 2/2/7 | 2/7/2 | 2 |

Coverage thật ở [coverage.json](../../../data/processed/pilot-b/pilot-b-20261010-v7/reports/coverage.json). Train có P/N cho cả hai target; U bị mask khỏi loss/metric. Fully-known hoặc số crop không phải acceptance metric của model. Val49 khác E003 về cohort và target support sau correction, không so scalar BCE như cùng tập.

11 test giữ ID/source/crop/target/context/rights và evidence freeze gốc; group ID và version đóng gói chuyển sang assignment whole-family v7 đã nghiệm thu. Inline freeze pin manifest/split/test serialization mới, không chọn lại test. Exporter chỉ hash/decode/copy để kiểm integrity; không tính feature/prediction hoặc tuning test. Loader từ chối select test nếu không có explicit final-test access.

## Validation và tái tạo

[Verification](verification.json) và [rebuild verification](rebuild-verification.json):

- Schema/usage/target mask của 900 record, manifest749, assignment và inline freeze PASS; canonical loader đọc đúng 689 train/49 val.
- 498 parent records giữ source/crop SHA và geometry; v6 manifest SHA `9fac24a0…` không đổi. Test11 bảo toàn targets/context/rights/crop/evidence gốc; các correction chỉ trong version mới.
- 871 crop file khớp hash; 375 crop train mới letterbox224 khớp nguyên pixel input224 đã review. Cả hai unknown không xuất trong manifest.
- 10 ZIP intake source local deterministic có hash giống rebuild; original upstream registry/archive/page/video provenance vẫn giữ riêng, không gọi ZIP local là archive upstream mới tải.
- Canonical exporter tái tạo crop/ledger/manifest/assignment/selection/reports/schema/release từ pinned sources. Dataset card tiếng Việt là metadata đã review được giữ nguyên; toàn package rebuild so SHA từng file.
- **257 tests PASS**, Ruff `src/tests/scripts` PASS, mypy ba module mới PASS, `git diff --check` PASS, repository checker failures0 (Git index, không bao gồm untracked).

Logic release ở [v7_release_acceptance.py](../../../src/ai_exam_monitoring/data/v7_release_acceptance.py), dùng schema và exporter hiện có. Lệnh tái tạo trong workspace phục hồi có đủ pinned inputs và chưa tồn tại output/cache:

```powershell
$env:PYTHONPATH = 'src'
outputs/E001-env/Scripts/python.exe -X utf8 -m ai_exam_monitoring.data.v7_release_acceptance --config configs/datasets/pilot_b_release_v7.yaml
```

Builder từ chối ghi đè release/cache. [Provenance](provenance.json) ghi source/config/input SHA, Git commit nền và dirty workspace; chưa commit/push. [Finalization trước pointer đầu](prepublication-metadata-finalization.json) ghi việc sửa dấu tiếng Việt của mô tả YAML bị stdin PowerShell chuyển thành `?` và dùng đúng serializer cuối; manifest/split/crop không đổi. Rebuild ban đầu có JSON tương đương nhưng khác byte serialization của `release.json`; đã sửa quy trình kiểm để khớp canonical serializer và kiểm lại.

## Phạm vi hoàn tất và bước tiếp theo

Đã hoàn tất nhập quyết định, crop/annotation QA, whole-family/rights, final acceptance và đóng release v7 local. Bản chuẩn bị 694/49/11 là upper bound lịch sử; 689/49/11 mới là release accepted sau kiểm gate. Các báo cáo cũ và mismatch seal R7/R8/source-funnel được giữ nguyên, không reseal hoặc suy nguyên nhân.

E004 training cần config/recipe/compute/metric và approval riêng; independent real-world holdout và crop runtime vẫn là gate riêng. Không train model, inference test, upload, remote DVC, HTML hoặc dashboard trong task này. Release dataset không chứng minh model promotion/generalization.
