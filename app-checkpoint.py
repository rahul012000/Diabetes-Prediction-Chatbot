import pickle
import numpy as np
import streamlit as st

st.set_page_config(page_title="Diabetes Risk Predictor", layout="centered")
st.title("🩺 Diabetes Risk Prediction App")
st.image("Image.jpeg")

# --- Language Selection ---
language = st.radio("Choose Language / \u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902", ["English", "Hindi"], index=0)

def t(eng,hin):
  return hin if language=="Hindi" else eng

# ============================== Load Model and Scaler ==============================
try:
    with open('Model/ModelForPrediction.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('Model/Standard_Scaler.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    st.success("✅ Model and scaler loaded successfully!")
except FileNotFoundError:
    model = None
    scaler = None
    st.error("❌ Model or scaler file not found. Please check the files.")

# ============================== Helper Functions ==============================
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0

def diabetes_pedigree_function(num_relatives, weights):
    return round(sum(weights), 2) if num_relatives else 0.0

def interpret_bp(systolic, diastolic):
    if systolic < 90 or diastolic < 60:
        return "Low (Hypotension)"
    elif 90 <= systolic < 120 and 60 <= diastolic < 80:
        return "Normal"
    elif 120 <= systolic < 130 and diastolic < 80:
        return "Elevated"
    elif 130 <= systolic < 140 or 80 <= diastolic < 90:
        return "High (Stage 1)"
    elif 140 <= systolic < 180 or 90 <= diastolic < 120:
        return "High (Stage 2)"
    elif systolic >= 180 or diastolic >= 120:
        return "Hypertensive Crisis"
    else:
        return "Unknown"

def estimate_bp(age, bmi, smoker=False, active=True, stress=False):
    systolic = 100 + (0.5 * age) + (0.3 * bmi)
    diastolic = 60 + (0.2 * age) + (0.2 * bmi)
    if smoker: systolic += 5; diastolic += 3
    if not active: systolic += 5; diastolic += 2
    if stress: systolic += 4; diastolic += 3
    return round(systolic, 1), round(diastolic, 1)

def estimate_skin_thickness(bmi, age):
    if bmi < 18.5:
        return 10
    elif 18.5 <= bmi < 25:
        return 20
    elif 25 <= bmi < 30:
        return 25
    else:
        return 35

def estimate_insulin(glucose, bmi, pregnancies):
    base = 50
    if glucose > 140:
        base += 40
    elif glucose > 100:
        base += 20
    if bmi > 30:
        base += 30
    base += pregnancies * 2
    return round(base, 1)

def estimate_glucose(age, bmi, insulin, active=True):
    glucose = 85 + (0.6 * age) + (0.4 * bmi)
    if insulin > 150:
        glucose += 20
    if not active:
        glucose += 15
    return round(glucose, 1)

# ============================== Input Section ==============================

st.markdown("<h4>👤 Basic Details</h4>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    gender = st.radio("Gender", ["Male", "Female"], index=1)
with col2:
    Age = st.number_input("Age (years)", 1, 120, 30)

if gender == "Female":
    Pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
else:
    Pregnancies = 0
    st.info("Pregnancy count is automatically set to 0 for male.")

# BMI
st.markdown("<h4>⚖️ Body Mass Index (BMI)</h4>", unsafe_allow_html=True)
know_bmi = st.radio("Do you know your BMI?", ["No, calculate it", "Yes, I know it"], index=0)

if know_bmi == "Yes, I know it":
    bmi_result = st.number_input("BMI (kg/m²)", 10.0, 60.0, 24.0)
else:
    weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
    height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
    bmi_result = calculate_bmi(weight, height)
    st.success(f"Calculated BMI: {bmi_result}")

# Skin Thickness and Insulin
st.markdown("<h4>🧪 Skin Thickness and Insulin</h4>", unsafe_allow_html=True)
know_skin = st.radio("Do you know your Skin Thickness?", ["Yes", "No"])
know_insulin = st.radio("Do you know your Insulin level?", ["Yes", "No"])

if know_skin == "Yes":
    SkinThickness = st.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
else:
    SkinThickness = estimate_skin_thickness(bmi_result, Age)
    st.success(f"Estimated Skin Thickness: {SkinThickness} mm")

if know_insulin == "Yes":
    Insulin = st.number_input("Insulin (mu U/ml)", 0.0, 1000.0, 80.0)
else:
    Insulin = estimate_insulin(100, bmi_result, Pregnancies)
    st.success(f"Estimated Insulin: {Insulin} mu U/ml")

# Glucose
st.markdown("<h4>🩸 Glucose Level</h4>", unsafe_allow_html=True)
know_glucose = st.radio("Do you know your Glucose level?", ["Yes", "No"], index=0)

if know_glucose == "Yes":
    Glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 100.0)
else:
    active_glucose = st.checkbox("Are you physically active?", value=True)
    Glucose = estimate_glucose(Age, bmi_result, Insulin, active_glucose)
    st.success(f"Estimated Glucose Level: {Glucose} mg/dL")

# Blood Pressure
st.markdown("<h4>🩺 Blood Pressure (BP)</h4>", unsafe_allow_html=True)
know_bp = st.radio("Do you know your BP?", ["No, calculate it", "Yes, I know it"], index=0)

if know_bp == "Yes, I know it":
    bp_type = st.radio("Input Type", ["Systolic & Diastolic", "Single Average Value"])
    if bp_type == "Systolic & Diastolic":
        systolic = st.number_input("Systolic (mmHg)", 70.0, 250.0, 120.0)
        diastolic = st.number_input("Diastolic (mmHg)", 40.0, 150.0, 80.0)
        BloodPressure = (systolic + diastolic) / 2
        st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")
    else:
        one_value = st.number_input("Enter single BP value", 40.0, 250.0, 72.0)
        BloodPressure = one_value
else:
    st.write("Let's estimate your BP.")
    smoker = st.checkbox("Do you smoke?", value=False)
    active = st.checkbox("Are you physically active?", value=True)
    stress = st.checkbox("Do you feel high stress?", value=False)
    systolic, diastolic = estimate_bp(Age, bmi_result, smoker, active, stress)
    BloodPressure = (systolic + diastolic) / 2
    st.success(f"Estimated Systolic: {systolic} mmHg")
    st.success(f"Estimated Diastolic: {diastolic} mmHg")
    st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")

# DPF
st.markdown("<h4>🧬 Diabetes Pedigree Function (DPF)</h4>", unsafe_allow_html=True)
know_dpf = st.radio("Do you know your DPF?", ["No, calculate it", "Yes, I know it"], index=0)

if know_dpf == "Yes, I know it":
    DiabetesPedigreeFunction = st.number_input("DPF Value", 0.0, 2.5, 0.5)
else:
    st.markdown("### 👨‍👩‍👧‍👦 Family History")
    num_relatives = st.slider("How many diabetic relatives do you have?", 0, 10, 0)
    relation_weights = []
    if num_relatives > 0:
        for i in range(num_relatives):
            relation = st.selectbox(f"Relative #{i+1}", 
                                    ["Parent", "Sibling", "Grandparent", "Aunt/Uncle", "Cousin"],
                                    key=f"rel_{i}")
            weight_map = {
                "Parent": 1.0,
                "Sibling": 0.8,
                "Grandparent": 0.5,
                "Aunt/Uncle": 0.4,
                "Cousin": 0.2
            }
            relation_weights.append(weight_map[relation])
    DiabetesPedigreeFunction = diabetes_pedigree_function(num_relatives, relation_weights)
    st.caption(f"Calculated DPF: {DiabetesPedigreeFunction}")

# ============================== Input Calculation Summary ==============================
if st.button("🧮 Calculate Inputs"):
    st.markdown("<h4>📋 Input Summary (Calculated/Estimated Values)</h4>", unsafe_allow_html=True)
    st.info(f"Pregnancies: {Pregnancies}")
    st.info(f"Glucose: {Glucose} mg/dL")
    st.info(f"Blood Pressure: {BloodPressure} mmHg")
    st.info(f"Skin Thickness: {SkinThickness} mm")
    st.info(f"Insulin: {Insulin} mu U/ml")
    st.info(f"BMI: {bmi_result} kg/m²")
    st.info(f"DPF (Diabetes Pedigree Function): {DiabetesPedigreeFunction}")
    st.info(f"Age: {Age} years")
    st.success("✅ You can now proceed to prediction if you're ready.")

# ============================== Prediction ==============================
if model and scaler:
    if st.button("🔍 Predict Diabetes Risk"):
        input_data = [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                       bmi_result, DiabetesPedigreeFunction, Age]]
        scaled_input = scaler.transform(input_data)
        prediction = model.predict(scaled_input)[0]
        probability = model.predict_proba(scaled_input)[0][1]

        st.markdown("<h4>📊 Prediction Result</h4>", unsafe_allow_html=True)
        st.success(f"Risk Score: {round(probability * 100, 2)}%")
        st.progress(min(int(probability * 100), 100))

        if prediction == 1:
            st.error("🚨 Prediction: Person is Diabetic.")
            st.warning("Please consult a healthcare provider.")
        else:
            st.success("✅ Prediction: Person is Non-Diabetic.")
            st.info("No immediate risk detected.")

        st.markdown("""
        ### 📝 Next Steps:
        - Maintain a balanced diet and healthy weight  
        - Exercise regularly  
        - Schedule regular health checkups  
        - Monitor blood sugar if at risk
        """)
