from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import schedule
import sys
from colorama import Fore, Back, Style, init
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def iniciar_driver():
    """Configura e inicia o WebDriver."""
    chrome_options = Options()
    arguments = [
        '--lang=pt-BR',
        '--window-size=800,600',
        '--incognito',
        '--disable-notifications'
    ]
    for argument in arguments:
        chrome_options.add_argument(argument)
    
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': 'D:\\Storage\\Desktop\\projetos selenium\\downloads',
        'download.directory_upgrade': True,
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1,
    })

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extrair_dados(driver):
    """Extrai dados de temperatura e condições do tempo do site."""
    driver.get('https://www.tempo.com/gn/3448744.htm')
    time.sleep(3)
    driver.minimize_window()

    dados = {}

    # Extraindo dados para hoje
    dados['minima_hoje'] = driver.find_elements(By.CSS_SELECTOR, 'span[class="min changeUnitT"]')[0].text if driver.find_elements(By.CSS_SELECTOR, 'span[class="min changeUnitT"]') else 'Não disponível'
    dados['maxima_hoje'] = driver.find_elements(By.CSS_SELECTOR, 'span[class="max changeUnitT"]')[0].text if driver.find_elements(By.CSS_SELECTOR, 'span[class="max changeUnitT"]') else 'Não disponível'
    dados['condicao_tempo_hoje'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d1 activo']/span[@class='col day_col']/span[@class='prediccion col']/span/img[@class='simbW']").get_attribute('alt')

    # Extraindo dados para o primeiro dia
    dados['minima_amanha'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d2']/span[@class='col day_col']/span[@class='temp']/span[@class='min changeUnitT']").text
    dados['maxima_amanha'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d2']/span[@class='col day_col']/span[@class='temp']/span[@class='max changeUnitT']").text
    dados['condicao_tempo_amanha'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d2']/span[@class='col day_col']/span[@class='prediccion col']/span/img[@class='simbW']").get_attribute('alt')

    # Extraindo dados para o segundo dia
    dados['minima_segundo_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d3']/span[@class='col day_col']/span[@class='temp']/span[@class='min changeUnitT']").text
    dados['maxima_segundo_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d3']/span[@class='col day_col']/span[@class='temp']/span[@class='max changeUnitT']").text
    dados['condicao_tempo_segundo_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d3']/span[@class='col day_col']/span[@class='prediccion col']/span/img[@class='simbW']").get_attribute('alt')

    # Extraindo dados para o terceiro dia
    dados['minima_terceiro_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d4']/span[@class='col day_col']/span[@class='temp']/span[@class='min changeUnitT']").text
    dados['maxima_terceiro_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d4']/span[@class='col day_col']/span[@class='temp']/span[@class='max changeUnitT']").text
    dados['condicao_tempo_terceiro_dia'] = driver.find_element(By.XPATH, "//ul[@class='grid-container-7 dias_w']/li[@class='grid-item dia d4']/span[@class='col day_col']/span[@class='prediccion col']/span/img[@class='simbW']").get_attribute('alt')

    return dados

def obter_datas():
    """Obtém as datas de hoje e dos próximos dias."""
    hoje = datetime.now().date()
    datas = {
        'hoje': hoje.strftime('%d-%m-%Y'),
        'amanha': (hoje + timedelta(days=1)).strftime('%d-%m-%Y'),
        'segundo_dia': (hoje + timedelta(days=2)).strftime('%d-%m-%Y'),
        'terceiro_dia': (hoje + timedelta(days=3)).strftime('%d-%m-%Y')
    }

    return datas

def criar_email(dados, datas):
    """Cria o conteúdo do e-mail com os dados extraídos."""
    mensagem = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsão do Tempo Para São José/SC</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 300px;
            max-width: 90%;
        }}
        h2 {{
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }}
        .weather-info {{
            margin-bottom: 20px;
        }}
        .weather-info h3 {{
            margin: 0 0 10px 0;
            color: #555;
        }}
        .weather-info p {{
            margin: 5px 0;
        }}
        .weather-info span {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Previsão do Tempo</h2>
        <div class="weather-info">
            <h3>Hoje</h3>
            <h3>{datas['hoje']}</h3>
            <p>Temperatura mínima: {dados['minima_hoje']}</p>
            <p>Temperatura máxima: {dados['maxima_hoje']}</p>
            <p>Descrição do Tempo: {dados['condicao_tempo_hoje']}</p>
        </div>

        <div class="weather-info">
           
            <h3>{datas['amanha']}</h3>
            <p>Temperatura mínima: {dados['minima_amanha']}</p>
            <p>Temperatura máxima: {dados['maxima_amanha']}</p>
            <p>Descrição do Tempo: {dados['condicao_tempo_amanha']}</p>
        </div>

        <div class="weather-info">
            
            <h3>{datas['segundo_dia']}</h3>
            <p>Temperatura mínima: {dados['minima_segundo_dia']}</p>
            <p>Temperatura máxima: {dados['maxima_segundo_dia']}</p>
            <p>Descrição do Tempo: {dados['condicao_tempo_segundo_dia']}</p>
        </div>

        <div class="weather-info">
           
            <h3>{datas['terceiro_dia']}</h3>
            <p>Temperatura mínima: {dados['minima_terceiro_dia']}</p>
            <p>Temperatura máxima: {dados['maxima_terceiro_dia']}</p>
            <p>Descrição do Tempo: {dados['condicao_tempo_terceiro_dia']}</p>
        </div>
    </div>
</body>
</html>
'''
    return mensagem

def enviar_email(mensagem):
    """Envia o e-mail com a previsão do tempo."""
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    mail = EmailMessage()
    mail['Subject'] = 'Tempo e Temperatura'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = EMAIL_ADDRESS
    mail.add_header('Content-Type', 'text/html')
    mail.set_payload(mensagem.encode('utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as email:
        email.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        email.send_message(mail)

    print(Back.BLUE + Fore.WHITE + "\nE-mail enviado com sucesso!" + Style.RESET_ALL)

def app_previsao_tempo(intervalo_envio):
    """Função principal para obter e enviar a previsão do tempo."""
    start_time = time.time()  # Início do contador

    driver = iniciar_driver()
    dados = extrair_dados(driver)
    datas = obter_datas()
    mensagem = criar_email(dados, datas)
    enviar_email(mensagem)
    driver.quit()

    end_time = time.time()  # Fim do contador
    print(Fore.GREEN + f"\nTempo total de execução do app:{end_time - start_time:.2f} segundos"+ Style.RESET_ALL)

    # Configura o agendamento para execução da função novamente
    schedule.every(intervalo_envio).seconds.do(lambda: app_previsao_tempo(intervalo_envio))

def mostrar_tempo_execucao():
    """Mostra o tempo total de execução em um contador ativo."""
    start_time = time.time()  # Início do contador

    try:
        while True:
            elapsed_time = time.time() - start_time
            sys.stdout.write(Fore.YELLOW + f"\rExecutando app, aguarde.....: {elapsed_time:.2f} segundos"+ Style.RESET_ALL)
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExecução interrompida.")

# Solicita ao usuário o intervalo de envio
intervalo_envio = int(input("Digite o intervalo em segundos para envio do e-mail: "))

# Configura o agendamento inicial
app_previsao_tempo(intervalo_envio)

# Inicia o contador de tempo total
mostrar_tempo_execucao()