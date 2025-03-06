import streamlit as st
from groq import Groq

# Khởi tạo Groq API
client = Groq(api_key="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")

def ask_groq(query):
    messages = [
        {"role": "system", "content": "Bạn là giáo viên dạy tiếng Anh cho người Việt. Hãy trả lời dễ hiểu, giải thích rõ ràng, dùng ví dụ cụ thể, dịch nghĩa tiếng Việt. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp. Trả lời câu hỏi bằng tiếng Việt."},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(messages=messages, model="llama3-70b-8192")
    return response.choices[0].message.content

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# UI Streamlit
st.set_page_config(page_title="Chatbot Học Tiếng Anh", layout="wide")
st.title("🗣️ Chatbot Dạy Tiếng Anh")
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
            "Mẹo nhớ cách dùng giới từ trong tiếng Anh?"
        ]

    st.sidebar.subheader("🎯 Gợi ý câu hỏi")
    selected_query = None
    for s in st.session_state.suggestions:
        if st.sidebar.button(s):
            selected_query = s

    # Hiển thị lịch sử trò chuyện trong hộp cuộn
    st.subheader("📜 Lịch sử trò chuyện")
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
            st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")

    # Nhập câu hỏi cố định bên dưới
    def on_submit():
        query = st.session_state.query_input.strip()
        if query:
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(query)
            st.session_state.chat_history.append({"question": query, "answer": answer})
            st.session_state.query_input = ""
    
    st.text_input("Nhập câu hỏi của bạn:", key="query_input", on_change=on_submit)

elif mode == "Học phát âm":
    st.subheader("🔊 Học phát âm")
    word = st.text_input("Nhập từ cần phát âm:")
    if st.button("🔊 Nghe phát âm"):
        if word:
            text_to_speech(word)
        else:
            st.warning("Vui lòng nhập từ cần phát âm!")