else:
    st.warning("⚠️ Prediction disabled: Model or scaler not loaded.")



# import pickle
# import numpy as np
# import streamlit as st

# st.set_page_config(page_title="Diabetes Risk Predictor", layout="centered")
# st.title("🩺 Diabetes Risk Prediction App")
# st.image("Image.jpeg")

# # ============================== Load Model and Scaler ==============================
# try:
#     with open('ModelForPrediction.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open('Standard_Scaler.pkl', 'rb') as scaler_file:
#         scaler = pickle.load(scaler_file)
#     st.success("✅ Model and scaler loaded successfully!")
# except FileNotFoundError:
#     model = None
#     scaler = None
#     st.error("❌ Model or scaler file not found. Please check the files.")

# # ============================== Helper Functions ==============================
# def calculate_bmi(weight_kg, height_cm):
#     height_m = height_cm / 100
#     return round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0

# def diabetes_pedigree_function(num_relatives, weights):
#     return round(sum(weights), 2) if num_relatives else 0.0

# def interpret_bp(systolic, diastolic):
#     if systolic < 90 or diastolic < 60:
#         return "Low (Hypotension)"
#     elif 90 <= systolic < 120 and 60 <= diastolic < 80:
#         return "Normal"
#     elif 120 <= systolic < 130 and diastolic < 80:
#         return "Elevated"
#     elif 130 <= systolic < 140 or 80 <= diastolic < 90:
#         return "High (Stage 1)"
#     elif 140 <= systolic < 180 or 90 <= diastolic < 120:
#         return "High (Stage 2)"
#     elif systolic >= 180 or diastolic >= 120:
#         return "Hypertensive Crisis"
#     else:
#         return "Unknown"

