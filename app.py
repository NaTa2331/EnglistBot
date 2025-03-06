import streamlit as st
from groq import Groq

# Khởi tạo Groq API
client = Groq(api_key="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")

def ask_groq(query):
    messages = [
        {"role": "system", "content": "Bạn là giáo viên dạy tiếng Anh cho người Việt. Hãy trả lời dễ hiểu, giải thích rõ ràng, dùng ví dụ cụ thể, dịch nghĩa tiếng Việt khi cần thiết. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp. Trả lời câu hỏi bằng tiếng Việt."},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(messages=messages, model="llama3-70b-8192")
    return response.choices[0].message.content

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
        
        # Cập nhật gợi ý dựa trên chủ đề câu hỏi
        if "từ vựng" in query.lower():
            st.session_state.suggestions = [
                "Làm sao để nhớ từ vựng lâu dài?",
                "Có mẹo nào học từ vựng nhanh không?",
                "Những từ vựng phổ biến trong giao tiếp?",
                "Tôi nên học từ vựng theo chủ đề nào?"
            ]
        elif "ngữ pháp" in query.lower():
            st.session_state.suggestions = [
                "Những lỗi sai thường gặp trong ngữ pháp?",
                "Có cách nào học ngữ pháp dễ dàng hơn không?",
                "Ví dụ về câu sử dụng thì quá khứ hoàn thành?",
                "Sự khác biệt giữa 'will' và 'going to'?"
            ]
        else:
            st.session_state.suggestions = [
                "Hãy cho tôi thêm ví dụ về câu trên.",
                "Có quy tắc nào giúp nhớ điều này không?",
                "Cách dùng trong thực tế như thế nào?",
                "Có lỗi phổ biến nào khi sử dụng không?",
                "Làm sao để áp dụng kiến thức này vào giao tiếp hàng ngày?"
            ]

st.text_input("Nhập câu hỏi của bạn:", key="query_input", on_change=on_submit)

