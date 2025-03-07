import streamlit as st
from groq import Groq
from gtts import gTTS

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

def text_to_speech(text):
    tts = gTTS(text, lang=tts_lang)
    tts.save("output.mp3")
    st.audio("output.mp3", format="audio/mp3")

# UI Streamlit
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
            # Từ vựng
            "Làm thế nào để học từ vựng nhanh và nhớ lâu?",
            "Từ nào thường bị nhầm lẫn trong tiếng Anh?",
            "Những cụm từ (collocations) phổ biến trong giao tiếp?",

            # Phát âm
            "Làm sao để phát âm chuẩn giọng Anh - Mỹ?",
            "Cách phát âm đúng các từ trong Anh - Anh và Anh - Mỹ?",
            "Những âm dễ nhầm lẫn với người Việt (ví dụ: /θ/ và /s/)?",

            # Ngữ pháp
            "Cấu trúc thì hiện tại hoàn thành và cách dùng?",
            "Phân biệt 'will' và 'going to' trong thì tương lai?",
            "Cách sử dụng mạo từ 'a', 'an', 'the' đúng cách?",

            # Giao tiếp thực tế
            "Cách trả lời tự nhiên khi gặp người lạ?",
            "Những câu hỏi thông dụng khi đi du lịch?",
            "Cách nói lịch sự khi nhờ ai đó giúp đỡ?",

            # Mẹo học tiếng Anh
            "Làm thế nào để cải thiện kỹ năng nghe tiếng Anh?",
            "Có phương pháp nào giúp luyện nói tự tin hơn?",
            "Ứng dụng nào giúp học tiếng Anh hiệu quả?"
        ]

    st.sidebar.subheader("🎯 Gợi ý câu hỏi")
    for s in st.session_state.suggestions:
        if st.sidebar.button(s):
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(s)
            st.session_state.chat_history.append({"question": s, "answer": answer})

    # Hiển thị lịch sử trò chuyện
    st.subheader("📜 Lịch sử trò chuyện")
    for chat in st.session_state.chat_history:
        st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
        st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")

    def update_suggestions(last_question):
        """Cập nhật gợi ý dựa trên câu hỏi gần nhất"""
        if "phát âm" in last_question.lower():
            st.session_state.suggestions = [
                "Làm sao để phát âm chuẩn hơn?",
                "Những lỗi phát âm phổ biến là gì?",
                "Cách cải thiện ngữ điệu khi nói?",
        ]
        elif "ngữ pháp" in last_question.lower():
            st.session_state.suggestions = [
                "Các lỗi ngữ pháp phổ biến?",
                "So sánh thì hiện tại đơn và hiện tại tiếp diễn?",
                "Làm sao để nhớ cấu trúc câu dễ dàng hơn?",
            ]
        elif "từ vựng" in last_question.lower():
            st.session_state.suggestions = [
                "Cách học từ vựng hiệu quả?",
                "Làm sao để nhớ từ vựng lâu?",
                "Có mẹo nào để học từ vựng nhanh không?",
            ]
        else:
            st.session_state.suggestions = [
                "Làm thế nào để học ngôn ngữ hiệu quả?",
                "Có phương pháp nào giúp nhớ nhanh hơn không?",
                "Cách giao tiếp tự nhiên hơn?",
        ]
    def on_submit():
        query = st.session_state.query_input.strip()
        if query:
            with st.spinner("Đang tạo câu trả lời..."):
                answer = ask_groq(query)
            st.session_state.chat_history.append({"question": query, "answer": answer})
            update_suggestions(query)  # Cập nhật gợi ý theo câu hỏi mới nhất
            st.session_state.query_input = ""

    st.text_input("Nhập câu hỏi của bạn:", key="query_input", on_change=on_submit)

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
