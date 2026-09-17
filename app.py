
import streamlit as st
st.image("logo.jpg")
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


# =========================
# CÁC HÀM HỖ TRỢ
# =========================

def dinh_dang_tien(so_tien):
    return f"{so_tien:,.0f} VNĐ"


def them_thang(ngay, so_thang):
    """
    Cộng số tháng vào ngày.
    Ví dụ: 31/01 + 1 tháng = 28/02 hoặc 29/02.
    """
    return ngay + relativedelta(months=so_thang)


def so_ngay(ngay_bat_dau, ngay_ket_thuc):
    """
    Số ngày tính lãi.
    Theo yêu cầu: từ ngày gửi đến trước ngày rút/đáo hạn.
    """
    return (ngay_ket_thuc - ngay_bat_dau).days


def tinh_lai(goc, lai_suat, so_ngay):
    """
    Công thức:
    Lãi = Gốc × Lãi suất năm × Số ngày / 365
    """
    return goc * (lai_suat / 100) * so_ngay / 365


def tinh_cac_ky(goc, ngay_gui, ngay_rut, ky_han_thang, lai_suat_co_han):
    """
    Tách khoản tiền gửi thành các kỳ hạn hoàn thành
    và phần kỳ hạn đang chạy.
    """

    cac_ky = []
    ngay_bat_dau = ngay_gui
    tien_goc = goc
    so_ky_hoan_thanh = 0

    while True:
        ngay_daohan = them_thang(ngay_bat_dau, ky_han_thang)

        # Đã hoàn thành một kỳ hạn
        if ngay_rut >= ngay_daohan:
            ngay_ket_thuc = ngay_daohan
            ngay_tinh = so_ngay(ngay_bat_dau, ngay_ket_thuc)

            tien_lai = tinh_lai(
                tien_goc,
                lai_suat_co_han,
                ngay_tinh
            )

            cac_ky.append({
                "ky": so_ky_hoan_thanh + 1,
                "tu_ngay": ngay_bat_dau,
                "den_ngay": ngay_ket_thuc,
                "so_ngay": ngay_tinh,
                "lai_suat": lai_suat_co_han,
                "tien_lai": tien_lai,
                "hoan_thanh": True
            })

            so_ky_hoan_thanh += 1
            ngay_bat_dau = ngay_daohan

        else:
            # Chưa đủ một kỳ hạn
            ngay_tinh = so_ngay(ngay_bat_dau, ngay_rut)

            cac_ky.append({
                "ky": so_ky_hoan_thanh + 1,
                "tu_ngay": ngay_bat_dau,
                "den_ngay": ngay_rut,
                "so_ngay": ngay_tinh,
                "lai_suat": lai_suat_co_han,
                "tien_lai": 0,
                "hoan_thanh": False
            })

            break

    return cac_ky, so_ky_hoan_thanh


# =========================
# CẤU HÌNH TRANG
# =========================

