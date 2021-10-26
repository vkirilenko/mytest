#! usr/bin/python

from pathlib import Path
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2
import sys

Path('Codes').mkdir(parents=True, exist_ok=True)
directory = '.' if not sys.argv[1:] else sys.argv[1]
new_file = Path(directory, 'Codes/recognised.csv')

csv = open(new_file, "w")
found = set()

capture = imutils.video.VideoStream(usePiCamera=True).start()
time.sleep(2)

while True:
    frame = capture.read()
    if not frame:
        print("Error: Can't get frame!")
        break

    frame = imutils.resize(frame, width=600)

    codes = pyzbar.decode(frame)

    for num, code in enumerate(codes):
        (x, y, w, h) = code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        codeData = code.data.decode("utf-8")
        codeType = code.type

        text = "{} ({})".format(codeData, codeType)
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if codeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(), codeData))
            csv.flush()
            found.add(codeData)

    cv2.imshow("Scanned code: ", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:
        break

csv.close()
cv2.destroyAllWindows()
capture.stop()
