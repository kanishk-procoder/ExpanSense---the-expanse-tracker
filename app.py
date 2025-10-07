import streamlit as st
from torchgen.api.types import layoutT

from db import init_db
from utils import fetch_table, insert_record
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ExpenSense", layout="wide")
init_db()

# Navigation helper
if "nav" not in st.session_state:
    st.session_state.nav = "Home"

def navigate(page):
    st.session_state.nav = page
    st.rerun("app.py")

menu = [
    "Home", "Expense Section", "Borrow/Lend", "Credit",
    "Analytics", "Accounts", "Add Person"
]
st.sidebar.image("logo.png", width=300)
choice = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state.nav))
st.session_state.nav = choice  # sync state

# ---------------- HOME ----------------
if choice == "Home":
    st.image("logo.png", width=200)
    st.markdown("### Welcome to your personal expense tracker with multi-currency, borrowing & lending records, and smart graphs!")

    # Hyperlinks for each section
    st.markdown("#### Quick Navigation")
    for page in menu:
        st.markdown(f"- [{page}](?nav={page})")

# ---------------- ADD EXPENSE ----------------
elif choice == "Expense Section":
    st.subheader("➕ Add New Expense")
    categories = ["Food", "Travel", "Shopping", "Utilities", "Others"]
    cat = st.selectbox("Category", categories)
    amt = st.number_input("Amount", min_value=0.01)
    e_date = st.date_input("Date")

    currency = fetch_table("currency")
    accounts = fetch_table("accounts")

    currency["label"] = currency["symbol"] + " " + currency["cur_name"]
    curr_choice = st.selectbox("Currency", currency["label"])
    curr_id = int(currency[currency["label"] == curr_choice]["cur_id"])

    acc_choice = st.selectbox("Account", accounts["acc_name"])
    acc_id = int(accounts[accounts["acc_name"] == acc_choice]["acc_id"])

    if st.button("Add Expense"):
        insert_record(
            "INSERT INTO expanse (e_cat, e_date, e_amt, e_curr_id, e_acc_id) VALUES (?, ?, ?, ?, ?)",
            (cat, str(e_date), amt, curr_id, acc_id)
        )
        st.success("Expense added!")

# ---------------- BORROW/LEND ----------------
elif choice == "Borrow/Lend":
    st.subheader("💸 Borrow or Lend Money")
    mode = st.radio("Choose", ["Borrow", "Lend"])
    people = fetch_table("person")
    currency = fetch_table("currency")
    accounts = fetch_table("accounts")

    currency["label"] = currency["symbol"] + " " + currency["cur_name"]
    person = st.selectbox("Person", people["p_name"]) if not people.empty else st.warning("No persons found.")
    amount = st.number_input("Amount", min_value=0.01)
    curr_choice = st.selectbox("Currency", currency["label"])
    curr_id = int(currency[currency["label"] == curr_choice]["cur_id"])

    if mode == "Borrow":
        borrow_date = st.date_input("Borrow Date")
        repay_date = st.date_input("Repay Date")
        if st.button("Add Borrow"):
            insert_record(
                "INSERT INTO borrow (p_id, b_amt, b_curr_id, borrow_date, repay_date) VALUES (?, ?, ?, ?, ?)",
                (int(people[people["p_name"] == person]["p_id"]), amount, curr_id, str(borrow_date), str(repay_date))
            )
            st.success("Borrow record added.")
    else:
        acc_choice = st.selectbox("Account", accounts["acc_name"])
        acc_id = int(accounts[accounts["acc_name"] == acc_choice]["acc_id"])
        if st.button("Add Lending"):
            insert_record(
                "INSERT INTO lending (p_id, l_amt, l_curr_id, acc_id) VALUES (?, ?, ?, ?)",
                (int(people[people["p_name"] == person]["p_id"]), amount, curr_id, acc_id)
            )
            st.success("Lending record added.")

# ---------------- CREDIT ----------------
elif choice == "Credit":
    st.subheader("🏦 Credit Account")
    accounts = fetch_table("accounts")
    currency = fetch_table("currency")

    currency["label"] = currency["symbol"] + " " + currency["cur_name"]
    acc_choice = st.selectbox("Account", accounts["acc_name"])
    acc_id = int(accounts[accounts["acc_name"] == acc_choice]["acc_id"])
    amt = st.number_input("Amount", min_value=0.01)
    curr_choice = st.selectbox("Currency", currency["label"])
    curr_id = int(currency[currency["label"] == curr_choice]["cur_id"])
    c_date = st.date_input("Date")

    if st.button("Credit"):
        insert_record(
            "INSERT INTO credit (acc_id, c_amt, c_curr_id, c_date) VALUES (?, ?, ?, ?)",
            (acc_id, amt, curr_id, str(c_date))
        )
        st.success(f"{acc_choice} is credited with {amt} {curr_choice}.")

