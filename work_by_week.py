# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 10:50:51 2023

@author: PC-2308003!
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Streamlit UI 설정
st.title("주간 작업량")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")

if uploaded_file is not None:
    # 업로드된 CSV 파일 읽기
    df = pd.read_csv(uploaded_file)
    
    # 데이터 전처리
    df['일시'] = pd.to_datetime(df['일시'])
    df_chat = df[df['유형'] == 'chat']
    df_chat['계'] = df_chat['계'] - df_chat['미작업'] - df_chat['작업중'] - df_chat['보류']
    pivot_table = df_chat.pivot_table(index=['ID', '일시'], values='계', aggfunc='sum').reset_index()
    
    # 최신 날짜와 비교 날짜 구하기
    latest = pivot_table['일시'].max()
    weekago = latest - timedelta(7)
    
    # 해당 날짜로 df 분리
    latest_sum = pivot_table[pivot_table['일시'] == latest].reset_index(drop=True)
    weekago_sum = pivot_table[pivot_table['일시'] == weekago].reset_index(drop=True)
    
    # 작업량 계산
    merged_data = latest_sum.merge(weekago_sum, on='ID', suffixes=('_latest', '_weekago'))
    merged_data['주간작업량'] = merged_data['계_latest'] - merged_data['계_weekago']
    
    # 결과 출력
    result = merged_data[['ID', '주간작업량']]
    result = result[result['주간작업량'] >= 0].reset_index(drop=True)
    
    st.subheader("결과 출력")
    st.write(result)