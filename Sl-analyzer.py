import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Smart Shopping Analyzer", layout="wide")
st.title("🛒 Smart Shopping Analyzer")
st.markdown("Edit prices – min/max ranges are auto‑generated (±50–100). Probability and rating update instantly.")

# --- Initialize session state with your data ---
if "items_df" not in st.session_state:
    initial_data = [
        {"Item": "All Season Soap 10kg", "Price": 1100},
        {"Item": "Bella Tissue Paper", "Price": 2500},
        {"Item": "Colgate", "Price": 1000},
        {"Item": "Cooking Oil 20L", "Price": 4600},
        {"Item": "Sugar (Sukhi) 50kg", "Price": 6000},
        {"Item": "Milk (2 cans)", "Price": 5200},
        {"Item": "Rice", "Price": 3300},
        {"Item": "Drinking Chocolate", "Price": 500},
        {"Item": "Coffee", "Price": 500},
        {"Item": "Pilau Masala", "Price": 900},
        {"Item": "Jumbo (2 packs)", "Price": 600},
        {"Item": "Ushindi Paste (2)", "Price": 350},
        {"Item": "Harpic", "Price": 350},
        {"Item": "Tomato Paste", "Price": 400},
        {"Item": "Blue Band", "Price": 500},
        {"Item": "Beans 10kg", "Price": 1500},
        {"Item": "Ajab (28 bales)", "Price": 4400},
        {"Item": "Maize Flour", "Price": 600},
        {"Item": "Onions", "Price": 1800},
        {"Item": "Tomatoes", "Price": 500},
        {"Item": "Potatoes", "Price": 1500},
        {"Item": "Cabbage", "Price": 250},
        {"Item": "Gas", "Price": 2600},
        {"Item": "Bar Soap", "Price": 1000},
        {"Item": "Baking Powder", "Price": 250},
    ]
    st.session_state.items_df = pd.DataFrame(initial_data)
    st.session_state.items_df["Min"] = 0
    st.session_state.items_df["Max"] = 0

# --- Helper: generate range (±50–100) ---
def generate_range(price):
    if pd.isna(price) or price <= 0:
        return 0, 0
    lower = price - random.randint(50, 100)
    upper = price + random.randint(50, 100)
    return max(0, lower), upper

# --- Auto‑generate min/max for rows where price changed ---
def update_ranges(df):
    for idx, row in df.iterrows():
        # If min/max are zero or price changed, regenerate
        if row["Min"] == 0 or row["Max"] == 0:
            mn, mx = generate_range(row["Price"])
            df.at[idx, "Min"] = mn
            df.at[idx, "Max"] = mx
    return df

# --- Sidebar controls ---
with st.sidebar:
    st.header("Manage Items")
    new_item = st.text_input("New item name")
    new_price = st.number_input("Price", min_value=0.0, step=10.0)
    if st.button("➕ Add Item"):
        if new_item and new_price > 0:
            mn, mx = generate_range(new_price)
            new_row = pd.DataFrame([{
                "Item": new_item, "Price": new_price,
                "Min": mn, "Max": mx
            }])
            st.session_state.items_df = pd.concat(
                [st.session_state.items_df, new_row], ignore_index=True
            )
            st.rerun()
        else:
            st.warning("Enter name and price > 0")

    st.markdown("---")
    if st.button("🎲 Regenerate All Min/Max"):
        for idx in st.session_state.items_df.index:
            price = st.session_state.items_df.at[idx, "Price"]
            mn, mx = generate_range(price)
            st.session_state.items_df.at[idx, "Min"] = mn
            st.session_state.items_df.at[idx, "Max"] = mx
        st.rerun()

    st.markdown("---")
    st.header("Export")
    csv = st.session_state.items_df.to_csv(index=False)
    st.download_button("📥 Download CSV", data=csv, file_name="shopping_list.csv")

