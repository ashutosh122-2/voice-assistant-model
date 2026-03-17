import cv2
import numpy as np
import os
import speech_recognition as sr
import webbrowser
import openai
from config import apikey
import time
import random
import pyaudio
import pyttsx3
import subprocess

chatStr = ""
def chat(query):
    global chatStr
    print(chatStr)
    openai.api_key = apikey
    chatStr += f"ashut: {query}\n Jarvis: "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=chatStr,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    say(response["choices"][0]["text"])
    chatStr += f"{response['choices'][0]['text']}\n"
    return response["choices"][0]["text"]

def ai(prompt):
    openai.api_key = apikey
    text = f"OpenAI response for Prompt: {prompt} \n *************************\n\n"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # todo: Wrap this inside of a  try catch block
    # print(response["choices"][0]["text"])
    text += response["choices"][0]["text"]
    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    # with open(f"Openai/prompt- {random.randint(1, 2343434356)}", "w") as f:
    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip() }.txt", "w") as f:
        f.write(text)

# def say(text):
#     os.system(f'say "{text}"')

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
def perform_math(query):
    operation = None
    num1 = None
    num2 = None

    if "add" in query:
        operation = "add"
    elif "subtract" in query:
        operation = "subtract"
    elif "multiply" in query:
        operation = "multiply"
    elif "divide" in query:
        operation = "divide"

    numbers = [float(num) for num in query.split() if num.replace(".", "", 1).isdigit()]
    
    if len(numbers) == 2:
        num1, num2 = numbers
        result = None
        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            result = num1 / num2 if num2 != 0 else "Cannot divide by zero"
        
        return f"The result of {operation}ing {num1} and {num2} is {result}"
    else:
        return "I couldn't find two numbers to perform the operation. Please try again."

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            return "Some Error Occurred. Sorry from Jarvis"

def face_lock():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def capture_reference_face():
        print("Please show your face to the camera to register...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
               
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)[:1]
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    face_data = gray[y:y + h, x:x + w]
                    cap.release()
                    cv2.destroyAllWindows()
                    return cv2.resize(face_data, (100, 100))  
            cv2.imshow('Register Face', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return None

    def verify_face(reference_face):
        print("Verifying face... Please look at the camera.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                # Sort by area and pick the largest face
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)[:1]
                for (x, y, w, h) in faces:
                    face_data = gray[y:y + h, x:x + w]
                    face_data = cv2.resize(face_data, (100, 100))  # Resize to match reference_face
                    diff = cv2.norm(reference_face, face_data, cv2.NORM_L2)
                    print(f"Face similarity score: {diff}")
                    if diff < 5000:  # Adjust threshold based on testing
                        cap.release()
                        cv2.destroyAllWindows()
                        return True

            cv2.imshow('Verify Face', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return False

    reference_face = capture_reference_face()
    if reference_face is None:
        print("Face capture failed. Exiting...")
        exit()

    if verify_face(reference_face):
        print("Access granted! Welcome, sir!")
        say("Access granted! Welcome, sir!")
    else:
        print("Access denied. Goodbye!")
        say("Access denied. Goodbye!")
        exit()


if __name__ == '__main__':
    print('Starting Jarvis with Face Lock...')
    face_lock()  
    print('Welcome you SIR..... ')
    say("I am your personal assistant. How may I help you?")

    while True:
        print("Listening...")
        query = takeCommand()
        
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], ["google", "https://www.google.com"],["chat GPT", "https://chat.openai.com"]]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
        

        if "google" in query.lower() or "search google" in query.lower() :
            print(query.lower())
            webbrowser.open(f"https://www.google.com/search?q={query.lower().split('google')[1]}")
        if "play music" in query or "open music" in query:
            musicPath = "C:/Users/DELL/Downloads/a.mp3.mp3"
            os.system(f"start {musicPath}")
        
        
        elif "Whatsapp".lower() in query.lower():
            subprocess.run(["start", "https://www.microsoft.com/store/productId/9NKSQGP7F2NH?ocid=pdpshare"], shell=True)

        elif "Jarvis Quit".lower() in query.lower():
            print("Exiting...")
            say("Exiting")
            exit()

        elif "reset chat".lower() in query.lower():
            chatStr = ""
            print("Chat reset.")
            say("Chat reset")


        elif "math" in query.lower(): 
            result = perform_math(query.lower())
            say(result)
            print(result)

        elif "time" in query.lower():
            
            current_time = time.strftime("%I:%M %p") 
            Time = f"The current time is {current_time}."
            
            hr = current_time.split(":")[0].lstrip('0')
            min = current_time.split(":")[1].lstrip('0')
            
            print(Time)
            Time = f"Its {hr} {min}"
            say(Time)

        elif "open calculator" in query.lower():
            say("opening calculator")
            os.system("calc" if os.name == 'nt' else "open -a Calculator")
            
        elif "soja" in query.lower() or 'so ja' in query.lower():
            say("shuting down your laptop")
            os.system("shutdown /s /t 1")
        
        elif "stop music" in query.lower():
            os.system(f"taskkill /f /im Microsoft.Media.Player.exe")
            print("Music stopped.")

        
        else:
            print("Chatting...")
            





        # say(query)