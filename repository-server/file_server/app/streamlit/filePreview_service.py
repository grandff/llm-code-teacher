import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from PIL import Image
import PyPDF2


def preview_file(file_url):
    """
    파일 미리보기 기능.
    파일 URL에서 파일을 가져와 파일 유형에 따라 Streamlit에 표시.
    """
    st.write("file_url : {file_url}")
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # 요청 에러가 발생하면 예외를 일으킴
        file_content = response.content  # 파일 내용을 바이트로 받음

        # 파일 형식에 따라 처리
        if file_url.endswith(".txt"):
            # 텍스트 파일 처리
            text_content = file_content.decode("utf-8")
            st.text_area("파일 미리보기 (텍스트)", value=text_content, height=300)

        elif file_url.endswith(".pdf"):
            # PDF 파일 처리
            st.write("PDF 파일 미리보기:")
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            pdf_text = ""
            for page_num in range(len(pdf_reader.pages)):
                pdf_text += pdf_reader.pages[page_num].extract_text()
            st.text_area("PDF 텍스트 미리보기", value=pdf_text, height=300)

        elif file_url.endswith((".png", ".jpg", ".jpeg")):
            # 이미지 파일 처리
            image = Image.open(BytesIO(file_content))
            st.image(image, caption="이미지 미리보기")

        elif file_url.endswith(".xlsx"):
            # 엑셀 파일 처리
            st.write("Excel 파일 미리보기:")
            excel_data = pd.read_excel(BytesIO(file_content))
            st.dataframe(excel_data)

        else:
            st.error("지원되지 않는 파일 형식입니다.")

    except requests.exceptions.RequestException as e:
        st.error(f"파일을 불러오는 중 오류가 발생했습니다: {e}")