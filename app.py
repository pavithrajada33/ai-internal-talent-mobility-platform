import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------
st.set_page_config(
    page_title="AI Internal Talent Mobility Platform",
    layout="wide"
)

st.title("AI-Powered Reskilling and Internal Talent Mobility Platform")
st.write(
    "This prototype helps employees check internal role suitability, identify skill gaps, "
    "complete a role-based assessment if eligible, and submit interest to HR."
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Dissertation Excel.xlsx"
    employee_df = pd.read_excel(file_path, sheet_name="Employee Data")
    course_df = pd.read_excel(file_path, sheet_name="Courses")
    return employee_df, course_df

employee_df, course_df = load_data()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "submitted_interests" not in st.session_state:
    st.session_state.submitted_interests = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def clean_skill_list(skill_text):
    if pd.isna(skill_text):
        return []
    return [
        skill.strip().lower()
        for skill in str(skill_text).split(",")
        if skill.strip() != ""
    ]

def find_skill_gap(current_skills, required_skills):
    current = set(clean_skill_list(current_skills))
    required = set(clean_skill_list(required_skills))
    missing = required - current

    if not missing:
        return "No skill gap"

    return ", ".join([skill.title() for skill in sorted(missing)])

def calculate_match_score(current_skills, required_skills):
    current = set(clean_skill_list(current_skills))
    required = set(clean_skill_list(required_skills))

    if len(required) == 0:
        return 0

    matched = current.intersection(required)
    score = (len(matched) / len(required)) * 100
    return round(score, 2)

course_mapping = dict(
    zip(
        course_df["skill"].str.lower().str.strip(),
        course_df["recommended_course"]
    )
)

def recommend_courses(skill_gap):
    if skill_gap == "No skill gap":
        return "No additional course required. Employee is ready for the role."

    missing_skills = clean_skill_list(skill_gap)
    recommendations = []

    for skill in missing_skills:
        course = course_mapping.get(skill)
        if course:
            recommendations.append(course)
        else:
            recommendations.append(f"No mapped course found for {skill.title()}")

    return ", ".join(recommendations)

def readiness_status(score):
    if score >= 80:
        return "Ready for Internal Transition"
    elif score >= 70:
        return "Eligible to Apply - Minor Upskilling Suggested"
    elif score >= 50:
        return "Needs Moderate Upskilling"
    else:
        return "Needs Significant Upskilling"

# -------------------------------------------------
# ROLE-BASED QUIZ BANK
# -------------------------------------------------
quiz_bank = {
    "HR Executive": [
        {"q": "What is the main purpose of recruitment?", "options": ["Hiring suitable candidates", "Preparing budgets", "Writing code"], "answer": "Hiring suitable candidates"},
        {"q": "What does employee engagement refer to?", "options": ["Employee involvement and motivation", "Payroll processing", "Data cleaning"], "answer": "Employee involvement and motivation"},
        {"q": "Which skill is important for HR communication?", "options": ["Active listening", "Python coding", "Network security"], "answer": "Active listening"}
    ],

    "HR Manager": [
        {"q": "What is HR analytics used for?", "options": ["Data-driven HR decisions", "Graphic design", "Software testing"], "answer": "Data-driven HR decisions"},
        {"q": "Which skill is most important for managing HR teams?", "options": ["Leadership", "SEO", "Networking"], "answer": "Leadership"},
        {"q": "What is workforce planning?", "options": ["Aligning talent with business needs", "Creating logos", "Writing SQL only"], "answer": "Aligning talent with business needs"}
    ],

    "Talent Acquisition Lead": [
        {"q": "What is talent acquisition?", "options": ["Strategic hiring process", "Financial auditing", "Website design"], "answer": "Strategic hiring process"},
        {"q": "Why is stakeholder management important?", "options": ["To align hiring needs", "To clean data", "To design apps"], "answer": "To align hiring needs"},
        {"q": "What is candidate screening?", "options": ["Shortlisting suitable applicants", "Preparing invoices", "Building dashboards"], "answer": "Shortlisting suitable applicants"}
    ],

    "Financial Analyst": [
        {"q": "What is financial reporting?", "options": ["Presenting financial performance", "Recruiting staff", "Testing software"], "answer": "Presenting financial performance"},
        {"q": "What is budgeting?", "options": ["Planning income and expenses", "Designing websites", "Managing networks"], "answer": "Planning income and expenses"},
        {"q": "Which tool is commonly used in finance analysis?", "options": ["Excel", "Figma", "Photoshop"], "answer": "Excel"}
    ],

    "Finance Lead": [
        {"q": "What is a key responsibility of a finance lead?", "options": ["Managing financial performance", "Writing marketing content", "Testing apps"], "answer": "Managing financial performance"},
        {"q": "Why is leadership important in finance?", "options": ["To guide financial decision-making", "To create animations", "To manage social media"], "answer": "To guide financial decision-making"},
        {"q": "What does financial planning support?", "options": ["Business decision-making", "Logo design", "Data entry only"], "answer": "Business decision-making"}
    ],

    "Operations Analyst": [
        {"q": "What does process improvement focus on?", "options": ["Improving efficiency", "Hiring employees", "Creating advertisements"], "answer": "Improving efficiency"},
        {"q": "What is operational data used for?", "options": ["Improving business processes", "Making posters", "Writing contracts"], "answer": "Improving business processes"},
        {"q": "Which tool is useful for operations analysis?", "options": ["Excel", "Instagram", "Paint"], "answer": "Excel"}
    ],

    "Marketing Lead": [
        {"q": "What does SEO stand for?", "options": ["Search Engine Optimisation", "Sales Entry Operation", "System Error Output"], "answer": "Search Engine Optimisation"},
        {"q": "What does Google Analytics measure?", "options": ["Website traffic and behaviour", "Employee payroll", "Network speed"], "answer": "Website traffic and behaviour"},
        {"q": "Why is leadership important in marketing?", "options": ["To guide campaigns and teams", "To clean databases", "To fix hardware"], "answer": "To guide campaigns and teams"}
    ],

    "IT Engineer": [
        {"q": "What is SQL mainly used for?", "options": ["Managing databases", "Designing posters", "Recruiting staff"], "answer": "Managing databases"},
        {"q": "What does system administration involve?", "options": ["Managing IT systems", "Writing job descriptions", "Preparing invoices"], "answer": "Managing IT systems"},
        {"q": "Which skill is important for IT problem solving?", "options": ["Troubleshooting", "Payroll", "SEO"], "answer": "Troubleshooting"}
    ],

    "Business Analyst": [
        {"q": "What is the role of a business analyst?", "options": ["Bridge business needs and solutions", "Design logos", "Manage payroll only"], "answer": "Bridge business needs and solutions"},
        {"q": "Why is SQL useful for business analysts?", "options": ["To extract and analyse data", "To edit images", "To manage recruitment"], "answer": "To extract and analyse data"},
        {"q": "What is requirement gathering?", "options": ["Understanding stakeholder needs", "Creating advertisements", "Fixing servers"], "answer": "Understanding stakeholder needs"}
    ],

    "Operations Manager": [
        {"q": "What is a core responsibility of an operations manager?", "options": ["Managing processes and efficiency", "Coding applications only", "Creating marketing graphics"], "answer": "Managing processes and efficiency"},
        {"q": "Why is project management useful in operations?", "options": ["To deliver work effectively", "To write payroll reports", "To design websites"], "answer": "To deliver work effectively"},
        {"q": "What does process improvement reduce?", "options": ["Waste and inefficiency", "Employee skills", "Customer service"], "answer": "Waste and inefficiency"}
    ],

    "Data Analyst": [
        {"q": "What is Python used for in analytics?", "options": ["Data analysis and automation", "Payroll approval", "Graphic design"], "answer": "Data analysis and automation"},
        {"q": "What is SQL used for?", "options": ["Querying databases", "Designing logos", "Writing contracts"], "answer": "Querying databases"},
        {"q": "What does Power BI help create?", "options": ["Dashboards and reports", "Job adverts", "Network cables"], "answer": "Dashboards and reports"}
    ],

    "BI Analyst": [
        {"q": "What is a BI dashboard used for?", "options": ["Presenting business insights", "Writing contracts", "Hiring staff"], "answer": "Presenting business insights"},
        {"q": "Which tool is commonly used for BI reporting?", "options": ["Power BI", "Photoshop", "Payroll system"], "answer": "Power BI"},
        {"q": "Why is data visualisation important?", "options": ["To communicate insights clearly", "To create passwords", "To fix hardware"], "answer": "To communicate insights clearly"}
    ],

    "Digital Marketing Analyst": [
        {"q": "What does Google Analytics help measure?", "options": ["Website traffic and user behaviour", "Employee payroll", "Server storage"], "answer": "Website traffic and user behaviour"},
        {"q": "What is SEO used for?", "options": ["Improving search visibility", "Managing finance", "Testing software"], "answer": "Improving search visibility"},
        {"q": "What is conversion rate?", "options": ["Percentage of users completing an action", "Salary percentage", "Network speed"], "answer": "Percentage of users completing an action"}
    ],

    "HRBP": [
        {"q": "What does HRBP stand for?", "options": ["Human Resources Business Partner", "Human Records Business Plan", "Hiring Resource Budget Process"], "answer": "Human Resources Business Partner"},
        {"q": "What is a key HRBP responsibility?", "options": ["Aligning HR strategy with business needs", "Creating software code", "Managing website traffic"], "answer": "Aligning HR strategy with business needs"},
        {"q": "Why is stakeholder management important for HRBP?", "options": ["To support managers and employees", "To build databases", "To run adverts"], "answer": "To support managers and employees"}
    ],

    "Marketing Head": [
        {"q": "What is a marketing strategy?", "options": ["A plan to reach target customers", "A payroll process", "A database table"], "answer": "A plan to reach target customers"},
        {"q": "What does digital marketing include?", "options": ["Online campaigns and analytics", "Server maintenance", "Financial auditing"], "answer": "Online campaigns and analytics"},
        {"q": "Why is analytics useful in marketing?", "options": ["To measure campaign performance", "To write contracts", "To manage hardware"], "answer": "To measure campaign performance"}
    ],

    "Senior Business Analyst": [
        {"q": "What does a senior business analyst often manage?", "options": ["Complex requirements and stakeholders", "Only data entry", "Only graphic design"], "answer": "Complex requirements and stakeholders"},
        {"q": "Why is stakeholder management important?", "options": ["To align business expectations", "To create passwords", "To print documents"], "answer": "To align business expectations"},
        {"q": "What is process modelling?", "options": ["Mapping business workflows", "Designing logos", "Installing software"], "answer": "Mapping business workflows"}
    ],

    "Executive Assistant": [
        {"q": "What is a key skill for an executive assistant?", "options": ["Organisation", "Machine learning", "Network security"], "answer": "Organisation"},
        {"q": "Why is communication important?", "options": ["To coordinate effectively", "To query databases", "To build apps"], "answer": "To coordinate effectively"},
        {"q": "What does scheduling involve?", "options": ["Managing meetings and calendars", "Preparing financial models", "Writing code"], "answer": "Managing meetings and calendars"}
    ],

    "Senior Secretary": [
        {"q": "What is document management?", "options": ["Organising and maintaining documents", "Programming websites", "Analysing databases"], "answer": "Organising and maintaining documents"},
        {"q": "Which skill supports diary management?", "options": ["Scheduling", "Python", "SEO"], "answer": "Scheduling"},
        {"q": "Why is confidentiality important?", "options": ["To protect sensitive information", "To improve website speed", "To design dashboards"], "answer": "To protect sensitive information"}
    ],

    "Software Team Lead": [
        {"q": "What is a key responsibility of a software team lead?", "options": ["Guiding developers and delivery", "Managing payroll", "Recruiting only"], "answer": "Guiding developers and delivery"},
        {"q": "Why is problem solving important in software?", "options": ["To resolve technical challenges", "To create invoices", "To plan holidays"], "answer": "To resolve technical challenges"},
        {"q": "Which skill is useful for software development?", "options": ["Python", "Payroll", "SEO"], "answer": "Python"}
    ],

    "Product Owner": [
        {"q": "What does a product owner manage?", "options": ["Product backlog and priorities", "Employee payroll", "Network security"], "answer": "Product backlog and priorities"},
        {"q": "What is Agile?", "options": ["Iterative project delivery approach", "Accounting method", "Graphic design tool"], "answer": "Iterative project delivery approach"},
        {"q": "Why is stakeholder management important?", "options": ["To align product requirements", "To clean spreadsheets only", "To install hardware"], "answer": "To align product requirements"}
    ],

    "Marketing Executive": [
        {"q": "What is digital marketing?", "options": ["Promoting products online", "Managing payroll", "Writing Python scripts"], "answer": "Promoting products online"},
        {"q": "Why is SEO useful?", "options": ["To improve search visibility", "To manage finance", "To test software"], "answer": "To improve search visibility"},
        {"q": "What is campaign communication?", "options": ["Delivering marketing messages", "Database backup", "Recruitment screening"], "answer": "Delivering marketing messages"}
    ],

    "Senior Software Engineer": [
        {"q": "What is system design?", "options": ["Planning software architecture", "Preparing payroll", "Creating adverts"], "answer": "Planning software architecture"},
        {"q": "Why is SQL useful?", "options": ["To manage and query data", "To design posters", "To manage recruitment"], "answer": "To manage and query data"},
        {"q": "What does debugging mean?", "options": ["Finding and fixing code issues", "Writing job adverts", "Preparing reports only"], "answer": "Finding and fixing code issues"}
    ],

    "Network Analyst": [
        {"q": "What is networking?", "options": ["Connecting computer systems", "Hiring employees", "Preparing budgets"], "answer": "Connecting computer systems"},
        {"q": "What does troubleshooting involve?", "options": ["Identifying and fixing issues", "Writing marketing plans", "Recruiting staff"], "answer": "Identifying and fixing issues"},
        {"q": "Why is system administration useful?", "options": ["To maintain IT systems", "To calculate salaries", "To create logos"], "answer": "To maintain IT systems"}
    ],

    "UI/UX Designer": [
        {"q": "What does UX stand for?", "options": ["User Experience", "User Execution", "Unit Extension"], "answer": "User Experience"},
        {"q": "What is wireframing?", "options": ["Creating layout sketches", "Writing SQL queries", "Preparing budgets"], "answer": "Creating layout sketches"},
        {"q": "Why is user research important?", "options": ["To understand user needs", "To manage payroll", "To configure networks"], "answer": "To understand user needs"}
    ],

    "UI/UX Lead": [
        {"q": "What is UX strategy?", "options": ["Plan for improving user experience", "Finance reporting", "Recruitment planning"], "answer": "Plan for improving user experience"},
        {"q": "Why is leadership important in UX?", "options": ["To guide design teams", "To manage payroll", "To run servers"], "answer": "To guide design teams"},
        {"q": "What is usability testing?", "options": ["Testing how easy a product is to use", "Checking financial statements", "Managing databases"], "answer": "Testing how easy a product is to use"}
    ],

    "Software Test Lead": [
        {"q": "What is software testing?", "options": ["Checking software quality", "Designing adverts", "Managing payroll"], "answer": "Checking software quality"},
        {"q": "What is automation testing?", "options": ["Using tools to run tests automatically", "Manual spreadsheet editing", "Recruitment screening"], "answer": "Using tools to run tests automatically"},
        {"q": "Why is leadership useful in testing?", "options": ["To coordinate testing teams", "To create campaigns", "To manage budgets only"], "answer": "To coordinate testing teams"}
    ],

    "Network Engineer": [
        {"q": "What is cybersecurity?", "options": ["Protecting systems from threats", "Preparing invoices", "Writing job descriptions"], "answer": "Protecting systems from threats"},
        {"q": "What does troubleshooting mean?", "options": ["Finding and fixing technical problems", "Creating advertisements", "Making dashboards only"], "answer": "Finding and fixing technical problems"},
        {"q": "Which skill is central to network engineering?", "options": ["Networking", "Payroll", "SEO"], "answer": "Networking"}
    ],

    "Operations Executive": [
        {"q": "What does coordination involve?", "options": ["Organising tasks and people", "Writing software", "Managing social media"], "answer": "Organising tasks and people"},
        {"q": "Why is Excel useful in operations?", "options": ["Tracking and analysing tasks", "Designing websites", "Hiring staff"], "answer": "Tracking and analysing tasks"},
        {"q": "What is operational efficiency?", "options": ["Completing work with less waste", "Increasing design colours", "Writing emails only"], "answer": "Completing work with less waste"}
    ],

    "Head of Recruitment": [
        {"q": "What is recruitment strategy?", "options": ["Plan to attract suitable talent", "Plan for software testing", "Plan for finance auditing"], "answer": "Plan to attract suitable talent"},
        {"q": "Why is leadership important in recruitment?", "options": ["To guide hiring teams", "To maintain servers", "To design dashboards"], "answer": "To guide hiring teams"},
        {"q": "What is employer branding?", "options": ["Company image as an employer", "Payroll calculation", "Network setup"], "answer": "Company image as an employer"}
    ],

    "Research Scientist": [
        {"q": "What are research methods?", "options": ["Structured approaches to investigation", "Marketing slogans", "Payroll processes"], "answer": "Structured approaches to investigation"},
        {"q": "Why is statistics important in research?", "options": ["To analyse evidence", "To create posters", "To manage staff rotas"], "answer": "To analyse evidence"},
        {"q": "How can Python support research?", "options": ["Data analysis and modelling", "Writing job adverts", "Managing phone calls"], "answer": "Data analysis and modelling"}
    ],

    "Logistics Lead": [
        {"q": "What is logistics management?", "options": ["Managing movement of goods/resources", "Writing software", "Recruiting employees"], "answer": "Managing movement of goods/resources"},
        {"q": "Why is coordination important in logistics?", "options": ["To ensure smooth operations", "To design campaigns", "To write SQL only"], "answer": "To ensure smooth operations"},
        {"q": "Which tool can help track logistics data?", "options": ["Excel", "Figma", "Photoshop"], "answer": "Excel"}
    ],

    "Head of Logistics": [
        {"q": "What is a key responsibility of Head of Logistics?", "options": ["Overseeing logistics operations", "Writing code only", "Managing recruitment only"], "answer": "Overseeing logistics operations"},
        {"q": "Why is operations knowledge important?", "options": ["To improve supply and delivery processes", "To create graphics", "To run payroll"], "answer": "To improve supply and delivery processes"},
        {"q": "What does logistics leadership involve?", "options": ["Managing teams and processes", "Creating posters", "Testing apps"], "answer": "Managing teams and processes"}
    ]
}

def calculate_quiz_score(desired_role):
    st.subheader("Role-Based Knowledge Assessment")

    questions = quiz_bank.get(desired_role, [])

    if len(questions) == 0:
        st.info("No quiz is currently available for this role.")
        return None

    correct_count = 0
    answered_count = 0

    for i, item in enumerate(questions):
        answer = st.radio(
            item["q"],
            item["options"],
            index=None,
            key=f"quiz_{desired_role}_{i}"
        )

        if answer is not None:
            answered_count += 1
            if answer == item["answer"]:
                correct_count += 1

    if answered_count < len(questions):
        st.warning("Please answer all quiz questions to continue.")
        return None

    quiz_score = round((correct_count / len(questions)) * 100, 2)
    st.metric("Quiz Score", f"{quiz_score}%")
    return quiz_score

# -------------------------------------------------
# ROLE SKILL MAPPING
# -------------------------------------------------
role_skill_mapping = employee_df.drop_duplicates("desired_role")[["desired_role", "required_skills"]]

# -------------------------------------------------
# PORTAL SELECTION
# -------------------------------------------------
portal = st.sidebar.radio(
    "Select Portal",
    ["Employee Portal", "Admin / HR Portal"]
)

# -------------------------------------------------
# EMPLOYEE PORTAL
# -------------------------------------------------
if portal == "Employee Portal":

    st.header("Employee Career Mobility Portal")
    st.write("Enter your details below to check your suitability for an internal role.")

    col1, col2 = st.columns(2)

    with col1:
        employee_id = st.text_input("Employee ID", value="E001")
        current_role = st.text_input("Current Role", value="HR Assistant")
        experience_years = st.number_input("Experience Years", min_value=0, max_value=40, value=2)

    with col2:
        current_skills = st.text_area(
            "Current Skills",
            value="Excel, Communication",
            help="Enter skills separated by commas"
        )

        desired_role = st.selectbox(
            "Desired Role",
            sorted(employee_df["desired_role"].dropna().unique())
        )

    selected_required_skills = role_skill_mapping[
        role_skill_mapping["desired_role"] == desired_role
    ]["required_skills"].iloc[0]

    st.subheader("Required Skills for Selected Role")
    st.warning(selected_required_skills)

    if st.button("Analyse My Career Fit"):
        skill_gap = find_skill_gap(current_skills, selected_required_skills)
        match_score = calculate_match_score(current_skills, selected_required_skills)
        courses = recommend_courses(skill_gap)

        st.session_state.latest_result = {
            "employee_id": employee_id,
            "current_role": current_role,
            "experience_years": experience_years,
            "current_skills": current_skills,
            "desired_role": desired_role,
            "required_skills": selected_required_skills,
            "skill_gap": skill_gap,
            "match_score": match_score,
            "recommended_courses": courses
        }

    if st.session_state.latest_result is not None:

        result = st.session_state.latest_result

        st.header("AI Career Recommendation Result")

        st.metric("Skill Match Score", f"{result['match_score']}%")

        st.subheader("Skill Gap")
        if result["skill_gap"] == "No skill gap":
            st.success("No skill gap identified.")
        else:
            st.error(result["skill_gap"])

        st.subheader("Recommended Reskilling Courses")
        st.info(result["recommended_courses"])

        st.subheader("Application Eligibility")

        if result["match_score"] >= 70:
            st.success("Your match score is 70% or above. Please complete the role-based quiz to apply.")

            quiz_score = calculate_quiz_score(result["desired_role"])

            if quiz_score is not None:
                overall_score = round((result["match_score"] + quiz_score) / 2, 2)
                status = readiness_status(overall_score)

                st.subheader("Final Readiness Result")
                st.metric("Overall Readiness Score", f"{overall_score}%")
                st.info(status)

                if overall_score >= 70:
                    st.success("You are eligible to submit interest to HR.")

                    if st.button("Submit Interest to HR"):
                        submitted_record = {
                            "employee_id": result["employee_id"],
                            "current_role": result["current_role"],
                            "experience_years": result["experience_years"],
                            "current_skills": result["current_skills"],
                            "desired_role": result["desired_role"],
                            "required_skills": result["required_skills"],
                            "skill_gap": result["skill_gap"],
                            "match_score": result["match_score"],
                            "quiz_score": quiz_score,
                            "overall_score": overall_score,
                            "recommended_courses": result["recommended_courses"],
                            "readiness_status": status
                        }

                        st.session_state.submitted_interests.append(submitted_record)
                        st.success("Your interest has been submitted to HR successfully.")

                else:
                    st.warning("Your overall readiness score is below 70%. Please improve your skills before applying.")

        else:
            st.warning("Your match score is below 70%. Please complete the recommended courses before applying.")

# -------------------------------------------------
# ADMIN / HR PORTAL
# -------------------------------------------------
elif portal == "Admin / HR Portal":

    st.header("Admin / HR Talent Mobility Dashboard")

    admin_passcode = st.text_input("Enter Admin Passcode", type="password")

    if admin_passcode != "admin123":
        st.warning("Please enter the correct admin passcode to access the HR dashboard.")
        st.stop()

    st.success("Admin access granted.")

    st.write(
        "This dashboard shows employees who submitted interest and achieved an overall readiness score of 70% or above."
    )

    if len(st.session_state.submitted_interests) == 0:
        st.info("No eligible employee interests have been submitted yet.")
    else:
        interests_df = pd.DataFrame(st.session_state.submitted_interests)

        interests_df = interests_df[interests_df["overall_score"] >= 70]

        if len(interests_df) == 0:
            st.info("No submitted employees currently meet the 70% overall readiness threshold.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Eligible Submitted Interests", len(interests_df))

            with col2:
                st.metric("Average Overall Score", round(interests_df["overall_score"].mean(), 2))

            with col3:
                st.metric("Highest Overall Score", interests_df["overall_score"].max())

            st.subheader("Filter by Desired Role")

            selected_admin_role = st.selectbox(
                "Select Role",
                ["All Roles"] + sorted(interests_df["desired_role"].dropna().unique())
            )

            if selected_admin_role != "All Roles":
                filtered_df = interests_df[interests_df["desired_role"] == selected_admin_role]
            else:
                filtered_df = interests_df

            st.subheader("Eligible Internal Candidates")

            st.dataframe(
                filtered_df[
                    [
                        "employee_id",
                        "current_role",
                        "experience_years",
                        "current_skills",
                        "desired_role",
                        "skill_gap",
                        "match_score",
                        "quiz_score",
                        "overall_score",
                        "recommended_courses",
                        "readiness_status"
                    ]
                ].sort_values(by="overall_score", ascending=False)
            )