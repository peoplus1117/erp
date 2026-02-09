import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# 페이지 설정
st.set_page_config(page_title="Heeju's Car ERP", layout="wide")

st.title("🚀 희주님 전용 중고차 정산 ERP")

# 구글 시트 연결 (Secrets 설정이 필요합니다)
url = "https://docs.google.com/spreadsheets/d/1uoINlUiBRuYHfwMjhIWq3XwF3xzXMa8JX9_H9-yrtGY/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0)
except Exception as e:
    st.error(f"연동 에러 발생: {e}")
    st.info("Streamlit Cloud의 App Settings -> Secrets에 시트 URL 설정을 확인해주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📝 정산서 작성", "📊 판매 히스토리"])

with tab1:
    with st.form("main_form"):
        # [섹션 1: 차량정보] - 시트 B3~B7 양식
        st.subheader("📋 차량정보 (B3~B7)")
        col1, col2 = st.columns(2)
        with col1:
            b3_car_no = st.text_input("B3. 차량번호", value="27무6392")
            b4_model = st.text_input("B4. 모델명", value="테슬라 모델S 플래드")
        with col2:
            b5_buy_date = st.date_input("B5. 매입일", date(2026, 1, 1))
            b6_sell_date = st.date_input("B6. 판매일", date(2026, 2, 9))
        
        # B7 판매기간 자동 계산
        period = (b6_sell_date - b5_buy_date).days + 1
        st.info(f"**B7. 판매기간:** {period}일 (매입일 포함)")

        st.divider()

        # [섹션 2: 매매 정보 및 매출내역]
        st.subheader("💰 매매 및 매출내역")
        c3, c4 = st.columns(2)
        with c3:
            b9_buy_price = st.number_input("B9. 매입가", value=105000000, step=100000)
            d9_sell_total = st.number_input("D9. 총 판매가격", value=115000000, step=100000)
            d10_sell_vat = st.number_input("D10. 판매가격(VAT분)", value=110000000, step=100000)
        
        with c4:
            if d9_sell_total == d10_sell_vat:
                st.write(f"### 확정 판매가: ₩{d10_sell_vat:,}")
            else:
                st.write(f"### 판매가(VAT분): ₩{d10_sell_vat:,}")
                st.write(f"<p style='color:gray;'>총 판매가격(D9): ₩{d9_sell_total:,}</p>", unsafe_allow_html=True)

        st.divider()

        # [섹션 3: 지출 상세]
        st.subheader("💸 지출 및 상품화 비용")
        
        with st.expander("📦 상품화비용 상세 보기 (B18~B28)"):
            b18_adv = st.number_input("B18. 광고비", value=276500)
            b19_repair = st.number_input("B19. 수리 및 보수비", value=500000)
            b23_perf = st.number_input("B23. 성능 점검비", value=200000)
            b29_sum = b18_adv + b19_repair + b23_perf
            st.write(f"**상품화 합계(B29):** ₩{b29_sum:,}")

        with st.expander("⚙️ 기타비용 상세 보기 (D19~D27)"):
            d19_delivery = st.number_input("D19. 탁송료", value=150000)
            auto_d22 = int(b9_buy_price * 0.0105) if b9_buy_price >= 28500001 else 0
            d22_reg = st.number_input("D22. 매입등록비용", value=auto_d22)
            d28_val = b29_sum
            d30_sum = d19_delivery + d22_reg + d28_val
            st.write(f"**기타비용 합계(D30):** ₩{d30_sum:,}")

        b30_fixed = st.number_input("이자 + 주차비 (B30)", value=1000000)

        st.divider()

        # [섹션 4: 수익 계산 엔진]
        b14_net = ((d10_sell_vat - b9_buy_price) - b29_sum) / 1.1
        b16_tax = (b14_net - d22_reg) * 0.033
        c13_margin = d9_sell_total - d10_sell_vat
        final_profit = int(b14_net + c13_margin - b16_tax - b30_fixed)

        st.subheader("🏆 최종 정산 결과")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("최종 소득액 (E31)", f"₩{final_profit:,}")
        res_col2.metric("마진율 (F31)", f"{(final_profit/b9_buy_price)*100:.2f}%")

        if st.form_submit_button("✅ 시트에 데이터 누적 저장"):
            st.balloons()
            st.success("성공!")

with tab2:
    st.subheader("📊 전체 판매 히스토리")
    st.dataframe(df, use_container_width=True)
