import streamlit as st
import pandas as pd
from pykrx import stock
import requests
from bs4 import BeautifulSoup
import mplfinance as mpf
import datetime
import matplotlib.pyplot as plt


# ticker
ticker_name = ['한미반도체']
ticker_list = ['042700']
d = {'Ticker Name':ticker_name, 'Ticker':ticker_list}
data = pd.DataFrame(data=d)

# 실시간 주식 가져오기
def get_stock_prices(ticker):
    prices = []  # 가격정보가 담길 리스트

    url = 'https://finance.naver.com/item/main.nhn?code=' + ticker

    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    today = soup.select_one('#chart_area > div.rate_info > div')
    price = today.select_one('.blind')
    prices.append(price.get_text())

    previous_close = soup.select_one('#chart_area > div.rate_info > table .blind').get_text()
    prices.append(previous_close)

    return prices

# 링크를 HTML 형식으로 변환하는 함수
def make_clickable(link):
    return f'<a href="{link}" target="_blank">{link}</a>'


# 네이버 뉴스 크롤링 함수
def fetch_naver_news(ticker_name):
    url = f'https://search.naver.com/search.naver?where=news&query={ticker_name}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds=2024.01.14&de=2024.05.13&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20240114to20240514&is_sug_officeid=0&office_category=0&service_area=0'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_list = []
    
    for item in soup.select('ul.list_news > li'):
        title = item.select_one('a.news_tit').get_text().strip()
        description = item.select_one('div.news_dsc').get_text().strip() if item.select_one('div.news_dsc') else '내용 없음'
        news_list.append({'제목': title, '내용': description})
    
    
    df_news = pd.DataFrame(news_list)

    return df_news

# 100일간의 주식데이터 가져오는 함수
def get_recent_days_data(ticker):
    # 오늘 날짜 5월 14일로 지정
    end_date = datetime.datetime(2024, 4, 23)
    # 10일 전 날짜 (주말 포함을 고려)
    start_date = end_date - datetime.timedelta(days=100)

    # 날짜 형식을 문자열로 변환
    end_date_str = end_date.strftime('%Y%m%d')
    start_date_str = start_date.strftime('%Y%m%d')

    # pykrx를 사용하여 데이터 가져오기
    df = stock.get_market_ohlcv_by_date(start_date_str, end_date_str, ticker)
    
    # 인덱스(날짜)를 내림차순으로 정렬
    df = df.sort_index(ascending=False)
    
    return df

# 100일간 주식차트 그리는 함수
def plot_candlestick(data, ticker_name):
    # 인덱스(날짜)를 내림차순으로 정렬
    data = data.sort_index(ascending=True)
    data = data.rename(columns={'날짜': 'Date', '시가': 'Open', '고가': 'High', '저가': 'Low',  '종가': 'Close', '거래량': 'Volume' })

    # 인덱스를 날짜 형식으로 변환
    data.index = pd.to_datetime(data.index)

    # 캔들스틱 그래프 그리기
    mpf.plot(data, type='candle', style='yahoo', ylabel='Price', volume=True, show_nontrading=False)

# --------------------------------구현 ------------------------------------

st.set_page_config("주식 뉴비(Newbie)를 위한 딥러닝 기반 투자결정 지원 프로그램", "🌱", layout="wide")

t1, empty, t2 = st.columns((0.07, 0.05, 1))
t1.image('seed.png', width=140)
t2.title("주식 뉴비(Newbie)를 위한 딥러닝 기반 투자결정 지원 프로그램")

st.header('') # 빈 공간을 만들기 위한 코드
st.header('') # 빈 공간을 만들기 위한 코드

# 회사 이름을 선택하는 셀렉트 박스 생성
st.subheader('예측 결과를 알고 싶은 종목을 선택하세요.')
selected_corp = st.selectbox('', ticker_name)

st.header('') # 빈 공간을 만들기 위한 코드
st.header('') # 빈 공간을 만들기 위한 코드

st.subheader('금일 뉴스 별 전일 대비 종가 등락 예측 결과')
st.markdown("#### <span style = 'color:red'> 금일 뉴스 31건 중,</span>", unsafe_allow_html=True)

# 등락 결과 데이터 추출
df = pd.read_excel('C:/Users/pemo/Downloads/최종/df3.xlsx')
df_und = df[['text', 'predicted_label']]
up_df = df_und[df_und['predicted_label'] == 1].reset_index(drop=True)
down_df = df_und[df_und['predicted_label'] == 0].reset_index(drop=True)


