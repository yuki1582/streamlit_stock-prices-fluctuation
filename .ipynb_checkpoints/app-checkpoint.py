import pandas as pd
import yfinance as yf
import streamlit as st
import altair as alt

st.title('米国株価可視化アプリ')

st.sidebar.write("""
    # GAFA株価
    こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます   
""")

st.sidebar.write("""
    ## 表示日数選択
    
""")

days = st.sidebar.slider('日数',1, 50, 20)

st.write(f"""
### 過去 **{days}日間** のGAFA株価
    
""")

#キャッシュで高速処理
@st.cache
def get_data(days, tickers):
    #df空のデータにhistを追加
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        #日付と株価の値の取得
        hist = tkr.history(period=f'{days}d')
        #日付のインデックスのフォーマット変更
        hist.index = hist.index.strftime('%d %B %Y')
        #クローズの終わりのみ取得
        hist = hist[['Close']]
        #カラム名を'apple'
        hist.columns = [company]
        #横向きに変更
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: #例外処理
    st.sidebar.write("""
        ## 株価の範囲指定
        
    """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 3500.0, (0.0, 3500.0)
    )

    #辞書型
    tickers = {
            'apple': 'AAPL',
            'facebook': 'META',
            'google': 'GOOG',
            'microsoft': 'MSFT',
            'netflix': 'NFLX',
            'amazon': 'AMZN'
    }

    df = get_data(days, tickers)

    #会社名の選択
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価(USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color="Name:N"
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "何か問題が発生しました"
    )        