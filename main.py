import speech_recognition as sr
import pyttsx3
import webbrowser
import musicLibrary
import requests
import pyaudio
import qrcode
import os
import re
import datetime as dt
import cv2
import pywhatkit
import sys
import face_recognition
import time
from datetime import datetime
import pyautogui
from groq import Groq



# WhatsApp Alert Function

INTRUDER_PHONE = "+917908669305"
def capture_and_alert(phone_number=INTRUDER_PHONE, message="🚨 Jarvis: Someone is trying to access me... ⚠️ Be Alert! 🔐"):
    print("Starting capture and alert process...")
    cam = cv2.VideoCapture(0) # Help to acess the camera
    if not cam.isOpened():
        print("Retrying camera with CAP_DSHOW (Windows fallback)...")
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cam.isOpened():
            print("Camera access failed.")
            return

    ret, frame = cam.read()
    if not ret:
        print("Failed to capture image.")
        cam.release()
        return
    if not os.path.exists("intruders"): # Folder 
        os.makedirs("intruders")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # It save the current image 
    filename = f"intruder_live_{timestamp}.jpg"
    save_path = os.path.join("intruders", filename)

    try:
        cv2.imwrite(save_path, frame)
        print(f"Image saved at {save_path}")
    except Exception as e:
        print(f"Image save error: {e}")
        return
    finally:
        cam.release()
        cv2.destroyAllWindows()
    try:                                          # Send image via Whatsapp 
        print("Sending image via WhatsApp...")
        pywhatkit.sendwhats_image(
            receiver=phone_number,
            img_path=save_path,
            caption=message,
            wait_time=20,  
            tab_close=True  # After sending the image it automatically colsed the Whatsapp Web
        )
        print("Image sent successfully!")
        time.sleep(5)  #  A small delay to ensure the image is sent properly
    except Exception as e:
        print(f"WhatsApp send error: {e}")

capture_and_alert(phone_number=INTRUDER_PHONE) # Call the function for testing 



  # It converts TEXT-TO-IMAGE 

engine = pyttsx3.init()

def speak(text): 
    engine.say(text)
    engine.runAndWait()


# OPENAI -> Groq Cloud 

def aiprocess(command):
    
    client = Groq(api_key="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") # Own API KEY

    # Send chat request
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": command # if i ask to Jarvis some different Question 
            }
        ]
    )

    
    return response.choices[0].message.content  # Return the command 

# Listen function Using speech_recognization(sr)

def listen(prompt=""):
    if prompt:
        speak(prompt)

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

    try:
        text = r.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
        speak("Sorry, I could not understand.")
        return None
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        speak("There was an error with the speech service.")
        return None



# UPI Payment QR Code generator function -> It request payment from customer via generating QR Code
 
def generate_upi_qr(customer_name, amount, note="Payment to Vendor"):
    upi_id = "7908669305@naviaxis"
    payee_name = "SHRI RAM AGRO TRADING"
    upi_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.make(upi_url)
    filename = f"qr_{customer_name}_{amount}.png"
    qr.save(filename)
    print(f"Saved QR code as {filename}")

    try:
        if os.name == 'nt':
            os.startfile(filename)
        elif os.name == 'posix':
            os.system(f'xdg-open "{filename}"')
        else:
            raise Exception("Unknown OS")
    except Exception:
        try:
            img = cv2.imread(filename)
            cv2.imshow("UPI QR Code", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Could not open QR image: {e}")


# Weather Function 


weather_api = "c53ada158c7f4cdb2063c968d9f4fb8f" #  Own Weather API Key 

def get_weather(city=None):
    if not city or city.lower() == "weather":
        speak("Which city do you want the weather for?")
        city = listen()
        if not city:
            speak("Sorry, I didn't catch the city name.")
            return "City not recognized."

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        report = f"The weather in {city} is {weather} with a temperature of {temp:.1f} degrees Celsius."
        print(report)
        return report
    except Exception as e:
        print(f"Weather error: {e}")
        return "Sorry, I couldn't fetch the weather."
    


# Command Handler
def processcommand(c):
    command = c.lower()

    if "open google" in command:
        webbrowser.open("https://google.com")

    elif "open instagram" in command:
        webbrowser.open("https://www.instagram.com/")

    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in command:
        webbrowser.open("https://linkedin.com")

    elif "open facebook" in command:
        webbrowser.open("https://facebook.com")

    elif "open github" in command:
        webbrowser.open("https://github.com/Flash019")

    elif command.startswith("play"):
        song = command.split(" ")[1]
        link = musicLibrary.music.get(song)
        if link:
            webbrowser.open(link)
        else:
            speak("Sorry, I couldn't find that song.")

    elif "weather" in command:
        match = re.search(r"weather (in|at)?\s*([\w\s]+)", command)
        city = match.group(2).strip() if match else "Delhi"
        report = get_weather(city)
        speak(report)

    elif "request a payment" in command:
        match = re.search(r"request a payment of (?:rs )?(\d+)\s*from\s*(\w+)", command)
        if match:
            amount = match.group(1)
            customer = match.group(2).capitalize()
            print(f"Generating QR for Rs {amount} from {customer}")
            speak(f"Generating payment QR for {customer} of rupees {amount}")
            generate_upi_qr(customer, amount)
        else:
            speak("Sorry, I couldn't extract the amount or name.")
    else:
        output = aiprocess(c)
        speak(output) 


# When Jarvis Activated 
if __name__ == "__main__":
    speak("Welcome back Sir. What can I help you with today?")

    while True:
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                print("Listening..........")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
            word = recognizer.recognize_google(audio)

            if word.lower() == "jarvis":
                speak("Yes")
                with sr.Microphone() as source:
                    print("Jarvis active... Listening for command...")
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
                if audio:
                    command = recognizer.recognize_google(audio)
                    print(f"Command received: {command}")
                    processcommand(command)

        except sr.WaitTimeoutError:
            print("Timeout ......")
        except sr.UnknownValueError:
            print(" sorry, Could not understand audio.")
        except Exception as e:
            print(f"Error: {e}")