# --- Main editable table ---
st.subheader("📋 Your Shopping List – Click to Edit Prices")
edited_df = st.data_editor(
    st.session_state.items_df,
    column_config={
        "Item": st.column_config.TextColumn("Item", disabled=True),
        "Price": st.column_config.NumberColumn("Price (KSh)", min_value=0, step=10),
        "Min": st.column_config.NumberColumn("Min Price", disabled=True),
        "Max": st.column_config.NumberColumn("Max Price", disabled=True),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
)

# --- Process edited data ---
if not edited_df.equals(st.session_state.items_df):
    # Detect which rows have price changes to regenerate min/max
    for idx in edited_df.index:
        old_price = st.session_state.items_df.at[idx, "Price"] if idx < len(st.session_state.items_df) else None
        new_price = edited_df.at[idx, "Price"]
        if old_price != new_price or edited_df.at[idx, "Min"] == 0:
            mn, mx = generate_range(new_price)
            edited_df.at[idx, "Min"] = mn
            edited_df.at[idx, "Max"] = mx
    st.session_state.items_df = edited_df
    st.rerun()

# --- Calculations ---
df = st.session_state.items_df.copy()
df = df[df["Min"] > 0]  # Only rows with valid ranges

if not df.empty:
    df["Range"] = df["Max"] - df["Min"]
    df["Position"] = (df["Price"] - df["Min"]) / df["Range"]
    df["Position"] = df["Position"].clip(0, 1)

    df["Prob Good Deal (%)"] = (1 - df["Position"]) * 100
    df["Prob Cheaper Exists (%)"] = df["Position"] * 100

    def rating(prob):
        if prob >= 70:
            return "✅ Good"
        elif prob >= 40:
            return "⚖️ Average"
        else:
            return "❌ Expensive"
    df["Deal Rating"] = df["Prob Good Deal (%)"].apply(rating)

    # --- Display analysis table ---
    st.subheader("📊 Deal Analysis")
    display_cols = ["Item", "Price", "Min", "Max", "Prob Good Deal (%)", "Prob Cheaper Exists (%)", "Deal Rating"]
    st.dataframe(
        df[display_cols].style.format({
            "Price": "{:.0f}", "Min": "{:.0f}", "Max": "{:.0f}",
            "Prob Good Deal (%)": "{:.0f}", "Prob Cheaper Exists (%)": "{:.0f}"
        }),
        use_container_width=True,
        hide_index=True,
    )

    # --- Summary totals ---
    total_min = df["Min"].sum()
    total_max = df["Max"].sum()
    total_your = df["Price"].sum()
    overall_pos = (total_your - total_min) / (total_max - total_min) if total_max > total_min else 0.5
    overspend_prob = overall_pos * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Min Possible Total", f"{total_min:,.0f}")
    col2.metric("💸 Max Possible Total", f"{total_max:,.0f}")
    col3.metric("🧾 Your Total", f"{total_your:,.0f}")
    col4.metric("⚠️ Overspend Probability", f"{overspend_prob:.1f}%")

    if overspend_prob < 40:
        st.success("✅ Overall: You're getting a great deal!")
    elif overspend_prob < 70:
        st.warning("⚖️ Overall: Moderate – check 'Expensive' items below.")
    else:
        st.error("🔴 Overall: You're likely overpaying – seek better prices.")

    # --- Highlight best & worst ---
    st.subheader("🔍 Best & Risky Purchases")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**✅ Best Deals**")
        best = df[df["Deal Rating"].str.contains("Good")]
        if not best.empty:
            for _, row in best.iterrows():
                st.write(f"- {row['Item']}: {row['Price']:.0f} (Good deal probability {row['Prob Good Deal (%)']:.0f}%)")
        else:
            st.write("None")
    with colB:
        st.markdown("**❌ Risky / Expensive**")
        worst = df[df["Deal Rating"].str.contains("Expensive")]
        if not worst.empty:
            for _, row in worst.iterrows():
                st.write(f"- {row['Item']}: {row['Price']:.0f} (Cheaper exists {row['Prob Cheaper Exists (%)']:.0f}%)")
        else:
            st.write("None")
else:
    st.info("Add items or generate min/max ranges to see analysis.")
