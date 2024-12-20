from flask import Flask 
from flask import render_template
from flask import request
import pandas as pd
from flask import jsonify
import requests
import os
app = Flask(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Please set the HUGGINGFACE_API_TOKEN environment variable")
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    "Content-Type": "application/json"
}

upload_folder = 'uploads'
app.config['upload_folder']= upload_folder

def generate_data(csv_data):
    prompt = f"""Analyze the following dataset in JSON format and provide comprehensive insights:

     

    Dataset Details:
    {
        
[
  {
    "PatientId": 29872499824296,
    "AppointmentID": 5642903,
    "Gender": "F",
    "ScheduledDay": "2016-04-29T18:38:08Z",
    "AppointmentDay": "2016-04-29T00:00:00Z",
    "Age": 62,
    "Neighbourhood": "JARDIM DA PENHA",
    "Scholarship": 0,
    "Hipertension": 1,
    "Diabetes": 0,
    "Alcoholism": 0,
    "Handcap": 0,
    "SMS_received": 0,
    "No-show": "No"
  }
]
    }

    Please provide:
    1. PatientId and summary of data.
     


Respond in a clear, structured manner."""
############################################## prompt ends here #########################
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 108,  
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    try :
        response = requests.post(API_URL,headers = HEADERS, json = payload)
        if response.status_code == 200:
            generate_data = response.text
            return generate_data
        else:
            return print(f"API ERROR: {response.status_code} error :  {response.text}")
    except:
        return f"error generating data"


@app.route('/',methods= ['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = os.path.join(app.config['upload_folder'],file.filename)
            file.save(filename)
            df = pd.read_csv(filename)
            csv_data = df.head(10).to_json(orient = 'records')

            answer = generate_data(csv_data)
            
            
            return render_template('upload.html', success=True, filename=file.filename,answer = answer)

        else:
            return render_template('upload.html', error="Please upload a valid CSV file.")
    return render_template('upload.html')



if __name__ == '__main__':
    app.run(debug=True)

""" 
pass csv data file to func that preprocesses """