# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 15:51:31 2023

@author: PC-2308003!
"""

import streamlit as st

def remove_text(target_text, text_to_remove):
    lines = target_text.split('\n')
    new_lines = []

    for line in lines:
        new_line = line.replace(text_to_remove, "")
        new_lines.append(new_line)

    new_text = '\n'.join(new_lines)
    return new_text

def main():
    st.title("Text Editor")

    target_text = st.text_area("Enter your text:", "")
    text_to_remove = st.text_input("Enter text to remove:", "")

    if st.button("Remove"):
        if target_text and text_to_remove:
            new_text = remove_text(target_text, text_to_remove)
            st.subheader("Modified Text:")
            st.text_area("Result:", value=new_text)  # 결과가 입력창에 나타남
        else:
            st.warning("Please enter both the target text and text to remove.")

if __name__ == "__main__":
    main()