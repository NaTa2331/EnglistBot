import streamlit as st
from groq import Groq

# Khởi tạo Groq API
client = Groq(api_key="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")

def ask_groq(query):
    messages = [
        {"role": "system", "content": "Bạn là giáo viên dạy tiếng Anh cho người Việt. Hãy trả lời dễ hiểu, giải thích rõ ràng, dùng ví dụ cụ thể, dịch nghĩa tiếng Việt khi cần thiết. Nếu có thể, hãy cung cấp mẹo ghi nhớ hoặc cách sử dụng thực tế trong giao tiếp. Trả lời bằng tiếng Việt."},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(messages=messages, model="mixtral-8x7b-32768")
    return response.choices[0].message.content

# UI Streamlit
st.set_page_config(page_title="Chatbot Học Tiếng Anh", layout="wide")
st.title("🗣️ Chatbot Dạy Tiếng Anh")
st.write("Hỏi về từ vựng, ngữ pháp, cách phát âm hoặc giao tiếp thực tế!")

query = st.text_input("Nhập câu hỏi của bạn:")
if query:
    with st.spinner("Đang tạo câu trả lời..."):
        answer = ask_groq(query)
    st.write("**🧑‍🏫 Trợ lý AI:**")
    st.write(answer)