# def estimate_bp(age, bmi, smoker=False, active=True, stress=False):
#     systolic = 100 + (0.5 * age) + (0.3 * bmi)
#     diastolic = 60 + (0.2 * age) + (0.2 * bmi)
#     if smoker: systolic += 5; diastolic += 3
#     if not active: systolic += 5; diastolic += 2
#     if stress: systolic += 4; diastolic += 3
#     return round(systolic, 1), round(diastolic, 1)

# def estimate_skin_thickness(bmi, age):
#     if bmi < 18.5:
#         return 10
#     elif 18.5 <= bmi < 25:
#         return 20
#     elif 25 <= bmi < 30:
#         return 25
#     else:
#         return 35

# def estimate_insulin(glucose, bmi, pregnancies):
#     base = 50
#     if glucose > 140:
#         base += 40
#     elif glucose > 100:
#         base += 20
#     if bmi > 30:
#         base += 30
#     base += pregnancies * 2
#     return round(base, 1)

# def estimate_glucose(age, bmi, insulin, active=True):
#     glucose = 85 + (0.6 * age) + (0.4 * bmi)
#     if insulin > 150:
#         glucose += 20
#     if not active:
#         glucose += 15
#     return round(glucose, 1)

# # ============================== Input Section ==============================

# st.markdown("<h4>👤 Basic Details</h4>", unsafe_allow_html=True)
# col1, col2 = st.columns(2)
# with col1:
#     gender = st.radio("Gender", ["Male", "Female"], index=1)
# with col2:
#     Age = st.number_input("Age (years)", 1, 120, 30)

# if gender == "Female":
#     Pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
# else:
#     Pregnancies = 0
#     st.info("Pregnancy count is automatically set to 0 for male.")

# # BMI
# st.markdown("<h4>⚖️ Body Mass Index (BMI)</h4>", unsafe_allow_html=True)
# know_bmi = st.radio("Do you know your BMI?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_bmi == "Yes, I know it":
#     bmi_result = st.number_input("BMI (kg/m²)", 10.0, 60.0, 24.0)
# else:
#     weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
#     height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
#     bmi_result = calculate_bmi(weight, height)
#     st.success(f"Calculated BMI: {bmi_result}")

# # Skin Thickness and Insulin
# st.markdown("<h4>🧪 Skin Thickness and Insulin</h4>", unsafe_allow_html=True)
# know_skin = st.radio("Do you know your Skin Thickness?", ["Yes", "No"])
# know_insulin = st.radio("Do you know your Insulin level?", ["Yes", "No"])

# if know_skin == "Yes":
#     SkinThickness = st.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
# else:
#     SkinThickness = estimate_skin_thickness(bmi_result, Age)
#     st.success(f"Estimated Skin Thickness: {SkinThickness} mm")

# if know_insulin == "Yes":
#     Insulin = st.number_input("Insulin (mu U/ml)", 0.0, 1000.0, 80.0)
# else:
#     Insulin = estimate_insulin(100, bmi_result, Pregnancies)
#     st.success(f"Estimated Insulin: {Insulin} mu U/ml")

# # Glucose
# st.markdown("<h4>🩸 Glucose Level</h4>", unsafe_allow_html=True)
# know_glucose = st.radio("Do you know your Glucose level?", ["Yes", "No"], index=0)

# if know_glucose == "Yes":
#     Glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 100.0)
# else:
#     active_glucose = st.checkbox("Are you physically active?", value=True)
#     Glucose = estimate_glucose(Age, bmi_result, Insulin, active_glucose)
#     st.success(f"Estimated Glucose Level: {Glucose} mg/dL")

# # Blood Pressure
# st.markdown("<h4>🩺 Blood Pressure (BP)</h4>", unsafe_allow_html=True)
# know_bp = st.radio("Do you know your BP?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_bp == "Yes, I know it":
#     bp_type = st.radio("Input Type", ["Systolic & Diastolic", "Single Average Value"])
#     if bp_type == "Systolic & Diastolic":
#         systolic = st.number_input("Systolic (mmHg)", 70.0, 250.0, 120.0)
#         diastolic = st.number_input("Diastolic (mmHg)", 40.0, 150.0, 80.0)
#         BloodPressure = (systolic + diastolic) / 2
#         st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")
#     else:
#         one_value = st.number_input("Enter single BP value", 40.0, 250.0, 72.0)
#         BloodPressure = one_value
# else:
#     st.write("Let's estimate your BP.")
#     smoker = st.checkbox("Do you smoke?", value=False)
#     active = st.checkbox("Are you physically active?", value=True)
#     stress = st.checkbox("Do you feel high stress?", value=False)
#     systolic, diastolic = estimate_bp(Age, bmi_result, smoker, active, stress)
#     BloodPressure = (systolic + diastolic) / 2
#     st.success(f"Estimated Systolic: {systolic} mmHg")
#     st.success(f"Estimated Diastolic: {diastolic} mmHg")
#     st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")

