import streamlit as st
from google import genai
from PIL import Image

# إعداد واجهة الصفحة
st.set_page_config(page_title="مساعد الذكاء الاصطناعي الشامل", page_icon="🤖", layout="wide")
st.title("🤖 محادثة الذكاء الاصطناعي وتحليل الصور")

# 1. جلب المفتاح بأمان من Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ لم يتم العثور على المفتاح! يرجى إضافته في Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. تهيئة ذاكرة المحادثة (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. القائمة الجانبية (Sidebar) لرفع الصور وإدارة الجلسة
with st.sidebar:
    st.header("📷 إرفاق صورة")
    uploaded_file = st.file_uploader("اختر صورة للتحليل مع سؤالك...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="الصورة المرفقة حالياً", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ مسح المحادثة والبدء من جديد"):
        st.session_state.messages = []
        st.rerun()

# 4. عرض كافة الرسائل السابقة في الواجهة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=300)
        st.write(message["content"])

# 5. استقبال مدخلات المستخدم من شريط المحادثة
if prompt := st.chat_input("اكتب رسالتك أو سؤالك عن الصورة هنا..."):
    
    # قراءة الصورة إن وجدت
    current_image = Image.open(uploaded_file) if uploaded_file else None

    # عرض رسالة المستخدم فوراً في الشاشة
    with st.chat_message("user"):
        if current_image:
            st.image(current_image, width=300)
        st.write(prompt)

    # حفظ رسالة المستخدم والصورة في السجل
    user_msg = {"role": "user", "content": prompt}
    if current_image:
        user_msg["image"] = current_image
    st.session_state.messages.append(user_msg)

    # إرسال الطلب إلى Gemini API
    with st.chat_message("assistant"):
        with st.spinner("جاري المعالجة والتفكير..."):
            try:
                # تجميع المحتويات (الصورة + النص)
                contents = []
                if current_image:
                    contents.append(current_image)
                contents.append(prompt)

                # التوليد باستخدام نموذج متعدد الوسائط (Multimodal)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )
                
                # عرض النتيجة
                st.write(response.text)
                
                # حفظ استجابة النموذج في الذاكرة
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {e}")