# ---------------- ANALYTICS ----------------
elif choice == "Analytics":
    st.subheader("📊 Analytics Dashboard")
    exp = fetch_table("expanse")
    cur = fetch_table("currency")

    if exp.empty:
        st.warning("No expenses found.")
    else:
        merged = pd.merge(exp, cur, left_on="e_curr_id", right_on="cur_id")
        merged["amt_in_inr"] = merged["e_amt"] * merged["in_inr"]
        merged["e_date"] = pd.to_datetime(merged["e_date"])

        col1, col2 = st.columns(2)

        with col1:
            st.write("### 📂 By Category")
            cat_data = merged.groupby("e_cat")["amt_in_inr"].sum().reset_index()
            cat_data = cat_data.set_index("e_cat")
            st.bar_chart(cat_data, use_container_width=True)

        with col2:
            st.write("### 📅 Over Time")
            time_data = merged.groupby("e_date")["amt_in_inr"].sum().reset_index()
            time_data = time_data.set_index("e_date")
            st.line_chart(time_data, use_container_width=True)

# ---------------- ACCOUNTS ----------------
elif choice == "Accounts":
    st.subheader("🏦 Account Management")

    tab = st.selectbox("Select Operation", ["➕ Add Account", "📋 View All Accounts", "💰 View Account Balances"])

    accounts_df = fetch_table("accounts")
    currency_df = fetch_table("currency")

    if tab == "➕ Add Account":
        acc_no = st.text_input("Account Number")
        acc_name = st.text_input("Account Name")
        if st.button("Add Account"):
            if acc_no and acc_name:
                insert_record(
                    "INSERT INTO accounts (acc_no, acc_name) VALUES (?, ?)",
                    (acc_no, acc_name)
                )
                st.success("Account added successfully!")
            else:
                st.warning("Please fill in both fields.")

    elif tab == "📋 View All Accounts":
        st.dataframe(accounts_df)

    elif tab == "💰 View Account Balances":
        credit_df = fetch_table("credit")
        exp_df = fetch_table("expanse")
        lend_df = fetch_table("lending")

        credit_df = credit_df.merge(currency_df, left_on="c_curr_id", right_on="cur_id", how="left")
        exp_df = exp_df.merge(currency_df, left_on="e_curr_id", right_on="cur_id", how="left")
        lend_df = lend_df.merge(currency_df, left_on="l_curr_id", right_on="cur_id", how="left")

        credit_df["credit_inr"] = credit_df["c_amt"] * credit_df["in_inr"]
        exp_df["exp_inr"] = exp_df["e_amt"] * exp_df["in_inr"]
        lend_df["lend_inr"] = lend_df["l_amt"] * lend_df["in_inr"]

        credits_sum = credit_df.groupby("acc_id")["credit_inr"].sum()
        exp_sum = exp_df.groupby("e_acc_id")["exp_inr"].sum()
        lend_sum = lend_df.groupby("acc_id")["lend_inr"].sum()

        balances = []
        for acc_id in accounts_df["acc_id"]:
            credited = credits_sum.get(acc_id, 0)
            spent = exp_sum.get(acc_id, 0)
            lent = lend_sum.get(acc_id, 0)
            net = credited - spent - lent
            acc_name = accounts_df[accounts_df["acc_id"] == acc_id]["acc_name"].values[0]
            balances.append({
                "Account Name": acc_name,
                "Total Credit": f"₹ {round(credited, 2)}",
                "Total Expense": f"₹ {round(spent, 2)}",
                "Total Lending": f"₹ {round(lent, 2)}",
                "Net Balance": f"₹ {round(net, 2)}"
            })

        st.dataframe(pd.DataFrame(balances))

# ---------------- PERSON ----------------
elif choice == "Add Person":
    st.subheader("🙎‍♂️ add a person")
    person_name = st.text_input("Enter Name of Person")
    person_id = st.text_input("Enter a ID you want to give to this person")
    if st.button("Add Person"):
        insert_record(
            "INSERT INTO person (p_id, p_name) VALUES (?, ?)",
            (person_id, person_name)
        )
        st.success("person added")
