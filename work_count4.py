# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 12:57:30 2023

@author: PC-2308003!
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 17:46:46 2023

@author: PC-2308003!
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:52 2023

@author: PC-2308003!
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta



def daily_work(date, user):
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  # Create a connection object.
  credentials = service_account.Credentials.from_service_account_info(
      st.secrets["gcp_service_account"],
      scopes=[
          "https://www.googleapis.com/auth/spreadsheets",
          'https://spreadsheets.google.com/feeds', 
          'https://www.googleapis.com/auth/drive'
      ],
  )
  client = gspread.authorize(credentials)

  sheet_name = 'hpr_static'



#     # 이전 날짜에 해당하는 시트 불러오기
  sheet1_name = date
  today = datetime.strptime(date,'%y%m%d')
  sheet2_name = (datetime.strptime(date,'%y%m%d') - timedelta(1)).strftime('%y%m%d')
  
  sheet1 = client.open(sheet_name).worksheet(sheet1_name)
  sheet2 = client.open(sheet_name).worksheet(sheet2_name)
#     # 데이터 읽어오기
  data1 = sheet1.get_all_records()
  data2 = sheet2.get_all_records()
  df_t = pd.DataFrame(data1)
  df_y = pd.DataFrame(data2)

  # 필요한 컬럼만 남기기
  df_y['작업수량'] = df_y['재할당']+df_y['검수 대기']+df_y['검수 완료']
  df_t['작업수량'] = df_t['재할당']+df_t['검수 대기']+df_t['검수 완료']

  df_y = df_y[['Domain','ID','작업수량','계']]#.set_index('ID')
  df_t = df_t[['Domain','ID','작업수량','계']]#.set_index('ID')


  tmp = pd.merge(df_t, df_y, how = 'left', on = ['Domain','ID'])

  tmp = tmp.fillna(0)

  tmp['일작업량'] = tmp['작업수량_x'] - tmp['작업수량_y']
  result = tmp.groupby('ID')['일작업량'].sum().reset_index()
  result = result.sort_values('일작업량', ascending=False)
  
  user_workload = result.loc[result['ID'] == user, '일작업량'].values[0] if user in result['ID'].tolist() else 0

  
  return user_workload




def main():
    st.title('일일 작업량 게시')

    # 사용자 입력 받기
    date_input = st.text_input('날짜 (YYMMDD 형식으로 입력하세요  ex)230915 ):')
    user_input = st.text_input('사용자 ID를 입력하세요 ( ex) FRA18000 )  :')

    if date_input and user_input:
        user_workload = daily_work(date_input, user_input)
        st.write(f"{user_input}님의 {date_input}의 작업량은 {user_workload}개 입니다.")
    



if __name__ == '__main__':
    main()






