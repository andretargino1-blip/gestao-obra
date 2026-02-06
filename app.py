import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Gestão de Obras - Rota", layout="wide", page_icon="🏗️")

# --- SIMULAÇÃO DE BANCO DE DADOS (Session State) ---
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame(columns=['Material', 'Quantidade', 'Unidade', 'Obra'])
if 'db_compras' not in st.session_state:
    st.session_state.db_compras = pd.DataFrame(columns=['ID', 'Obra', 'Fornecedor', 'Item', 'Valor', 'Status', 'Data'])
if 'db_obras' not in st.session_state:
    st.session_state.db_obras = pd.DataFrame([
        {'Obra': 'Residencial Rota 01', 'Orcado': 250000.0, 'Status': 'Em Andamento'},
        {'Obra': 'Condomínio Solar', 'Orcado': 600000.0, 'Status': 'Planejamento'}
    ])

# --- BARRA LATERAL (MENU PONTO 6) ---
with st.sidebar:
    st.title("SGO - Rota")
    st.write(f"**Usuário:** Administrador")
    menu = st.radio("Módulos", ["Dashboard", "Compras", "Financeiro", "Estoque", "Relatórios"])
    st.divider()
    if st.button("Sair"):
        st.stop()

# --- PONTO 4: RELATÓRIOS & DASHBOARD ---
if menu == "Dashboard":
    st.header("📊 Indicadores de Gestão")
    
    col1, col2, col3, col4 = st.columns(4)
    total_gasto = st.session_state.db_compras[st.session_state.db_compras['Status'] == 'Pago']['Valor'].sum()
    
    col1.metric("Gasto Total (Pago)", f"R$ {total_gasto:,.2f}")
    col2.metric("Pedidos Pendentes", len(st.session_state.db_compras[st.session_state.db_compras['Status'] == 'Pendente']))
    col3.metric("Obras Ativas", len(st.session_state.db_obras))
    col4.metric("Itens em Estoque", len(st.session_state.db_estoque))

    st.subheader("Orçado vs. Realizado (Por Obra)")
    # Integração Financeiro x Obras
    gastos_obra = st.session_state.db_compras.groupby('Obra')['Valor'].sum().reset_index()
    df_comp = pd.merge(st.session_state.db_obras, gastos_obra, on='Obra', how='left').fillna(0)
    fig = px.bar(df_comp, x='Obra', y=['Orcado', 'Valor'], barmode='group', labels={'value': 'R$', 'variable': 'Tipo'})
    st.plotly_chart(fig, use_container_width=True)

# --- PONTO 1: COMPRAS ---
elif menu == "Compras":
    st.header("🛒 Módulo de Compras")
    
    with st.expander("Novo Pedido de Compra"):
        with st.form("add_compra"):
            c1, c2 = st.columns(2)
            obra = c1.selectbox("Obra", st.session_state.db_obras['Obra'])
            fornecedor = c2.text_input("Fornecedor")
            item = c1.text_input("Material/Insumo")
            valor = c2.number_input("Valor Total (R$)", min_value=0.0)
            
            if st.form_submit_button("Gerar Pedido"):
                novo_id = len(st.session_state.db_compras) + 1
                nova_linha = pd.DataFrame([{
                    'ID': novo_id, 'Obra': obra, 'Fornecedor': fornecedor, 
                    'Item': item, 'Valor': valor, 'Status': 'Pendente', 'Data': datetime.now().strftime("%d/%m/%Y")
                }])
                st.session_state.db_compras = pd.concat([st.session_state.db_compras, nova_linha], ignore_index=True)
                st.success(f"Pedido #{novo_id} registrado!")

    st.subheader("Aprovação e Histórico")
    st.dataframe(st.session_state.db_compras, use_container_width=True)

# --- PONTO 2: FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Fluxo Financeiro")
    
    st.subheader("Contas a Pagar (Pedidos Aprovados)")
    df_financeiro = st.session_state.db_compras[st.session_state.db_compras['Status'] != 'Pago']
    
    if not df_financeiro.empty:
        for index, row in df_financeiro.iterrows():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(f"**{row['Fornecedor']}** | {row['Item']} - R$ {row['Valor']:,.2f}")
            if col_c.button("Confirmar Pagamento", key=f"pay_{row['ID']}"):
                st.session_state.db_compras.at[index, 'Status'] = 'Pago'
                st.rerun()
    else:
        st.info("Não há pagamentos pendentes.")

# --- PONTO 3: ESTOQUE ---
elif menu == "Estoque":
    st.header("📦 Controle de Estoque")
    
    with st.form("entrada_estoque"):
        st.write("Entrada Manual de Material")
        c1, c2, c3 = st.columns(3)
        mat = c1.text_input("Material")
        qtd = c2.number_input("Quantidade", min_value=0.0)
        un = c3.selectbox("Unidade", ["m³", "kg", "Unid", "m²"])
        obra_e = st.selectbox("Almoxarifado da Obra", st.session_state.db_obras['Obra'])
        
        if st.form_submit_button("Dar Entrada"):
            novo_item = pd.DataFrame([{'Material': mat, 'Quantidade': qtd, 'Unidade': un, 'Obra': obra_e}])
            st.session_state.db_estoque = pd.concat([st.session_state.db_estoque, novo_item], ignore_index=True)
            st.success("Estoque atualizado!")

    st.subheader("Saldos por Obra")
    st.table(st.session_state.db_estoque)

# --- PONTO 4: RELATÓRIOS DETALHADOS ---
elif menu == "Relatórios":
    st.header("📋 Relatórios Gerenciais")
    
    obra_f = st.selectbox("Filtrar por Obra", ["Todas"] + list(st.session_state.db_obras['Obra']))
    
    df_rel = st.session_state.db_compras
    if obra_f != "Todas":
        df_rel = df_rel[df_rel['Obra'] == obra_f]
        
    st.write(f"Exibindo dados de: **{obra_f}**")
    st.dataframe(df_rel, use_container_width=True)
    
    st.download_button("Exportar para Excel (CSV)", df_rel.to_csv().encode('utf-8'), "relatorio_obras.csv")
