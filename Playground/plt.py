
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

plt.figure(figsize=(12,4))
plt.subplot(1,3,1)
plt.show()

img = Image.open('download.jpg')
a = np.array(img) / 255.0
print(a)