# # DPF
# st.markdown("<h4>🧬 Diabetes Pedigree Function (DPF)</h4>", unsafe_allow_html=True)
# know_dpf = st.radio("Do you know your DPF?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_dpf == "Yes, I know it":
#     DiabetesPedigreeFunction = st.number_input("DPF Value", 0.0, 2.5, 0.5)
# else:
#     st.markdown("### 👨‍👩‍👧‍👦 Family History")
#     num_relatives = st.slider("How many diabetic relatives do you have?", 0, 10, 0)
#     relation_weights = []
#     if num_relatives > 0:
#         for i in range(num_relatives):
#             relation = st.selectbox(f"Relative #{i+1}", 
#                                     ["Parent", "Sibling", "Grandparent", "Aunt/Uncle", "Cousin"],
#                                     key=f"rel_{i}")
#             weight_map = {
#                 "Parent": 1.0,
#                 "Sibling": 0.8,
#                 "Grandparent": 0.5,
#                 "Aunt/Uncle": 0.4,
#                 "Cousin": 0.2
#             }
#             relation_weights.append(weight_map[relation])
#     DiabetesPedigreeFunction = diabetes_pedigree_function(num_relatives, relation_weights)
#     st.caption(f"Calculated DPF: {DiabetesPedigreeFunction}")

# # ============================== Prediction ==============================

# if model and scaler:
#     if st.button("🔍 Predict Diabetes Risk"):
#         input_data = [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
#                        bmi_result, DiabetesPedigreeFunction, Age]]
#         scaled_input = scaler.transform(input_data)
#         prediction = model.predict(scaled_input)[0]
#         probability = model.predict_proba(scaled_input)[0][1]

#         st.markdown("<h4>📊 Prediction Result</h4>", unsafe_allow_html=True)
#         st.success(f"Risk Score: {round(probability * 100, 2)}%")
#         st.progress(min(int(probability * 100), 100))

#         if prediction == 1:
#             st.error("🚨 Prediction: Person is Diabetic.")
#             st.warning("Please consult a healthcare provider.")
#         else:
#             st.success("✅ Prediction: Person is Non-Diabetic.")
#             st.info("No immediate risk detected.")

#         st.markdown("""
#         ### 📝 Next Steps:
#         - Maintain a balanced diet and healthy weight  
#         - Exercise regularly  
#         - Schedule regular health checkups  
#         - Monitor blood sugar if at risk
#         """)
# else:
#     st.warning("⚠️ Prediction disabled: Model or scaler not loaded.")

















# import pickle
# import numpy as np
# import streamlit as st

# st.title("Diabetes Risk Prediction App")
# st.image("Image.jpeg")

# # ======================================Load Model and Scaler ============================================
# try:
#     with open('ModelForPrediction.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open('Standard_Scaler.pkl', 'rb') as scaler_file:
#         scaler = pickle.load(scaler_file)
#     st.success("Model and scaler loaded successfully!")
# except FileNotFoundError:
#     st.error("Model or scaler file not found. Please check and try again.")

# # =======================================Helper Functions====================================================
# def calculate_bmi(weight_kg, height_cm):
#     height_m = height_cm / 100
#     return round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0
# #=======================================Diabetes Pedigree Function==========================================
# def diabetes_pedigree_function(num_relatives, weights):
#     return round(sum(weights), 2) if num_relatives else 0.0
# #======================================Interpret Blood Pressure=============================================
# def interpret_bp(systolic, diastolic):
#     if systolic < 90 or diastolic < 60:
#         return "Low (Hypotension)"
#     elif 90 <= systolic < 120 and 60 <= diastolic < 80:
#         return "Normal"
#     elif 120 <= systolic < 130 and diastolic < 80:
#         return "Elevated"
#     elif 130 <= systolic < 140 or 80 <= diastolic < 90:
#         return "High (Stage 1)"
#     elif 140 <= systolic < 180 or 90 <= diastolic < 120:
#         return "High (Stage 2)"
#     elif systolic >= 180 or diastolic >= 120:
#         return "Hypertensive Crisis"
#     else:
#         return "Unknown"
# #==========================================Estimate Blood Pressuse=====================================
# def estimate_bp(age, bmi, smoker=False, active=True, stress=False):
#     systolic = 100 + (0.5 * age) + (0.3 * bmi)
#     diastolic = 60 + (0.2 * age) + (0.2 * bmi)
#     if smoker: systolic += 5; diastolic += 3
#     if not active: systolic += 5; diastolic += 2
#     if stress: systolic += 4; diastolic += 3
#     return round(systolic, 1), round(diastolic, 1)
# #==========================================Estimate Blood Pressuse=====================================
# def estimate_skin_thickness(bmi, age):
#     if bmi < 18.5:
#         return 10
#     elif 18.5 <= bmi < 25:
#         return 20
#     elif 25 <= bmi < 30:
#         return 25
#     else:
#         return 35
# #==========================================Estimate Insulin============================================
# def estimate_insulin(glucose, bmi, pregnancies):
#     base = 50
#     if glucose > 140:
#         base += 40
#     elif glucose > 100:
#         base += 20
#     if bmi > 30:
#         base += 30
#     base += pregnancies * 2
#     return round(base, 1)
# #==========================================Estimate Glucose ===========================================
# def estimate_glucose(age, bmi, insulin, active=True):
#     glucose = 85 + (0.6 * age) + (0.4 * bmi)
#     if insulin > 150:
#         glucose += 20
#     if not active:
#         glucose += 15
#     return round(glucose, 1)

# #========================================== Input Section ============================================
# st.subheader("Basic Details")

# # Gender and Pregnancy
# gender = st.radio("Select your gender", ["Male", "Female"], index=1)
# if gender == "Female":
#     Pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
# else:
#     Pregnancies = 0
#     st.info("Pregnancy count automatically set to 0 for male.")

# # Age
# Age = st.number_input("Age", 1, 120, 30)

