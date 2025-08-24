# app.py (Phiên bản giao diện Gemini-style)

import google.generativeai as genai
import gradio as gr
import os
import time

# --- Cấu hình API Key ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Lỗi: Vui lòng đặt GEMINI_API_KEY troHEYGAY...")
model = genai.GenerativeModel('gemini-2.5-flash')
print("Khởi tạo mô hình thành công!")


# --- BẮT ĐẦU PHẦN NÂNG CẤP GIAO DIỆN ---

def handle_file_upload(file_obj, chat_history_display):
    """
    Hàm này được gọi ngay khi người dùng tải tệp lên qua UploadButton.
    Nó không gọi API Gemini, chỉ lưu tệp vào state và cập nhật giao diện.
    """
    if file_obj is not None:
        # Cập nhật lịch sử hiển thị để thông báo cho người dùng
        # Điều này không gửi đến AI, chỉ là phản hồi trên UI
        chat_history_display.append(
            (None, f"📁 Đã tải lên tệp: **{os.path.basename(file_obj.name)}**. Bây giờ hãy đặt câu hỏi về nó.")
        )
        # Trả về đối tượng tệp để lưu vào state và lịch sử hiển thị đã cập nhật
        return file_obj, chat_history_display
    # Nếu không có tệp, không trả về gì
    return None, chat_history_display


def gemini_chatbot_response(user_text, file_state_obj, chat_session, chat_history_display):
    """
    Hàm logic chính, giờ đây nhận tệp từ 'file_state_obj'.
    """
    if chat_session is None:
        print("Bắt đầu một phiên trò chuyện mới.")
        chat_session = model.start_chat(history=[])

    parts = []
    
    # Chỉ xử lý tệp NẾU nó tồn tại trong state
    if file_state_obj is not None:
        try:
            print(f"Đang xử lý tệp từ state: {file_state_obj.name}")
            uploaded_file = genai.upload_file(path=file_state_obj.name)
            
            while uploaded_file.state.name == "PROCESSING":
                print("Tệp đang được xử lý, vui lòng đợi...")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name != "ACTIVE":
                raise ValueError(f"Xử lý tệp thất bại với trạng thái: {uploaded_file.state.name}")
            
            print(f"Tệp đã ở trạng thái ACTIVE: {uploaded_file.name}")
            parts.append(uploaded_file)
            
        except Exception as e:
            chat_history_display.append((user_text, f"Lỗi khi xử lý tệp: {e}"))
            # Vẫn trả về file_state_obj để người dùng có thể thử lại với câu lệnh khác
            return "", chat_session, chat_history_display, file_state_obj

    if user_text:
        parts.append(user_text)
    else: # Nếu người dùng chỉ gửi tệp mà không có văn bản
        # Yêu cầu người dùng nhập thêm
        chat_history_display.append((None, "Vui lòng nhập một câu hỏi hoặc yêu cầu liên quan đến tệp."))
        return "", chat_session, chat_history_display, file_state_obj
        
    try:
        print("Đang gửi tin nhắn đến phiên trò chuyện của Gemini...")
        response = chat_session.send_message(parts)
        model_response = response.text
        print("Đã nhận phản hồi.")
    except Exception as e:
        model_response = f"Rất tiếc, đã xảy ra lỗi: {e}"

    chat_history_display.append((user_text, model_response))

    # Sau khi gửi, xóa tệp khỏi state để chuẩn bị cho lượt tiếp theo
    return "", chat_session, chat_history_display, None


def start_new_chat():
    """Reset mọi thứ để bắt đầu cuộc trò chuyện mới."""
    print("Yêu cầu tạo cuộc trò chuyện mới.")
    return None, None, []


# --- Giao diện Gradio với CSS tùy chỉnh ---
# Thêm CSS để tạo kiểu cho nút tải lên và ô nhập liệu
css = """
/* Căn chỉnh các mục trong hàng chat-input */
#chat-input-row {
    align-items: center;
}
/* Tạo kiểu cho nút tải lên trông giống như nút biểu tượng */
#upload-button {
    min-width: 45px !important;
    max-width: 45px !important;
    height: 45px !important;
    border-radius: 50% !important; /* Bo tròn */
    font-size: 20px !important; /* Kích thước icon '+' */
    margin-right: 10px !important;
}
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo"), css=css) as demo:
    # State để lưu phiên trò chuyện (trí nhớ)
    chat_session_state = gr.State(None)
    # State để lưu đối tượng tệp đã tải lên
    file_state = gr.State(None)

    gr.Markdown("# 🤖 Chatbot Đa phương thức HEYGAY")
    gr.Markdown("TÔI CÓ THỂ GIÚP GÌ CHO BẠN.")

    chatbot_display = gr.Chatbot(label="Cuộc trò chuyện", height=600, bubble_full_width=False, avatar_images=("user.png", "bot.png"))

    # Đặt các thành phần nhập liệu vào một hàng để căn chỉnh
    with gr.Row(elem_id="chat-input-row"):
        upload_btn = gr.UploadButton(
            "+", 
            file_types=["image", "video", "audio"],
            elem_id="upload-button" # ID để áp dụng CSS
        )
        text_input = gr.Textbox(
            label="Nhập tin nhắn của bạn...",
            placeholder="Ví dụ: Tóm tắt nội dung trong video này cho tôi.",
            scale=4, # Làm cho ô văn bản rộng hơn
            show_label=False # Ẩn label "Nhập tin nhắn của bạn..."
        )
        send_btn = gr.Button("Gửi", variant="primary", scale=1)

    clear_btn = gr.Button("🔄 Trò chuyện mới")
    
    # --- Định nghĩa các luồng sự kiện ---
    
    # 1. Khi người dùng tải tệp lên qua nút '+'
    upload_btn.upload(
        fn=handle_file_upload,
        inputs=[upload_btn, chatbot_display],
        outputs=[file_state, chatbot_display]
    )

    # 2. Khi người dùng nhấn nút 'Gửi'
    send_btn.click(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_state, chat_session_state, chatbot_display],
        outputs=[text_input, chat_session_state, chatbot_display, file_state] # Xóa file_state sau khi gửi
    )
    text_input.submit(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_state, chat_session_state, chatbot_display],
        outputs=[text_input, chat_session_state, chatbot_display, file_state]
    )
    
    # 3. Khi người dùng muốn bắt đầu cuộc trò chuyện mới
    clear_btn.click(
        fn=start_new_chat,
        inputs=[],
        outputs=[chat_session_state, file_state, chatbot_display]
    )

# --- Khởi chạy ứng dụng ---
print("Đang khởi chạy giao diện Gradio trên server...")
demo.launch(server_name="0.0.0.0", server_port=7860)
