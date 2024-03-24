import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import locale
from PIL import Image
from streamlit_gsheets import GSheetsConnection
import datetime




# Imposta la configurazione della pagina
st.set_page_config(
    layout="wide",
    page_title='REPORT PLANYWAY')
            
            
            
st.title("ANALISI OPERATIVITA'")
st.markdown("_source.PL v.1.0_")


# Accedi al segreto
password_segreta = st.secrets["pass"]

# Input per la password
password_input = st.sidebar.text_input("Inserisci la password", type="password")

if password_input:
    if password_input == password_segreta:
        # Create a connection object.
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PLANYWAY")
        
        
        # Seleziona solo le colonne desiderate
        desired_columns = ["Board", "List", "Card", "Member", "Date", "StartTime", "EndTime", "DurationHours"]
        df = df[desired_columns]

  
        # Assicurati che la colonna "Date" sia interpretata come una data
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        
        # Estrai il mese e formattalo come "gg-mmmm-aaaa"
        df['Mese'] = df['Date'].dt.strftime('%B')

        # Puoi anche rimuovere l'orario dalla colonna "Date" se non ti serve più
        df['Date'] = df['Date'].dt.date
        
        # Sostituisci i valori vuoti nella colonna "Member" con "LOST"
        df['Member'].fillna('LOST', inplace=True)
        
        # Ora hai un DataFrame con la colonna "Mese", la colonna "Member" pulita, e il formato desiderato per la data
        
        # Puoi anche rimuovere le righe con valori mancanti, se necessario
        df.dropna(inplace=True)

        
        with st.expander("Preview Table"):
            st.dataframe(df)


        
        ##FILTRO MESE
        ##selected_month = st.sidebar.selectbox("Seleziona il mese", df["Mese"].unique())

        ##FILTRO PERIODO PERSONALIZZATO
        ## ATTENZIONE IO USO IL NOME VARIABILE "selected_month" per comodità così non devo modificare il nome di tutte le variabili
        
       
        today = datetime.datetime.now()
        this_year = today.year
        jan_1 = datetime.date(this_year, 1, 1)
        dec_31 = datetime.date(this_year, 12, 31)

        selected_month_filter = st.sidebar.date_input(
            "seleziona il periodo",
            (jan_1, datetime.date(this_year, 1, 7)),
            jan_1,
            dec_31,
            format="MM.DD.YYYY",)
        st.sidebar.write(selected_month_filter)
            
        
        filtered_df = df[df["Date"] == selected_month_filter]
        
        
        # Calcola la somma totale di "DurationHours"
        total_duration = filtered_df['DurationHours'].sum()
        
        
        
        # Calcola il totale in minuti e giorni
        total_duration_minutes = round(total_duration * 60,2)
        total_duration_days = round(total_duration / 24,2)
        
        # Ora hai calcolato i totali in minuti e giorni
        colA, colB, colC = st.columns(3)
        
        with colB:
            with st.container(border=True):
                st.metric(label='ORE',value=total_duration)
        with colA:
            with st.container(border=True):
                st.metric("MINUTI", total_duration_minutes)
        with colC:
            with st.container(border=True):
                st.metric("GIORNI", total_duration_days)
        
        
        
        # Creazione della selezione per il tipo di analisi
        tipo_analisi = st.sidebar.radio("Seleziona il tipo di analisi:", ["ANALISI TEAM :sunglasses:", "ANALISI LAVORAZIONI :necktie:"])
        
        # Blocco per l'ANALISI TEAM
        if tipo_analisi == "ANALISI TEAM :sunglasses:":
            st.subheader("_ANALISI TEAM_", divider="orange")
        
            # Calcola le somme di "DurationHours" basate su ogni valore unico di "Member"
            member_duration = filtered_df.groupby('Member')['DurationHours'].sum()
        
            # Distribuisci le KPI su righe con 4 colonne per riga
            col1, col2, col3, col4 = st.columns(4)
            kpi_columns = st.columns(4)
        
            for i, (member, duration) in enumerate(member_duration.items()):
                    kpi_columns[i % 4].metric(member, duration)
        
            # Crea una selezione a radio per il tipo di visualizzazione
            visualizzazione = st.radio("Seleziona il tipo di visualizzazione:", ["Bar Charts 📊", "Pie Charts 🥧"])
            if visualizzazione == "Bar Charts 📊":
                # Distribuisci i grafici a barre per ogni "Member" due a due in una colonna sotto l'altra
                members = list(member_duration.keys())
                for i in range(0, len(members), 2):
                    col1, col2 = st.columns(2)
                    member1 = members[i]
                    member_df1 = filtered_df[df['Member'] == member1]
                    fig1 = px.histogram(member_df1, x='Board', y='DurationHours', title=f'KPI per {member1}')
                    fig1.update_layout(xaxis_title="Board", yaxis_title="DurationHours")
                    col1.plotly_chart(fig1)
        
                    if i + 1 < len(members):
                        member2 = members[i + 1]
                        member_df2 = filtered_df[df['Member'] == member2]
                        fig2 = px.histogram(member_df2, x='Board', y='DurationHours', title=f'KPI per {member2}')
                        fig2.update_layout(xaxis_title="Board", yaxis_title="DurationHours")
                        col2.plotly_chart(fig2)
            elif visualizzazione == "Pie Charts 🥧":
                # Distribuisci i grafici a torta impostati come % per ogni Member
                members = list(member_duration.keys())
                for i in range(0, len(members), 2):
                    col1, col2 = st.columns(2)
                    member1 = members[i]
                    member_df1 = filtered_df[df['Member'] == member1]
                    fig1 = px.pie(member_df1, names='Board', values='DurationHours', title=f'KPI per {member1} (%)')
                    col1.plotly_chart(fig1)
        
                    if i + 1 < len(members):
                        member2 = members[i + 1]
                        member_df2 = filtered_df[df['Member'] == member2]
                        fig2 = px.pie(member_df2, names='Board', values='DurationHours', title=f'KPI per {member2} (%)')
                        col2.plotly_chart(fig2)
        
        # Blocco per l'ANALISI LAVORAZIONI
        elif tipo_analisi == "ANALISI LAVORAZIONI :necktie:":
            st.subheader("_ANALISI LAVORAZIONI_", divider="orange")
            
            # Selezione per il livello di analisi
            livello_analisi = st.radio("Seleziona il livello di analisi:", ["BOARD LEVEL", "LIST LEVEL", "CARD LEVEL"])
            
            if livello_analisi == "BOARD LEVEL":
                st.write("_ANALISI BOARD LEVEL_")
            
                # Raggruppa il DataFrame per la colonna "Board" e calcola la somma di "DurationHours" per ciascun valore unico
                board_level_data = filtered_df.groupby('Board')['DurationHours'].sum().reset_index()
        
                # Crea un grafico a barre
                fig = px.bar(board_level_data, x='Board', y='DurationHours', title='Analisi BOARD LEVEL')
                fig.update_layout(xaxis_title="Board", yaxis_title="Total DurationHours")
            
                # Visualizza il grafico
                st.plotly_chart(fig, use_container_width=True)
                
            # Visualizza la preview della tabella
                with st.expander("Anteprima dei dati utilizzati per il grafico"):
                    st.dataframe(board_level_data)
           # Codice per l'analisi a livello di "LIST LEVEL" con grafico a torta in percentuale
            # Codice per l'analisi a livello di "LIST LEVEL" con filtro per il numero di voci da visualizzare nei grafici
            elif livello_analisi == "LIST LEVEL":
                st.write("_ANALISI LIST LEVEL_")
        
                # Raggruppa il DataFrame per le colonne "List" e "Member" e calcola la somma di "DurationHours"
                list_level_data = filtered_df.groupby(['List', 'Member'])['DurationHours'].sum().reset_index()
        
                # Aggiungi un filtro per "Member"
                selected_member = st.selectbox("Seleziona un Member", list_level_data['Member'].unique())
        
                # Filtra i dati in base al Member selezionato
                list_level_data_filtered = list_level_data[list_level_data['Member'] == selected_member]
        
                # Ordina il DataFrame in base a "DurationHours" in ordine decrescente
                list_level_data_filtered = list_level_data_filtered.sort_values(by='DurationHours', ascending=False)
        
                # Calcola la percentuale per il grafico a torta
                list_level_data_filtered['Percentage'] = (list_level_data_filtered['DurationHours'] / list_level_data_filtered['DurationHours'].sum()) * 100
        
                # Crea un grafico a barre
                fig_bar = px.bar(list_level_data_filtered, x='List', y='DurationHours', title=f'Analisi LIST LEVEL - Member: {selected_member} (Bar Chart)')
                fig_bar.update_layout(xaxis_title="List", yaxis_title="Total DurationHours")
        
                # Visualizza il grafico a barre
                st.plotly_chart(fig_bar, use_container_width=True)
        
                # Crea il grafico a torta
                fig_pie = px.pie(list_level_data_filtered, names='List', values='Percentage', title=f'Analisi LIST LEVEL - Member: {selected_member} (Pie Chart in %)')
        
                # Visualizza il grafico a torta
                st.plotly_chart(fig_pie, use_container_width=True)
            # Codice per l'analisi a livello di "CARD LEVEL"
            elif livello_analisi == "CARD LEVEL":
                st.write("_ANALISI CARD LEVEL_")
        
                # Aggiungi un filtro per la selezione di "List" ordinata per "DurationHours" decrescente
                selected_list = st.selectbox("Seleziona una List", df.groupby('List')['DurationHours'].sum().reset_index().sort_values(by='DurationHours', ascending=False)['List'].tolist())
        
                # Filtra il DataFrame in base alla List selezionata
                filter_list_df = filtered_df[filtered_df['List'] == selected_list]
        
                # Crea un grafico a barre con "Card" in X e "DurationHours" in Y
                fig_bar = px.histogram(filter_list_df, x='Card', y='DurationHours', title=f'Analisi CARD LEVEL - List: {selected_list} (Bar Chart)')
                fig_bar.update_layout(xaxis_title="Card", yaxis_title="DurationHours")
        
                # Visualizza il grafico a barre principale
                st.plotly_chart(fig_bar, use_container_width=True)
        
                # Crea un secondo grafico a barre con "Member" in X, "DurationHours" in Y, e colori diversi per ogni "Member"
                member_bar_data = filter_list_df.groupby('Member')['DurationHours'].sum().reset_index()
                fig_member_bar = px.histogram(member_bar_data, x='Member', y='DurationHours', title=f'Analisi CARD LEVEL - List: {selected_list} (Member Bar Chart)', color='Member')
                fig_member_bar.update_layout(xaxis_title="Member", yaxis_title="DurationHours")
        
                # Visualizza il secondo grafico a barre
                st.plotly_chart(fig_member_bar, use_container_width=True)