# # BMI
# st.subheader("Body Mass Index (BMI)")
# know_bmi = st.radio("Do you know your BMI?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_bmi == "Yes, I know it":
#     bmi_result = st.number_input("Enter your BMI directly", 10.0, 60.0, 24.0)
# else:
#     weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
#     height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
#     bmi_result = calculate_bmi(weight, height)
#     st.success(f"Calculated BMI: {bmi_result}")

# # Skin Thickness & Insulin (must come before glucose estimation)
# st.subheader("Do you know your Skin Thickness and Insulin?")
# know_skin = st.radio("Do you know your Skin Thickness?", ["Yes", "No"], key="skin")
# know_insulin = st.radio("Do you know your Insulin level?", ["Yes", "No"], key="insulin")

# if know_skin == "Yes":
#     SkinThickness = st.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
# else:
#     SkinThickness = estimate_skin_thickness(bmi_result, Age)
#     st.success(f"Estimated Skin Thickness: {SkinThickness} mm")

# if know_insulin == "Yes":
#     Insulin = st.number_input("Insulin (mu U/ml)", 0.0, 1000.0, 80.0)
# else:
#     Insulin = estimate_insulin(100, bmi_result, Pregnancies)  # using temp glucose = 100
#     st.success(f"Estimated Insulin: {Insulin} mu U/ml")

# # Glucose (after Insulin)
# st.subheader("Glucose Level")
# know_glucose = st.radio("Do you know your Glucose level?", ["Yes", "No"], index=0)

# if know_glucose == "Yes":
#     Glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 100.0)
# else:
#     active_glucose = st.checkbox("Are you physically active?", value=True, key="glucose_active")
#     Glucose = estimate_glucose(Age, bmi_result, Insulin, active_glucose)
#     st.success(f"Estimated Glucose Level: {Glucose} mg/dL")

# # Blood Pressure
# st.subheader("Blood Pressure (BP)")
# know_bp = st.radio("Do you know your BP?", ["No, calculate it", "Yes, I know it"], index=0)
# if know_bp == "Yes, I know it":
#     bp_type = st.radio("What do you want to enter?", ["Systolic & Diastolic", "Only one value (e.g., 72)"], index=0)

#     if bp_type == "Systolic & Diastolic":
#         systolic = st.number_input("Enter Systolic BP (mmHg)", 70.0, 250.0, 120.0)
#         diastolic = st.number_input("Enter Diastolic BP (mmHg)", 40.0, 150.0, 80.0)
#         BloodPressure = (systolic + diastolic) / 2
#         st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")
#     else:
#         one_value = st.number_input("Enter the single BP value you know (mmHg)", 40.0, 250.0, 72.0)
#         BloodPressure = one_value
#         st.info("Using single BP value as average BP.")
# else:
#     st.write("Let's estimate your BP.")
#     smoker = st.checkbox("Do you smoke?", value=False)
#     active = st.checkbox("Are you physically active?", value=True)
#     stress = st.checkbox("Do you feel high stress?", value=False)
#     systolic, diastolic = estimate_bp(Age, bmi_result, smoker, active, stress)
#     BloodPressure = (systolic + diastolic) / 2
#     st.success(f"Estimated Systolic BP: {systolic} mmHg")
#     st.success(f"Estimated Diastolic BP: {diastolic} mmHg")
#     st.info(f"Estimated BP Category: {interpret_bp(systolic,diastolic)}")


# # --- Diabetes Pedigree Function (DPF) ---
# st.subheader("Diabetes Pedigree Function (DPF)")

# know_dpf = st.radio("Do you know your DPF?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_dpf == "Yes, I know it":
#     DiabetesPedigreeFunction = st.number_input("Enter your DPF value", 0.0, 2.5, 0.5)
# else:
#     st.subheader("Family History")
#     num_relatives = st.slider("How many diabetic relatives do you have?", 0, 10, 0)
#     relation_weights = []
#     if num_relatives > 0:
#         for i in range(num_relatives):
#             relation = st.selectbox(f"Relative #{i+1}", 
#                                     ["Parent", "Sibling", "Grandparent", "Aunt/Uncle", "Cousin"],
#                                     key=f"rel_{i}")
#             weight_map = {
#                 "Parent": 1.0,
#                 "Sibling": 0.8,
#                 "Grandparent": 0.5,
#                 "Aunt/Uncle": 0.4,
#                 "Cousin": 0.2
#             }
#             relation_weights.append(weight_map[relation])
#     DiabetesPedigreeFunction = diabetes_pedigree_function(num_relatives, relation_weights)
#     st.caption(f"Calculated DPF: {DiabetesPedigreeFunction}")

# # --- Prediction ---
# if st.button("Predict Diabetes Risk"):
#     input_data = [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
#                    bmi_result, DiabetesPedigreeFunction, Age]]
#     scaled_input = scaler.transform(input_data)
#     prediction = model.predict(scaled_input)[0]
#     probability = model.predict_proba(scaled_input)[0][1]

#     st.subheader("Prediction Result")
#     st.success(f"Risk Score: {round(probability * 100, 2)}%")
#     if prediction == 1:
#         st.error("Prediction: Person is Diabetic.")
#         st.warning("Please consult a doctor.")
#     else:
#         st.success("Prediction: Person is Non-Diabetic.")
#         st.info("No immediate risk detected.")





# import pickle
# import numpy as np
# import streamlit as st

# st.title("Diabetes Risk Prediction App")
# st.image("Image.jpeg")

# # --- Load Model and Scaler ---
# try:
#     with open('ModelForPrediction.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open('Standard_Scaler.pkl', 'rb') as scaler_file:
#         scaler = pickle.load(scaler_file)
#     st.success("Model and scaler loaded successfully!")
# except FileNotFoundError:
#     st.error("Model or scaler file not found. Please check and try again.")

