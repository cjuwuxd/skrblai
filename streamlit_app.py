from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import config
import streamlit as st
from streamlit_drawable_canvas import *
import streamlit.components.v1 as components
import time
import threading
import numpy as np


theme = {
    "base": "dark",
    "primaryColor": "#40da16",
    "font": "monospace"
}

genai.configure(api_key=config.api_key)  
model = genai.GenerativeModel(model_name='gemini-2.0-flash')
st.set_page_config(page_title="SKRBL.ai", layout="wide", page_icon="✍️")
st.title("SKRBL.ai")

tab1, tab2 = st.tabs(["SKRBL Mode", "Capture Mode"])

try:
    with tab1:
        SKRBL_main()
    
    with tab2:
        SKRBL_cam()

except streamlit.errors.StreamlitDuplicateElementKey:
    pass


fill_color = "#000000"
width = 1080
height = 720

def SKRBL_main():
    global canvas_result
    canvas_result = st_canvas(
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            fill_color=fill_color,
            width=width,
            height=height,
            key="full_app"
        )

    canvas_result = canvas_result.image_data
    canvas_result = Image.fromarray(canvas_result)
    config.canvasImage = canvas_result
    

def SKRBL_cam():
    cam_mode = st.checkbox("Enable Camera")
    picture = st.camera_input("SKRBL your question!" , disabled=not cam_mode)
    
    if picture is not None:
        img = Image.open(picture)
        img_array = np.array(img)
        img_array = Image.fromarray(img_array)
        config.canvasImage = img_array

def defaultVariables():
    config.uses = 2
    config.lock = False
    config.exampleQuestion = " "
    config.history = " "

def get_image_canvas(canvas_result):
    canvas_result = Image.fromarray(canvas_result)
    handle_usage_limit(canvas_result)

def stream(text):
    for word in text.split(" "):
            yield word + " "
            time.sleep(0.02)
        
def evaluate(image):

    if config.mode == 1:
        global model
        
        prompt = f"Analyze the image and solve it mathematically and keep the answer short and still explains it, and explain it in a step by step process. {user_input}"
    
        response = model.generate_content([prompt, image])
        #popup = f"<script> alert({response.text})</script>"
        #components.html(popup,height=0,width=0)
        st.write_stream(stream(response.text))
        
        
        print("Uses Remaining: "  + str(config.uses) )
        print(response.text)
        config.history = response.text
        return response.text

    elif config.mode == 2:
        pass




def handle_usage_limit(image):
    global model
    st.write("Uses Left: " + str(config.uses))
    if config.uses <= 0 and config.lock == False:
        studentLock()
        timer_threading.start()

    elif config.lock == True:
        studentUnlock(question=config.exampleQuestion, image=image)
    else:
        evaluate(image)
        config.uses -= 1

def studentLock():
    config.lock = True
    print("Can't solve Question student limit reached")
    genQuestion = f"Analyze the past few questions that I drew earlier and generate a sample question based on the ones I gave earlier -> {config.history}, don't tell me the answer only the question itself nothing else"
    question = model.generate_content([genQuestion])
    
    print(question.text)
    st.write("To continue using SKRBL.ai please answer the sample question: " + question.text)
    config.exampleQuestion = question.text
    

def studentUnlock(question, image):
    prompt_question = f"What is the answer to this question and compare it to mine {question}, if its correct just say TRUE"
    answer = model.generate_content([prompt_question, image])
    print(answer.text)

    if config.uses <= 0:
        if "TRUE" in answer.text:
            st.success("Correct!")
            defaultVariables()
            timer_threading.stop()
        else:
            st.write(question)
            st.error("That is incorrect. Please try again!")


def startTimer(t):
    while t: 
        ph = st.empty()
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins,secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
        ph.metric("Refreshing Uses in: ", timer)
    defaultVariables()
    
timer_threading = threading.Thread(target=startTimer, args=(300,))
timer_threading.daemon = True

user_input = st.chat_input("Enter your input:")
    #commands
if user_input:
    handle_usage_limit(config.canvasImage)
    if user_input == "/skibidi":
        config.uses += 999
        st.write("yay")
    elif user_input == "/unskibidi":
        config.uses = 5

col1, col2, col3 = st.columns(3)


with col1:
    if st.button("Calculate"):
        handle_usage_limit(config.canvasImage)
        
        

stroke_width = st.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.color_picker("Stroke color: ", "#ffffff")



   
if __name__ == "__main__":
    #root = tk.Tk()
    #app = Calculator(root)
    #root.mainloop()
    # try:
        
    #     get_image_canvas()
    # except TypeError:
    #     print("Error:" + TypeError)
    
    pass
