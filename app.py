import os
from flask import Flask, request, jsonify
import face_recognition
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Specify the directory where you want to save the images
save_directory = r'C:/Users/USER/Desktop/pic'

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Two image files required'})

    file1 = request.files['file1']
    file2 = request.files['file2']

    # Save file1 to specified directory
    file1_path = os.path.join(save_directory, 'file1.jpeg')
    file1.save(file1_path)

    # Save file2 to specified directory
    file2_path = os.path.join(save_directory, 'file2.jpeg')
    file2.save(file2_path)

    # Fix EXIF rotation for both images
    fix_exif_rotation(file1_path, 'file1.jpeg')
    fix_exif_rotation(file2_path, 'file2.jpeg')

    # Load images for face recognition
    picture_of_me = face_recognition.load_image_file(file1_path)
    unknown_picture = face_recognition.load_image_file(file2_path)
   
    # Perform face recognition
    my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
    unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

    results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)

    # Return results
    if results[0] == True:
        return jsonify({'result': "It's a picture of me!"})
    else:
        return jsonify({'result': "It's not a picture of me!"})
    

def fix_exif_rotation(image_path, img_name):
    image = Image.open(image_path)

    # Check if the image has EXIF orientation information
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif is not None:
            orientation = exif.get(0x0112)
            if orientation is not None:
                # Rotate the image according to the EXIF orientation tag
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)

    # Save the fixed image with correct orientation
    image.save(os.path.join(save_directory, img_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
