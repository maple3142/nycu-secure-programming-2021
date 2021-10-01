import cv2

ar1 = cv2.imread("flag_enc.png", cv2.IMREAD_GRAYSCALE)
ar2 = cv2.imread("golem_enc.png", cv2.IMREAD_GRAYSCALE)

h, w = ar1.shape
for i in range(h):
    for j in range(w):
        ar1[i][j] ^= ar2[i][j]


cv2.imwrite("flag.png", ar1)
