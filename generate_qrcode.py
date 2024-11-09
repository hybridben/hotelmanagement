# generate_qrcode.py

import qrcode

# URL for the check-in route (ensure it matches your deployment)
checkin_url = 'http://localhost:5000/checkin'

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=5
)

qr.add_data(checkin_url)
qr.make(fit=True)

img = qr.make_image(fill='black', back_color='white')

# Save the QR code image to the static folder
img.save('static/qr_code.png')
print("Universal QR code generated and saved to static/qr_code.png")
