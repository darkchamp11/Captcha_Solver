import requests, re, base64, unicodedata, pytesseract
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageFilter

# Set path to tesseract (adjust if different)
pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

def clean_image_noise(img):
    img = img.convert("RGBA")
    pixdata = img.load()

    # Clean noise: if pixel is black, set it to white
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = (255, 255, 255, 255)

    width, height = img.size
    new_size = width * 8, height * 8
    img = img.resize(new_size, Image.LANCZOS)
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 155 else 255, '1')
    img = img.filter(ImageFilter.MedianFilter())

    return img

def fetch_image(headers):
    response = requests.get('http://challenge01.root-me.org/programmation/ch8/', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    image_src = soup.img['src']
    base64_data = re.sub('^data:image/.+;base64,', '', image_src)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img

def get_captcha_value_and_submit(img, headers):
    headers['Referer'] = 'http://challenge01.root-me.org/programmation/ch8/'
    headers['Cookie'] = 'PHPSESSID=i0enc8t6egnc2g4h67cj0j9pq0'  # Replace with your valid session ID

    img.save("debug_captcha.png")  # Save for debugging

    config = '--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    captcha_value = pytesseract.image_to_string(img, config=config)
    captcha_value = unicodedata.normalize('NFKD', captcha_value).encode('ascii', 'ignore').decode('ascii')
    captcha_value = captcha_value.strip()

    print(f"OCR Extracted CAPTCHA: '{captcha_value}'")

    payload = {'cametu': captcha_value}
    print('Sending payload:', payload)

    response = requests.post('http://challenge01.root-me.org/programmation/ch8/', data=payload, headers=headers)
    return response.text

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    response = 'Failed'
    attempt = 0

    while 'Failed' in response:
        attempt += 1
        print(f"\nAttempt #{attempt}")
        img = fetch_image(headers)
        img = clean_image_noise(img)
        response = get_captcha_value_and_submit(img, headers)

    print("\n✅ Challenge Solved!\nResponse:")
    print(response)