# # --- Helper Functions ---
# def calculate_bmi(weight_kg, height_cm):
#     height_m = height_cm / 100
#     return round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0

# def diabetes_pedigree_function(num_relatives, weights):
#     return round(sum(weights), 2) if num_relatives else 0.0

# def interpret_bp(systolic, diastolic):
#     if systolic < 90 or diastolic < 60:
#         return "Low (Hypotension)"
#     elif 90 <= systolic < 120 and 60 <= diastolic < 80:
#         return "Normal"
#     elif 120 <= systolic < 130 and diastolic < 80:
#         return "Elevated"
#     elif 130 <= systolic < 140 or 80 <= diastolic < 90:
#         return "High (Stage 1)"
#     elif 140 <= systolic < 180 or 90 <= diastolic < 120:
#         return "High (Stage 2)"
#     elif systolic >= 180 or diastolic >= 120:
#         return "Hypertensive Crisis"
#     else:
#         return "Unknown"

# def estimate_bp(age, bmi, smoker=False, active=True, stress=False):
#     systolic = 100 + (0.5 * age) + (0.3 * bmi)
#     diastolic = 60 + (0.2 * age) + (0.2 * bmi)
#     if smoker: systolic += 5; diastolic += 3
#     if not active: systolic += 5; diastolic += 2
#     if stress: systolic += 4; diastolic += 3
#     return round(systolic, 1), round(diastolic, 1)

# def estimate_skin_thickness(bmi, age):
#     if bmi < 18.5:
#         return 10
#     elif 18.5 <= bmi < 25:
#         return 20
#     elif 25 <= bmi < 30:
#         return 25
#     else:
#         return 35

# def estimate_insulin(glucose, bmi, pregnancies):
#     base = 50
#     if glucose > 140:
#         base += 40
#     elif glucose > 100:
#         base += 20
#     if bmi > 30:
#         base += 30
#     base += pregnancies * 2
#     return round(base, 1)

# # --- Input Section ---
# st.subheader("Basic Details")

# # Gender and Pregnancy
# gender = st.radio("Select your gender", ["Male", "Female"], index=1)
# if gender == "Female":
#     Pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
# else:
#     Pregnancies = 0
#     st.info("Pregnancy count automatically set to 0 for male.")

# #-------AGE Section
# Age = st.number_input("Age", 1, 120, 30)

# # --- BMI Section ---
# st.subheader("Body Mass Index (BMI)")
# know_bmi = st.radio("Do you know your BMI?", ["No, calculate it", "Yes, I know it"], index=0)

# if know_bmi == "Yes, I know it":
#     bmi_result = st.number_input("Enter your BMI directly", 10.0, 60.0, 24.0)
# else:
#     weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
#     height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
#     bmi_result = calculate_bmi(weight, height)
#     st.success(f"Calculated BMI: {bmi_result}")
# # weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
# # height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)

# # # Auto-calculate BMI
# # if st.button("Calculate BMI"):
# #     bmi_result = calculate_bmi(weight, height)
# #     st.success(f"Your BMI is: {bmi_result}")
# # else:
# #     bmi_result = calculate_bmi(weight, height)

# # --- Glucose Section ---

# # Glucose Input
# st.subheader("Glucose Level")
# Glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 100.0)

# # Blood Pressure
# st.subheader("Blood Pressure Info")
# know_bp = st.radio("Do you know your BP reading?", ["Yes", "No"])
# if know_bp == "No":
#     smoker = st.checkbox("Do you smoke?")
#     active = st.checkbox("Are you physically active?", value=True)
#     stress = st.checkbox("Do you feel high stress?", value=False)
#     systolic, diastolic = estimate_bp(Age, bmi_result, smoker, active, stress)
#     st.success(f"Estimated Systolic: {systolic}")
#     st.success(f"Estimated Diastolic: {diastolic}")
#     st.info(f"Estimated BP Category: {interpret_bp(systolic, diastolic)}")
#     BloodPressure = (systolic + diastolic) / 2
# else:
#     systolic = st.number_input("Systolic BP", 70.0, 250.0, 120.0)
#     diastolic = st.number_input("Diastolic BP", 40.0, 150.0, 80.0)
#     BloodPressure = (systolic + diastolic) / 2
#     st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")

# # Skin Thickness & Insulin
# st.subheader("Do you know your Skin Thickness and Insulin?")
# know_skin = st.radio("Do you know your Skin Thickness?", ["Yes", "No"], key="skin")
# know_insulin = st.radio("Do you know your Insulin level?", ["Yes", "No"], key="insulin")

# if know_skin == "Yes":
#     SkinThickness = st.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
# else:
#     SkinThickness = estimate_skin_thickness(bmi_result, Age)
#     st.success(f"Estimated Skin Thickness: {SkinThickness} mm")

# if know_insulin == "Yes":
#     Insulin = st.number_input("Insulin (mu U/ml)", 0.0, 1000.0, 80.0)
# else:
#     Insulin = estimate_insulin(Glucose, bmi_result, Pregnancies)
#     st.success(f"Estimated Insulin: {Insulin} mu U/ml")

