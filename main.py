from flask import Flask,request,jsonify,render_template
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity,JWTManager
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
app=Flask(__name__)
app.config["MONGO_URI"]="mongodb+srv://admin:root@cluster0.mtdfqct.mongodb.net/Appoint?retryWrites=true&w=majority&appName=Cluster0"
app.config["JWT_SECRET_KEY"]="77777"
app.config["CACHE_TYPE"]='SimpleCache'
app.config["CACHE_DEFAULT_TIMEOUT"]=60
jwt=JWTManager(app)
mongo=PyMongo(app)
limiter=Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day","50 per minute"],
    storage_uri="memory://"

)
CORS(app)
cache=Cache(app)
@app.route("/")
def Welcome():
    return "Welcome to appointments"
@app.route("/website")
def website():
    return render_template("index.html")
@app.route("/login",methods=["POST"])
def login():
    data=request.get_json()
    admin=data.get("Admin")
    Admin=mongo.db.Appoint.find_one({"Admin":admin})
    if(data.get("password")==Admin["password"]):
        access=create_access_token(identity=admin)
        return jsonify(access_token=access),200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route("/all")
@jwt_required()
@limiter.limit("3 per minute")
@cache.cached(timeout=60)
def all():
    data=list(mongo.db.Appoint.find({}))
    for i in data:
        i["_id"]=str(i["_id"])
    return jsonify(data)
@app.route("/date/<date>")
@jwt_required()
@limiter.limit("3 per minute")
@cache.cached(timeout=60)
def specc(date,methods=["POST"]):
    data=list(mongo.db.Appoint.find({"date":date}))
    for i in data:
        i["_id"]=str(i["_id"])
    return jsonify(data)

@app.route("/book",methods=["POST"])
@limiter.limit("1 per minute")
def book():
    data=request.get_json()
    name=data.get("name")
    date=data.get("date")
    issue=data.get("issue")
    booking={
        "name":name,
        "date":date,
        "issue":issue
    }
    mongo.db.Appoint.insert_one(booking)
    return "Inserted"
@app.route("/name/<name>")
@limiter.limit("3 per minute")
@cache.cached(timeout=60)
@jwt_required()
def spec(name,methods=["POST"]):
    data=list(mongo.db.Appoint.find({"name":name}))
    for i in data:
        i["_id"]=str(i["_id"])
    return jsonify(data)
@app.route("/delete/<name>")
@jwt_required()
def deletee(name,methods=["DELETE"]):
    mongo.db.Appoint.delete_one({"name":name})
    return "deleted"

    



if(__name__=="__main__"):
    app.run(debug=True)
    
