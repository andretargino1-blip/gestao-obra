import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="ERP Construção - Rota", layout="wide", page_icon="🏗️")

# --- BANCO DE DADOS EM MEMÓRIA (Session State) ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Quantidade', 'Unidade', 'Estoque Mínimo'])
if 'compras' not in st.session_state:
    st.session_state.compras = pd.DataFrame(columns=['ID', 'Obra', 'Fornecedor', 'Item', 'Valor', 'Status', 'Data'])
if 'obras' not in st.session_state:
    st.session_state.obras = pd.DataFrame([
        {'Obra': 'Residencial Sul', 'Orçamento': 800000.0, 'Gasto': 0.0},
        {'Obra': 'Edifício Norte', 'Orçamento': 1500000.0, 'Gasto': 0.0}
    ])

# --- NAVEGAÇÃO ---
st.sidebar.title("ERP Rota Empreendimentos")
menu = st.sidebar.selectbox("Módulos", [
    "🏠 Dashboard Gerencial",
    "🛒 Compras & Cotações",
    "💰 Financeiro",
    "📦 Estoque & Insumos",
    "🏗️ Gestão de Obras",
    "👥 Usuários & Permissões"
])

# --- MÓDULO 8: DASHBOARD ---
if menu == "🏠 Dashboard Gerencial":
    st.header("📍 Painel de Controle Operacional")
    
    c1, c2, c3 = st.columns(3)
    total_gasto = st.session_state.compras['Valor'].sum()
    c1.metric("Custo Total de Obras", f"R$ {total_gasto:,.2f}")
    c2.metric("Pedidos em Aprovação", len(st.session_state.compras[st.session_state.compras['Status'] == 'Pendente']))
    c3.metric("Obras Ativas", len(st.session_state.obras))

    st.subheader("Previsto vs Realizado por Projeto")
    fig = px.bar(st.session_state.obras, x='Obra', y=['Orçamento', 'Gasto'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO 1: COMPRAS ---
elif menu == "🛒 Compras & Cotações":
    st.header("🛒 Gestão de Aquisições")
    
    tab1, tab2 = st.tabs(["Novo Pedido", "Histórico de Compras"])
    
    with tab1:
        with st.form("form_compra"):
            col1, col2 = st.columns(2)
            obra = col1.selectbox("Obra Destino", st.session_state.obras['Obra'])
            fornecedor = col2.text_input("Fornecedor")
            item = col1.text_input("Material")
            valor = col2.number_input("Valor da Cotação (R$)", min_value=0.0)
            
            if st.form_submit_button("Gerar Pedido de Compra"):
                nova_compra = pd.DataFrame([{
                    'ID': len(st.session_state.compras)+1, 'Obra': obra, 
                    'Fornecedor': fornecedor, 'Item': item, 'Valor': valor, 
                    'Status': 'Pendente', 'Data': datetime.now().strftime("%d/%m/%Y")
                }])
                st.session_state.compras = pd.concat([st.session_state.compras, nova_compra], ignore_index=True)
                st.success("Pedido enviado para aprovação hierárquica.")

    with tab2:
        st.dataframe(st.session_state.compras, use_container_width=True)

# --- MÓDULO 3: ESTOQUE ---
elif menu == "📦 Estoque & Insumos":
    st.header("📦 Controle de Almoxarifado")
    
    with st.expander("Entrada de Material"):
        mat = st.text_input("Nome do Material")
        qtd = st.number_input("Quantidade", min_value=0)
        un = st.selectbox("Unidade", ["m³", "kg", "Un", "m²"])
        if st.button("Atualizar Estoque"):
            st.success(f"{qtd} {un} de {mat} adicionados ao inventário.")

    # Alerta de Estoque Mínimo (Lógica Simulada)
    st.warning("⚠️ Alerta: Cimento CP-II abaixo do estoque mínimo!")

# --- MÓDULO 2: FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Gestão Financeira")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contas a Pagar")
        st.table(st.session_state.compras[st.session_state.compras['Status'] == 'Aprovado'])
    
    with col2:
        st.subheader("Fluxo de Caixa Mensal")
        # Gráfico simulado
        st.line_chart([100, 150, 120, 200, 180])

# --- MÓDULO 7: USUÁRIOS ---
elif menu == "👥 Usuários & Permissões":
    st.header("🔐 Controle de Acesso")
    st.write("Configuração de perfis: Engenheiro, Comprador, Financeiro e Diretor.")
    st.checkbox("Exigir aprovação do Diretor para compras acima de R$ 5.000,00")
