# app.py (Phiên bản giao diện nâng cấp với thẻ đính kèm)

import google.generativeai as genai
import gradio as gr
import os
import time
from PIL import Image

# --- Cấu hình API Key ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Lỗi: Vui lòng đặt GEMINI_API_KEY trong environment...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
print("Khởi tạo mô hình thành công!")


# --- HELPER FUNCTIONS ---

def get_file_type(file_path):
    """Xác định loại file dựa trên extension"""
    if not file_path:
        return "unknown"
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        return "image"
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        return "video"
    elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
        return "audio"
    elif ext in ['.pdf']:
        return "pdf"
    else:
        return "document"


def create_attachment_card(file_obj, is_uploading=False):
    """Tạo HTML cho thẻ đính kèm file"""
    if is_uploading:
        return """
        <div style="
            display: flex;
            align-items: center;
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 8px 0;
            animation: pulse 2s infinite;
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 3px solid #4a90e2;
                border-top: 3px solid transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 12px;
            "></div>
            <div>
                <div style="font-weight: 600; color: #4a90e2; font-size: 14px;">
                    Đang tải file lên...
                </div>
                <div style="color: #64748b; font-size: 12px;">
                    Vui lòng đợi trong giây lát
                </div>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.8; }
            }
        </style>
        """
    
    if not file_obj:
        return ""
    
    file_name = os.path.basename(file_obj.name)
    file_type = get_file_type(file_obj.name)
    file_size = os.path.getsize(file_obj.name) if os.path.exists(file_obj.name) else 0
    file_size_mb = round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
    
    # Icon dựa trên loại file
    if file_type == "image":
        icon = "🖼️"
        color = "#10b981"
    elif file_type == "video":
        icon = "🎥"
        color = "#f59e0b"
    elif file_type == "audio":
        icon = "🎵"
        color = "#8b5cf6"
    elif file_type == "pdf":
        icon = "📄"
        color = "#ef4444"
    else:
        icon = "📁"
        color = "#6b7280"
    
    return f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    " onmouseover="this.style.boxShadow='0 4px 8px rgba(0, 0, 0, 0.15)'" 
       onmouseout="this.style.boxShadow='0 2px 4px rgba(0, 0, 0, 0.1)'">
        <div style="display: flex; align-items: center;">
            <div style="
                font-size: 24px;
                margin-right: 12px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: {color}15;
                border-radius: 8px;
            ">
                {icon}
            </div>
            <div>
                <div style="
                    font-weight: 600;
                    color: #1e293b;
                    font-size: 14px;
                    margin-bottom: 2px;
                    max-width: 200px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                ">
                    {file_name}
                </div>
                <div style="color: #64748b; font-size: 12px;">
                    {file_type.title()} • {file_size_mb} MB
                </div>
            </div>
        </div>
        <button onclick="clearAttachment()" style="
            background: #fee2e2;
            color: #dc2626;
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        " onmouseover="this.style.background='#fecaca'" onmouseout="this.style.background='#fee2e2'">
            ×
        </button>
    </div>
    <script>
        function clearAttachment() {{
            // Trigger clear attachment event
            const clearBtn = document.querySelector('[data-testid="clear-attachment-btn"]');
            if (clearBtn) clearBtn.click();
        }}
    </script>
    """


# --- MAIN FUNCTIONS ---

def handle_file_upload(file_obj, chat_history_display, attachment_display):
    """Xử lý khi người dùng tải file lên"""
    if file_obj is not None:
        print(f"File uploaded: {file_obj.name}")
        
        # Hiển thị trạng thái đang tải lên
        uploading_card = create_attachment_card(None, is_uploading=True)
        
        # Simulate upload delay (trong thực tế, bạn có thể bỏ phần này)
        time.sleep(1)
        
        # Tạo thẻ đính kèm hoàn chỉnh
        attachment_card = create_attachment_card(file_obj)
        
        return file_obj, attachment_card
    
    return None, ""


def clear_attachment():
    """Xóa file đính kèm"""
    return None, ""


def gemini_chatbot_response(user_text, file_state_obj, chat_session, chat_history_display, attachment_display):
    """Hàm xử lý phản hồi từ Gemini"""
    if not user_text.strip() and file_state_obj is None:
        return "", chat_session, chat_history_display, file_state_obj, attachment_display
    
    if chat_session is None:
        print("Bắt đầu phiên trò chuyện mới.")
        chat_session = model.start_chat(history=[])

    parts = []
    
    # Xử lý file nếu có
    if file_state_obj is not None:
        try:
            print(f"Đang xử lý file: {file_state_obj.name}")
            uploaded_file = genai.upload_file(path=file_state_obj.name)
            
            while uploaded_file.state.name == "PROCESSING":
                print("File đang được xử lý...")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name != "ACTIVE":
                raise ValueError(f"Xử lý file thất bại: {uploaded_file.state.name}")
            
            print(f"File đã sẵn sàng: {uploaded_file.name}")
            parts.append(uploaded_file)
            
        except Exception as e:
            error_msg = f"❌ Lỗi khi xử lý file: {e}"
            chat_history_display.append((user_text, error_msg))
            return "", chat_session, chat_history_display, file_state_obj, attachment_display

    if user_text.strip():
        parts.append(user_text)
    elif file_state_obj is not None:
        # Nếu chỉ có file mà không có text, tự động tạo prompt
        file_type = get_file_type(file_state_obj.name)
        if file_type == "image":
            parts.append("Hãy mô tả nội dung trong hình ảnh này.")
        elif file_type == "video":
            parts.append("Hãy tóm tắt nội dung trong video này.")
        elif file_type == "audio":
            parts.append("Hãy phiên âm và tóm tắt nội dung âm thanh này.")
        else:
            parts.append("Hãy phân tích nội dung trong file này.")
        
    try:
        print("Đang gửi tin nhắn đến Gemini...")
        response = chat_session.send_message(parts)
        model_response = response.text
        print("Đã nhận phản hồi từ Gemini.")
    except Exception as e:
        model_response = f"❌ Rất tiếc, đã xảy ra lỗi: {e}"

    # Thêm tin nhắn vào lịch sử
    user_display = user_text if user_text.strip() else "📎 [Đã gửi file đính kèm]"
    chat_history_display.append((user_display, model_response))

    # Reset file và attachment sau khi gửi
    return "", chat_session, chat_history_display, None, ""


def start_new_chat():
    """Bắt đầu cuộc trò chuyện mới"""
    print("Tạo cuộc trò chuyện mới.")
    return None, None, [], ""


# --- CSS STYLING ---
css = """
/* Main container styling */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Chat input row alignment */
#chat-input-row {
    align-items: flex-end;
    gap: 8px;
}