# 화살표와 건수 및 퍼센트 
empty1, up1, up2, empty, down1, down2, empty = st.columns((0.2, 0.09, 0.13, 0.25, 0.09, 0.07, 0.2))
up1.image('C:/Users/pemo/Downloads/최종/up.png', width=130)
down1.image('C:/Users/pemo/Downloads/최종/down.png', width=130)

up2.title('30건')
down2.title('1건')

# 예측 결과 데이터 프레임 불러오기
empty, col1, col2 = st.columns((0.04, 0.3, 0.3))

with col1:
    st.header("주가 상승 예측")
    st.dataframe(up_df, width= 800)

with col2:
    st.header("주가 하락 예측")
    st.dataframe(down_df, width= 700)

st.header('') # 빈 공간을 만들기 위한 코드

# --------------------------------------------------- 감성 분석 -------------------------------------------------------

st.subheader('금일 뉴스 별 투자 심리 분류 결과')
st.header('') # 빈 공간을 만들기 위한 코드

# 감성분석 결과 데이터 추출
df_sent = df[['text', 'sentiment']]
posi_df = df_sent[df_sent['sentiment'] == '긍정'].reset_index(drop=True)
neut_df = df_sent[df_sent['sentiment'] == '중립'].reset_index(drop=True)
nega_df = df_sent[df_sent['sentiment'] == '부정'].reset_index(drop=True)

# 화살표와 건수 
empty1, posi1, posi2, empty, neut1, neut2, empty, nega1, nega2, empty = st.columns((0.2, 0.18, 0.13, 0.35, 0.18, 0.13, 0.4, 0.18, 0.13, 0.2))
posi1.image('C:/Users/pemo/Downloads/최종/posi.png', width=130)
neut1.image('C:/Users/pemo/Downloads/최종/neut.png', width=130)
nega1.image('C:/Users/pemo/Downloads/최종/nega.png', width=130)

posi2.title('23건')
neut2.title('7건')
nega2.title('1건')

# 예측 결과 데이터 프레임 불러오기
col1, col2, col3 = st.columns((0.3, 0.3, 0.3))
with col1:
    st.header("긍정")
    st.dataframe(posi_df, width= 750)

with col2:
    st.header("중립")
    st.dataframe(neut_df, width= 750)

with col3:
    st.header("부정")
    st.dataframe(nega_df, width= 750)

st.header('') # 빈 공간을 만들기 위한 코드


st.header('') # 빈 공간을 만들기 위한 코드

if selected_corp:
    # 선택된 회사의 인덱스를 기반으로 티커 값을 가져옴
    ticker = ticker_list[ticker_name.index(selected_corp)]

    # ---------------------23일 시가 -------------------------

    date_23 = "20240423"
    date_22 = "20240422"

    # 특정 종목의 시가 및 전일 종가 데이터를 가져오기
    if date_23 and date_22 and ticker:
        df_23 = stock.get_market_ohlcv_by_date(date_23, date_23, ticker)
        df_22 = stock.get_market_ohlcv_by_date(date_22, date_22, ticker)

        open_price_14 = df_23['시가'].iloc[0]
        close_price_13 = df_22['종가'].iloc[0]

    # 두 개의 컬럼을 만들어서 각각의 컬럼에 metric과 pyplot을 배치
        st.subheader('실시간 주가 및 뉴스 정보')        

        empty, rt = st.columns((0.07, 0.2))
        rt.metric(
                label=selected_corp,
                value=round(open_price_14),
                delta=round(open_price_14) - round(close_price_13)
        )
    
    # 주가 데이터 가져오기
    #st.set_option('deprecation.showPyplotGlobalUse', False)  # 오류 해결
    df_stock = get_recent_days_data(ticker)
    
    st.markdown('#### 최근 100일치 차트')
    empty, chart, empty = st.columns((0.2, 0.45, 0.2))
    chart.pyplot(plot_candlestick(df_stock, selected_corp))


    st.header('') # 빈 공간을 만들기 위한 코드

    st.markdown('#### 한미반도체 뉴스 관련도 순')
    # 네이버 뉴스 데이터 가져오기
    df_news = fetch_naver_news(selected_corp)

    empty, col1 = st.columns((0.03, 0.3))

    with col1:
        st.dataframe(df_news, width= 1400)


