import streamlit as st

st.set_page_config(page_title="Singh Gas EOS Solver", page_icon="🧪", layout="centered")

GAS_DICTIONARY = {
    'AIR':  {'a': 1.33,   'b': 0.0366},
    'CO2':  {'a': 3.59,   'b': 0.0427},
    'H2O':  {'a': 5.46,   'b': 0.0305},
    'CH4':  {'a': 2.25,   'b': 0.0428},
    'N2':   {'a': 1.39,   'b': 0.0391},
    'O2':   {'a': 1.36,   'b': 0.0318},
    'HE':   {'a': 0.034,  'b': 0.0237},
    'H2':   {'a': 0.244,  'b': 0.0266},
    'NH3':  {'a': 4.17,   'b': 0.0371}
}

st.title("🧪 Singh Gas EOS Solver")
st.markdown("""Designed by Kawalpreet Chawla
This application calculates gas properties using both the **Ideal Gas Law ($PV=nRT$)** and the **Van der Waals Equation of State** for real gases, using custom Newton-Raphson numerical solvers where required.
""")

st.divider()

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Calculator Settings")
engine_choice = st.sidebar.radio("Select Equation of State:", ["Ideal Gas Law", "Van der Waals (Real Gas)"])

# Common gas constant
R = 0.08206  # L*atm/(mol*K)

# --- HOOK UP INPUTS WITH UNIT CONVERSIONS ---
def input_pressure(key_suffix):
    val = st.number_input("Pressure Value", min_value=0.0, value=1.0, step=0.1, key=f"P_{key_suffix}")
    unit = st.selectbox("Pressure Unit", ["atm", "mmHg", "Pa", "kPa"], key=f"P_unit_{key_suffix}")
    if unit == "mmHg": return val / 760
    if unit == "Pa": return val / 101325
    if unit == "kPa": return val / 101.325
    return val

def input_volume(key_suffix):
    val = st.number_input("Volume Value", min_value=0.0, value=1.0, step=0.1, key=f"V_{key_suffix}")
    unit = st.selectbox("Volume Unit", ["L", "mL"], key=f"V_unit_{key_suffix}")
    if unit == "mL": return val / 1000
    return val

def input_temperature(key_suffix):
    val = st.number_input("Temperature Value", value=298.15, step=1.0, key=f"T_{key_suffix}")
    unit = st.selectbox("Temperature Unit", ["K (Kelvin)", "°C (Celsius)", "°F (Fahrenheit)"], key=f"T_unit_{key_suffix}")
    if unit == "°C (Celsius)": return val + 273.15
    if unit == "°F (Fahrenheit)": return (val - 32) * (5 / 9) + 273.15
    return val

# --- DISPLAY OUTPUT FUNCTIONS ---
def display_pressure(P_atm):
    st.success("### 🎉 Calculated Pressure Results")
    st.metric("Atmospheres", f"{P_atm:.5f} atm")
    st.write(f"* **mmHg:** {P_atm * 760:.2f} mmHg")
    st.write(f"* **Pascals:** {P_atm * 101325:.1f} Pa")
    st.write(f"* **kiloPascals:** {P_atm * 101.325:.3f} kPa")

def display_volume(V_L):
    st.success("### 🎉 Calculated Volume Results")
    st.metric("Liters", f"{V_L:.5f} L")
    st.write(f"* **Milliliters:** {V_L * 1000:.2f} mL")

def display_temperature(T_K):
    T_C = T_K - 273.15
    T_F = (T_C * 9 / 5) + 32
    st.success("### 🎉 Calculated Temperature Results")
    st.metric("Kelvin", f"{T_K:.2f} K")
    st.write(f"* **Celsius:** {T_C:.2f} °C")
    st.write(f"* **Fahrenheit:** {T_F:.2f} °F")


