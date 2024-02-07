# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import os
# аргументы парсинга(по дефолту данные хранятся в barcodes.csv)
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
	help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())
# инициализация видеопотока
print("[INFO] starting video stream...")
vs = VideoStream('rtsp://логин:пароль@адрес').start()
time.sleep(2.0)
# открыть файл(barcodes.csv) для записи
csv = open(args["output"], "w")
found = set()
# циклически перебираем кадры из видеопотока
while True:
	# взять кадр из потокового видеопотока и изменить его размер на
	#  400 пикселей(макс ширина)
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	# поиск штрих-кодов в рамке и расшифровка каждого из них
	barcodes = pyzbar.decode(frame)
	# циклически перебирать обнаруженные штрих-коды
	for barcode in barcodes:
		# рисовка ограничивающей рамки штрих-кода
		(x, y, w, h) = barcode.rect
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
		# данные штрих-кода представляют собой байтовый объект, поэтому, если мы хотим его нарисовать
		# в нашем выходном изображении нам нужно сначала преобразовать его в строку
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type
		# нарисовать данные штрих-кода и тип на изображении, запустить звуковое оповещание
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(frame, text, (x, y - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		print("[INFO] Found {} barcode: Time {}".format(text,str(datetime.datetime.now())))
		# записывает если текста штрих-кода в данный момент нет в нашем CSV-файле
		# устанавливает отметку времени + штрих-код на диск и обновление 
		if barcodeData not in found:
			csv.write("{},{}\n".format(datetime.datetime.now(),
				barcodeData))
			csv.flush()
			found.add(barcodeData)
	# Вывод фрайма
	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(1) & 0xFF
	# нажмите  q для завершения
	if key == ord("q"):
		break
print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()
