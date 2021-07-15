import requests
import selenium
from datetime import datetime
from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup
import sketches
"""
# Fill:
<img class="imgDesafio" name="imgDesafio" id="imgDesafio"> [Captcha]
<input type="text" name="txtCodigo"> [Captcha]
<input type="text" name="txtDocCNH"> [CNH]
<input type="text" name="txtDocPrincipal">] [CPF]
"""

def crawler():
	two_captcha_key = sketches.two_captcha_key
	cpf = sketches.cpf
	registro = sketches.registro
	session_cookie_key = "ASPSESSIONIDACCABAAT"
	url_detran_sc = "http://consultas.detrannet.sc.gov.br/servicos/ConsultaPontuacaoCondutor.asp"
	url_captcha_detran_sc = "http://consultas.detrannet.sc.gov.br/Servicos/BitMap.asp?{}"

#%% 
	get_response_detran = requests.get(url_detran_sc)

	session_cookies = {
		session_cookie_key: get_response_detran.cookies.get(session_cookie_key)
	}

	detran_get_request_timestamp = datetime.strptime(
		get_response_detran.headers["Date"], "%a, %d %b %Y %X %Z"
	).strftime("%s")

#%% 
	captcha_image_get_response = requests.get(
		url_captcha_detran_sc.format(detran_get_request_timestamp),
		cookies=session_cookies,
	)
	if captcha_image_get_response.status_code == 200:
		file = open("detran_captcha.png", "wb")
		for block in captcha_image_get_response:
			file.write(block)
		file.close()

		twocaptcha = TwoCaptcha(two_captcha_key)
		codigo = twocaptcha.normal("detran_captcha.png")['code']

		detran_post_response = requests.post(
			url_detran_sc,
			data={
				'txtDocCNH': registro,
				"txtDocPrincipal": cpf,
				"txtCodigo": codigo,
				"oculto": "C",
			},
			cookies=session_cookies,
		)
	
	#TODO
	soup = BeautifulSoup(detran_post_response.text, 'html.parser')
	scorediv = soup.find('div', attrs={'id':'divPontuacao'})



if __name__ == "__main__":
    crawler()

# %%
