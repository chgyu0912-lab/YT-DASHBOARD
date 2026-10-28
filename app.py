import streamlit as st
import re
from googleapiclient.discovery import build
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="유튜브 영상 효율 분석 대시보드", page_icon="📊", layout="wide")

# [보안 수정됨] Streamlit Secrets를 사용하여 API 키를 안전하게 불러옵니다.
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

def extract_video_id(url):
    """유튜브 URL에서 영상 ID를 추출하는 함수"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_stats(video_id):
    """유튜브 API를 이용해 영상의 통계 데이터를 가져오는 함수"""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="statistics,snippet",
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            stats = response['items'][0]['statistics']
            snippet = response['items'][0]['snippet']
            return {
                'title': snippet['title'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
        return None
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# 웹 앱 화면 구성
st.title("📊 크리에이터를 위한 경쟁 영상 효율 분석 대시보드")
st.write("비교하고 싶은 두 개의 유튜브 영상 링크를 입력하여 성과를 분석해 보세요.")

# 레이아웃 나누기 (입력창 2개)
col1, col2 = st.columns(2)

with col1:
    url1 = st.text_input("첫 번째 유튜브 영상 링크")

with col2:
    url2 = st.text_input("두 번째 유튜브 영상 링크 (비교 대상)")

# 분석 버튼
if st.button("데이터 분석하기"):
    if url1 and url2:
        with st.spinner("데이터를 분석하는 중입니다..."):
            id1 = extract_video_id(url1)
            id2 = extract_video_id(url2)
            
            if id1 and id2:
                stats1 = get_video_stats(id1)
                stats2 = get_video_stats(id2)
                
                if stats1 and stats2:
                    st.divider()
                    st.subheader("💡 분석 결과")
                    
                    # 효율성(참여도) 계산: (좋아요 / 조회수) * 100
                    eng_rate1 = (stats1['likes'] / stats1['views']) * 100 if stats1['views'] > 0 else 0
                    eng_rate2 = (stats2['likes'] / stats2['views']) * 100 if stats2['views'] > 0 else 0

                    # 결과 지표 출력 (Metrics)
                    res_col1, res_col2 = st.columns(2)
                    
                    with res_col1:
                        st.markdown(f"**{stats1['title']}**")
                        st.metric("조회수", f"{stats1['views']:,}회")
                        st.metric("좋아요", f"{stats1['likes']:,}개")
                        st.metric("시청자 참여도 (조회수 대비 좋아요)", f"{eng_rate1:.2f}%")
                        
                    with res_col2:
                        st.markdown(f"**{stats2['title']}**")
                        st.metric("조회수", f"{stats2['views']:,}회")
                        st.metric("좋아요", f"{stats2['likes']:,}개")
                        st.metric("시청자 참여도 (조회수 대비 좋아요)", f"{eng_rate2:.2f}%")
                        
                    # 시각화 (막대 차트)
                    st.divider()
                    st.subheader("📈 데이터 시각화 비교")
                    
                    # 차트를 그리기 위한 데이터프레임 생성
                    data = pd.DataFrame({
                        '영상': ['영상 1', '영상 2'],
                        '조회수': [stats1['views'], stats2['views']],
                        '좋아요': [stats1['likes'], stats2['likes']]
                    })
                    
                    # 조회수와 좋아요 수를 나누어 차트로 표시
                    chart_col1, chart_col2 = st.columns(2)
                    with chart_col1:
                        st.write("**조회수 비교**")
                        st.bar_chart(data.set_index('영상')['조회수'])
                    with chart_col2:
                        st.write("**좋아요 수 비교**")
                        st.bar_chart(data.set_index('영상')['좋아요'])

            else:
                st.error("올바른 유튜브 링크 형식이 아닙니다.")
    else:
        st.warning("두 개의 영상 링크를 모두 입력해주세요.")