# # DPF Input
# st.subheader("Family History")
# num_relatives = st.slider("How many diabetic relatives?", 0, 10, 0)
# relation_weights = []
# if num_relatives > 0:
#     for i in range(num_relatives):
#         relation = st.selectbox(f"Relative #{i+1}", 
#                                 ["Parent", "Sibling", "Grandparent", "Aunt/Uncle", "Cousin"],
#                                 key=f"rel_{i}")
#         weight_map = {"Parent": 1.0, "Sibling": 0.8, "Grandparent": 0.5, "Aunt/Uncle": 0.4, "Cousin": 0.2}
#         relation_weights.append(weight_map[relation])
# DiabetesPedigreeFunction = diabetes_pedigree_function(num_relatives, relation_weights)
# st.caption(f"Calculated DPF: {DiabetesPedigreeFunction}")

# # --- Prediction ---
# if st.button("Predict Diabetes Risk"):
#     input_data = [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
#                    bmi_result, DiabetesPedigreeFunction, Age]]
#     scaled_input = scaler.transform(input_data)
#     prediction = model.predict(scaled_input)[0]
#     probability = model.predict_proba(scaled_input)[0][1]

#     st.subheader("Prediction Result")
#     st.success(f"Risk Score: {round(probability * 100, 2)}%")
#     if prediction == 1:
#         st.error("Prediction: Person is Diabetic.")
#         st.warning("Please consult a doctor.")
#     else:
#         st.success("Prediction: Person is Non-Diabetic.")
#         st.info("No immediate risk detected.")


# # # import pickle
# # # import numpy as np
# # # import streamlit as st

# # # st.title("Diabetes Risk Prediction App")
# # # st.image("Image.jpeg")

# # # # Load model and scaler
# # # try:
# # #     with open('ModelForPrediction.pkl', 'rb') as model_file:
# # #         model = pickle.load(model_file)
# # #     with open('Standard_Scaler.pkl', 'rb') as scaler_file:
# # #         scaler = pickle.load(scaler_file)
# # #     st.success("Model and scaler loaded successfully!")
# # # except FileNotFoundError:
# # #     st.error("Model or scaler file not found. Please check and try again.")

# # # # --- Helper Functions ---
# # # def calculate_bmi(weight_kg, height_cm):
# # #     height_m = height_cm / 100
# # #     return round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0

# # # def diabetes_pedigree_function(num_relatives, weights):
# # #     return round(sum(weights), 2) if num_relatives else 0.0

# # # def interpret_bp(systolic, diastolic):
# # #     if systolic < 90 or diastolic < 60:
# # #         return "Low (Hypotension)"
# # #     elif 90 <= systolic < 120 and 60 <= diastolic < 80:
# # #         return "Normal"
# # #     elif 120 <= systolic < 130 and diastolic < 80:
# # #         return "Elevated"
# # #     elif 130 <= systolic < 140 or 80 <= diastolic < 90:
# # #         return "High (Stage 1)"
# # #     elif 140 <= systolic < 180 or 90 <= diastolic < 120:
# # #         return "High (Stage 2)"
# # #     elif systolic >= 180 or diastolic >= 120:
# # #         return "Hypertensive Crisis"
# # #     else:
# # #         return "Unknown"

# # # def estimate_bp(age, bmi, smoker=False, active=True, stress=False):
# # #     systolic = 100 + (0.5 * age) + (0.3 * bmi)
# # #     diastolic = 60 + (0.2 * age) + (0.2 * bmi)
# # #     if smoker: systolic += 5; diastolic += 3
# # #     if not active: systolic += 5; diastolic += 2
# # #     if stress: systolic += 4; diastolic += 3
# # #     return round(systolic, 1), round(diastolic, 1)

# # # def estimate_glucose(age, bmi, dpf, symptoms_score=0):
# # #     base_glucose = 85
# # #     if age > 45: base_glucose += 10
# # #     if age > 60: base_glucose += 20
# # #     if bmi >= 25: base_glucose += 15
# # #     if bmi >= 30: base_glucose += 25
# # #     base_glucose += dpf * 20
# # #     base_glucose += symptoms_score * 5
# # #     return round(base_glucose, 1)

# # # # --- Input Section ---
# # # st.subheader("Enter the following details:")
# # # Pregnancies = st.number_input("Pregnancies", 0, 20, 0)

# # # # Age Input (before Glucose for use in estimation)
# # # Age = st.number_input("Age", 1, 120, 30)

# # # # Weight & Height input (for BMI)
# # # weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
# # # height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)

# # # # Auto-calculate BMI
# # # if st.button("Calculate BMI"):
# # #     bmi_result = calculate_bmi(weight, height)
# # #     st.success(f"Your BMI is: {bmi_result}")
# # # else:
# # #     bmi_result = calculate_bmi(weight, height)

# # # # DPF Input
# # # st.subheader("Family History")
# # # num_relatives = st.slider("How many diabetic relatives?", 0, 10, 0)
# # # relation_weights = []
# # # if num_relatives > 0:
# # #     for i in range(num_relatives):
# # #         relation = st.selectbox(f"Relative #{i+1}", 
# # #                                 ["Parent", "Sibling", "Grandparent", "Aunt/Uncle", "Cousin"],
# # #                                 key=f"rel_{i}")
# # #         weight_map = {"Parent": 1.0, "Sibling": 0.8, "Grandparent": 0.5, "Aunt/Uncle": 0.4, "Cousin": 0.2}
# # #         relation_weights.append(weight_map[relation])
# # # DiabetesPedigreeFunction = diabetes_pedigree_function(num_relatives, relation_weights)
# # # st.caption(f"Calculated DPF: {DiabetesPedigreeFunction}")

# # # # Glucose Input or Estimate
# # # st.subheader("Glucose (Fasting) Info")
# # # know_glucose = st.radio("Do you know your glucose level?", ["Yes", "No"])
# # # symptoms_score = 0

