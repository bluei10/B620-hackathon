import json
import boto3
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import pygame

# Initialize the Rekognition and Polly clients
rekognition_client = boto3.client('rekognition', region_name='us-east-2')  # Replace with your region
polly_client = boto3.client('polly', region_name='us-east-2')  # Replace with your region

# Initialize pygame for playing audio
pygame.mixer.init()

# Function to detect faces and display the result
def detect_faces():
    try:
        # Get the file name from the entry field
        file_name = file_name_entry.get()

        # Check if the file exists
        if not file_name:
            messagebox.showerror("Error", "Please enter the file name")
            return

        # Call AWS Rekognition to detect faces
        response = rekognition_client.detect_faces(
            Image={'S3Object': {'Bucket': 'face-sic-mundus', 'Name': file_name}},  # Replace with your S3 bucket
            Attributes=['ALL']
        )

        # Process the response and display the results
        results_text.delete(1.0, tk.END)  # Clear previous results
        speech_text = ""

        relaxation_suggestion = ""
        stress_level = "Normal"

        # Check if the response contains FaceDetails
        if 'FaceDetails' in response and response['FaceDetails']:
            for faceDetail in response['FaceDetails']:
                # Extract age range
                age_range = faceDetail['AgeRange']
                age_text = f"Detected face: {age_range['Low']} - {age_range['High']} years old\n"
                results_text.insert(tk.END, age_text)
                speech_text += age_text

                # Extract gender
                gender = faceDetail['Gender']['Value']
                gender_text = f"Gender: {gender}\n"
                results_text.insert(tk.END, gender_text)
                speech_text += gender_text

                # Extract emotions
                emotions = faceDetail['Emotions']
                if emotions:
                    dominant_emotion = max(emotions, key=lambda x: x['Confidence'])
                    emotion_text = f"Emotional State: {dominant_emotion['Type']} (Confidence: {dominant_emotion['Confidence']}%)\n"
                    results_text.insert(tk.END, emotion_text)
                    speech_text += emotion_text

                    # Analyze stress based on dominant emotions
                    stress_level = analyze_stress(dominant_emotion['Type'])
                    
                    # Provide relaxation assistance based on detected emotion and stress level
                    if stress_level == "High":
                        relaxation_suggestion = "It seems you're experiencing high stress. Try deep breathing exercises, meditation, or taking a short walk."
                    elif stress_level == "Medium":
                        relaxation_suggestion = "It seems you're feeling some stress. Try listening to calming music or doing some light stretches."
                    else:
                        relaxation_suggestion = "You seem to be in a normal state. Keep up with your routine to stay relaxed."

                    results_text.insert(tk.END, relaxation_suggestion + "\n")
                    speech_text += relaxation_suggestion

                # Check for beard and mustache
                facial_hair = "None"
                if 'Beard' in faceDetail:
                    if faceDetail['Beard']['Value']:
                        facial_hair = "Beard detected"
                if 'Mustache' in faceDetail:
                    if faceDetail['Mustache']['Value']:
                        facial_hair = "Mustache detected"

                facial_hair_text = f"Facial Hair: {facial_hair}\n"
                results_text.insert(tk.END, facial_hair_text)
                speech_text += facial_hair_text

                # Check for accessories (e.g., glasses)
                accessories = "None"
                if 'Sunglasses' in faceDetail:
                    if faceDetail['Sunglasses']['Value']:
                        accessories = "Sunglasses detected"
                elif 'Eyeglasses' in faceDetail:
                    if faceDetail['Eyeglasses']['Value']:
                        accessories = "Eyeglasses detected"

                accessories_text = f"Accessories: {accessories}\n"
                results_text.insert(tk.END, accessories_text)
                speech_text += accessories_text

                results_text.insert(tk.END, "-"*40 + "\n")  # Separator between faces
        else:
            # No faces detected, show message and add speech text
            messagebox.showinfo("No Faces Detected", "No faces were detected in the image.")
            speech_text += "No faces were detected in the image."

        # Call Polly to convert the speech text to audio if text exists
        if speech_text:
            synthesize_speech(speech_text)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to analyze stress level based on emotion
