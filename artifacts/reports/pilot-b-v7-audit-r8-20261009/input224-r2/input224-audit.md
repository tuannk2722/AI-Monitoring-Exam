# Kiểm evidence sau preprocessing224 — R7 Draft

Đã xem đúng80 B và39 D qua30 sheets gồm source/crop/native224/nearest448. Một số device/visibility flags đã xem thêm source gốc như ghi từng hàng. Dùng RGB/BILINEAR letterbox224/fill[124,116,104] từ E003 đã pin; PNG trước normalize, không inference. Nearest448 không thêm thông tin. Clear/ambiguous/lost là nhận xét qualitative, không threshold hoặc acceptance gate mới.

R7 crop/nhãn giữ bất biến. Source label proposal và input224 usability là hai vấn đề khác nhau: ambiguity224 không tự downgrade P nguồn rõ. Ca source thiếu device/own-workarea evidence cần owner review. Supplemental delta chỉ là Draft; root final recrop/owner overrides có precedence và cần xem ảnh mới.

| ID | R7 phone/looking | Source/crop/224 | Lý do cuối cho QA |
|---|---|---|---|
| V7-B-001 | P/U | clear/clear/clear | Nữ áo hoa bên phải cầm mobile đen trên giấy của mình; còn thấy thân thiết bị giữa hai tay ở224; looking U vì chưa chốt own gaze. |
| V7-B-002 | N/N | clear/clear/clear | Anchor áo trắng đang viết trong sách mở, hai tay ở vùng bài; low-resolution nhưng tay/giấy còn phân biệt ở224, không thấy mobile trong vùng này. |
| V7-B-003 | P/U | clear/clear/clear | Nam áo plaid cầm mobile đen bằng hai tay; tay của người bên trái hướng tới máy nhưng không thay anchor; thân phone còn rõ ở224. |
| V7-B-005 | P/U | clear/clear/clear | Nữ áo hồng cầm mobile trắng; mặt lưng và ownership giữa hai tay vẫn rõ sau224. |
| V7-B-007 | P/U | clear/clear/clear | Nữ áo sọc tím cầm mobile đỏ trên bàn/giấy, còn thấy thân máy và liên kết tay ở224. |
| V7-B-009 | P/U | clear/clear/clear | Nam áo xanh foreground cầm smartphone trắng màn hình sáng; hai tay và màn hình rõ ở224. |
| V7-B-010 | N/N | clear/clear/clear | Nữ tiền cảnh áo xanh viết giấy, tay viết và tay giữ giấy còn nhìn được; phone N không dựa trên absence annotation. |
| V7-B-011 | P/U | clear/clear/clear | Nam bên trái thao tác smartphone trắng dưới bàn; ownership trực tiếp ở tay, màn hình còn rõ ở224. |
| V7-B-013 | P/U | clear/clear/clear | Nữ plaid tiền cảnh cầm mobile vàng; người bên phải cũng có own phone nhưng không gán máy đó cho anchor; phone anchor rõ224. |
| V7-B-015 | P/U | clear/clear/clear | Nữ tóc xoăn áo denim cầm mobile đen trong nhóm; tay cầm và thân máy đọc được224, gaze nhóm giữ U. |
| V7-B-016 | N/N | clear/clear/clear | Người áo trắng ở giữa cúi xuống sách và viết; source thấp phân giải, nhưng còn phân biệt bút/tay/giấy ở224; không suy head tilt thành looking P. |
| V7-B-017 | P/U | clear/clear/clear | Trẻ áo đỏ tiền cảnh cầm phone đen bằng hai tay; trẻ phía sau giữ own device, ownership anchor còn rõ224. |
| V7-B-018 | N/N | clear/clear/clear | Anchor áo vàng viết giấy trên bàn riêng; hai tay và bút thấy được224 dù nhiều học sinh cùng crop. |
| V7-B-019 | P/U | clear/clear/clear | Anchor áo sọc tiền cảnh giữ mobile đen/đỏ; có nhiều device/person nhưng tay anchor liên kết trực tiếp, còn rõ224. |
| V7-B-020 | N/N | clear/clear/clear | Nữ tiền cảnh áo trắng đọc/viết giấy của mình, hai tay đặt bài; cả source có watermark/noise nhưng evidence N còn đọc được224. |
| V7-B-021 | P/U | clear/clear/clear | Nam áo cam giữa hàng giữ mobile dựng; phone nhỏ nhưng thân đen và hai tay còn phân biệt ở224. |
| V7-B-022 | N/N | clear/clear/clear | Anchor áo trắng bên phải viết giấy; mặt bị giới hạn cạnh source, tay viết/bàn vẫn đủ quan sát cho phone N; không dùng mặt bị cắt làm device evidence. |
| V7-B-023 | P/U | clear/clear/clear | Anchor trái áo xanh có thiết bị đen cầm ngang và mobile đen trên bàn ngay vùng của mình; phone P có desk evidence, không chỉ dựa thiết bị cầm ngang. |
| V7-B-024 | N/N | clear/clear/clear | Trẻ áo sọc đỏ giữa crop có tay/bài trên bàn, không thấy mobile ở vùng anchor; còn đọc được224 nhưng người foreground che một phần bàn. |
| V7-B-025 | P/U | clear/clear/clear | Người đội khăn từ camera cao cầm mobile sáng màn hình gần bàn laptop; thiết bị/tay rõ224, looking giữ U. |
| V7-B-026 | N/N | clear/clear/clear | Trẻ áo xám viết bằng bút chì, tay kia giữ giấy; hai tay và bút/giấy rõ224, hỗ trợ N/N. |
| V7-B-027 | P/U | clear/clear/clear | Nữ tiền cảnh thư viện giữ phone case xanh/hồng ngang; thân phone và hai tay rõ224, looking U vì ngữ cảnh tương tác chưa chốt own gaze. |
| V7-B-028 | N/N | clear/clear/clear | Nữ áo vàng tiền cảnh viết giấy; bút, tay viết, tay giữ bài rõ224, phone N trong vùng quan sát. |
| V7-B-029 | P/U | clear/clear/ambiguous | Đã xem source512: mobile màu vàng/đen nằm giữa hai tay nam áo đen; ở224 thân máy chỉ còn phần mép nhỏ giữa ngón tay, identity yếu. Giữ source P Draft, cần owner quyết usability224. |
| V7-B-030 | N/N | clear/clear/clear | Người áo trắng/xanh ở giữa viết giấy; crop chứa nhiều học sinh lớn nên cần explicit unit, evidence tay/bài anchor còn đọc được224. |
| V7-B-031 | P/U | clear/clear/clear | Nam áo xám nhìn mobile trắng trong tay; neighbor chạm máy nhưng hai tay anchor giữ rõ, phone vẫn đọc được224. |
| V7-B-032 | N/N | ambiguous/ambiguous/ambiguous | Đã xem source640: anchor đeo kính/khăn đỏ phía giữa sau foreground bị đầu người phía trước và túi che own desk/tay; không đủ chứng minh mobile N hay own-workarea looking N. Đề xuất U/U pending owner, không dùng source label để điền N. |
| V7-B-034 | N/N | clear/clear/clear | Nữ tiền cảnh đặt hai tay trên bàn/vở; source nén mạnh nhưng tay/bài đủ phân biệt224, không thấy mobile vùng anchor. |
| V7-B-035 | P/U | clear/clear/ambiguous | Đã xem source512: nam áo đỏ/plaid trong lớp giữ vật trắng dạng phone giữa hai tay; source nhỏ, tại224 chỉ còn cụm sáng/fingers mờ, giữ source P Draft và yêu cầu owner usability/device review. |
| V7-B-039 | P/U | clear/clear/clear | Nam áo xám giữ mobile đen trên sách mở; thân máy/tay vẫn rõ224, gaze chưa chốt riêng giữ U. |
| V7-B-040 | N/N | clear/ambiguous/ambiguous | Người áo xám ở giữa đang viết giấy, N/N source hợp lý; crop có nam áo sọc foreground lớn bị cắt mặt và che workarea. Owner đã yêu cầu recrop tập trung anchor, phải QA crop mới. |
| V7-B-041 | P/U | clear/clear/ambiguous | Đã xem source512: hai nữ foreground chia sẻ phone trắng gần tay nữ áo tím; máy lộ partial dưới ngón tay,224 rất nhỏ và crop có hai unit lớn. Giữ source P Draft với explicit holder; owner review anchor/usability. |
| V7-B-042 | N/N | clear/clear/clear | Anchor áo xanh bên phải viết giấy, phone N trong vùng tay/bài; crop dọc làm người nhỏ và mặt cắt cạnh source, vẫn đọc được hoạt động ở224. |
| V7-B-043 | P/U | clear/clear/clear | Nữ cardigan nâu giữ phone nhỏ đen trên bàn; thân máy và tay đọc được224, source ownership trực tiếp. |
| V7-B-046 | N/N | clear/clear/clear | Trẻ áo xanh viết bằng bút chì, tay còn lại giữ giấy; hai tay và vùng bài rõ224, hỗ trợ N/N. |
| V7-B-047 | P/U | clear/clear/clear | Nam áo navy cầm mobile ngang thấp trước bàn máy tính; máy nhỏ nhưng outline và hai tay còn đọc được224; không nhầm mouse/laptop thành phone. |
| V7-B-048 | N/N | clear/lost/lost | R7 unit foreground-pink-girl nhưng crop chỉ giữ tay/cạnh người áo hồng bên phải, thiếu head và own-workarea, trong khi người áo tím lớn chiếm crop. Source có thể recrop người áo hồng đang viết; root đã đề xuất bbox mới N/N, cần QA phiên bản mới. |
| V7-B-049 | P/U | clear/clear/clear | Nữ áo xám tiền cảnh giữ mobile trắng; có nhiều person/device nhưng liên kết trực tiếp tay anchor, máy đọc được224; cần explicit unit. |
| V7-B-051 | P/U | clear/clear/clear | Nam tóc vàng áo hoodie cầm phone đen gần mặt, hai tay trực tiếp; partial phone nhưng outline đọc được224, phone foreground khác không gán anchor. |
| V7-B-053 | P/U | clear/clear/clear | Nam áo trắng giữa lớp thao tác phone đen nhỏ bằng hai tay; mobile khác trên bàn bên dưới không thay ownership; device anchor rõ224. |
| V7-B-055 | P/U | clear/clear/clear | Nữ đeo kính bên trái cầm mobile đỏ trên giấy; nữ neighbor xem/chạm nhưng anchor holding rõ224, looking giữ U. |
| V7-B-057 | P/U | ambiguous/ambiguous/ambiguous | Đã xem source512: nữ tiền cảnh giữ hình chữ nhật trắng rất nhỏ sát trang sách; chưa đọc được rõ mobile identity so với paper/card ở cả source và224. Source P vẫn là proposal pending device review, không tính đã nghiệm thu hoặc guaranteed phone evidence. |
| V7-B-059 | P/U | clear/clear/clear | Nữ áo trắng foreground phải giữ mobile vàng nhỏ bằng hai tay; case/outline và linked hands còn đọc được224. |
| V7-B-061 | P/U | ambiguous/ambiguous/ambiguous | Đã xem source512: nam áo trắng tiền cảnh giữ vật gần như che toàn bộ bởi hai bàn tay; chỉ lộ mép rất nhỏ, chưa chắc mobile identity;224 không khôi phục chi tiết. P nguồn vẫn pending owner device review, không coi posture cầm là chứng minh mobile. |
| V7-B-062 | N/N | clear/clear/clear | Anchor áo trắng ở tiền cảnh trái cúi xuống bài, tay gần mặt và vùng sách/bàn thấy được; giữ N/N Draft, foreground head làm evidence nhỏ ở224. |
| V7-B-063 | P/U | clear/clear/clear | Nam áo xám đeo kính cầm smartphone đen thấp trên bàn ghế; thân máy và tay còn rõ224. |
| V7-B-065 | P/U | clear/clear/clear | Nam áo cyan giữ phone nhỏ sát bụng bằng tay phải, tay kia ở giấy; linked device còn phân biệt224 dù phone rất nhỏ. |
| V7-B-066 | N/P | clear/ambiguous/ambiguous | Anchor background-middle-boy có hai cẳng tay trên bàn và đang quay sang bên; R7crop cắt cạnh phải mặt/tay và nhiều foreground che workarea, phone absence tại224 yếu. Source N/P còn pending crop/anchor review; không suy P phone từ neighbor. |
| V7-B-067 | P/U | clear/clear/clear | Nam áo đen cầm mobile nhỏ bên tay trái/lap trong phòng thiết bị; cạnh máy/linked hand còn phân biệt224, earphone cable không là device evidence độc lập. |
| V7-B-069 | P/U | clear/clear/clear | Nam áo caro cầm mobile đen giữa tay thấp; người foreground nhìn sang không thay anchor, phone còn đọc được224. |
| V7-B-071 | P/U | clear/clear/clear | Nữ áo xanh cầm smartphone tím ngang trên desk; screen/outline và linked hands rõ224, auxiliary context giữ looking U. |
| V7-B-073 | P/U | clear/clear/clear | Nam sơ mi trắng/dây đỏ giữa crowd cầm smartphone xanh; device trong tay mình rõ224, thiết bị neighbor không gán nhầm. |
| V7-B-074 | P/U | clear/clear/clear | Nam áo nâu cầm mobile đen có màn hình lớn sát tay; phone identity/ownership rõ224 dù partial bị ngón tay che. |
| V7-B-076 | P/U | clear/clear/clear | Người áo plaid cầm mobile trắng hai tay, mặt lưng và camera/outline rõ224. |
| V7-B-077 | P/U | clear/clear/ambiguous | Đã xem source1024: nam áo xanh ở giữa có mobile đen giữa hai tay;224 chỉ còn phần cạnh tối nhỏ bị fingers che. Giữ source P Draft, quality224 cần owner; neighbors cũng có own devices. |
| V7-B-078 | P/U | clear/clear/clear | Nam áo cam giữa crop cầm mobile dạng flip mở, màn hình và liên kết tay đọc được224; người cam phía sau không thay anchor. |
| V7-B-079 | P/U | ambiguous/ambiguous/ambiguous | Tay nữ chạm má, không thấy mobile rõ; annotation phone không đủ làm P. Owner/root đã rà lại: đề xuất U/U, recrop giữ đủ hai tay/book, quarantine không phone P tới xác minh. |
| V7-B-080 | P/U | ambiguous/ambiguous/ambiguous | Người trong lab cầm thiết bị chữ nhật cạnh oscilloscope/pliers; chưa chắc mobile. Owner/root đề xuất U/U tới highres/device review; không biến chưa thấy phone thành N. |
| V7-B-086 | N/U | clear/clear/clear | Nam áo tím dùng headphone trắng bằng một tay, tay kia ở mixing desk; equipment khác mobile, evidence phân biệt headphone/N còn rõ224; looking U. |
| V7-B-087 | N/P | ambiguous/ambiguous/ambiguous | Đã xem source640: nam học sinh bên trái pose với laptop, chỉ một tay thấy rõ, tay kia bị laptop/thân che; phone N chưa đủ evidence. Looking P là proposal ngoài exam/work-task chưa xác lập, cần owner domain/workarea review. |
| V7-B-089 | N/N | clear/clear/clear | Nữ áo trắng bên trái source viết bài, hai tay/bút rõ224; phone của nam bên phải nằm ngoài crop và không gán cho nữ; N/N hợp lý trong vùng nhìn. |
| V7-B-090 | N/U | ambiguous/ambiguous/ambiguous | Đã xem source416: nữ bên phải ngậm pen và một tay lên mặt; tay/bàn còn lại bị neighbor che, không đủ mobile absence. R7 N/U vẫn pending owner visibility review; pen không phải phone. |
| V7-B-092 | N/N | clear/clear/clear | Nam đọc sách và đánh dấu bằng highlighter, hai tay cùng vùng bài rõ224; N/N có workarea evidence. |
| V7-B-093 | N/P | clear/clear/clear | Người áo xanh dùng handset dây của điện thoại bàn; mobile-only theo ADR018 không P chỉ vì handset. Tay còn lại ở giấy/bàn thấy được224; N/P vẫn Draft ngoài exam. |
| V7-B-094 | N/N | clear/clear/clear | Người áo xám làm vật liệu/giấy trên bàn, hai tay liên kết own workarea; N/N evidence còn đọc được224, đầu/tay hướng bài không là looking P. |
| V7-B-096 | N/N | ambiguous/ambiguous/ambiguous | Đã xem source1024: vật xanh dạng phone nằm trên desk ngay cạnh mouse/tay người nữ dùng laptop; mobile N chưa chắc. Cần device review, đề xuất phone U/looking N nếu owner chưa xác minh; không suy P chỉ từ hình chữ nhật. |
| V7-B-097 | N/N | clear/clear/clear | Nam đọc/viết giấy tại laptop; hai tay ở vùng bài/bàn còn đọc được224, phone N trong vùng quan sát. |
| V7-B-098 | N/N | clear/clear/clear | Nam dùng keyboard/trackpad, hai tay rõ và vùng bàn thấy được; earbud dây không tự là phone P; N/N còn đọc được224. |
| V7-B-099 | N/N | clear/clear/clear | Người dùng laptop trong lab, hai tay ở bàn phím; headphone/instrument không là mobile, N/N còn đọc được224. |
| V7-B-100 | N/N | ambiguous/ambiguous/ambiguous | Đã xem source1024: người sau cash register có một tay thao tác và tay kia bị register/penholder che; mobile N chưa đủ vùng nhìn. Không dùng việc đăng ký không có phone annotation để chứng minh N. |
| V7-B-101 | N/U | clear/clear/clear | Người áo plaid một tay che miệng, tay kia ở keyboard; hai tay và desk quan sát được, không thấy mobile vùng này; looking U vì không chốt gaze task. |
| V7-B-102 | N/P | clear/clear/clear | Nữ bên trái ở bàn họp giữ pen đỏ và tay còn lại trên giấy; hai tay/bàn rõ224, không nhầm pen thành mobile, nhìn ngoài vùng giấy là looking proposal P pending domain. |
| V7-B-103 | N/P | clear/clear/clear | Nữ áo cyan hai tay chắp trước mặt, vùng desk giấy/salad không có mobile; phone N đọc được224, looking P vẫn Draft trong auxiliary context. |
| V7-B-104 | N/U | clear/clear/clear | Nam áo đen bên trái dùng headphone và đặt hai tay lên desk; equipment radio không mobile, hands rõ224, looking U. |
| V7-B-106 | N/N | clear/clear/clear | Nữ áo vàng viết giấy/map, hai tay và pen/workarea đủ thấy224; N/N support không dựa head tilt đơn lẻ. |
| V7-B-107 | N/N | clear/clear/clear | Nam áo nâu bên phải dùng laptop, hai tay ở keyboard/desk; nữ bên trái là partner khác, phone N/gaze N đọc được224 với own workarea. |
| V7-B-108 | N/U | clear/clear/clear | Nam áo trắng chắp hai tay trên bàn, vùng desk hiện rõ; mobile N trong vùng quan sát, looking U vì task/workarea chưa xác lập. |
| V7-B-109 | N/N | clear/clear/clear | Nữ jacket vàng foreground dùng desk computer, hai tay ở mouse/bàn; nam phía sau lớn bị cắt đầu nhưng không là anchor, N/N own workarea còn rõ224. |
| V7-B-110 | N/N | clear/clear/clear | Người áo sọc đỏ thao tác keyboard/mouse, hai tay và own desk rõ224; N/N Draft hợp lý trong vùng nhìn. |
| V7-B-111 | N/P | clear/lost/lost | Đã xem source1024: người mặc gown cầm pen trên open book, hai tay không mobile rõ. R7crop cắt tay viết mép trái nên224 mất evidence đó; cần recrop giữ đủ bàn/tay, không downgrade source N do224. |
| V7-D-002 | P/U | clear/clear/clear | Nữ áo kem giữ mobile đen, nữ bên cạnh xem chung; linked holder rõ224, không có own workarea đủ để looking P, không co-occurrence. |
| V7-D-004 | P/U | clear/clear/clear | Người áo trắng giữa hàng cầm own mobile thấp, neighbors có devices riêng; ownership direct còn đọc được224; gaze/workarea U. |
| V7-D-005 | P/U | clear/clear/clear | Nam kính áo denim giữ mobile đen, nữ bên trái xem cùng; phone thuộc linked holder, looking U vì hoạt động nhóm không có own workarea rõ. |
| V7-D-006 | P/U | ambiguous/ambiguous/ambiguous | Đã xem source512: thiết bị lớn dựng đứng có case/support giữa nam áo xanh và nữ plaid, giống tablet; chưa chứng minh mobile. Đề xuất U/U/device review, không co-occurrence và không nhận phone P từ class nguồn. |
| V7-D-008 | P/U | clear/clear/clear | Nam áo cyan giữ mobile đen hai tay, nữ đỏ neighbor chạm/xem; phone holder rõ224, task nhóm chưa đủ looking P. |
| V7-D-009 | P/P | clear/clear/clear | Nữ áo cyan có own mobile trong tay phải và sách mở trên bàn trước người; mắt hướng mobile ngoài vùng sách, both P/P là proposal có visible phone+workarea, owner vẫn chốt gaze/task. |
| V7-D-010 | P/U | clear/ambiguous/ambiguous | Crop có nữ plaid foreground giữ mobile đỏ dựng và nữ áo trắng giữ mobile xanh ngang, cả hai linked own hands. Metadata anchor không chỉ người nào, cần explicit unit; root đề xuất foreground-plaid-phone-user P/U và recrop. Không gộp hai người thành co-occurrence. |
| V7-D-011 | P/U | clear/clear/clear | Nữ plaid bên trái giữ mobile trắng; người cạnh có own phone riêng, holder và device rõ224; gaze U, không both P. |
| V7-D-012 | P/U | clear/clear/clear | Nam plaid tiền cảnh cầm mobile selfie giữa nhóm; direct ownership rõ224, không có vùng bài riêng để looking P. |
| V7-D-013 | P/U | clear/clear/clear | Nam áo xám kính giữ mobile nhỏ ngang, nam nâu cạnh là neighbor; phone/hand đọc được224, activity nhóm giữ looking U. |
| V7-D-014 | P/U | clear/clear/clear | Nữ bên trái giữ phone đen; nữ neighbor chỉ tay vào màn hình, không thay holder;224 thấy outline/ownership, looking U. |
| V7-D-015 | P/U | clear/clear/clear | Nam áo đen phía sau giữ own mobile gần mặt; nhiều phone foreground nhưng linked own device đọc được224; looking U. |
| V7-D-017 | U/P | clear/clear/clear | Nữ kính bên phải nhìn sang phone người nữ trái, tay cầm pen sát bài riêng; phone ownership của anchor chưa rõ nên U, looking P là proposal own-workarea/neighbor evidence, không co-occurrence. |
| V7-D-018 | P/U | clear/clear/clear | Nam áo trắng ở giữa chạm phone desk ngay vùng bàn của mình; nam bên phải cầm mobile khác. Linked desk phone đọc được224, looking U do có tương tác nhóm. |
| V7-D-020 | P/U | clear/clear/clear | Nam áo xám/trắng giữa lớp cầm mobile sáng bằng hai tay trên bài; device rõ224, looking U chờ task/gaze owner, không tự cả hai P. |
| V7-D-021 | P/P | clear/clear/clear | Nữ tóc tết áo denim foreground giữ own mobile và giấy trước người; mắt hướng phone ngoài giấy. P/P có visible device+own-workarea nhưng task/gaze vẫn proposal owner review, không chỉ nhìn đầu suy P. |
| V7-D-022 | U/P | clear/clear/clear | Nam áo sọc bên trái vươn tay/nhìn sang phone của nam plaid bên phải, có sách mở trước người; phone U ownership, looking P proposal. Phone ngoài R7crop không được gán own phone. |
| V7-D-023 | P/U | clear/clear/clear | Nữ tóc xoăn phải giữ mobile đen ngang trên lap, linked hands đọc được224; giấy lap có nhưng task/gaze chưa chốt nên U, không both P. |
| V7-D-025 | P/U | ambiguous/ambiguous/ambiguous | Nữ áo pink giữ thiết bị xanh landscape có hình như smartphone hoặc compact camera; chưa đủ mobile identity. Đề xuất U/U tới owner device review; hình chữ nhật/annotation nguồn không tự là P. |
| V7-D-026 | P/U | ambiguous/ambiguous/ambiguous | Phone đen ở tay nam teacher thấp bên trái; nữ áo sọc anchor đang viết bằng pen, tay kia giữ bài. Không gán teacher phone cho writer; R7 phone P không có evidence của đúng anchor. Root đề xuất N/N, bbox tập trung nữ [190,110,445,512]. Đây là hard negative attribution, không co-occurrence. |
| V7-D-027 | P/U | clear/lost/lost | Nam áo xám bên trái có phone sát tay nhưng R7crop cắt thân máy ở cạnh phải, chỉ còn fingers mờ224. Source scene có thể recrop để giữ device; root đang QA bbox mới, giữ source label pending thấy crop mới. |
| V7-D-028 | P/U | clear/clear/clear | Nữ tóc ngắn cardigan vàng giữ phone dạng keyboard bằng hai tay; thân máy/keyboard/ownership đọc được224, seated group không own workarea rõ nên looking U. |
| V7-D-029 | P/U | clear/clear/clear | Người áo sọc đứng cầm mobile trắng nhỏ gần hip; linked hand/device đọc được224, crowd context không xác lập own workarea, looking U. |
| V7-D-031 | P/U | clear/clear/clear | Nam áo trắng bên phải giữ mobile đen ngang sát tay trên bàn ăn; phone direct ownership đọc được224, không work-task evidence để looking P. |
| V7-D-033 | P/U | ambiguous/ambiguous/ambiguous | Đã xem source640: nữ xanh giữ thiết bị trắng landscape/thân dày giống compact camera hoặc handheld khác; chưa chắc mobile. Đề xuất U/U/device review; không lấy COCO class phone thay visual identity. |
| V7-D-034 | P/U | clear/clear/clear | Nữ áo đen giữ mobile flip trắng đóng có screen nhỏ trên bàn; linked hand/phone rõ224, source posed/bàn ăn không own workarea task nên looking U. |
| V7-D-035 | P/U | clear/clear/clear | Nữ khăn tối foreground giữ mobile nâu trong tay trái và vật cầm tay khác bên phải; không gán vật khác thành phone, device anchor rõ224, looking U. |
| V7-D-038 | P/U | clear/clear/clear | Nữ bên trái giữ smartphone màn hình sáng trong nhóm chụp/xem cùng; nam neighbors không ownership thay holder; rõ224, không own workarea, looking U. |
| V7-D-042 | P/U | clear/clear/clear | Nam áo đen bên trái giữ mobile trắng mỏng phía trên sổ; laptop foreground che phần desk, linked fingers/device còn rõ224, looking U chờ task evidence. |
| V7-D-044 | P/U | clear/clear/ambiguous | Nam suit xám bên trái giữ phone nhỏ giữa tay; source holder/device đọc được nhưng224 chỉ còn mép máy rất nhỏ. Giữ source P Draft, owner chọn usability224; không dùng số crop thay diversity. |
| V7-D-046 | P/U | clear/clear/ambiguous | Nữ áo xám bên phải giữ mobile nhỏ cạnh bàn laptop, direct own hands;224 chỉ còn thin edge khó đọc identity. Giữ source P Draft với input ambiguity, looking U. |
| V7-D-049 | U/N | clear/clear/clear | Nữ tóc đỏ foreground nhìn laptop/workarea, tay còn lại bị che nên phone U hợp lý; nam bên cạnh là unit riêng. Looking N có linked own/shared workarea, không co-occurrence. |
| V7-D-050 | P/N | clear/clear/clear | Nam áo xanh ở giữa có smartphone trên lap của mình và tay/pen chỉ bài trước người; phone direct own-lap rõ224, looking N proposal làm việc theo bài. Đây là P/N fully-known, không both P. |
| V7-D-051 | P/U | clear/clear/clear | Nữ áo xanh bên phải giữ mobile case pink trong tay sát lap; device/hand đọc được224, mobile nữ trái khác không gán anchor; looking U. |
| V7-D-053 | U/N | clear/clear/clear | Nữ áo đỏ trái nhìn laptop shared task; tay còn lại sau laptop nên phone U, looking N proposal workarea rõ; bàn/phone absence chưa đủ N. |
| V7-D-054 | U/N | clear/clear/clear | Nữ writer foreground phải viết giấy trong nhóm, own pen/paper rõ224; crowd/partition che phone vùng khác nên U giữ, looking N không suy từ head tilt đơn lẻ. |
| V7-D-056 | U/N | clear/clear/clear | Nam áo xanh cà vạt đỏ dùng keyboard; desktop monitor che vùng phone nên U, workarea/keyboard rõ cho looking N; không gán phone do rectangular desk clutter. |
| V7-D-057 | U/N | clear/clear/clear | Nam áo tối ở giữa nhìn own desktop/workarea, tay/bàn bị monitor che nên phone U. Phone đen trên bàn foreground thuộc người khác, không gán cho middle anchor; looking N proposal. |
| V7-D-058 | P/U | clear/clear/clear | Nữ áo đen bên trái giữ mobile đỏ sát lap và thao tác bằng hai tay; linked device còn đọc được224, nữ blue neighbor own phone riêng, looking U. |