# # # if know_glucose == "Yes":
# # #     Glucose = st.number_input("Glucose (mg/dL)", 0.0, 300.0, 100.0)
# # # else:
# # #     st.markdown("### We’ll estimate based on your health profile and symptoms")
    
# # #     # Optional Symptoms
# # #     urination = st.checkbox("Frequent urination")
# # #     thirst = st.checkbox("Increased thirst")
# # #     fatigue = st.checkbox("Fatigue")
# # #     vision = st.checkbox("Blurry vision")
    
# # #     symptoms_score = sum([urination, thirst, fatigue, vision])
# # #     Glucose = estimate_glucose(Age, bmi_result, DiabetesPedigreeFunction, symptoms_score)
# # #     st.success(f"Estimated Glucose: {Glucose} mg/dL")

# # # # Blood Pressure Input or Estimate
# # # st.subheader("Blood Pressure Info")
# # # know_bp = st.radio("Do you know your BP reading?", ["Yes", "No"])
# # # if know_bp == "No":
# # #     smoker = st.checkbox("Do you smoke?")
# # #     active = st.checkbox("Are you physically active?", value=True)
# # #     stress = st.checkbox("Do you feel high stress?", value=False)
# # #     systolic, diastolic = estimate_bp(Age, bmi_result, smoker, active, stress)
# # #     st.success(f"Estimated Systolic: {systolic}")
# # #     st.success(f"Estimated Diastolic: {diastolic}")
# # #     st.info(f"Estimated BP Category: {interpret_bp(systolic, diastolic)}")
# # #     BloodPressure = round((systolic + (2 * diastolic)) / 3, 1)  # Mean arterial pressure approximation
# # # else:
# # #     systolic = st.number_input("Systolic BP", 70.0, 250.0, 120.0)
# # #     diastolic = st.number_input("Diastolic BP", 40.0, 150.0, 80.0)
# # #     BloodPressure = st.number_input("Blood Pressure (mmHg)", 0.0, 200.0, 70.0)
# # #     st.info(f"BP Category: {interpret_bp(systolic, diastolic)}")

# # # # Skin Thickness & Insulin
# # # SkinThickness = st.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
# # # Insulin = st.number_input("Insulin (mu U/ml)", 0.0, 1000.0, 80.0)

# # # # --- Final Prediction ---
# # # if st.button("Predict Diabetes Risk"):
# # #     input_data = [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
# # #                    bmi_result, DiabetesPedigreeFunction, Age]]
# # #     scaled_input = scaler.transform(input_data)
# # #     prediction = model.predict(scaled_input)[0]
# # #     probability = model.predict_proba(scaled_input)[0][1]

# # #     st.subheader("Prediction Result")
# # #     st.success(f"Risk Score: {round(probability * 100, 2)}%")
# # #     if prediction == 1:
# # #         st.error("Prediction: Person is Diabetic.")
# # #         st.warning("Please consult a doctor.")
# # #     else:
# # #         st.success("Prediction: Person is Non-Diabetic.")
# # #         st.info("No immediate risk detected.")


# # # # import pickle
# # # # import numpy as np
# # # # import streamlit as st

# # # # st.title("Machine Learning")
# # # # st.image("Image.jpeg")
# # # # # Load model and scaler
# # # # try:
# # # #     with open('ModelForPrediction.pkl', 'rb') as model_file:
# # # #         model = pickle.load(model_file)
# # # #     with open('Standard_Scaler.pkl', 'rb') as scaler_file:
# # # #         scaler = pickle.load(scaler_file)
# # # #     st.success("Model and scaler loaded successfully!")
# # # # except FileNotFoundError:
# # # #     st.error("Model or scaler file not found. Please check and try again.")

# # # # # Input form for user data
# # # # st.subheader("Enter the following details:")

# # # # Pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, step=1)
# # # # Glucose = st.number_input("Glucose", min_value=0.0, max_value=300.0, step=1.0)
# # # # BloodPressure = st.number_input("Blood Pressure", min_value=0.0, max_value=200.0, step=1.0)
# # # # weight = st.number_input("Weight (kg)", min_value=0.0, max_value=200.0, step=0.1)
# # # # height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1)
# # # # # Function to calculate BMI
# # # # def calculate_bmi(weight_kg, height_cm):
# # # #     height_m = height_cm / 100  # Convert height to meters
# # # #     if height_m == 0:
# # # #         return 0
# # # #     bmi = weight_kg / (height_m ** 2)
# # # #     return round(bmi, 2)

# # # # # Button to calculate BMI
# # # # if st.button("Calculate BMI"):
# # # #     bmi_result = calculate_bmi(weight, height)
# # # #     st.success(f"Your BMI is: {bmi_result}")

# # # # DiabetesPedigreeFunction = st.number_input("Diabetes Pedigree Function", min_value=0.008, max_value=2.420, step=0.01)
# # # # Age = st.number_input("Age", min_value=0, max_value=100, step=1)

# # # # # Button for prediction
# # # # if st.button("Predict"):
# # # #     # Prepare the input data and scale it
# # # #     input_data = scaler.transform([[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]])
# # # #     prediction = model.predict(input_data)

# # # #     # Display the result
# # # #     if prediction[0] ==1:
# # # #         st.error("The prediction is: Person is Diabetic....")
# # # #         st.success("Please Consult With Doctor Immediately...")
      
# # # #     else:
# # # #         st.success("The prediction is: Person is Non-Diabetic....")
# # # #         st.success("Don't Warry It's Okk...")