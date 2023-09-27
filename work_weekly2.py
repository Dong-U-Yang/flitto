# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 18:40:56 2023

@author: PC-2308003!
"""



import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta

def find_id_by_email(email):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
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
    resource_sheet_name = '리소스'

    resource_sheet = client.open(sheet_name).worksheet(resource_sheet_name)
    data = resource_sheet.get_all_records()

    df_resource = pd.DataFrame(data)
    df_resource.columns = ['ID','name','email']
    
    # 이메일에 해당하는 ID 찾기(리소스 시트의 열이 잘못되어있음)
    user_id = df_resource.loc[df_resource['email'] == email, 'ID'].values[0] if email in df_resource['email'].tolist() else None
    user_name = df_resource.loc[df_resource['email'] == email, 'name'].values[0] if email in df_resource['email'].tolist() else None

    return user_id, user_name




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
  sheet1_name = today
  today = datetime.strptime(today,'%y%m%d')
  sheet2_name = today - timedelta(days=today.weekday())
  
#     # 데이터 읽어오기
  data1 = sheet1.get_all_records()
  data2 = sheet2.get_all_records()


  #미배분 파일 가져오기 (파일명 - key)
  df_t = pd.DataFrame(data1)
  df_y = pd.DataFrame(data2)

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
    date_input = st.text_input('날짜 (YYMMDD 형식으로 입력하세요 ex) 230915 ):')
    email_input = st.text_input('사용자 이메일을 입력하세요 (ex) abcd1234@flitto.com):')

    if date_input and email_input:
        # 이메일에 해당하는 ID 찾기
        user_id = find_id_by_email(email_input)[0]
        user_name = find_id_by_email(email_input)[1]

        if user_id:
            user_workload = daily_work(date_input, user_id)
            st.write(f"{user_name} 님(ID: {user_id})의 {date_input}의 작업량은 {user_workload}개 입니다.")
        else:
            st.write(f"입력한 이메일 ({email_input})에 해당하는 사용자를 찾을 수 없습니다.")


if __name__ == '__main__':
    main()


