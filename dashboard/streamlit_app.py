import streamlit as st
import pandas as pd
import io
# -------- School Management Class ------
class School:
    def __init__(self, data_file="students.csv"):
        self.data_file = data_file
        self.df = self.load_data()

    def load_data(self):
        try:
            df = pd.read_csv(self.data_file)
        except FileNotFoundError:
            # If file doesn't exist, create empty df with columns
            df = pd.DataFrame(columns=["student_class", "student_age", "student_name"])
        return df

    def save_data(self):
        self.df.to_csv(self.data_file, index=False)

    def add_student(self, student_class, student_age, student_name):
        new_student = {"student_class": student_class, "student_age": student_age, "student_name": student_name}
        self.df = pd.concat([self.df, pd.DataFrame([new_student])], ignore_index=True)
        self.save_data()

    def delete_student(self, student_name):
        prev_len = len(self.df)
        self.df = self.df[self.df["student_name"] != student_name]
        self.save_data()
        return len(self.df) < prev_len

    def search_students(self, keyword):
        keyword = keyword.lower()
        return self.df[self.df.apply(lambda row: keyword in str(row["student_name"]).lower() or keyword in str(row["student_class"]).lower(), axis=1)]

    def update_student(self, old_name, new_class, new_age, new_name):
        idx = self.df.index[self.df["student_name"] == old_name]
        if not idx.empty:
            idx = idx[0]
            self.df.at[idx, "student_class"] = new_class
            self.df.at[idx, "student_age"] = new_age
            self.df.at[idx, "student_name"] = new_name
            self.save_data()
            return True
        return False

    def get_all_students(self):
        return self.df

    def students_per_class(self):
        return self.df["student_class"].value_counts()

    def average_age_per_class(self):
        return self.df.groupby("student_class")["student_age"].mean()

# ---------- Excel Export Helper ----------

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)  # Important to reset buffer to start
    return output.read()


# ---------- Streamlit App UI ----------

school = School()

st.title("🏫 School Management System")

# --- Add Student ---
st.header("➕ Add Student")
with st.form("add_student_form", clear_on_submit=True):
    student_class = st.text_input("Class")
    student_age = st.number_input("Age", min_value=5, max_value=20)
    student_name = st.text_input("Name")
    submitted = st.form_submit_button("Add Student")
    if submitted:
        if student_class and student_name:
            school.add_student(student_class, student_age, student_name)
            st.success(f"Student '{student_name}' added.")
        else:
            st.error("Please enter valid Name and Class.")

# --- Search Student ---
st.header("🔎 Search Students")
search_term = st.text_input("Search by Name or Class")
if search_term:
    results = school.search_students(search_term)
    if results.empty:
        st.info("No students found.")
    else:
        st.dataframe(results)

# --- Edit Student ---
st.header("✏️ Edit Student")
df = school.get_all_students()
if not df.empty:
    selected_name = st.selectbox("Select student to edit", df["student_name"].unique())
    selected_student = df[df["student_name"] == selected_name].iloc[0]

    with st.form("edit_student_form"):
        new_name = st.text_input("New Name", value=selected_student["student_name"])
        new_age = st.number_input("New Age", value=int(selected_student["student_age"]), min_value=5, max_value=20)
        new_class = st.text_input("New Class", value=selected_student["student_class"])
        update = st.form_submit_button("Update Student")
        if update:
            success = school.update_student(selected_name, new_class, new_age, new_name)
            if success:
                st.success(f"Student '{selected_name}' updated.")
            else:
                st.error("Update failed.")

# --- Delete Student ---
st.header("🗑️ Delete Student")
del_name = st.text_input("Enter Exact Name to Delete")
if st.button("Delete"):
    if del_name:
        deleted = school.delete_student(del_name)
        if deleted:
            st.success(f"Student '{del_name}' deleted.")
        else:
            st.error(f"No student named '{del_name}' found.")
    else:
        st.error("Please enter a name.")

# --- View All Students ---
st.header("📋 All Students")
all_students = school.get_all_students()
if not all_students.empty:
    st.dataframe(all_students)
else:
    st.info("No student data available.")

# --- Students Per Class Bar Chart ---
st.header("📊 Students Per Class")
if not all_students.empty:
    spc = school.students_per_class()
    st.bar_chart(spc)
else:
    st.info("No data to show chart.")

# --- Average Age Per Class ---
st.header("📈 Average Age Per Class")
if not all_students.empty:
    avg_age = school.average_age_per_class()
    st.bar_chart(avg_age)
else:
    st.info("No data to show average age.")

# --- Export to Excel ---
st.header("📤 Export Data")
if not all_students.empty:
    excel_data = to_excel(all_students)
    st.download_button(
        label="📥 Download Student Data as Excel",
        data=excel_data,
        file_name="students.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No data to export.")
