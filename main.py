from google import genai
API_KEY = "ضع_مفتاحك_هنا"

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import database
import random
import os

# --- نافذة تسجيل الدخول ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Store Management System")
        self.root.geometry("400x300")
        self.root.config(bg="#2c3e50")
        self.root.resizable(False, False)

        self.username_var = StringVar()
        self.password_var = StringVar()

        frame = Frame(self.root, bg="white", bd=2, relief="groove")
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=340, height=240)

        Label(frame, text="System Login", font=("Tahoma", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=15)

        Label(frame, text="Username:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="w", padx=25)
        Entry(frame, textvariable=self.username_var, font=("Tahoma", 10), bd=1, relief="solid").pack(fill="x", padx=25, pady=5)

        Label(frame, text="Password:", font=("Tahoma", 9, "bold"), bg="white").pack(anchor="w", padx=25)
        Entry(frame, textvariable=self.password_var, show="*", font=("Tahoma", 10), bd=1, relief="solid").pack(fill="x", padx=25, pady=5)

        Button(frame, text="Login", font=("Tahoma", 10, "bold"), bg="#27ae60", fg="white", bd=0, command=self.verify_login).pack(fill="x", padx=25, pady=15)

    def verify_login(self):
        user = self.username_var.get()
        pwd = self.password_var.get()
        if user == "admin" and pwd == "1234":
            self.root.destroy()
            main_root = Tk()
            MainWindow(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

# --- النافذة الرئيسية والتطبيق ---
class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Store Management System")
        self.root.geometry("1000x600")
        
        # يمكنك إضافة دالة فتح التقارير وزر AI Advisor داخل نافذة التقارير لديك هكذا:
        # Button(bottom_rep_frame, text="🤖 AI Advisor", font=("Tahoma", 9, "bold"), bg="#6f42c1", fg="white", command=lambda: open_ai_advisor(sales_data, total_sales_revenue, report_win)).pack(side=RIGHT, padx=5)

# --- دوال الذكاء الاصطناعي (Gemini AI) ---
def get_ai_business_advice(sales_data, total_revenue):
    if API_KEY == "ضع_مفتاحك_هنا":
        return "⚠️ تنبيه: يرجى إدخال مفتاح Gemini API الصحيح في الكود."
    
    try:
        client = genai.Client(api_key=API_KEY)
        
        summary_text = f"إجمالي الإيرادات: {total_revenue} دينار.\nعدد عمليات البيع: {len(sales_data)}.\nآخر عمليات البيع:\n"
        for s in sales_data[-10:]:
            summary_text += f"- منتج: {s[2]}, الكمية: {s[4]}, الإجمالي: {s[5]}\n"
            
        prompt = f"""
        أنت مستشار تجاري لأنظمة المحلات (POS). بناءً على بيانات المبيعات التالية، أعطني تحليلاً قصيراً ومفيداً بالعربي يوضح:
        1. تقييم أداء المبيعات.
        2. توصيات لزيادة الأرباح أو إدارة المخزون.
        
        البيانات:
        {summary_text}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def open_ai_advisor(sales_data, total_sales_revenue, report_win):
    ai_win = Toplevel(report_win)
    ai_win.title("Gemini AI Business Consultant")
    ai_win.geometry("600x450")
    ai_win.config(bg="white")

    Label(ai_win, text="🧠 AI Analysis & Recommendations", font=("Tahoma", 12, "bold"), bg="white", fg="#6f42c1").pack(pady=10)

    text_frame = Frame(ai_win, bg="white")
    text_frame.pack(fill="both", expand=True, padx=15, pady=5)

    ai_scroll = Scrollbar(text_frame)
    ai_scroll.pack(side=RIGHT, fill=Y)

    ai_text_box = Text(text_frame, font=("Tahoma", 10), wrap=WORD, yscrollcommand=ai_scroll.set, bd=1, relief="solid")
    ai_scroll.pack(fill="both", expand=True)

    ai_text_box.insert(END, "⏳ جاري تحليل المبيعات باستخدام الذكاء الاصطناعي...")
    ai_win.update()

    advice = get_ai_business_advice(sales_data, total_sales_revenue)
    
    ai_text_box.delete("1.0", END)
    ai_text_box.insert(END, advice)

if __name__ == "__main__":
    root = Tk()
    LoginWindow(root)
    root.mainloop()

 