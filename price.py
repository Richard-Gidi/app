import streamlit as st

def calculate_transaction_cost(supplier_premium, fob):
    return supplier_premium + fob

def calculate_exchange_loss(transaction_cost):
    return 0.01 * transaction_cost

def calculate_implant_losses(transaction_cost):
    return 0.0025 * transaction_cost

def calculate_ex_refinery_usdmt(transaction_cost, trade_margin, storage_fees, cbm_fees, demurrage_provision, implant_losses, exchange_loss_premium):
    return transaction_cost + trade_margin + storage_fees + cbm_fees + demurrage_provision + implant_losses + exchange_loss_premium

def calculate_ex_refinery_usdl(ex_refinery_usdmt, density):
    return ex_refinery_usdmt / (1000 / density)

def calculate_ex_refinery_ghsl(ex_refinery_usdl, spot_fx):
    return ex_refinery_usdl * spot_fx

def main():
    st.title("Ex Refinery Calculator")

    st.header("Input Parameters")
    trade_margin = st.number_input("Trade Margin", value=0.0)
    storage_fees = st.number_input("Storage Fees", value=0.0)
    cbm_fees = st.number_input("CBM Fees", value=0.0)
    demurrage_provision = st.number_input("Demurrage Provision", value=0.0)
    supplier_premium = st.number_input("Supplier Premium", value=0.0)
    fob = st.number_input("FOB", value=0.0)

    transaction_cost = calculate_transaction_cost(supplier_premium, fob)
    exchange_loss_premium = calculate_exchange_loss(transaction_cost)
    implant_losses = calculate_implant_losses(transaction_cost)
    ex_refinery_usdmt = calculate_ex_refinery_usdmt(transaction_cost, trade_margin, storage_fees, cbm_fees, demurrage_provision, implant_losses, exchange_loss_premium)

    st.header("Ex Refinery (USD/MT)")
    #st.write(ex_refinery_usdmt)

    density = st.number_input("Density of the Product", value=0.0)
    spot_fx = st.number_input("Spot Fx", value=0.0)

    ex_refinery_usdl = calculate_ex_refinery_usdl(ex_refinery_usdmt, density)
    ex_refinery_ghsl = calculate_ex_refinery_ghsl(ex_refinery_usdl, spot_fx)

    st.header("Ex Refinery (GHS/L)")
    st.write(ex_refinery_ghsl)

if __name__ == "__main__":
    main()