def analyze_stress(emotion):
    high_stress_emotions = ['ANGRY', 'FEAR', 'SAD']
    medium_stress_emotions = ['DISGUST', 'SURPRISED']

    if emotion in high_stress_emotions:
        return "High"
    elif emotion in medium_stress_emotions:
        return "Medium"
    else:
        return "Low"

# Function to synthesize speech using Polly and play it
def synthesize_speech(text):
    try:
        # Stop any currently playing music before starting new audio
        pygame.mixer.music.stop()

        # Wait for the current audio to fully stop before proceeding
        pygame.mixer.music.fadeout(1000)  # Fade out for 1 second

        # Call Polly to synthesize speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'  # You can change the voice to others like 'Matthew', 'Ivy', etc.
        )
        
        # Save the speech to a file
        audio_stream = response['AudioStream']
        with open("speech_output.mp3", 'wb') as file:
            file.write(audio_stream.read())

        # Play the audio file using pygame
        pygame.mixer.music.load("speech_output.mp3")
        pygame.mixer.music.play()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating speech: {str(e)}")

# Function to open file dialog and select image
def open_file():
    filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if filename:
        file_name_entry.delete(0, tk.END)
        file_name_entry.insert(tk.END, filename.split("/")[-1])  # Show only the file name
        display_image(filename)  # Display the selected image

# Function to display the image in the Tkinter window
def display_image(filename):
    try:
        img = Image.open(filename)
        img = img.resize((250, 250))  # Resize image for the preview
        img_tk = ImageTk.PhotoImage(img)

        # Display image in the label
        image_label.config(image=img_tk)
        image_label.image = img_tk  # Keep a reference to avoid garbage collection
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the image: {str(e)}")

# Set up the tkinter window
window = tk.Tk()
window.title("Sic Mundus Face Recognition App")
window.geometry("800x900")  # Adjusted for image display

# Set background color
window.config(bg='#ecf0f1')

# Add a modern icon if available
try:
    window.iconbitmap("path_to_icon.ico")  # Provide a path to your icon file
except:
    pass

# Create a frame for the header and controls
header_frame = tk.Frame(window, bg="#2C3E50")
header_frame.pack(fill=tk.X, pady=20)

title_label = tk.Label(header_frame, text="Sic Mundus Face Recognition App", font=("Helvetica", 20, "bold"), fg="white", bg="#2C3E50")
title_label.pack()

# Create the input area frame
input_frame = tk.Frame(window, bg="#ecf0f1")
input_frame.pack(pady=10, padx=20)

file_name_label = tk.Label(input_frame, text="Enter Image File Name (from S3 Bucket):", font=("Helvetica", 14), bg='#ecf0f1', fg="#34495e")
file_name_label.grid(row=0, column=0, pady=10)

file_name_entry = ttk.Entry(input_frame, width=40, font=("Helvetica", 12))
file_name_entry.grid(row=0, column=1, pady=10)

# Add a button to open file dialog (optional for local testing)
open_button = ttk.Button(input_frame, text="Browse File", command=open_file)
open_button.grid(row=1, column=0, columnspan=2, pady=10)

# Add a button to trigger the face detection
detect_button = ttk.Button(input_frame, text="Detect Faces", command=detect_faces)
detect_button.grid(row=2, column=0, columnspan=2, pady=10)

# Create the image preview area
image_frame = tk.Frame(window, bg="#ecf0f1")
image_frame.pack(pady=20)

image_label = tk.Label(image_frame, bg='#ecf0f1')
image_label.pack(pady=10)

# Results display area
results_frame = tk.Frame(window, bg="#ecf0f1")
results_frame.pack(pady=20)

results_text = tk.Text(results_frame, height=12, width=70, font=("Comfortaa", 12), bg="#ecf0f1", fg="#34495e", wrap=tk.WORD, bd=2, relief=tk.SOLID)
results_text.pack()

# Style the buttons with a custom theme
style = ttk.Style(window)
style.configure('TButton', background='#3498db', font=("Comfortaa", 12, 'bold'), padding=10)
style.map('TButton', background=[('active', '#2980b9')])  # Change color when clicked

# Start the GUI event loop
window.mainloop()
