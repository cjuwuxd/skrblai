
from PIL import Image
import google.generativeai as genai

import streamlit as st
from streamlit_drawable_canvas import *
import streamlit.components.v1 as components



st.set_page_config(page_title="SKRBL.ai", layout="wide", page_icon="✍️",)
st.title("SKRBL.ai")


bg_color = "black"
uses = 3
lock = False

stroke_width = st.sidebar.slider("Stroke width: ", 1, 5, 3)
stroke_color = st.sidebar.color_picker("Stroke color: ", "#ffffff")
fill_color = "#000000"
width = 500
height = 500

canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        fill_color=fill_color,
        width=width,
        height=height,
    )

canvas_result = canvas_result.image_data
def get_image_canvas():
    global canvas_result
    
    canvas_result = Image.fromarray(canvas_result)
    return canvas_result


def evaluate(image):
    
    global model
    genai.configure(api_key='AIzaSyBKJMlo6CU6-DIfAT8WFaHBn_MplihXyQQ')  
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')

    prompt = f"Analyze the image and solve it mathematically and keep the answer short and still explains it, and explain it in a step by step process. {user_input}"

    response = model.generate_content([prompt, image])
    popup = f"<script> alert({response.text})</script>"
    components.html(popup,height=0,width=0)
    st.success(response.text)
    
    
    print(response.text)
    return response.text


def handle_usage_limit(image):
    global uses
    if uses <= 0:
        print("Can't solve Question student limit reached")
        prompt_answer = f"What is the answer to your question and compare it to mine, if its correct just say TRUE"
        answer = model.generate_content([prompt_answer])
        print(answer.text)
        st.write(answer.text)
        
        if "TRUE" in answer.text:
            st.success("Correct!")
        else:
            st.error("That is incorrect. Please try again!")
    else:
        evaluate(image)
        uses -= 1

user_input = st.text_input("Enter your input:")

col1, col2, col3 = st.columns(3)


with col1:
    if st.button("Calculate"):
        
        handle_usage_limit(get_image_canvas())
        
        


   
if __name__ == "__main__":
    #root = tk.Tk()
    #app = Calculator(root)
    #root.mainloop()
    try:
        get_image_canvas()
    except TypeError:
        print("Error")
    