# ====================================
#      IDEAL GAS LAW INTERFACE
# ====================================
if engine_choice == "Ideal Gas Law":
    st.header("Ideal Gas Calculator ($PV=nRT$)")
    solve_for = st.selectbox("Solve For:", ["Pressure (P)", "Volume (V)", "Moles (n)", "Temperature (T)"])
    
    if solve_for == "Pressure (P)":
        V = input_volume("ideal")
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_ideal_P")
        T = input_temperature("ideal")
        if V > 0: display_pressure((n * R * T) / V)
            
    elif solve_for == "Volume (V)":
        P = input_pressure("ideal")
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_ideal_V")
        T = input_temperature("ideal")
        if P > 0: display_volume((n * R * T) / P)
            
    elif solve_for == "Moles (n)":
        P = input_pressure("ideal")
        V = input_volume("ideal")
        T = input_temperature("ideal")
        if T > 0:
            n = (P * V) / (R * T)
            st.success(f"### Calculated Moles: {n:.5f} mol")
            
    elif solve_for == "Temperature (T)":
        P = input_pressure("ideal")
        V = input_volume("ideal")
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_ideal_T")
        if n > 0: display_temperature((P * V) / (n * R))

# ====================================
#    VAN DER WAALS REAL GAS INTERFACE
# ====================================
else:
    st.header("Real Gas Calculator (Van der Waals)")
    
    # Gas Lookup Menu
    gas_list = list(GAS_DICTIONARY.keys()) + ["CUSTOM GAS"]
    gas_choice = st.selectbox("Select Gas from Database:", gas_list)
    
    if gas_choice != "CUSTOM GAS":
        a = GAS_DICTIONARY[gas_choice]['a']
        b = GAS_DICTIONARY[gas_choice]['b']
        st.info(f"Loaded constants for **{gas_choice}**: $a$ = {a} $L^2\\cdot atm/mol^2$, $b$ = {b} $L/mol$")
    else:
        a = st.number_input("Enter Custom constant 'a'", min_value=0.0, value=1.0)
        b = st.number_input("Enter Custom constant 'b'", min_value=0.0, value=0.04)

    solve_for = st.selectbox("Solve For:", ["Pressure (P)", "Volume (V)", "Moles (n)", "Temperature (T)"])

    if solve_for == "Pressure (P)":
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_real_P")
        T = input_temperature("real")
        V = input_volume("real")
        if (V - n*b) > 0 and V > 0:
            P = ((n * R * T) / (V - n * b)) - (a * (n / V)**2)
            display_pressure(P, gas_choice)
            
    elif solve_for == "Volume (V)":
        P = input_pressure("real")
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_real_V")
        T = input_temperature("real")
        
        if P > 0 and n > 0:
            # Newton-Raphson for Volume
            V_guess = (n * R * T) / P
            for _ in range(100):
                f_V = P*(V_guess**3) - (P*n*b + n*R*T)*(V_guess**2) + a*(n**2)*V_guess - a*(n**3)*b
                df_V = 3*P*(V_guess**2) - 2*(P*n*b + n*R*T)*V_guess + a*(n**2)
                if df_V == 0: break
                V_new = V_guess - (f_V / df_V)
                if abs(V_new - V_guess) < 1e-7:
                    V_guess = V_new
                    break
                V_guess = V_new
            display_volume(V_guess)

    elif solve_for == "Moles (n)":
        P = input_pressure("real")
        V = input_volume("real")
        T = input_temperature("real")
        
        if P > 0 and V > 0 and T > 0:
            n_guess = (P * V) / (R * T)
            for _ in range(100):
                f_n = a*b*(n_guess**3) - a*V*(n_guess**2) + (P*V*b + R*T*V)*n_guess - P*(V**2)
                df_n = 3*a*b*(n_guess**2) - 2*a*V*n_guess + P*V*b + R*T*V
                if df_n == 0: break
                n_new = n_guess - (f_n / df_n)
                if abs(n_new - n_guess) < 1e-7:
                    n_guess = n_new
                    break
                n_guess = n_new
            st.success(f"### Calculated Real Moles for {gas_choice}: {n_guess:.5f} mol")

    elif solve_for == "Temperature (T)":
        P = input_pressure("real")
        V = input_volume("real")
        n = st.number_input("Moles (mol)", min_value=0.0, value=1.0, step=0.1, key="n_real_T")
        if n > 0 and (V - n*b) > 0 and V > 0:
            T = (P + a * (n / V)**2) * (V - n * b) / (n * R)
            display_temperature(T)