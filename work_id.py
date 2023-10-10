# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 12:38:26 2023

@author: PC-2308003!
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta

def daily_work(user):
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
  today = datetime.now()
  weekday = today.weekday()  # 0(월)부터 6(일)까지, 5(토)와 6(일)이 주말입니다.
# 월요일일 경우, 지난 주 월요일과 비교하여 지난 주 작업량이 나오게 할 것.  
  if weekday ==5 or weekday == 6:
      while today.weeday() !=4:
          today -= timedelta(days=1)
          
  if weekday ==0 :
      monday = today - timedelta(7)
  else :
      monday = today - timedelta(days=weekday)        
 
  today = today.strftime('%y%m%d')
  monday = monday.strftime('%y%m%d')
   
  
  sheet1 = client.open(sheet_name).worksheet(today)
  sheet2 = client.open(sheet_name).worksheet(monday)
#     # 데이터 읽어오기
  data1 = sheet1.get_all_records()
  data2 = sheet2.get_all_records()


  #미배분 파일 가져오기 (파일명 - key)
  df_t = pd.DataFrame(data1)
  df_y = pd.DataFrame(data2)

  df_y['작업수량'] = df_y['재할당']+df_y['검수 대기']+df_y['검수 완료']
  df_t['작업수량'] = df_t['재할당']+df_t['검수 대기']+df_t['검수 완료']

  df_y = df_y[['Domain','ID','작업수량','계']]
  df_t = df_t[['Domain','ID','작업수량','계']]


  tmp = pd.merge(df_t, df_y, how = 'left', on = ['Domain','ID']).fillna(0)


  tmp['일작업량'] = tmp['작업수량_x'] - tmp['작업수량_y']
  result = tmp.groupby('ID')['일작업량'].sum().reset_index()
  result = result.sort_values('일작업량', ascending=False)
  
  user_workload = result.loc[result['ID'] == user, '일작업량'].values[0] 

  
  return user_workload



def main():
    st.title('일일 작업량 게시')

    # 사용자 입력 받기
    id_input = st.text_input('사용자 ID를 입력하세요 (ex) FRA16000:')
    user_workload = daily_work(id_input)
   
    if id_input:
        work = daily_work(id_input)
        if work is not None:
            st.write(f"{id_input}님의 금주 작업량은 {user_workload}개 입니다.")
        else:
            st.write(f"입력한 ID ({id_input})에 해당하는 사용자를 찾을 수 없습니다.")


if __name__ == '__main__':
    main()






