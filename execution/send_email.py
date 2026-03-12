import sys
import json
import requests
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

def send_email(target_email, subject, body_text):
    service_id = os.getenv('EMAILJS_SERVICE_ID')
    template_id = os.getenv('EMAILJS_TEMPLATE_ID')
    public_key = os.getenv('EMAILJS_PUBLIC_KEY')
    private_key = os.getenv('EMAILJS_PRIVATE_KEY')

    if not all([service_id, template_id, public_key]):
        return {
            "status": "error", 
            "message": "Credenciais do EmailJS não encontradas. Configure EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY (e opcionalmente EMAILJS_PRIVATE_KEY) no arquivo .env."
        }

    url = 'https://api.emailjs.com/api/v1.0/email/send'
    
    payload = {
        'service_id': service_id,
        'template_id': template_id,
        'user_id': public_key, # O public key é enviado como user_id
        'template_params': {
            'to_email': target_email,
            'subject': subject,
            'message': body_text
        }
    }
    
    if private_key:
        payload['accessToken'] = private_key

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Lança exceção se o status não for 200 OK
        return {"status": "success", "message": f"E-mail enviado para {target_email} com sucesso via EmailJS!"}
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" - Detalhes: {e.response.text}"
        return {"status": "error", "message": f"Falha no envio do email via EmailJS: {error_msg}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Faltam dados JSON de entrada"}))
        sys.exit(1)
        
    try:
        input_data = json.loads(sys.argv[1])
        target = input_data.get('target', '')
        subject = input_data.get('subject', '')
        body = input_data.get('body', '')
        
        result = send_email(target, subject, body)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
