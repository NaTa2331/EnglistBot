import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
from groq import Groq
from gtts import gTTS
import numpy as np
import os
import queue

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

ddef text_to_speech(text):
    tts = gTTS(text, lang=tts_lang)
    tts.save("output.mp3")
    st.audio("output.mp3", format="audio/mp3")

# Sử dụng streamlit_webrtc để nhận giọng nói
st.session_state.audio_buffer = []

def audio_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray()
    st.session_state.audio_buffer.append(audio)
    return frame

# UI Streamlit
st.title("🗣️ Chatbot Dạy Ngôn Ngữ")
st.write("Hỏi về từ vựng, ngữ pháp, cách phát âm hoặc giao tiếp thực tế!")

# Tạo sidebar để chuyển đổi giữa các chế độ
mode = st.sidebar.radio("Chọn chế độ:", ["Chatbot", "Học phát âm"])

if mode == "Chatbot":
    # Lịch sử trò chuyện
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Nhận giọng nói bằng WebRTC
    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=1024,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
    )

    if webrtc_ctx.audio_receiver:
        st.write("🎤 Đang lắng nghe... Hãy nói gì đó!")
        audio_data = np.concatenate(st.session_state.audio_buffer, axis=0)
        try:
            from speech_recognition import Recognizer, AudioData
            recognizer = Recognizer()
            audio = AudioData(audio_data.tobytes(), sample_rate=16000, sample_width=2)
            text = recognizer.recognize_google(audio, language="vi-VN")
            st.success(f"Bạn đã nói: {text}")

            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(text)
            st.session_state.chat_history.append({"question": text, "answer": answer})
            st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")

        except Exception as e:
            st.warning(f"Lỗi nhận diện giọng nói: {str(e)}")

    # Hiển thị lịch sử trò chuyện
    st.subheader("📜 Lịch sử trò chuyện")
    for chat in st.session_state.chat_history:
        st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
        st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")
    
    query = st.text_input("Nhập câu hỏi của bạn:")
    if st.button("Gửi"):
        if query:
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(query)
            st.session_state.chat_history.append({"question": query, "answer": answer})
            st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")

elif mode == "Học phát âm":
    st.subheader("🔊 Học phát âm")
    word = st.text_input("Nhập từ cần phát âm:")
    
    if st.button("📖 Dịch nghĩa"):
        if word:
            meaning = ask_groq(f"Dịch nghĩa từ '{word}' sang tiếng Việt")
            st.write(f"📖 Nghĩa của '{word}': {meaning}")
        else:
            st.warning("Vui lòng nhập từ cần dịch!")
    
    if st.button("🔊 Nghe phát âm"):
        if word:
            text_to_speech(word)
        else:
            st.warning("Vui lòng nhập từ cần phát âm!")