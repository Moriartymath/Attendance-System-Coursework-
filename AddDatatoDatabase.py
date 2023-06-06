
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pathlib import Path
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-f2a4c-default-rtdb.firebaseio.com/",
    'storageBucket': "attendance-system-f2a4c.appspot.com"
})

database_ref = db.reference('Students')

data = {
    "312512": {
        "name": "Volodymyr Zeleskyy",
        "major": "Law",
        "starting year": 2015,
        "total attendance": 10,
        "standing": "G",
        "year": 4,
        "last attendance time": "2019-10-12 06:42:52",
        "passed": False
    },
    "203412": {
        "name": "Valerii Zaluzhnyi",
        "major": "Military",
        "starting year": 2017,
        "total attendance": 5,
        "standing": "G",
        "year": 2,
        "last attendance time": "2019-10-12 06:42:52",
        "passed": False
    },
    "152352": {
        "name": "Elon Musk",
        "major": "Physics",
        "starting year": 2016,
        "total attendance": 11,
        "standing": "G",
        "year": 3,
        "last attendance time": "2019-10-12 06:42:52",
        "passed": False
    },
}

for key, value in data.items():
    database_ref.child(key).set(value)


for file in Path('Faces').iterdir():
    bucket = storage.bucket()
    blod = bucket.blob(f"{Path('Faces')}/{Path(file.name)}")
    blod.upload_from_filename(file)