st.set_page_config(
    page_title="Tính lãi tiết kiệm",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 ỨNG DỤNG TÍNH LÃI TIỀN GỬI TIẾT KIỆM_TRẦN YẾN NHI")
st.caption("Công cụ mô phỏng tính tiền gốc và tiền lãi theo kỳ hạn")


# =========================
# NHẬP THÔNG TIN
# =========================

st.subheader("1. Thông tin khoản tiền gửi")

col1, col2 = st.columns(2)

with col1:
    tien_gui = st.number_input(
        "Số tiền khách hàng gửi (VNĐ)",
        min_value=0.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    lai_suat_co_han = st.number_input(
        "Lãi suất có kỳ hạn (%/năm)",
        min_value=0.0,
        value=6.0,
        step=0.1
    )

    lai_suat_khong_ky_han = st.number_input(
        "Lãi suất không kỳ hạn (%/năm)",
        min_value=0.0,
        value=0.2,
        step=0.1
    )

with col2:
    ngay_gui = st.date_input(
        "Ngày gửi tiền",
        value=date.today()
    )

    ngay_rut = st.date_input(
        "Ngày khách hàng rút tiền",
        value=date.today() + relativedelta(months=12)
    )

    ky_han = st.selectbox(
        "Kỳ hạn gửi tiền",
        options=[1, 3, 6, 12, 18, 24],
        format_func=lambda x: f"{x} tháng"
    )


phuong_thuc = st.radio(
    "Phương thức nhận tiền lãi",
    [
        "Nhận lãi trước",
        "Nhận lãi hàng tháng",
        "Nhận lãi cuối kỳ"
    ],
    horizontal=True
)


# =========================
# TÍNH TOÁN
# =========================

if st.button("🧮 TÍNH TOÁN", type="primary", use_container_width=True):

    # Kiểm tra dữ liệu
    if tien_gui <= 0:
        st.error("Số tiền gửi phải lớn hơn 0.")
        st.stop()

    if ngay_rut < ngay_gui:
        st.error("Ngày rút tiền không được nhỏ hơn ngày gửi tiền.")
        st.stop()

    if lai_suat_co_han < 0 or lai_suat_khong_ky_han < 0:
        st.error("Lãi suất không được nhỏ hơn 0.")
        st.stop()

    # Ngày đáo hạn kỳ đầu
    ngay_dao_han_dau = them_thang(ngay_gui, ky_han)

    # Có rút trước kỳ hạn đầu không?
    rut_truoc_han = ngay_rut < ngay_dao_han_dau

    # =====================================================
    # TRƯỜNG HỢP 1: RÚT TRƯỚC HẠN
    # =====================================================

    if rut_truoc_han:

        ngay_tinh = so_ngay(ngay_gui, ngay_rut)

        lai_thuc_te = tinh_lai(
            tien_gui,
            lai_suat_khong_ky_han,
            ngay_tinh
        )

        # -----------------------------------------------
        # NHẬN LÃI TRƯỚC + RÚT TRƯỚC HẠN
        # -----------------------------------------------

        if phuong_thuc == "Nhận lãi trước":

            # Lãi đã được trả trước theo lãi suất kỳ hạn
            lai_da_nhan_truoc = tinh_lai(
                tien_gui,
                lai_suat_co_han,
                so_ngay(
                    ngay_gui,
                    ngay_dao_han_dau
                )
            )

            chenh_lech = lai_da_nhan_truoc - lai_thuc_te

            # Nếu lãi nhận trước lớn hơn lãi thực tế:
            # ngân hàng khấu trừ phần chênh lệch vào tiền gốc.
            if chenh_lech > 0:
                tien_goc_thuc_nhan = tien_gui - chenh_lech
            else:
                tien_goc_thuc_nhan = tien_gui

            tong_loi_ich = lai_da_nhan_truoc + tien_goc_thuc_nhan

            st.warning("⚠️ Khách hàng đang rút tiền trước hạn.")

            st.subheader("📊 Kết quả")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Tiền lãi đã nhận trước",
                dinh_dang_tien(lai_da_nhan_truoc)
            )

            c2.metric(
                "Lãi thực tế được hưởng",
                dinh_dang_tien(lai_thuc_te)
            )

            c3.metric(
                "Phần lãi phải hoàn lại",
                dinh_dang_tien(max(chenh_lech, 0))
            )

            st.divider()

            st.write(
                f"**Tiền gốc ban đầu:** "
                f"{dinh_dang_tien(tien_gui)}"
            )

            st.write(
                f"**Tiền gốc thực nhận khi rút:** "
                f"{dinh_dang_tien(tien_goc_thuc_nhan)}"
            )

            st.write(
                f"**Tổng lợi ích khách hàng đã nhận:** "
                f"{dinh_dang_tien(tong_loi_ich)}"
            )

            st.info(
                "Tiền lãi đã nhận trước được đối chiếu với "
                "tiền lãi thực tế theo lãi suất không kỳ hạn. "
                "Phần nhận thừa được khấu trừ vào tiền gốc."
            )

        # -----------------------------------------------
        # NHẬN LÃI HÀNG THÁNG / CUỐI KỲ
        # -----------------------------------------------

        else:

            tong_tien = tien_gui + lai_thuc_te

            st.warning("⚠️ Khách hàng rút tiền trước hạn.")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Tiền gốc",
                dinh_dang_tien(tien_gui)
            )

            c2.metric(
                "Tiền lãi",
                dinh_dang_tien(lai_thuc_te)
            )

            c3.metric(
                "Tổng tiền nhận",
                dinh_dang_tien(tong_tien)
            )

            st.write(
                f"**Số ngày thực gửi:** {ngay_tinh} ngày"
            )

            st.write(
                f"**Lãi suất áp dụng:** "
                f"{lai_suat_khong_ky_han:.2f}%/năm"
            )

    # =====================================================
    # TRƯỜNG HỢP 2: ĐẾN HẠN HOẶC SAU HẠN
    # =====================================================

    else:

        cac_ky, so_ky_hoan_thanh = tinh_cac_ky(
            tien_gui,
            ngay_gui,
            ngay_rut,
            ky_han,
            lai_suat_co_han
        )

        tong_lai = 0

        for ky in cac_ky:
            if ky["hoan_thanh"]:
                tong_lai += ky["tien_lai"]

        # =================================================
        # NHẬN LÃI TRƯỚC
        # =================================================

        if phuong_thuc == "Nhận lãi trước":

            # Lãi của các kỳ đã hoàn thành
            tong_lai_da_nhan_truoc = 0

            for ky in cac_ky:
                if ky["hoan_thanh"]:
                    tong_lai_da_nhan_truoc += ky["tien_lai"]

            # Nếu đang ở kỳ mới và chưa hoàn thành
            ky_dang_chay = None

            for ky in cac_ky:
                if not ky["hoan_thanh"]:
                    ky_dang_chay = ky
                    break

            # Nếu rút đúng ngày đáo hạn thì không có kỳ đang chạy
            if ky_dang_chay is not None:
                if ngay_rut == ngay_dao_han_dau:
                    pass

            # Tổng tiền khách hàng đã/ sẽ nhận
            tong_nhan = tien_gui + tong_lai_da_nhan_truoc

            st.success("✅ Khoản tiền gửi đã hoàn thành kỳ hạn.")

            st.subheader("💰 Chi tiết phương thức nhận lãi trước")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Tiền gốc nhận khi đáo hạn",
                dinh_dang_tien(tien_gui)
            )

            c2.metric(
                "Tổng lãi đã nhận trước",
                dinh_dang_tien(tong_lai_da_nhan_truoc)
            )

            c3.metric(
                "TỔNG LỢI ÍCH",
                dinh_dang_tien(tong_nhan)
            )

            st.info(
                "Tiền lãi được nhận trước ở đầu mỗi kỳ hạn. "
                "Khi đến hạn, khách hàng nhận lại tiền gốc. "
                "Không cộng tiền lãi nhận trước vào tiền gốc để tính lãi tiếp."
            )

        # =================================================
        # NHẬN LÃI HÀNG THÁNG
        # =================================================

        elif phuong_thuc == "Nhận lãi hàng tháng":

            lai_moi_thang = (
                tien_gui *
                (lai_suat_co_han / 100) /
                12
            )

            tong_nhan = tien_gui + tong_lai

            st.success("✅ Tính toán hoàn tất.")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Lãi mỗi tháng",
                dinh_dang_tien(lai_moi_thang)
            )

            c2.metric(
                "Tổng tiền lãi",
                dinh_dang_tien(tong_lai)
            )

            c3.metric(
                "Tổng tiền nhận",
                dinh_dang_tien(tong_nhan)
            )

        # =================================================
        # NHẬN LÃI CUỐI KỲ
        # =================================================

        else:

            tong_nhan = tien_gui + tong_lai

            st.success("✅ Tính toán hoàn tất.")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Tiền gốc",
                dinh_dang_tien(tien_gui)
            )

            c2.metric(
                "Tiền lãi",
                dinh_dang_tien(tong_lai)
            )

            c3.metric(
                "TỔNG TIỀN NHẬN",
                dinh_dang_tien(tong_nhan)
            )

        # =================================================
        # THÔNG TIN CHUNG
        # =================================================

        st.divider()

        st.subheader("📋 Thông tin khoản tiền gửi")

        col1, col2, col3 = st.columns(3)

        col1.write(
            f"**Tiền gửi:** {dinh_dang_tien(tien_gui)}"
        )

        col1.write(
            f"**Ngày gửi:** {ngay_gui.strftime('%d/%m/%Y')}"
        )

        col2.write(
            f"**Ngày rút:** {ngay_rut.strftime('%d/%m/%Y')}"
        )

        col2.write(
            f"**Kỳ hạn:** {ky_han} tháng"
        )

        col3.write(
            f"**Ngày đáo hạn kỳ đầu:** "
            f"{ngay_dao_han_dau.strftime('%d/%m/%Y')}"
        )

        col3.write(
            f"**Số kỳ hoàn thành:** {so_ky_hoan_thanh}"
        )

        # =================================================
        # BẢNG CHI TIẾT CÁC KỲ
        # =================================================

        st.subheader("📑 Chi tiết từng kỳ")

        du_lieu_bang = []

        for ky in cac_ky:

            du_lieu_bang.append({
                "Kỳ": ky["ky"],
                "Từ ngày": ky["tu_ngay"].strftime("%d/%m/%Y"),
                "Đến ngày": ky["den_ngay"].strftime("%d/%m/%Y"),
                "Số ngày": ky["so_ngay"],
                "Lãi suất": f"{ky['lai_suat']:.2f}%",
                "Tiền lãi": dinh_dang_tien(ky["tien_lai"]),
                "Trạng thái": (
                    "Đã hoàn thành"
                    if ky["hoan_thanh"]
                    else "Đang thực hiện"
                )
            })

        st.dataframe(
            du_lieu_bang,
            use_container_width=True,
            hide_index=True
        )

