from flask import Flask, render_template
import os
import json

app = Flask(__name__)

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

@app.route('/')
def index():
    data = {}
    data_directory = os.path.join(os.getcwd(), 'DataRequestor')
    for folder in os.listdir(data_directory):
        folder_path = os.path.join(data_directory, folder)
        if os.path.isdir(folder_path):
            files_data = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    file_content = read_file_content(file_path)
                    files_data.append({'name': file_name, 'content': file_content})
            data[folder] = files_data
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
