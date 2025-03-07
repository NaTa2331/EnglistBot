import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Đặt cấu hình trang (phải là lệnh đầu tiên)
st.set_page_config(page_title="Chatbot Học Ngôn Ngữ", layout="wide")

# Khởi tạo Groq API
client = Groq(api_key="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")

# Lựa chọn ngôn ngữ
language = st.sidebar.radio("Chọn ngôn ngữ giảng dạy:", ["Tiếng Anh", "Tiếng Trung"])

# Xác định prompt theo ngôn ngữ
if language == "Tiếng Anh":
    system_prompt = "Bạn là giáo viên dạy tiếng Anh cho người Việt Nam. Hãy trả lời dễ hiểu, giải thích rõ ràng, đầy đủ (Cấu trúc, công thức), dùng ví dụ cụ thể, dịch nghĩa bằng tiếng Việt. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp bằng tiếng Việt. Lưu ý tất cả phải được trả lời bằng tiếng Việt"
    tts_lang = "en"
elif language == "Tiếng Trung":
    system_prompt = "Bạn là giáo viên dạy tiếng Trung cho người Việt Nam. Hãy trả lời dễ hiểu, giải thích rõ ràng, đầy đủ (Cấu trúc, công thức), dùng ví dụ cụ thể, dịch nghĩa bằng tiếng Việt. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp bằng tiếng Việt. Lưu ý tất cả phải được trả lời bằng tiếng Trung"
    tts_lang = "zh"

def ask_groq(query):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(messages=messages, model="llama3-70b-8192")
    return response.choices[0].message.content

# Hàm chuyển văn bản thành giọng nói
def text_to_speech(text):
    tts = gTTS(text, lang=tts_lang)
    tts.save("response.mp3")
    st.audio("response.mp3", format="audio/mp3")

# ===================== GHI ÂM VÀ XỬ LÝ GIỌNG NÓI =====================
st.title("🎙️ Chatbot Học Ngôn Ngữ")
st.write("Hãy nói vào micro, chatbot sẽ trả lời bằng giọng nói!")

# Chế độ hội thoại bằng giọng nói
def recognize_speech_from_audio(audio):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="vi-VN")
            return text
        except sr.UnknownValueError:
            return "Không nhận diện được giọng nói!"
        except sr.RequestError:
            return "Lỗi kết nối với API nhận diện giọng nói!"

# Nhận diện âm thanh từ microphone
webrtc_ctx = webrtc_streamer(
    key="speech-recognition",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=1024,
    media_stream_constraints={"video": False, "audio": True},
)

if webrtc_ctx.audio_receiver:
    try:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        audio = np.concatenate([frame.to_ndarray() for frame in audio_frames], axis=0)
        
        # Lưu âm thanh vào file tạm
        with open("temp_audio.wav", "wb") as f:
            f.write(audio)

        # Chuyển giọng nói thành văn bản
        user_text = recognize_speech_from_audio("temp_audio.wav")
        st.write(f"**🧑‍🎓 Bạn:** {user_text}")

        # Gửi câu hỏi đến AI
        if user_text:
            with st.spinner("💭 Đang suy nghĩ..."):
                answer = ask_groq(user_text)
                st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")
                
                # Chuyển văn bản thành giọng nói
                text_to_speech(answer)
    except Exception as e:
        st.error(f"Lỗi ghi âm: {e}")

