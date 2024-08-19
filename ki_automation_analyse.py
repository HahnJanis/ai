import streamlit as st
import numpy as np
import pandas as pd
import numpy_financial as npf
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# Festlegen des Standard-Themes direkt im Python-Code
st.set_page_config(page_title="Wirtschaftlichkeitsanalyse: KI-Automation durch KI-Assistenten", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

# App Title
st.title("Wirtschaftlichkeitsanalyse: KI-Automation durch KI-Assistenten")

# Veröffentlicht von und LinkedIn-Icon
st.markdown(
    """
    <div style='display: flex; justify-content: space-between;'>
        <div><strong>Veröffentlicht von:</strong> Janis Hahn</div>
        <div><a href='https://www.linkedin.com/in/janis-hahn-399a04276' target='_blank'><img src='https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png' width='20' height='20'></a></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Auswahl des Services
service_type = st.selectbox("Wähle den Service für die Analyse", 
                            ("KI-Assistent", "Team von KI-Assistenten"))

# Auswahl der Analyseart
analysis_type = st.selectbox("Wähle die Art der Wirtschaftlichkeitsanalyse", 
                             ("Jährlich", "Monatlich"))


# Einklappbarer Bereich für Eingabeparameter und monatliche Einsparungen
with st.expander("Eingabeparameter für die Einsparungen", expanded=False):
    hourly_wage = st.number_input("Stundenlohn (in EUR)", min_value=0.0, value=20.0, step=1.0)
    time_saved_per_day = st.number_input("Eingesparte Zeit pro Tag (in Stunden)", min_value=0.0, value=1.0, step=0.1)
    working_days_in_month = st.number_input("Arbeitstage pro Monat", min_value=0.0, value=20.0, step=1.0)

    # Berechnung der monatlichen Einsparungen
    monthly_time_saved = time_saved_per_day * working_days_in_month
    monthly_savings = monthly_time_saved * hourly_wage

    # Anzeige der Ergebnisse für monatliche Einsparungen (groß und hervorgehoben)
    st.markdown(
        f"""
        <div style="font-size: 22px; font-weight: bold; margin-bottom: 10px;">
            <div>Eingesparte Zeit pro Monat: {monthly_time_saved:.2f} Stunden</div>
            <div>Eingesparte Kosten pro Monat: {monthly_savings:,.2f} EUR</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Einklappbarer Bereich für Wirtschaftlichkeitsanalyse
with st.expander(f"Wirtschaftlichkeitsanalyse ({'Monatlich' if analysis_type == 'Monatlich' else 'Jährlich'})", expanded=False):
    investment = st.number_input("Investitionssumme (in EUR)", min_value=0.0, value=2000.0, step=100.0)
    discount_rate = st.number_input("Abzinsungssatz (in %)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

    def plot_cashflows(time_range, cashflows, analysis_type):
        fig, ax = plt.subplots(figsize=(12, 5))
        
        # Hintergrund weiß lassen
        ax.set_facecolor('white')
        ax.spines['bottom'].set_color('black')
        ax.spines['top'].set_color('black') 
        ax.spines['right'].set_color('black')
        ax.spines['left'].set_color('black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.tick_params(axis='x', colors='black')
        ax.tick_params(axis='y', colors='black')
        
        # Aufteilen der Zeitachse in Abschnitte für rot und grün
        crossing_point = np.where(cashflows >= 0)[0]
        if len(crossing_point) > 0:
            crossing_index = crossing_point[0]
            
            # Rot für die negative Phase
            ax.plot(time_range[:crossing_index+1], cashflows[:crossing_index+1], marker='o', color='red', linewidth=2, label='negativer Kapitalwert')
            
            # Grün für die positive Phase
            ax.plot(time_range[crossing_index:], cashflows[crossing_index:], marker='o', color='green', linewidth=2, label='positiver Kapitalwert')
            
            # Vertikale Linie beim ersten positiven Cashflow
            ax.axvline(x=time_range[crossing_index], color='gray', linestyle='--', linewidth=1)
        else:
            # Wenn der Cashflow nie positiv wird, alles rot
            ax.plot(time_range, cashflows, marker='o', color='red', linewidth=2, label='Kumulierte Cashflows')
        
        # Horizontale Linie bei y=0
        ax.axhline(0, color='gray', linestyle='--', linewidth=1)
        
        # Achsenbeschriftungen
        ax.set_xlabel('Monate' if analysis_type == 'Monatlich' else 'Jahre')
        ax.set_ylabel('EUR')
        
        # Legende hinzufügen
        ax.legend()

        st.pyplot(fig)  # Diagramm in der App anzeigen
        
        return fig  # Rückgabe des Figure-Objekts zur weiteren Verwendung

    if analysis_type == "Jährlich":
        analysis_years = st.number_input("Anzahl der Jahre für die Analyse", min_value=1, max_value=50, value=5, step=1)
        st.subheader("Jährliche Cashflows (in EUR)")
        cashflows = []
        for i in range(1, analysis_years + 1):
            cashflow = st.number_input(f"Cashflow Jahr {i}", min_value=0.0, value=monthly_savings * 12, step=100.0, key=f"year_{i}")
            cashflows.append(cashflow)
        npv = npf.npv(discount_rate / 100, [-investment] + cashflows)
        payback_period = np.where(np.cumsum(cashflows) >= investment)[0]
        payback_period = payback_period[0] + 1 if len(payback_period) > 0 else "Nicht innerhalb der Projektlaufzeit"
        cumulative_cashflows = np.cumsum([-investment] + cashflows)
        years_range = np.arange(0, analysis_years + 1)
        st.header("Ergebnisse der Wirtschaftlichkeitsanalyse")
        st.write(f"**Kapitalwert (NPV)**: {npv:,.2f} EUR")
        st.write(f"**Amortisationszeit**: {payback_period} Jahre")
        st.subheader("Cashflow Verlauf (Jährlich)")
        fig = plot_cashflows(years_range, cumulative_cashflows, analysis_type)

    else:
        analysis_months = st.number_input("Anzahl der Monate für die Analyse", min_value=1, max_value=600, value=6, step=1)
        st.subheader("Monatliche Cashflows (in EUR)")
        cashflows = []
        for i in range(1, analysis_months + 1):
            cashflow = st.number_input(f"Cashflow Monat {i}", min_value=0.0, value=monthly_savings, step=100.0, key=f"month_{i}")
            cashflows.append(cashflow)
        npv = npf.npv(discount_rate / 1200, [-investment] + cashflows)
        payback_period = np.where(np.cumsum(cashflows) >= investment)[0]
        payback_period = payback_period[0] + 1 if len(payback_period) > 0 else "Nicht innerhalb der Projektlaufzeit"
        cumulative_cashflows = np.cumsum([-investment] + cashflows)
        months_range = np.arange(0, analysis_months + 1)
        st.header("Ergebnisse der Wirtschaftlichkeitsanalyse")
        st.write(f"**Kapitalwert (NPV)**: {npv:,.2f} EUR")
        st.write(f"**Amortisationszeit**: {payback_period} Monate")
        st.subheader("Cashflow Verlauf (Monatlich)")
        fig = plot_cashflows(months_range, cumulative_cashflows, analysis_type)

# Angepasster PDF-Beschreibungstext mit dynamischer Amortisationszeit
amortization_label = "Jahre" if analysis_type == "Jährlich" else "Monate"

description_text = f"""
Sehr geehrte Damen und Herren,

im Rahmen unserer Untersuchung haben wir eine detaillierte Wirtschaftlichkeitsanalyse für den von Ihnen ausgewählten Service {service_type} durchgeführt. Diese Analyse hat zum Ziel, die finanziellen Einsparungen und den Kapitalwert (NPV) auf Basis der von Ihnen angegebenen Parametern zu ermitteln.

Wichtige Kennzahlen:
- Kapitalwert (NPV): {npv:,.2f} EUR
- Amortisationszeit: {payback_period} {amortization_label}
- Investitionssumme: {investment:,.2f} EUR

Die Ergebnisse zeigen klar, dass die Einführung eines KI-Assistenten erhebliche Effizienzgewinne und Kosteneinsparungen mit sich bringt. Laut einer Studie von McKinsey könnten Unternehmen durch den Einsatz von KI-basierter Automatisierung bis zu 20-30% ihrer Betriebskosten einsparen, was zu einer signifikanten Verbesserung der Profitabilität führt.

Unsere Analyse berücksichtigt sowohl die Investitionssumme als auch die abgezinsenen zukünftigen Cashflows, um Ihnen einen fundierten Überblick über den finanziellen Nutzen der Automatisierung zu bieten. Mit dieser Analyse möchten wir Ihnen eine solide Entscheidungsgrundlage für den Einsatz von KI-Technologien in Ihrem Unternehmen bieten.

Wir sind überzeugt, dass der Einsatz von KI-Assistenten nicht nur Ihre operativen Abläufe optimieren, sondern auch Ihre Wettbewerbsfähigkeit langfristig stärken wird.

Mit freundlichen Grüßen,

Janis Hahn 
"""


def create_text_pdf(service_type, description_text, npv, payback_period, investment):
    buf = BytesIO()
    with PdfPages(buf) as pdf:
        fig1, ax1 = plt.subplots(figsize=(8.27, 11.69))  # A4-Größe in Zoll (210mm x 297mm)
        ax1.axis('off')
        
        # Titel - mittig und mit weniger Abstand zum Text
        ax1.text(0.5, 0.98, f'Wirtschaftlichkeitsanalyse für {service_type}', ha='center', fontsize=16, weight='bold')
        
        # Beschreibungstext - näher an der Überschrift platziert
        ax1.text(0.05, 0.93, description_text, ha='left', va='top', wrap=True, fontsize=12)
        
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)
    return buf.getvalue()

def create_graph_pdf(fig):
    buf = BytesIO()
    with PdfPages(buf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    return buf.getvalue()

if st.button("PDFs herunterladen"):
    # Text-PDF erstellen
    text_pdf_data = create_text_pdf(service_type, description_text, npv, payback_period, investment)
    st.download_button(label="Text-PDF herunterladen", data=text_pdf_data, file_name="wirtschaftlichkeitsanalyse_text.pdf", mime="application/pdf")
    
    # Graph-PDF erstellen
    graph_pdf_data = create_graph_pdf(fig)
    st.download_button(label="Graph-PDF herunterladen", data=graph_pdf_data, file_name="wirtschaftlichkeitsanalyse_graph.pdf", mime="application/pdf")

# Sensitivitätsanalyse
st.subheader("Sensitivitätsanalyse")
sensitivity = st.slider("Ändere den Abzinsungssatz für die Sensitivitätsanalyse (%)", 0.0, 20.0, (discount_rate-2, discount_rate+2), 0.1)
if analysis_type == "Jährlich":
    npv_low = npf.npv(sensitivity[0] / 100, [-investment] + cashflows)
    npv_high = npf.npv(sensitivity[1] / 100, [-investment] + cashflows)
else:
    npv_low = npf.npv(sensitivity[0] / 1200, [-investment] + cashflows)
    npv_high = npf.npv(sensitivity[1] / 1200, [-investment] + cashflows)
st.write(f"**NPV bei {sensitivity[0]:.1f}% Abzinsungssatz:** {npv_low:,.2f} EUR")
st.write(f"**NPV bei {sensitivity[1]:.1f}% Abzinsungssatz:** {npv_high:,.2f} EUR")
