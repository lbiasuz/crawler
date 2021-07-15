import sys
import requests
import scrapy
from datetime import datetime
from twocaptcha import TwoCaptcha
import sketches #Complementary file containing sketches and sensitive variable values

def crawler(cpf:str, registro:str) -> dict:

	two_captcha_key = sketches.two_captcha_key
	session_cookie_key = "ASPSESSIONIDACCABAAT"
	url_detran_sc = "http://consultas.detrannet.sc.gov.br/servicos/ConsultaPontuacaoCondutor.asp"
	url_captcha_detran_sc = "http://consultas.detrannet.sc.gov.br/Servicos/BitMap.asp?{}"

	get_response_detran = requests.get(url_detran_sc)

	#Sets timestamp and session cookie required to get the captcha image
	session_cookies = {
		session_cookie_key: get_response_detran.cookies.get(session_cookie_key)
	}
	detran_get_request_timestamp = datetime.strptime(
		get_response_detran.headers["Date"], "%a, %d %b %Y %X %Z"
	).strftime("%s")

	#Request is sent to retrieve page captcha's image
	captcha_image_get_response = requests.get(
		url_captcha_detran_sc.format(detran_get_request_timestamp),
		cookies=session_cookies,
	)
	if captcha_image_get_response.status_code == 200:
		file = open("detran_captcha.png", "wb")
		for block in captcha_image_get_response:
			file.write(block)
		file.close()

		#"Decode" the image and return the value
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

		#Parses post response Html searching for required data	
		selector = scrapy.Selector(text=detran_post_response.text, type="html")
		data_arr: list = selector.xpath("//div[@id='divPontuacao']/table[last()]//td/text()").getall()
		name: str = selector.xpath("//div[@id='divDadosPontuacao']/table[position()<2]//td/text()").get()
		user_data: dict = {'cpf:':data_arr[0],'registro':data_arr[1],'periodo':data_arr[2],'Nome':name}
		
		return user_data

if __name__ == "__main__":
    print(crawler(sys.argv[1], sys.argv[2]))
