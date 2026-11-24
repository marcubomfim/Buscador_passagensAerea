import gradio as gr  # gradio to build the web app
import requests       # to fetch web pages
from bs4 import BeautifulSoup  # this library is to parse html
import pandas as pd   # to handle data tables
from datetime import datetime  # to add dates
import time  # import time for adding delays in requests

import threading  # for smooth background tasks
import os  # to save files
import random  # for random delays

# import retry tools to handle web errors
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FlightPriceMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Configura a sessão com headers e retry strategy"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(headers)
    
    def check_flight_price(self, origin, destination, date):
        """Verifica preços de passagens"""
        try:
            # Simular busca de preços (já que sites reais bloqueiam bots)
            time.sleep(random.uniform(1, 3))
            
            # Gerar preços simulados para demonstração
            base_price = random.randint(200, 800)
            variations = [base_price + random.randint(-50, 100) for _ in range(5)]
            
            results = []
            airlines = ["LATAM", "GOL", "Azul", "Copa Airlines", "American Airlines"]
            
            for i, price in enumerate(variations):
                results.append({
                    "Companhia": airlines[i % len(airlines)],
                    "Preço": f"R$ {price:.2f}",
                    "Data": date,
                    "Origem": origin,
                    "Destino": destination,
                    "Horário": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}"
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            return pd.DataFrame({"Erro": [str(e)]})
    
    def monitor_prices(self, origin, destination, target_date, target_price, update_interval):
        """Monitora preços continuamente"""
        results = []
        
        while True:
            df = self.check_flight_price(origin, destination, target_date)
            
            # Verificar se há preços abaixo do alvo
            for _, row in df.iterrows():
                if "Preço" in row:
                    price_str = row["Preço"].replace("R$ ", "").replace(",", ".")
                    try:
                        price = float(price_str)
                        if price <= target_price:
                            results.append(f"🎉 ALERTA: {row['Companhia']} - R$ {price:.2f} (abaixo de R$ {target_price:.2f})")
                    except:
                        pass
            
            # Aguardar antes da próxima verificação
            time.sleep(update_interval * 60)  # Converter minutos para segundos
            
            if len(results) > 10:  # Limitar resultados
                results = results[-10:]
        
        return "\n".join(results)

# Criar instância do monitor
monitor = FlightPriceMonitor()

def create_interface():
    """Cria a interface Gradio"""
    
    def check_prices(origin, destination, date):
        """Função para verificar preços uma vez"""
        return monitor.check_flight_price(origin, destination, date)
    
    def start_monitoring(origin, destination, date, target_price, interval):
        """Função para iniciar monitoramento contínuo"""
        # Em uma aplicação real, isso seria executado em background
        return f"Monitoramento iniciado para {origin} → {destination} em {date}\nPreço alvo: R$ {target_price}\nVerificando a cada {interval} minutos"
    
    # Interface Gradio
    with gr.Blocks(title="Monitor de Preços de Passagens") as demo:
        gr.Markdown("# ✈️ Monitor de Preços de Passagens")
        gr.Markdown("Monitore preços de passagens aéreas e receba alertas quando encontrar boas ofertas!")
        
        with gr.Tab("Verificar Preços"):
            with gr.Row():
                with gr.Column():
                    origin = gr.Textbox(label="Origem", placeholder="Ex: São Paulo (GRU)")
                    destination = gr.Textbox(label="Destino", placeholder="Ex: Recife (REC)")
                    date = gr.Textbox(label="Data", placeholder="Ex: 2024-02-15")
                    check_btn = gr.Button("🔍 Verificar Preços", variant="primary")
                
                with gr.Column():
                    results_df = gr.Dataframe(label="Resultados", headers=["Companhia", "Preço", "Data", "Origem", "Destino", "Horário"])
            
            check_btn.click(
                fn=check_prices,
                inputs=[origin, destination, date],
                outputs=results_df
            )
        
        with gr.Tab("Monitoramento Contínuo"):
            with gr.Row():
                with gr.Column():
                    origin_monitor = gr.Textbox(label="Origem", placeholder="Ex: São Paulo (GRU)")
                    destination_monitor = gr.Textbox(label="Destino", placeholder="Ex: Recife (REC)")
                    date_monitor = gr.Textbox(label="Data", placeholder="Ex: 2024-02-15")
                    target_price = gr.Number(label="Preço Alvo (R$)", placeholder="Ex: 300")
                    interval = gr.Slider(minimum=5, maximum=60, value=15, step=5, label="Intervalo de Verificação (minutos)")
                    monitor_btn = gr.Button("🚀 Iniciar Monitoramento", variant="primary")
                
                with gr.Column():
                    monitor_output = gr.Textbox(label="Status do Monitoramento", lines=10)
            
            monitor_btn.click(
                fn=start_monitoring,
                inputs=[origin_monitor, destination_monitor, date_monitor, target_price, interval],
                outputs=monitor_output
            )
        
        gr.Markdown("""
        ### 📝 Como usar:
        1. **Verificar Preços**: Digite origem, destino e data para ver preços atuais
        2. **Monitoramento Contínuo**: Configure alertas para preços abaixo de um valor específico
        
        ### ⚠️ Nota:
        Este é um protótipo que simula preços. Para uso real, seria necessário:
        - Integração com APIs de companhias aéreas
        - Implementação de Selenium para sites que bloqueiam bots
        - Sistema de notificações (email, WhatsApp, etc.)
        """)
    
    return demo

if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True, debug=True)