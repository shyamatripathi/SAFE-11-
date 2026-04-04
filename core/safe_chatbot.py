import google.generativeai as genai

genai.configure(api_key="AIzaSyD76bZ9d5KiVPY7N_4TQ9N2pjScL6hDOTg")

model = genai.GenerativeModel("gemini-2.0-flash")
def safe_chatbot(user_message, severity, symptoms, bmi, age):

    prompt = f"""
You are SAFE AI Assistant, a calm and empathetic health support assistant.

User Health Context:
Age: {age}
BMI: {bmi}
Current Risk Level: {severity}
Symptoms: {symptoms}

Rules:
- respond empathetically
- never diagnose diseases
- suggest consulting doctors when needed
- keep responses short and supportive

User message:
{user_message}
"""

    response = model.generate_content(prompt)

    return response.text