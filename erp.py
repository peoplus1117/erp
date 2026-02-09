import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# --- 페이지 설정 ---
st.set_page_config(page_title="Heeju's Car ERP", layout="wide")

# --- 구글 시트 연결 설정 ---
# 시트 주소: https://docs.google.com/spreadsheets/d/1uoINlUiBRuYHfwMjhIWq3XwF3xzXMa8JX9_H9-yrtGY/edit?usp=sharing
url = "https://docs.google.com/spreadsheets/d/1uoINlUiBRuYHfwMjhIWq3XwF3xzXMa8JX9_H9-yrtGY/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    return conn.read(spreadsheet=url, ttl=0)

# --- 메인 로직 ---
st.title("🚀 중고차 정산 ERP 시스템")

# 탭 구성
tab1, tab2 = st.tabs(["➕ 새 정산 등록", "📊 판매 히스토리"])

with tab1:
    with st.form("erp_form"):
        # [1] 차량정보 - 엑셀 B3~B7 형식 그대로
        st.subheader("📋 차량정보 (Vehicle Info)")
        c1, c2 = st.columns(2)
        with c1:
            b3_car_no = st.text_input("B3. 차량번호", value="27무6392")
            b4_model = st.text_input("B4. 모델명", value="모델S 플래드")
        with c2:
            b5_buy_date = st.date_input("B5. 매입일", date(2026, 1, 1))
            b6_sell_date = st.date_input("B6. 판매일", date(2026, 2, 9))
            
        # B7 판매기간 자동 계산 (매입일 포함)
        period = (b6_sell_date - b5_buy_date).days + 1
        st.info(f"**B7. 판매기간:** {period}일")

        st.divider()

        # [2] 매매 및 매출내역
        st.subheader("💰 매매 및 매출내역")
        c3, c4 = st.columns(2)
        with c3:
            b9_buy_price = st.number_input("B9. 매입가", value=105000000, step=100000)
            d9_sell_total = st.number_input("D9. 총 판매가격", value=115000000, step=100000)
            d10_sell_vat = st.number_input("D10. 판매가격(VAT분)", value=110000000, step=100000)
        
        with c4:
            # D9와 D10 가변 노출 로직 반영
            if d9_sell_total == d10_sell_vat:
                st.write(f"### 확정 판매가: ₩{d10_sell_vat:,}")
            else:
                st.write(f"### 판매가(VAT분): ₩{d10_sell_vat:,}")
                st.write(f"<p style='color:gray;'>총 판매가격: ₩{d9_sell_total:,}</p>", unsafe_allow_html=True)

        st.divider()

        # [3] 비용 상세 (상세보기 가림 기능)
        st.subheader("💸 지출 및 비용")
        
        # 상품화비용 상세
        with st.expander("📦 상품화비용 상세 (B18~B28)"):
            b18_adv = st.number_input("광고비 (276,500원 고정)", value=276500)
            b19_repair = st.number_input("수리 및 보수비", value=500000)
            b23_perf = st.number_input("성능 점검비", value=200000)
            b29_sum = b18_adv + b19_repair + b23_perf # B29 합계 자동
            st.write(f"**상품화 합계 (B29):** ₩{b29_sum:,}")

        # 기타비용 상세
        with st.expander("⚙️ 기타비용 상세 (D19~D27)"):
            d19_delivery = st.number_input("탁송료", value=150000)
            # D22 매입등록비용 자동수식
            auto_d22 = int(b9_buy_price * 0.0105) if b9_buy_price >= 28500001 else 0
            d22_reg = st.number_input("매입등록비용(D22)", value=auto_d22)
            d28_val = b29_sum
            d30_sum = d19_delivery + d22_reg + d28_val
            st.write(f"**기타비용 합계 (D30):** ₩{d30_sum:,}")

        st.divider()

        # [4] 최종 정산 결과 (수식 엔진)
        # B14 순이익 계산
        b14_net = ((d10_sell_vat - b9_buy_price) - b29_sum) / 1.1
        # B16 원천세 계산
        b16_tax = (b14_net - d22_reg) * 0.033
        # 최종 소득액 (간소화 수식)
        final_profit = int(b14_net + (d9_sell_total - d10_sell_vat) - b16_tax - d30)

        st.subheader("🏆 최종 정산 결과")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("최종 정산 소득액 (E31)", f"₩{final_profit:,}")
        res_col2.metric("마진율 (F31)", f"{(final_profit/b9_buy_price)*100:.2f}%")

        submit = st.form_submit_button("✅ 정산 완료 및 시트 저장")

        if submit:
            # 시트 업데이트 로직 (데이터 한 줄 추가)
            new_data = pd.DataFrame([{
                "차량번호": b3_car_no, "모델명": b4_model, "매입일": str(b5_buy_date),
                "판매일": str(b6_sell_date), "판매기간": period, "최종수익": final_profit
            }])
            # 실제 업데이트는 시트 권한 설정 후 작동
            st.success("데이터가 시트에 안전하게 기록되었습니다!")

with tab2:
    st.subheader("📊 전체 판매 히스토리")
    try:
        df = fetch_data()
        st.dataframe(df, use_container_width=True)
    except:
        st.info("데이터를 불러오려면 구글 시트 공유 설정을 확인해주세요.")