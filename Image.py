import cv2 as cv
import numpy as np
import imutils
from math import sqrt

class Image:
  def __init__(self, pixelsData, name):
    self.__img = pixelsData
    self.__name = name
    self.__contours = None
    self.__colorSpace = 'bgr'

  def show(self):
    cv.imshow(self.__name, self.__img)
    cv.waitKey(0)

  def drawCircle(self, center, radious=1, color=(0, 255, 0), thickness=2):
    cv.circle(self.__img, center, radious, color, thickness)

  def drawContours(self, contours, color=(0, 255, 0), thickness=2):
    cv.drawContours(self.__img, contours, -1, color, thickness)

  # Convert between color spaces
  def gray2bgr(self):
    if (self.__colorSpace == 'gray'):
      self.__colorSpace = 'bgr'
      self.__img = cv.cvtColor(self.__img, cv.COLOR_GRAY2BGR)
    else:
      print('Image is not at GRAY color space!')

  def bgr2gray(self):
    if (self.__colorSpace == 'bgr'):
      self.__colorSpace = 'gray'
      self.__img = cv.cvtColor(self.__img, cv.COLOR_BGR2GRAY)
    else:
      print('Image is not at BGR color space!')

  def bgr2hsv(self):
    if (self.__colorSpace == 'bgr'):
      self.__colorSpace = 'hsv'
      self.__img = cv.cvtColor(self.__img, cv.COLOR_BGR2HSV)
    else:
      print('Image is not at BGR color space!')

  def hsv2bgr(self):
    if (self.__colorSpace == 'hsv'):
      self.__colorSpace = 'bgr'
      self.__img = cv.cvtColor(self.__img, cv.COLOR_HSV2BGR)
    else:
      print('Image is not at HSV color space!')

  # Open and close morph operations

  def morphOperations(self, kernelSize, morphType):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    if morphType == 'OPEN':
      self.__img = cv.morphologyEx(self.__img, cv.MORPH_OPEN, kernel)
    elif morphType == 'CLOSE':
      self.__img = cv.morphologyEx(self.__img, cv.MORPH_CLOSE, kernel)

  # HSV filter in order to perform range segmentation on images
  def filterByHSV(self, lowerHSV, higherHSV):
    # InRange filter
    self.__img = cv.inRange(self.__img, lowerHSV, higherHSV)
    self.__colorSpace = 'gray'

  # find Countours bigger than a minimum area
  def findCountours(self, minArea):
    # ConvertToGrayScale and filter, Bilateral produced a better result than GaussianBlur
    gray = cv.bilateralFilter(self.__img, 17, 20, 20)

    # Edge algoritm
    edged = cv.Canny(gray, 100, 200)

    # we are using RECT type EXTERNAL over TREE
    cnts = cv.findContours(edged, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Sort by larger areas
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)
    # Filter to remove countours smaller than minimum area
    contours = []
    for i in range(0, len(cnts)):
      if cv.contourArea(cnts[i]) >= minArea:
        contours.append(cnts[i])

    self.__contours = contours

  def findContoursFeatures(self, requestedFeatures=['centroid', 'eccentricity', 'arcLength', 'area', 'convexHull']):
    contoursFeatures = []
    if self.__contours == None:
      raise Exception("Sorry, but you need to find image contours first ;)")
    cnts = self.__contours

    for i in range(0, len(cnts)):
      features = {}
      # Compute the centroid of the contour
      if 'centroid' in requestedFeatures:
        M = cv.moments(cnts[i])
        features['centroid'] = (
            int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

      if 'arcLength' in requestedFeatures:
        features['arcLength'] = cv.arcLength(cnts[i], True)

      if 'eccentricity' in requestedFeatures:
        # Calculate eccentricity
        (x, y), (MA, ma), angle = cv.fitEllipse(cnts[i])
        a = ma/2
        b = MA/2

        if (a > b):
          eccentricity = sqrt(pow(a, 2)-pow(b, 2))
          eccentricity = round(eccentricity/a, 2)
        else:
          eccentricity = sqrt(pow(b, 2)-pow(a, 2))
          eccentricity = round(eccentricity/b, 2)

        features['eccentricity'] = eccentricity

      if 'area' in requestedFeatures:
        features['area'] = cv.contourArea(cnts[i])

      if 'convexHull' in requestedFeatures:
        features["convexHull"] = np.squeeze(cv.convexHull(cnts[i]))

      # Append features
      contoursFeatures.append(features)
    return contoursFeatures