/* Upload button styling */
#upload-button {
    min-width: 44px !important;
    max-width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    font-size: 18px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important;
}

#upload-button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
}

/* Text input styling */
.textbox-container textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #ffffff !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    min-height: 44px !important;
    resize: none !important;
    transition: all 0.2s ease !important;
}

.textbox-container textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    outline: none !important;
}

/* Send button styling */
.send-button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 44px !important;
    transition: all 0.2s ease !important;
}

.send-button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3) !important;
}

/* Clear button styling */
.clear-button {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.clear-button:hover {
    background: linear-gradient(135deg, #475569 0%, #334155 100%) !important;
}

/* Chatbot container styling */
.chatbot-container {
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
}

/* Attachment display styling */
#attachment-display {
    margin-bottom: 8px;
}

/* Hide clear attachment button by default */
[data-testid="clear-attachment-btn"] {
    display: none !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    #chat-input-row {
        flex-direction: column;
        align-items: stretch;
    }
    
    #upload-button {
        align-self: flex-start;
        margin-bottom: 8px;
    }
}
"""

# --- GRADIO INTERFACE ---
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css=css,
    title="🤖 HEYGAY Chatbot"
) as demo:
    # State variables
    chat_session_state = gr.State(None)
    file_state = gr.State(None)

    # Header
    gr.HTML("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        ">🤖 HEYGAY Chatbot</h1>
        <p style="
            color: #64748b;
            font-size: 1.1rem;
            margin: 8px 0 0 0;
            font-weight: 400;
        ">Chatbot đa phương thức với AI Gemini</p>
    </div>
    """)

    # Main chat interface
    chatbot_display = gr.Chatbot(
        label="Cuộc trò chuyện",
        height=500,
        bubble_full_width=False,
        show_copy_button=True,
        elem_classes=["chatbot-container"]
    )
    
    # Attachment display area
    attachment_display = gr.HTML(
        value="",
        elem_id="attachment-display"
    )
    
    # Input area
    with gr.Row(elem_id="chat-input-row"):
        upload_btn = gr.UploadButton(
            "📎",
            file_types=["image", "video", "audio", ".pdf", ".txt", ".doc", ".docx"],
            elem_id="upload-button"
        )
        text_input = gr.Textbox(
            placeholder="Nhập tin nhắn của bạn... (hoặc tải file lên để phân tích)",
            show_label=False,
            container=False,
            scale=4,
            max_lines=3
        )
        send_btn = gr.Button(
            "Gửi",
            variant="primary",
            scale=1,
            elem_classes=["send-button"]
        )
    
    # Control buttons
    with gr.Row():
        clear_btn = gr.Button(
            "🔄 Cuộc trò chuyện mới",
            elem_classes=["clear-button"]
        )
        clear_attachment_btn = gr.Button(
            "Clear",
            elem_id="clear-attachment-btn",
            elem_classes=["hidden-button"]
        )

    # Event handlers
    upload_btn.upload(
        fn=handle_file_upload,
        inputs=[upload_btn, chatbot_display, attachment_display],
        outputs=[file_state, attachment_display]
    )
    
    clear_attachment_btn.click(
        fn=clear_attachment,
        outputs=[file_state, attachment_display]
    )
    
    send_btn.click(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_state, chat_session_state, chatbot_display, attachment_display],
        outputs=[text_input, chat_session_state, chatbot_display, file_state, attachment_display]
    )
    
    text_input.submit(
        fn=gemini_chatbot_response,
        inputs=[text_input, file_state, chat_session_state, chatbot_display, attachment_display],
        outputs=[text_input, chat_session_state, chatbot_display, file_state, attachment_display]
    )
    
    clear_btn.click(
        fn=start_new_chat,
        outputs=[chat_session_state, file_state, chatbot_display, attachment_display]
    )

# Launch the app
if __name__ == "__main__":
    print("🚀 Đang khởi chạy HEYGAY Chatbot...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )
