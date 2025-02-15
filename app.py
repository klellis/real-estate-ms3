import os
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_properties")
@app.route("/search")
def get_properties():
    properties = mongo.db.properties.find()
    featured = mongo.db.properties.find()
    types = mongo.db.type.find()
    return render_template("properties.html", properties=properties, featured=featured, types=types)


@app.route("/search", methods=["GET", "POST"])
def search():
    # query the database for all property types
    featured = mongo.db.properties.find()
    types = mongo.db.type.find()
    filtered_result = []
    # gets property type input from dropdown select and renders results 
    if request.method == "POST":
        property_types = request.form.get("propertytype")
        filtered_result = list(mongo.db.properties.find({'property_type' : property_types}))     
    return render_template("properties.html", types=types, properties=filtered_result, featured=featured)

# renders a new page for more info for each property listing clicked
@app.route("/property_detail/<property_id>")
def property_detail(property_id):
    property_id = mongo.db.properties.find({
        "_id": ObjectId(property_id),
    })
    return render_template("property_detail.html", property_id=property_id)
    
        
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
        }
        mongo.db.users.insert_one(register)

        # puts the user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Successfully registered")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checks if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            # ensure hashed password matches user inputed session
            if check_password_hash(
            existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Hey there, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # password invalid match
                flash(
                    " Sorry that Username and/or Password didn't match anything in our records"
                )
                return redirect(url_for("login"))

        else:
            # username invalid match
            flash(
                "Sorry that Username and/or Password didn't match anything in our records"
            )
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # gets the session user's username from the db
    username = mongo.db.users.find_one({"username": session["user"]})["username"]

    if session["user"]:
        my_properties = mongo.db.properties.find({"created_by": username})
        return render_template(
            "profile.html", username=username, my_properties=my_properties
        )

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # removes user session cookies
    flash("You've been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/list_property", methods=["GET", "POST"])
def list_property():
    if request.method == "POST":
        listing = {
            "property_type": request.form.get("property_type"),
            "price": request.form.get("price"),
            "city": request.form.get("city"),
            "bedrooms": request.form.get("bedrooms"),
            "description": request.form.get("description"),
            "img_url": request.form.getlist("img_url"),
            "created_by": session["user"],
        }
        mongo.db.properties.insert_one(listing)
        flash("Property Listing Successful!")
        return redirect(url_for("get_properties"))
    property_type = list(mongo.db.type.find().sort("property_type", 1))
    return render_template("list_property.html", property_type=property_type)


@app.route("/edit_property/<property_id>", methods=["GET", "POST"])
def edit_property(property_id):
    if request.method == "POST":
        submit= {
            "property_type": request.form.get("property_type"),
            "price": request.form.get("price"),
            "city": request.form.get("city"),
            "bedrooms": request.form.get("bedrooms"),
            "description": request.form.get("description"),
            "img_url": request.form.getlist("img_url"),
            "created_by": session["user"],
        }
        mongo.db.properties.replace_one({"_id": ObjectId(property_id)}, submit)
        flash("Property Listing Updated!")
    
    property = mongo.db.properties.find_one({"_id": ObjectId(property_id)})
    property_type = mongo.db.type.find().sort("property_type", 1)
    return render_template("edit_property.html", property=property, property_type=property_type)


@app.route("/delete_property/<property_id>")
def delete_property(property_id):
    mongo.db.properties.delete_one({"_id": ObjectId(property_id)})
    flash("Property Deleted")
    return redirect(url_for("get_properties"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
