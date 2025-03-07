import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import numpy as np
import queue
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

# Hàm gọi Groq API
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

# ===================== UI STREAMLIT =====================
st.title("🎙️ Chatbot Học Ngôn Ngữ")
st.write("Hãy nói vào micro, chatbot sẽ trả lời bằng giọng nói!")

# Chọn chế độ
mode = st.sidebar.radio("Chọn chế độ:", ["Trò chuyện văn bản", "Trò chuyện giọng nói", "Học phát âm"])

# ===================== CHẾ ĐỘ TRÒ CHUYỆN VĂN BẢN =====================
if mode == "Trò chuyện văn bản":
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

# ===================== CHẾ ĐỘ TRÒ CHUYỆN GIỌNG NÓI =====================
elif mode == "Trò chuyện giọng nói":    
    recognizer = sr.Recognizer()
    audio_queue = queue.Queue()

    def recognize_speech_from_stream(audio_data):
        """Chuyển đổi giọng nói từ stream thành văn bản theo thời gian thực."""
        try:
            return recognizer.recognize_google(audio_data, language="vi-VN")
        except sr.UnknownValueError:
            return "..."
        except sr.RequestError:
            return "Lỗi nhận diện giọng nói!"

    # Chế độ trò chuyện giọng nói
    st.subheader("🎙️ Trò chuyện bằng giọng nói (Thời gian thực)")

    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    if webrtc_ctx.audio_receiver:
        st.write("🎤 **Đang lắng nghe...**")
        transcript_placeholder = st.empty()

        try:
            while True:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if not audio_frames:
                    continue

                # Ghép nối các frame thành dạng NumPy array
                audio = np.concatenate([frame.to_ndarray() for frame in audio_frames], axis=0)

                # Chuyển sang dạng âm thanh cho SpeechRecognition
                audio_data = sr.AudioData(audio.tobytes(), sample_rate=16000, sample_width=2)
                recognized_text = recognize_speech_from_stream(audio_data)

                # Hiển thị văn bản đang nói theo thời gian thực
                transcript_placeholder.write(f"🗣️ **Bạn:** {recognized_text}")

                # Khi người dùng dừng nói, gửi nội dung đến chatbot
                if recognized_text and recognized_text != "...":
                    with st.spinner("💭 Đang suy nghĩ..."):
                        answer = client.chat.completions.create(
                            messages=[{"role": "user", "content": recognized_text}],
                            model="llama3-70b-8192"
                        ).choices[0].message.content

                    st.write(f"**🧑‍🏫 Trợ lý AI:** {answer}")

                    # Đọc to câu trả lời
                    tts = gTTS(answer, lang="vi")
                    tts.save("response.mp3")
                    st.audio("response.mp3", format="audio/mp3")

        except Exception as e:
            st.error(f"Lỗi ghi âm: {e}")

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
