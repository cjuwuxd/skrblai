from PIL import Image
import google.generativeai as genai
import config
import streamlit as st
from streamlit_drawable_canvas import *
import streamlit.components.v1 as components
import time
import threading

genai.configure(api_key=config.api_key)  
model = genai.GenerativeModel(model_name='gemini-1.5-flash')
st.set_page_config(page_title="SKRBL.ai", layout="centered", page_icon="✍️")
st.title("SKRBL.ai")


stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color: ", "#ffffff")
fill_color = "#000000"
width = 700
height = 500

canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        fill_color=fill_color,
        width=width,
        height=height,
        key="full_app"
    )

canvas_result = canvas_result.image_data

def defaultVariables():
    config.uses = 15
    config.lock = False
    config.exampleQuestion = " "
    config.history = " "

def get_image_canvas():
    global canvas_result
    
    canvas_result = Image.fromarray(canvas_result)
    return canvas_result


def evaluate(image):
    global model
    
    prompt = f"Analyze the image and solve it mathematically and keep the answer short and still explains it, and explain it in a step by step process. {user_input}"

    response = model.generate_content([prompt, image])
    popup = f"<script> alert({response.text})</script>"
    components.html(popup,height=0,width=0)
    st.success(response.text)
    
    print("Uses Remaining: "  + str(config.uses) )
    print(response.text)
    config.history = response.text
    return response.text


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
        pass
    
