import google.generativeai as genai
import gradio as gr
import os
import time

# --- Cấu hình API Key ---
# Render sẽ cung cấp API Key qua biến môi trường.
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Lỗi: Vui lòng đặt GEMINI_API_KEY trong biến môi trường của Render.")
genai.configure(api_key=api_key)

# --- Khởi tạo mô hình ---
print("Đang khởi tạo mô hình HEYGAY...")
model = genai.GenerativeModel('gemini-2.5-flash')
print("Khởi tạo mô hình thành công!")

# --- Hàm logic chính của Chatbot ---
def gemini_chatbot_response(user_text, file_obj, chat_history):
    parts = []
    
    if file_obj is not None:
        try:
            print(f"Đang xử lý tệp: {file_obj.name}")
            uploaded_file = genai.upload_file(path=file_obj.name)
            
            while uploaded_file.state.name == "PROCESSING":
                print("Tệp đang được xử lý, vui lòng đợi...")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name != "ACTIVE":
                raise ValueError(f"Xử lý tệp thất bại với trạng thái: {uploaded_file.state.name}")
            
            print(f"Tệp đã ở trạng thái ACTIVE: {uploaded_file.name}")
            parts.append(uploaded_file)
            
        except Exception as e:
            chat_history.append((user_text, f"Lỗi khi xử lý tệp: {e}"))
            return "", None, chat_history

    if user_text:
        parts.append(user_text)

    if not parts:
        chat_history.append(("", "Vui lòng nhập tin nhắn hoặc tải lên một tệp."))
        return "", None, chat_history

    try:
        print("Đang gửi yêu cầu đến HEYGAY...")
        response = model.generate_content(parts)
        model_response = response.text
        print("Đã nhận phản hồi từ Gemini.")
    except Exception as e:
        model_response = f"Rất tiếc, đã xảy ra lỗi: {e}"

    chat_history.append((user_text or "[Đã gửi một tệp]", model_response))
    return "", None, chat_history

# --- Giao diện Gradio ---
with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
    gr.Markdown("# 🤖 Chatbot Đa phương thức với ")
    gr.Markdown("Trò chuyện bằng văn bản hoặc tải lên hình ảnh, âm thanh, video để bắt đầu.")

    # Bạn cần có 2 file ảnh này trong thư mục dự án
    chatbot = gr.Chatbot(label="Cuộc trò chuyện", height=600, avatar_images=("user.png", "bot.png"))

    with gr.Row():
        file_upload = gr.File(label="Tải lên tệp (ảnh, âm thanh, video)", file_count="single")
        text_input = gr.Textbox(label="Nhập tin nhắn của bạn...", placeholder="Ví dụ: Tóm tắt nội dung trong video này cho tôi.", scale=3)

    send_btn = gr.Button("Gửi", variant="primary")

    send_btn.click(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_upload, chatbot],
        outputs=[text_input, file_upload, chatbot]
    )
    text_input.submit(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_upload, chatbot],
        outputs=[text_input, file_upload, chatbot]
    )

# --- Khởi chạy ứng dụng ---
# Chạy server trên 0.0.0.0 để Render có thể truy cập
print("Đang khởi chạy giao diện Gradio trên server...")
demo.launch(server_name="0.0.0.0", server_port=7860)
