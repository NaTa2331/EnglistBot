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

# Hàm chuyển văn bản thành giọng nói
def text_to_speech(text):
    tts = gTTS(text, lang="vi")
    tts.save("response.mp3")
    st.audio("response.mp3", format="audio/mp3")

# UI Streamlit
st.title("🗣️ Chatbot Dạy Ngôn Ngữ")
st.write("Hỏi về từ vựng, ngữ pháp, cách phát âm hoặc giao tiếp thực tế!")

# Chế độ Chat hoặc Học phát âm
mode = st.sidebar.radio("Chọn chế độ:", ["Chatbot", "Học phát âm", "Trò chuyện giọng nói"])

# ===================== CHẾ ĐỘ CHATBOT =====================
if mode == "Chatbot":
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.subheader("📜 Lịch sử trò chuyện")
    for chat in st.session_state.chat_history:
        st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
        st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")

    query = st.text_input("Nhập câu hỏi của bạn:")
    if st.button("Gửi"):
        if query:
            with st.spinner("💭 Đang suy nghĩ..."):
                answer = ask_groq(query)
            st.session_state.chat_history.append({"question": query, "answer": answer})
            st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")
            text_to_speech(answer)

# ===================== CHẾ ĐỘ HỌC PHÁT ÂM =====================
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

# ===================== CHẾ ĐỘ TRÒ CHUYỆN GIỌNG NÓI =====================
elif mode == "Trò chuyện giọng nói":
    st.subheader("🎙️ Trò chuyện bằng giọng nói")

    # Bộ nhận diện giọng nói
    recognizer = sr.Recognizer()
    audio_queue = queue.Queue()

    def recognize_speech_from_stream(audio_data):
        """Chuyển đổi giọng nói từ stream thành văn bản theo thời gian thực."""
        try:
            return recognizer.recognize_google(audio_data, language="vi-VN")
        except sr.UnknownValueError:
            return "Không nhận diện được, vui lòng thử lại."
        except sr.RequestError:
            return "Lỗi kết nối đến dịch vụ nhận diện giọng nói."

    # Ghi âm và xử lý giọng nói
    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    transcript_placeholder = st.empty()

    if webrtc_ctx.audio_receiver:
        st.write("🎤 **Đang lắng nghe...**")

        try:
            while True:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if not audio_frames:
                    continue

                # Chuyển đổi dữ liệu âm thanh
                audio = np.concatenate([frame.to_ndarray() for frame in audio_frames], axis=0)
                audio_data = sr.AudioData(audio.tobytes(), sample_rate=16000, sample_width=2)
                recognized_text = recognize_speech_from_stream(audio_data)

                transcript_placeholder.write(f"🗣️ **Bạn:** {recognized_text}")

                # Nếu có văn bản hợp lệ, gửi đến chatbot
                if recognized_text and recognized_text != "Không nhận diện được, vui lòng thử lại.":
                    with st.spinner("💭 Đang suy nghĩ..."):
                        answer = ask_groq(recognized_text)

                    st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")

                    # Đọc to câu trả lời
                    text_to_speech(answer)

        except Exception as e:
            st.error(f"Lỗi ghi âm: {e}")
