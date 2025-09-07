import streamlit as st
import uuid
from textblob import TextBlob
from datetime import date, datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="All-in-One App")
st.title("🎓 Student Productivity App")

# --- Dropdown Navigation ---
choice = st.selectbox(
    "Choose a module:",
    ["Course Management", "To-Do List", "Student Feedback"]
)

# ==============================================================
# 📚 COURSE MANAGEMENT
# ==============================================================
if choice == "Course Management":
    st.header("📚 Course Management")

    if "courses" not in st.session_state:
        st.session_state.courses = []
    if "editing" not in st.session_state:
        st.session_state.editing = {}

    # --- Add Course ---
    st.subheader("Add a Course")
    with st.form("add_course_form", clear_on_submit=True):
        new_name = st.text_input("Course Name")
        new_desc = st.text_area("Course Description (optional)")
        add_clicked = st.form_submit_button("Add Course")
        if add_clicked:
            if new_name.strip():
                cid = str(uuid.uuid4())
                st.session_state.courses.append({
                    "id": cid,
                    "name": new_name.strip(),
                    "description": new_desc.strip()
                })
                st.success(f"Course '{new_name.strip()}' added.")
            else:
                st.error("Course name cannot be empty.")

    st.markdown("---")

    # --- Display Courses ---
    st.subheader("Current Courses")
    if not st.session_state.courses:
        st.info("No courses added yet.")
    else:
        for course in list(st.session_state.courses):
            cid = course["id"]
            with st.form(f"form_{cid}"):
                col_name, col_desc, col_actions = st.columns([3, 5, 2])

                if st.session_state.editing.get(cid, False):
                    # --- EDIT MODE ---
                    edited_name = col_name.text_input(
                        "Course Name", value=course["name"], key=f"name_{cid}")
                    edited_desc = col_desc.text_area(
                        "Description", value=course["description"], key=f"desc_{cid}")
                    save = col_actions.form_submit_button("Save")
                    cancel = col_actions.form_submit_button("Cancel")

                    if save:
                        if edited_name.strip():
                            for c in st.session_state.courses:
                                if c["id"] == cid:
                                    c["name"] = edited_name.strip()
                                    c["description"] = edited_desc.strip()
                                    break
                            st.session_state.editing[cid] = False
                            st.success("Course updated.")
                        else:
                            st.error("Course name cannot be empty.")
                    elif cancel:
                        st.session_state.editing[cid] = False
                else:
                    # --- VIEW MODE ---
                    col_name.markdown(f"**{course['name']}**")
                    col_desc.write(course["description"] if course["description"].strip(
                    ) else "_No description provided._")

                    edit = col_actions.form_submit_button("Edit")
                    delete = col_actions.form_submit_button("Delete")

                    if edit:
                        st.session_state.editing[cid] = True
                    if delete:
                        st.session_state.courses = [
                            c for c in st.session_state.courses if c["id"] != cid]
                        st.session_state.editing.pop(cid, None)
                        st.success(f"Course '{course['name']}' deleted.")

# ==============================================================
# ✅ TO-DO LIST (with Deadlines + Priority + Completed at Bottom)
# ==============================================================
elif choice == "To-Do List":
    st.header("✅ To-Do Manager")

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    with st.form("add_task_form", clear_on_submit=True):
        task_input = st.text_input("Task Name")
        task_deadline = st.date_input("Deadline")
        add_task = st.form_submit_button("Add Task")

        if add_task:
            if task_input.strip():
                st.session_state.tasks.append({
                    "task": task_input,
                    "status": "Pending",
                    "deadline": str(task_deadline)
                })
                st.success("Task added!")

                # AI Suggestions
                if "assignment" in task_input.lower():
                    st.info(
                        "AI Suggestion: Set deadline before course submission date!")
                elif "exam" in task_input.lower():
                    st.info("AI Suggestion: Start revision 5 days earlier!")
            else:
                st.error("Task name cannot be empty.")

    st.subheader("Your Tasks (Prioritized by Deadline)")

    if not st.session_state.tasks:
        st.info("No tasks added yet.")
    else:
        today = date.today()

        # 🔥 Sort: Pending tasks first (by deadline), then Completed tasks
        sorted_tasks = sorted(
            st.session_state.tasks,
            key=lambda x: (x["status"] == "Completed", x["deadline"])
        )

        for i, t in enumerate(sorted_tasks):
            deadline_date = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
            days_left = (deadline_date - today).days

            # 🔴 Overdue | 🟡 Due soon | 🟢 Safe
            if t["status"] == "Completed":
                color = "gray"
                urgency = "Completed"
            else:
                if days_left < 0:
                    color = "red"
                    urgency = "Overdue!"
                elif days_left <= 2:
                    color = "orange"
                    urgency = f"Due in {days_left} days"
                else:
                    color = "green"
                    urgency = f"Due in {days_left} days"

            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.markdown(
                f"📌 <span style='color:{color}'>{t['task']}</span>  "
                f"(Deadline: {t['deadline']} – {urgency})",
                unsafe_allow_html=True
            )
            col2.write(f"Status: **{t['status']}**")

            if col3.button("✔️", key=f"done_{i}"):
                idx = st.session_state.tasks.index(t)
                st.session_state.tasks[idx]["status"] = "Completed"

            if col4.button("🗑️", key=f"del_{i}"):
                st.session_state.tasks.remove(t)
                st.rerun()


# ==============================================================
# 📝 STUDENT FEEDBACK
# ==============================================================
elif choice == "Student Feedback":
    st.header("📝 Student Feedback")

    if "feedbacks" not in st.session_state:
        st.session_state.feedbacks = []

    analyzer = SentimentIntensityAnalyzer()

    # Function to determine sentiment
    def get_sentiment(feedback):
        feedback_lower = feedback.lower()
        positive_words = ["good", "easy", "simple",
                          "helpful", "clear", "excellent"]
        negative_words = ["hard", "difficult",
                          "boring", "confusing", "poor", "tight"]

        pos_count = sum(word in feedback_lower for word in positive_words)
        neg_count = sum(word in feedback_lower for word in negative_words)

        if pos_count > 0 and neg_count > 0:
            return "Neutral"
        elif pos_count > 0:
            return "Positive"
        elif neg_count > 0:
            return "Negative"
        else:
            return "Neutral"

    # --- Input Subject ---
    subject_name = st.text_input("Enter Subject / Course Name")

    # --- Feedback Input ---
    feedback_input = st.text_area("Enter feedback for this subject")

    if st.button("Submit Feedback"):
        if subject_name.strip() == "":
            st.error("Please enter the subject/course name.")
        elif feedback_input.strip() == "":
            st.error("Please enter your feedback.")
        else:
            sentiment = get_sentiment(feedback_input)
            st.session_state.feedbacks.append({
                "subject": subject_name.strip(),
                "text": feedback_input,
                "sentiment": sentiment
            })
            st.success(f"Feedback for '{subject_name.strip()}' submitted!")

    # --- Display All Feedbacks ---
    st.subheader("All Feedbacks")
    for fb in st.session_state.feedbacks:
        st.write(f"📚 Subject: **{fb['subject']}**")
        st.write(
            f"📝 Feedback: {fb['text']}  |  Sentiment: **{fb['sentiment']}**")
        st.markdown("---")
