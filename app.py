# UI Streamlit
st.set_page_config(page_title="Chatbot Học Tiếng Anh", layout="wide")
st.title("🗣️ Chatbot Dạy Tiếng Anh")
st.write("Hỏi về từ vựng, ngữ pháp, cách phát âm hoặc giao tiếp thực tế!")

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

# Nhập câu hỏi
query = st.text_input("Nhập câu hỏi của bạn:", value=selected_query if selected_query else "")
if query:
    with st.spinner("Đang tạo câu trả lời..."):
        answer = ask_groq(query)
    st.session_state.chat_history.append({"question": query, "answer": answer})
    
    # Cập nhật gợi ý dựa trên câu hỏi
    st.session_state.suggestions = [
        "Hãy cho tôi thêm ví dụ về câu trên.",
        "Có quy tắc nào giúp nhớ điều này không?",
        "Cách dùng trong thực tế như thế nào?",
        "Có lỗi phổ biến nào khi sử dụng không?",
        "Làm sao để áp dụng kiến thức này vào giao tiếp hàng ngày?"
    ]

# Hiển thị lịch sử trò chuyện
st.subheader("📜 Lịch sử trò chuyện")
for chat in st.session_state.chat_history:
    st.write(f"**🧑‍🎓 Bạn:** {chat['question']}")
    st.write(f"**🧑‍🏫 Trợ lý AI:** {chat['answer']}")
