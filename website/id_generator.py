# from . import DateToolKit as dtk
from datetime import datetime
import datetime as dt
import random


letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
numbers = []
for x in range(10):
	numbers.append(x)

def generateTID():

    current_date = dt.date.today()
    current_time = datetime.now().strftime("%H:%M:%S")

    # Date Format: "YYYY-MM-DD"
    formatted_date = current_date.strftime("%Y-%m-%d")
    date = formatted_date
    time = current_time

    _ = f'{date}{random.choice(numbers)}{random.choice(numbers)}{random.choice(letters)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(letters)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{time}{random.choice(letters)}{random.choice(letters)}{random.choice(numbers)}{random.choice(letters)}{random.choice(numbers)}{random.choice(letters)}{random.choice(numbers)}{random.choice(letters)}'

    return _.replace("-", "").replace(":", "")

# import base64
# import imghdr
# import magic

# encoded_data = "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAACXBIWXMAAAsTAAALEwEAmpwYAAACK0lEQVR4nO2cS0oDURREayuCuos4MLpHf1vxtwl1D6IgOi9p6IiDgJ1+z9xKqg48cGCsc7uCUW46QAghhBBCCCGEdZwDuAbwAuBrPM8ArgCcrX1E6MIxgEcA/OM8ADjqExlWnAB4n3DxV2f43sXPo0PzM3+Ti786bwAO26LDwN2Mi786w6+s0PiCy8azbBFw56ZDAZfVQ+wyLx0KGP5EDTP57FDA8DPCTNjphJmkgGJSQDEpoJgUUEwKKCYFFJMCitmpAvZxU8RdKGCfN0VUL2DfN0VULsBhU0TlAhw2RVQtwGVTRNUCXDZFVC3AZVNE1QJcNkVULUBWzGVOWTGXOWXFXOaUFXOZU1bMZU5ZMZc5ZcVc5pQVc5lTVsxlThWx83/ewqnMKSd2vKUtXPWckmInW9zCpYDiLVwKKN7CpYDiLVwKKN7CpYDiLVwKKN7CpYDii5ECfpECDC8GCzJlxWiSKStGk0xZMZpkyorRJFNWjCaZsmI0yZQVo0mmrBhNMmXFaJIpK0aTTFkxmmTKitEkU1aMJpmyYjTJlBWjSaasGE0yZcVokikrRpNMWTGaZMqK0SRTVowmmbJiNMmUFaNJ5tbeJviRzPn0eKPsUzLnc92hgItkzuesQwGnyWzjtuHiD3cvJrORAwCvW/7YygOTzMksxqBNpFo/uHVhkjmZ4Ubo+wlSdx2fEUcmmRuxHG+Cexr/T/gcv76c8YI7FZfMEEIIIYQQAvaTb7k3MwcvLiYiAAAAAElFTkSuQmCC"

# decoded_data = base64.b64decode(encoded_data)
# mime_type = magic.from_buffer(decoded_data, mime=True)
# print(mime_type)

# decoded_data = base64.b64decode(encoded_data)
# image_type = imghdr.what(None, h=decoded_data)
# print(f'image/{image_type}' if image_type else '')