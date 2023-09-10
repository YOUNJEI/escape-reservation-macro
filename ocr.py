import easyocr
import cv2
import time

def ocr(file, gFlag):
    reader = easyocr.Reader(['ko', 'en'], gpu=gFlag)
    img = cv2.imread(file)
    text = reader.readtext(img, detail=0)
    print(text)
    return text

# ocr GPU 여부에 따른 성능테스트
def pTest():
    flag = [True, False]
    for _ in flag:
        print(_)
        timeArr = 0.0
        loop = 10

        for i in range(0, loop):
            start = time.time()
            ocr(_)
            end = time.time()
            t = end - start
            print(str(i + 1) + ": " + str(t))
            timeArr += t
        print("avg: " + str(timeArr / loop))