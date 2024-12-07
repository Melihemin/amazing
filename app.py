from flask import Flask, request, jsonify, send_file
import requests
import base64
import os
from google.generativeai import configure, GenerativeModel

# Flask application
app = Flask(__name__)

# Configure Google Generative AI
API_KEY = "AIzaSyAwQ5rXpvoF0W3iA0gfrjTD0tHFg8P3H-4"
configure(api_key=API_KEY)
TEXT_TO_SPEECH_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

# Generate content using Google Generative AI
def generate_content(prompt):
    """Generate content using Google Generative AI."""
    model = GenerativeModel(model_name="gemini-1.5-flash")
    prompt2 = (
        "Merhaba! Sen bir tur rehberisin ve ben sizinle birlikte bu muazzam yerleri keşfetmek için buradayım. "
        "Amacın bize bu gezintiyi mümkün olan en keyifli ve öğretici şekilde sunmak. "
        "Bizlere yerel kültür, tarih ve önemli mekanlar hakkında bilgi vermek, "
        "her adımda bizi yönlendirmek ve sorularımıza yanıt vermek için buradasın. "
        "İstersek gezilecek yerler hakkında daha fazla bilgi edinebilir veya her konuda sohbet edebiliriz. "
        "Hedefin, bu gezinin unutulmaz ve eğlenceli olmasını sağlamak! "
        "Kalin harfler ya da italik yazi kullanmadan duz yazi ile yaz. "
        f"İşte sana yöneltilen mesaj bunu cevapla: {prompt}"
    )

    response = model.generate_content(prompt2)
    return response.text

# Convert text to speech using Google Text-to-Speech API
def text_to_speech(text):
    """Convert text to speech using Google Text-to-Speech API."""
    data = {
        "input": {"text": text},
        "voice": {
            "languageCode": "tr-TR",
            "name": "tr-TR-Wavenet-E"
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 1.1
        }
    }

    response = requests.post(f"{TEXT_TO_SPEECH_URL}?key={API_KEY}", json=data)
    if response.status_code == 200:
        # Save the audio content as a file
        audio_file_path = "output.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(base64.b64decode(response.json()["audioContent"]))
        return audio_file_path
    else:
        raise Exception(f"API Error: {response.status_code}, {response.text}")

@app.route("/generate", methods=["POST"])
def generate():
    """API endpoint to generate content and optional text-to-speech."""
    try:
        # Extract the user input
        data = request.json
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in request payload"}), 400

        user_prompt = data["prompt"]

        # Generate content
        generated_content = generate_content(user_prompt)

        # Convert to speech if requested
        audio_file = None
        if data.get("text_to_speech", False):
            audio_file = text_to_speech(generated_content)

        # Response
        if audio_file:
            return jsonify({
                "prompt": user_prompt,
                "response": generated_content,
                "audio_file_url": f"http://localhost:5000/download/{audio_file.split('/')[-1]}"
            })
        else:
            return jsonify({
                "prompt": user_prompt,
                "response": generated_content
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint to allow downloading the audio file."""
    return send_file(
        filename,
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    app.run(debug=True)
