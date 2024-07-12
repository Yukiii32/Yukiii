import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF

def scrape_kabum(url="https://www.kabum.com.br/hardware/processadores/intel"):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(("css selector", "article"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    products = []
    for article in soup.find_all("article"):
        name = article.find("div", class_="sc-9d1f1537-15 JuCPR").text.strip()
        price = article.find("span", class_="sc-b1f5eb03-2 iaiQNF priceCard").text.strip()
        products.append({"Nome": name, "Preço": price})

    return pd.DataFrame(products)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "KABUM PROCESSADORES INTEL", 0, 1, "C")

    col_widths = (168, 25)  

    # Headers
    for col, width in zip(df.columns, col_widths):
        pdf.cell(width, 10, col, 1, 0, "C")
    pdf.ln()

    pdf.set_font("Arial", size=7) 
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, row['Nome'], 1, 0)  
        pdf.cell(col_widths[1], 8, row['Preço'], 1, 1)  

    return pdf.output(dest="S").encode("latin-1")

st.title("TRABALHO AVALIATIVO 07")
st.empty()  
st.markdown(" #   Diogo Dutra Teixeira") 

if st.button("PEGAR INFORMAÇÕES"):
    with st.empty():
     with st.spinner("CARREGANDO..."):
        df = scrape_kabum()

    st.subheader("KABUM RESULTADOS:")
    st.dataframe(df, use_container_width=True)  

    if not df.empty:
        st.download_button(
            "Download as PDF",
            data=create_pdf(df),
            file_name="kabum_processors_intel.pdf",
            mime="application/pdf",
        )
