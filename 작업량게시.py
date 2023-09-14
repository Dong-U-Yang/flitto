import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta

# 결과 시트 불러오기
def get_gsheet():
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

# 가져올 스프레드시트 
  sheet_name = 'hpr_static'

# 현재 날짜를 가져오고, 이전 날짜를 계산
  today =  datetime.now()
  if today.weekday() == 0:  # 월요일인 경우
    yday = today - timedelta(days=3)  # 이전 주 금요일로 설정
  else:
    yday = today - timedelta(days=1)


# 날짜에 해당하는 시트 불러오기
  sheet1_name = today.strftime('%y%m%d')
  sheet2_name = yday.strftime('%y%m%d')
  sheet1 = client.open(sheet_name).worksheet(sheet1_name)
  sheet2 = client.open(sheet_name).worksheet(sheet2_name)
# 시트 데이터 읽어오기
  data1 = sheet1.get_all_records()
  data2 = sheet2.get_all_records()
  df_t = pd.DataFrame(data1)
  df_y = pd.DataFrame(data2)

# 작업량 계산
  df_y['작업수량'] = df_y['재할당']+df_y['검수 대기']+df_y['검수 완료']
  df_t['작업수량'] = df_t['재할당']+df_t['검수 대기']+df_t['검수 완료']

  df_y = df_y[['Domain','ID','작업수량','계']]
  df_t = df_t[['Domain','ID','작업수량','계']]

  tmp = pd.merge(df_t, df_y, how = 'left', on = ['Domain','ID'])

  tmp = tmp.fillna(0)

  tmp['일작업량'] = tmp['작업수량_x'] - tmp['작업수량_y']
  result = tmp.groupby('ID')['일작업량'].sum().reset_index()
  result = result.sort_values('일작업량', ascending=False)

  return result


def main():
    st.title('일간 작업량 게시')

    # Google 스프레드시트에서 데이터 가져오기
    result = get_gsheet()

    # 데이터 출력
    st.subheader('일간 작업량:')
    st.write(result)

    

if __name__ == '__main__':
    main()

