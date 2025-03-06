import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Khởi tạo Groq API
client = Groq(api_key="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")

# Lựa chọn ngôn ngữ
language = st.radio("Chọn ngôn ngữ giảng dạy:", ["Tiếng Anh", "Tiếng Trung"])

# Xác định prompt theo ngôn ngữ
if language == "Tiếng Anh":
    system_prompt = "Bạn là giáo viên dạy tiếng Anh cho người Việt. Hãy trả lời dễ hiểu, giải thích rõ ràng, dùng ví dụ cụ thể, dịch nghĩa và trả lời bằng tiếng Việt. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp."
    tts_lang = "en"
elif language == "Tiếng Trung":
    system_prompt = "Bạn là giáo viên dạy tiếng Trung cho người Việt. Hãy trả lời dễ hiểu, giải thích rõ ràng, dùng ví dụ cụ thể, dịch nghĩa và trả lời bằng tiếng Việt. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp."
    tts_lang = "zh"

def ask_groq(query):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(messages=messages, model="llama3-70b-8192")
    return response.choices[0].message.content

def text_to_speech(text):
    tts = gTTS(text, lang=tts_lang)
    tts.save("output.mp3")
    st.audio("output.mp3", format="audio/mp3")

# UI Streamlit
st.set_page_config(page_title="Chatbot Học Ngôn Ngữ", layout="wide")
st.title("🗣️ Chatbot Dạy Ngôn Ngữ")
st.write("Hỏi về từ vựng, ngữ pháp, cách phát âm hoặc giao tiếp thực tế!")

# Tạo sidebar để chuyển đổi giữa các chế độ
mode = st.sidebar.radio("Chọn chế độ:", ["Chatbot", "Học phát âm"])

if mode == "Chatbot":
    # Lịch sử trò chuyện
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Gợi ý câu hỏi động
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = [
            "Làm thế nào để học từ vựng hiệu quả?",
            "Cách phát âm chuẩn từ 'schedule'?",
            "Sự khác biệt giữa 'say', 'tell', 'speak' và 'talk'?",
            "Cấu trúc thì hiện tại hoàn thành?",
            "Mẹo nhớ cách dùng giới từ trong ngôn ngữ này?"
        ]

    st.sidebar.subheader("🎯 Gợi ý câu hỏi")
    selected_query = None
    for s in st.session_state.suggestions:
        if st.sidebar.button(s):
            selected_query = s
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(selected_query)
            st.session_state.chat_history.append({"question": selected_query, "answer": answer})

    # Hiển thị lịch sử trò chuyện trong hộp cuộn
    st.subheader("📜 Lịch sử trò chuyện")
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
            st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")

    # Nhập câu hỏi cố định bên dưới
    query = st.text_input("Nhập câu hỏi của bạn:", key="query_input")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input("", key="query_input", on_change=lambda: on_submit() if st.session_state.query_input.strip() else None)
    with col2:
        if st.button("Gửi"):
            on_submit()

    def on_submit():
        query = st.session_state.query_input.strip()
        if query:
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(query)
            st.session_state.chat_history.append({"question": query, "answer": answer})
            st.session_state.query_input = ""

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
