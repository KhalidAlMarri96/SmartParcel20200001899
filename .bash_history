sudo dnf update -y
sudo dnf install python3 -y
pip3 install flask gunicorn boto3 requests --ignore-installed
sudo dnf install python3-pip -y
pip3 install flask gunicorn boto3 requests --ignore-installed
nano app.py
gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 app:app
nano lab_test.py
python3 lab_test.py
gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 app:app
exit 
python3 app.py
nano app.py
rm app.py 
nano app.py 
python3 app.py
ls 
python3 app.py 
python3 app.py
[200~aws sts get-caller-identity~
aws sts get-caller-identity
